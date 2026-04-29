import json
import os

from nvoip import NvoipClient


client = NvoipClient(base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v2"))

response = client.send_otp(
    payload={
        "sms": os.getenv("NVOIP_TARGET_NUMBER", "11999999999"),
    },
    napikey=os.environ["NVOIP_NAPIKEY"],
)

print(json.dumps(response, indent=2, ensure_ascii=False))
