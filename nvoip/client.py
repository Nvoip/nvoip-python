from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class NvoipError(RuntimeError):
    def __init__(self, status: int, payload: Any):
        super().__init__(f"Nvoip request failed with status {status}: {payload}")
        self.status = status
        self.payload = payload


@dataclass(slots=True)
class NvoipClient:
    base_url: str = "https://api.nvoip.com.br/v2"

    BASIC_AUTH = "TnZvaXBBcGlWMjpUblp2YVhCQmNHbFdNakl3TWpFPQ=="

    def create_access_token(self, numbersip: str, user_token: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/oauth/token",
            body=urlencode(
                {
                    "username": numbersip,
                    "password": user_token,
                    "grant_type": "password",
                }
            ).encode(),
            headers={
                "Authorization": f"Basic {self.BASIC_AUTH}",
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )

    def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/oauth/token",
            body=urlencode(
                {
                    "grant_type": "refresh_token",
                    "refresh_token": refresh_token,
                }
            ).encode(),
            headers={
                "Authorization": f"Basic {self.BASIC_AUTH}",
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
        flash_sms: bool = False,
        access_token: str | None = None,
        napikey: str | None = None,
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
            napikey=napikey,
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
        access_token: str | None = None,
        napikey: str | None = None,
    ) -> dict[str, Any]:
        query = urlencode({"callId": call_id, **({"napikey": napikey} if napikey else {})})
        return self._request(
            "GET",
            f"/calls?{query}",
            headers={"Authorization": f"Bearer {access_token}"} if access_token else {},
        )

    def send_otp(
        self,
        payload: dict[str, Any],
        access_token: str | None = None,
        napikey: str | None = None,
    ) -> dict[str, Any]:
        return self._request_json("POST", "/otp", payload, access_token=access_token, napikey=napikey)

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

    def _request_json(
        self,
        method: str,
        path: str,
        payload: dict[str, Any],
        access_token: str | None = None,
        napikey: str | None = None,
    ) -> dict[str, Any]:
        return self._request(
            method,
            path,
            body=json.dumps(payload).encode(),
            headers={
                "Content-Type": "application/json",
                **({"Authorization": f"Bearer {access_token}"} if access_token else {}),
            },
            napikey=napikey,
        )

    def _request(
        self,
        method: str,
        path: str,
        body: bytes | None = None,
        headers: dict[str, str] | None = None,
        napikey: str | None = None,
    ) -> dict[str, Any]:
        url = self.base_url.rstrip("/") + path
        if napikey:
            separator = "&" if "?" in url else "?"
            url = f"{url}{separator}{urlencode({'napikey': napikey})}"

        request = Request(url, data=body, method=method)
        for key, value in (headers or {}).items():
            request.add_header(key, value)

        with urlopen(request, timeout=30) as response:
            raw = response.read().decode()
            try:
                data = json.loads(raw) if raw else {}
            except json.JSONDecodeError:
                data = {"raw": raw}

            if response.status >= 400:
                raise NvoipError(response.status, data)

            return data
