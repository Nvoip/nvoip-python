import json
import os

from nvoip import NvoipClient


client = NvoipClient(base_url=os.getenv("NVOIP_BASE_URL", "https://api.nvoip.com.br/v2"))
oauth = client.create_access_token(
    numbersip=os.environ["NVOIP_NUMBERSIP"],
    user_token=os.environ["NVOIP_USER_TOKEN"],
)

response = client.get_balance(oauth["access_token"])
print(json.dumps(response, indent=2, ensure_ascii=False))
