import json
import os

from nvoip import NvoipClient


client = NvoipClient(
    base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v3"),
    oauth_client_id=os.getenv("NVOIP_OAUTH_CLIENT_ID"),
    oauth_client_secret=os.getenv("NVOIP_OAUTH_CLIENT_SECRET"),
)

response = client.create_client_credentials_token()

print(json.dumps(response, indent=2, ensure_ascii=False))
