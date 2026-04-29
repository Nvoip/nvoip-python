# nvoip-python

Cliente Python simples para a API v2 da Nvoip.

## Requisitos

- Python 3.10+

## Fluxos cobertos

- gerar `access_token`
- renovar token
- consultar saldo
- enviar SMS
- realizar chamada
- consultar chamada
- enviar OTP
- listar templates de WhatsApp
- enviar template de WhatsApp

## Configuração

```bash
export NVOIP_NUMBERSIP="seu_numbersip"
export NVOIP_USER_TOKEN="seu_user_token"
export NVOIP_TARGET_NUMBER="11999999999"
export NVOIP_SMS_MESSAGE="Mensagem de teste Nvoip"
```

## Exemplos

Enviar SMS:

```bash
python3 examples/send_sms.py
```

Consultar saldo:

```bash
python3 examples/get_balance.py
```

## Documentação oficial

- https://nvoip.docs.apiary.io/
- https://www.nvoip.com.br/api
