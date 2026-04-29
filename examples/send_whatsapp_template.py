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

payload = {
    "idTemplate": os.environ["NVOIP_WA_TEMPLATE_ID"],
    "destination": os.getenv("NVOIP_WA_DESTINATION", os.getenv("NVOIP_TARGET_NUMBER", "11999999999")),
    "instance": os.environ["NVOIP_WA_INSTANCE"],
    "language": os.getenv("NVOIP_WA_LANGUAGE", "pt_BR"),
}

body_variables = json.loads(os.getenv("NVOIP_WA_BODY_VARIABLES", "[]"))
header_variables = json.loads(os.getenv("NVOIP_WA_HEADER_VARIABLES", "[]"))

if body_variables:
    payload["bodyVariables"] = body_variables

if header_variables:
    payload["headerVariables"] = header_variables

if os.getenv("NVOIP_WA_TO_FLOW", "false").lower() == "true":
    payload["functions"] = {"to_flow": True}

response = client.send_whatsapp_template(payload, oauth["access_token"])
print(json.dumps(response, indent=2, ensure_ascii=False))
