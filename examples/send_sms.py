import json
import os

from nvoip import NvoipClient


client = NvoipClient(base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v2"))
oauth = client.create_access_token(
    numbersip=os.environ["NVOIP_NUMBERSIP"],
    user_token=os.environ["NVOIP_USER_TOKEN"],
)

response = client.send_sms(
    number_phone=os.getenv("NVOIP_TARGET_NUMBER", "11999999999"),
    message=os.getenv("NVOIP_SMS_MESSAGE", "Mensagem de teste Nvoip"),
    access_token=oauth["access_token"],
)

print(json.dumps(response, indent=2, ensure_ascii=False))
