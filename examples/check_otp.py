import json
import os

from nvoip import NvoipClient


client = NvoipClient(base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v2"))

response = client.check_otp(
    code=os.environ["NVOIP_OTP_CODE"],
    key=os.environ["NVOIP_OTP_KEY"],
)

print(json.dumps(response, indent=2, ensure_ascii=False))
