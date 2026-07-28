import json
import os
import re

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
    "instance": os.environ["NVOIP_WA_INSTANCE"],
    "language": os.getenv("NVOIP_WA_LANGUAGE", "pt_BR"),
}

recipient_type = os.getenv("NVOIP_WA_RECIPIENT_TYPE", "").strip().lower()
recipient_value = os.getenv("NVOIP_WA_RECIPIENT_VALUE", "").strip()
if recipient_type:
    if recipient_type not in {"phone", "bsuid", "parent_bsuid"} or not recipient_value:
        raise ValueError("NVOIP_WA_RECIPIENT_TYPE must be phone, bsuid or parent_bsuid and requires NVOIP_WA_RECIPIENT_VALUE")
    if recipient_value.startswith("@"):
        raise ValueError("@username is not a WhatsApp recipient; use a BSUID or parent BSUID")
    if recipient_type == "phone" and not re.fullmatch(r"\+?[0-9]{8,20}", recipient_value):
        raise ValueError("A phone recipient must contain only an optional leading + and 8 to 20 digits")
    if recipient_type != "phone" and (any(char.isspace() for char in recipient_value) or len(recipient_value) > 256):
        raise ValueError("A BSUID must be an opaque value without whitespace (maximum 256 characters)")
    payload["recipient"] = {"type": recipient_type, "value": recipient_value}
else:
    destination = os.getenv("NVOIP_WA_DESTINATION", os.getenv("NVOIP_TARGET_NUMBER", ""))
    if not re.fullmatch(r"\+?[0-9]{8,20}", destination):
        raise ValueError("NVOIP_WA_DESTINATION must be a phone number; use recipient for BSUID")
    payload["destination"] = destination

body_variables = json.loads(os.getenv("NVOIP_WA_BODY_VARIABLES", "[]"))
header_variables = json.loads(os.getenv("NVOIP_WA_HEADER_VARIABLES", "[]"))

if body_variables:
    payload["bodyVariables"] = body_variables

if header_variables:
    payload["headerVariables"] = header_variables

if os.getenv("NVOIP_WA_TO_FLOW", "false").lower() == "true":
    if recipient_type in {"bsuid", "parent_bsuid"}:
        raise ValueError("WhatsApp Flow and attendance require a phone recipient")
    payload["functions"] = {"to_flow": True}

response = client.send_whatsapp_template(payload, oauth["access_token"])
print(json.dumps(response, indent=2, ensure_ascii=False))
