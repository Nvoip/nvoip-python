import json
import os

from nvoip import NvoipClient


client = NvoipClient(
    base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v2"),
    oauth_basic_auth=os.getenv("NVOIP_OAUTH_BASIC_AUTH"),
    oauth_client_id=os.getenv("NVOIP_OAUTH_CLIENT_ID"),
    oauth_client_secret=os.getenv("NVOIP_OAUTH_CLIENT_SECRET"),
)
oauth = client.create_access_token(
    numbersip=os.environ["NVOIP_NUMBERSIP"],
    user_token=os.environ["NVOIP_USER_TOKEN"],
)

response = client.list_whatsapp_templates(oauth["access_token"])
print(json.dumps(response, indent=2, ensure_ascii=False))
