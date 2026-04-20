# :email: Filtro de spam no Gmail automatizado

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Status](https://img.shields.io/badge/Status-Concluído-success.svg)

---

 ## :mailbox_with_mail: Sobre 
Este projeto foi desenvolvido com o objetivo de aprimorar a filtragem de e-mails indesejados em contas do Gmail de forma automatizada. Embora a plataforma já disponha de mecanismos nativos de detecção de spam, esta aplicação permite a personalização do processo por meio da definição de frases específicas a serem identificadas no corpo das mensagens.

A partir dessas regras personalizadas, e-mails que contenham determinados padrões são automaticamente direcionados para a caixa de spam. No contexto deste projeto, foram utilizadas como base frases comumente presentes em respostas automáticas de processos seletivos que indicam reprovação, como: “não daremos seguimento à sua candidatura” e “decidimos seguir com outros candidatos”.

---

## 🔄 Fluxo da aplicação

A aplicação realiza a autenticação na conta do Gmail por meio do protocolo OAuth 2.0 e, em seguida, coleta o conteúdo dos 100 e-mails mais recentes da caixa de entrada. Após a normalização do texto, são aplicadas regras de verificação com base em padrões previamente definidos. Caso alguma correspondência seja identificada, o e-mail é automaticamente movido para a caixa de spam.

Todo esse processo é executado de forma automatizada por meio de rotinas agendadas, ocorrendo diariamente em dois horários: às 8h e às 23h.

---

## 🔐 Configuração

Para utilizar a aplicação, é necessário configurar as credenciais da API do Google:

1. Crie um projeto no Google Cloud Console  
2. Ative a Gmail API  
3. Gere as credenciais OAuth 2.0  
4. Baixe o arquivo `credentials.json` e adicione ao projeto  

Na primeira execução, será solicitado o login para autorização de acesso à conta.

---

## ⚙️ Como instalar?
Para configurar o ambiente de desenvolvimento, recomenda-se a utilização de um ambiente virtual (venv), garantindo o isolamento das dependências do projeto.
1. Criação e ativação do ambiente virtual
```bash
py -m venv venv
source venv/Scripts/activate
```

2. Instalação das dependências
Após a ativação do ambiente virtual, instale as bibliotecas necessárias listadas no arquivo [`requirements.txt`](./requirements.txt) com o seguinte comando:
```bash
pip install -r requirements.txt
```

---

## 🔨 Tecnologias Utilizadas

**Linguagem:**

* Python 3.9+

**Bibliotecas e módulos principais:**

* **Padrão da linguagem (Standard Library):**

  * `os` – manipulação de sistema de arquivos e variáveis de ambiente
  * `base64` – decodificação de conteúdos de e-mail
  * `logging` – registro e monitoramento de eventos da aplicação
  * `re` – processamento e busca de padrões com expressões regulares
  * `unicodedata` – normalização de caracteres Unicode
  * `datetime` – manipulação de datas e horários

* **Integração com APIs do Google:**

  * `google-auth` – autenticação com serviços do Google
  * `google-auth-oauthlib` – fluxo de autenticação OAuth 2.0
  * `google-api-python-client` – construção e consumo da API do Gmail

* **Automação e CI/CD:**

  * GitHub Actions – execução automatizada da aplicação em intervalos programados

---
