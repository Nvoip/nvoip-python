import json
import os

from nvoip import NvoipClient


client = NvoipClient(
    base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v2"),
    oauth_client_id=os.getenv("NVOIP_OAUTH_CLIENT_ID"),
    oauth_client_secret=os.getenv("NVOIP_OAUTH_CLIENT_SECRET"),
)
oauth = client.create_access_token(
    numbersip=os.environ["NVOIP_NUMBERSIP"],
    user_token=os.environ["NVOIP_USER_TOKEN"],
)

response = client.create_call(
    caller=os.environ["NVOIP_CALLER"],
    called=os.getenv("NVOIP_TARGET_NUMBER", "11999999999"),
    access_token=oauth["access_token"],
)

print(json.dumps(response, indent=2, ensure_ascii=False))
