from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen
from urllib.error import HTTPError


class NvoipError(RuntimeError):
    def __init__(self, status: int, payload: Any):
        super().__init__(f"Nvoip request failed with status {status}")
        self.status = status
        self.payload = payload


@dataclass(slots=True)
class NvoipClient:
    base_url: str = "https://api.nvoip.com.br/v3"
    oauth_client_id: str | None = None
    oauth_client_secret: str | None = None

    @staticmethod
    def encode_basic_auth(client_id: str, client_secret: str) -> str:
        raw = (
            f"{quote_plus(client_id)}:"
            f"{quote_plus(client_secret)}"
        ).encode()
        return base64.b64encode(raw).decode()

    def create_client_credentials_token(self) -> dict[str, Any]:
        return self._request(
            "POST",
            "https://api.nvoip.com.br/auth/oauth2/token",
            body=urlencode(
            {
                    "grant_type": "client_credentials",
                }
            ).encode(),
            headers={
                "Authorization": f"Basic {self._resolve_basic_auth()}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "https://api.nvoip.com.br/auth/oauth2/token",
            body=urlencode(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }
            ).encode(),
            headers={
                "Authorization": f"Basic {self._resolve_basic_auth()}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    def get_balance(self, access_token: str) -> dict[str, Any]:
        return self._request(
            "GET",
            "/balance",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def send_sms(
        self,
        number_phone: str,
        message: str,
        access_token: str,
        flash_sms: bool = False,
    ) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/sms",
            {
                "numberPhone": number_phone,
                "message": message,
                "flashSms": flash_sms,
            },
            access_token=access_token,
        )

    def create_call(self, caller: str, called: str, access_token: str) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/calls/",
            {"caller": caller, "called": called},
            access_token=access_token,
        )

    def get_call(
        self,
        call_id: str,
        access_token: str,
    ) -> dict[str, Any]:
        query = urlencode({"callId": call_id})
        return self._request(
            "GET",
            f"/calls?{query}",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def send_otp(
        self,
        payload: dict[str, Any],
        access_token: str,
    ) -> dict[str, Any]:
        return self._request_json("POST", "/otp", payload, access_token=access_token)

    def check_otp(self, code: str, key: str, access_token: str) -> dict[str, Any]:
        query = urlencode({"code": code, "key": key})
        return self._request("GET", f"/check/otp?{query}", headers={"Authorization": f"Bearer {access_token}"})

    def list_whatsapp_templates(self, access_token: str) -> dict[str, Any]:
        return self._request(
            "GET",
            "/wa/listTemplates",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    def send_whatsapp_template(self, payload: dict[str, Any], access_token: str) -> dict[str, Any]:
        return self._request_json(
            "POST",
            "/wa/sendTemplates",
            payload,
            access_token=access_token,
        )

    def _resolve_basic_auth(self) -> str:
        if self.oauth_client_id and self.oauth_client_secret:
            return self.encode_basic_auth(self.oauth_client_id, self.oauth_client_secret)

        raise RuntimeError("Missing OAuth client credentials. Configure oauth_client_id + oauth_client_secret.")

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
        access_token: str,
    ) -> dict[str, Any]:
        return self._request(
            method,
            path,
            body=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {access_token}",
            },
        )

    def _request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        url = path if path.startswith("http") else self.base_url.rstrip("/") + path

        request = Request(
            url,
            data=body,
            method=method,
            headers={"User-Agent": "Nvoip-Python/3.0.1"},
        )
        for key, value in (headers or {}).items():
            request.add_header(key, value)

        try:
            response = urlopen(request, timeout=30)
        except HTTPError as error:
            response = error

        with response as stream:
            raw = stream.read().decode()
            try:
                data = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                data = {"raw": raw}

            if stream.status >= 400:
                raise NvoipError(stream.status, data)

            return data
