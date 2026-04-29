# nvoip-python

Cliente Python simples para a API v2 da Nvoip, com foco nos fluxos principais de autenticacao, ligacoes, OTP e WhatsApp.

## Requisitos

- Python 3.10+

## Configuracao

```bash
export NVOIP_NUMBERSIP="seu_numbersip"
export NVOIP_USER_TOKEN="seu_user_token"
export NVOIP_OAUTH_CLIENT_ID="seu_client_id"
export NVOIP_OAUTH_CLIENT_SECRET="seu_client_secret"
export NVOIP_CALLER="1049"
export NVOIP_TARGET_NUMBER="11999999999"
```

Se a sua operacao ja armazena o header serializado, voce tambem pode enviar:

```bash
export NVOIP_OAUTH_BASIC_AUTH="basic_auth_base64"
```

## Fluxos cobertos

- gerar `access_token`
- renovar token
- consultar saldo
- enviar SMS
- realizar chamada
- enviar OTP
- validar OTP
- listar templates de WhatsApp
- enviar template de WhatsApp

## Exemplos

- `python3 examples/create_access_token.py`
- `python3 examples/get_balance.py`
- `python3 examples/create_call.py`
- `python3 examples/send_sms.py`
- `python3 examples/send_otp.py`
- `python3 examples/check_otp.py`
- `python3 examples/list_whatsapp_templates.py`
- `python3 examples/send_whatsapp_template.py`

## SDK web

Para o fluxo de popup com telefone e codigo, use o repositório `nvoip-web-sdk`. Este repo cobre o consumo server-side da API.

## Documentacao oficial

- https://nvoip.docs.apiary.io/
- https://www.nvoip.com.br/api
