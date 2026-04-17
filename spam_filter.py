import os
import base64
import logging
import re
import unicodedata
import unicodedata
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SPAM_PHRASES = [
    "não daremos seguimento",
    "decidimos seguir com",
    "optamos por seguir com outro(a)",
    "a posição não está mais disponível"    
]

# ─────────────────────────────────────────────
# Configurações
# ─────────────────────────────────────────────

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = "secret.json"
TOKEN_FILE = "token.json"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("spam_filter.log"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger(__name__)


# ─────────────────────────────────────────────
# Funções
# ─────────────────────────────────────────────

#Faz a autenticação com o oauth do google para acessar o gmail.
def authenticate():   
    creds = None
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_FILE, "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)

#Recebendo um serviço e um id, extrai todo o texto do email.
def get_email_text(service, msg_id):
    try:
        msg = service.users().messages().get(
            userId="me", id=msg_id, format="full"
        ).execute()

        headers = msg["payload"].get("headers", [])
        subject = next(
            (h["value"] for h in headers if h["name"].lower() == "subject"), ""
        )
        sender = next(
            (h["value"] for h in headers if h["name"].lower() == "from"), ""
        )

        body = extract_body(msg["payload"])
        full_text = f"{subject} {body}"
        return full_text, subject, sender

    except Exception as e:
        log.error(f"Erro ao obter email {msg_id}: {e}")
        return "", "", ""  # <-- retorno seguro em vez de None

#Ajusta o texto para evitar problemas quando comparar strings. A função deixa as letras minusculas, remove acentos e espaços.    
def normalize_text(text):    
    text = unicodedata.normalize("NFKD", text)    
    text = re.sub(r"\s+", " ", text)
    return text.lower().strip()

#Retorna a frase de spam ou nulo se não encontrar nada.
def contains_spam_phrase(text):
    """Retorna a frase detectada ou None."""
    normalized = normalize_text(text)
    for phrase in SPAM_PHRASES:
        if normalize_text(phrase) in normalized:
            return phrase
    return None

#Extrai e retorna o texto completo de um e-mail, decodificando e limpando HTML.
def extract_body(part):
    result = ""
    mime = part.get("mimeType", "")
    if mime in ("text/plain", "text/html") and part.get("body", {}).get("data"):
        data = part["body"]["data"]
        decoded = base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="ignore")
        if mime == "text/html":
            # Remove tags HTML
            decoded = re.sub(r"<[^>]+>", " ", decoded)
        result += decoded
    for subpart in part.get("parts", []):
        result += extract_body(subpart)
    return result

#Move o email para SPAM (adiciona label SPAM, remove INBOX).
def mark_as_spam(service, msg_id):    
    service.users().messages().modify(
        userId="me",
        id=msg_id,
        body={
            "addLabelIds": ["SPAM"],
            "removeLabelIds": ["INBOX"],
        },
    ).execute()

#Função principal que executa todas as anteriores além de armazenar em logs todo o processo. 
def run_filter():
    log.info("=" * 50)
    log.info(f"Iniciando verificação — {datetime.now().strftime('%d/%m/%Y %H:%M')}")

    service = authenticate()
   
    results = service.users().messages().list(
        userId="me",
        labelIds=["INBOX"],
        maxResults=100, 
    ).execute()

    messages = results.get("messages", [])
    log.info(f"{len(messages)} email(s) encontrado(s) na caixa de entrada")

    spam_count = 0
    for msg in messages:
        try:
            text, subject, sender = get_email_text(service, msg["id"])
            #print(f"De: {sender} | Assunto: {subject}") 
            detected = contains_spam_phrase(text)

            if detected:
                mark_as_spam(service, msg["id"])
                spam_count += 1
                log.info(f'[SPAM] De: {sender} | Assunto: "{subject}" | Frase: "{detected}"')

        except Exception as e:
            log.error(f"Erro ao processar mensagem {msg['id']}: {e}")

    log.info(f"Concluído — {spam_count} email(s) movido(s) para SPAM")
    log.info("=" * 50)


if __name__ == "__main__":
    run_filter()