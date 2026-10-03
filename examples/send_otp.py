import json
import os

from nvoip import NvoipClient


client = NvoipClient(base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v3"), oauth_client_id=os.environ["NVOIP_OAUTH_CLIENT_ID"], oauth_client_secret=os.environ["NVOIP_OAUTH_CLIENT_SECRET"])

oauth = client.create_client_credentials_token()

response = client.send_otp(
    payload={
        "phoneNumber": os.environ["NVOIP_TARGET_NUMBER"],
        "methods": {"sms": True},
    },
    access_token=oauth["access_token"],
)

print(json.dumps(response, indent=2, ensure_ascii=False))
