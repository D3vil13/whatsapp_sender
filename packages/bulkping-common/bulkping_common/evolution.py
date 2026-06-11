from __future__ import annotations

from typing import Any

import httpx


def extract_qr_base64(payload: dict[str, Any]) -> str | None:
    if not payload:
        return None
    qrcode = payload.get("qrcode")
    raw = None
    if isinstance(qrcode, dict):
        raw = qrcode.get("base64") or qrcode.get("code")
    elif isinstance(qrcode, str):
        raw = qrcode
    if not raw:
        raw = payload.get("base64")
    if raw:
        raw = raw.replace("data:image/png;base64,", "").replace("\n", "").replace("\r", "").replace(" ", "")
    return raw


class EvolutionAPIClient:
    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"apikey": api_key, "Content-Type": "application/json"}
        self._timeout = timeout

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=kwargs.pop("timeout", self._timeout)) as client:
            response = client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            if response.content:
                data = response.json()
                return data if isinstance(data, dict) else {}
            return {}

    def create_instance(self, instance_name: str) -> dict[str, Any]:
        return self._request(
            "POST",
            "/instance/create",
            json={
                "instanceName": instance_name,
                "qrcode": True,
                "integration": "WHATSAPP-BAILEYS",
            },
        )

    def connect_instance(self, instance_name: str) -> dict[str, Any]:
        return self._request("GET", f"/instance/connect/{instance_name}")

    def connection_state(self, instance_name: str) -> dict[str, Any]:
        return self._request("GET", f"/instance/connectionState/{instance_name}")

    def delete_instance(self, instance_name: str) -> dict[str, Any]:
        return self._request("DELETE", f"/instance/delete/{instance_name}")

    def fetch_instances(self) -> list[dict[str, Any]]:
        data = self._request("GET", "/instance/fetchInstances")
        if isinstance(data, list):
            return data
        return data.get("instances", []) if isinstance(data, dict) else []

    def send_text(self, instance_name: str, number: str, text: str) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/message/sendText/{instance_name}",
            json={"number": number, "text": text, "options": {"delay": 1200}},
        )

    def send_media(
        self,
        instance_name: str,
        number: str,
        media_url: str,
        caption: str = "",
        mediatype: str = "image",
        mimetype: str = "image/jpeg",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/message/sendMedia/{instance_name}",
            json={
                "number": number,
                "mediatype": mediatype,
                "mimetype": mimetype,
                "media": media_url,
                "caption": caption,
                "options": {"delay": 1200},
            },
        )

    def send_list(
        self,
        instance_name: str,
        number: str,
        title: str = "",
        description: str = "",
        button_text: str = "Select",
        sections: list[dict[str, Any]] | None = None,
        footer: str = "",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "number": number,
            "options": {"delay": 1200},
        }
        list_message: dict[str, Any] = {}
        if title:
            list_message["title"] = title
        if description:
            list_message["description"] = description
        list_message["buttonText"] = button_text
        if footer:
            list_message["footerText"] = footer
        list_message["sections"] = sections or []
        body["listMessage"] = list_message
        return self._request("POST", f"/message/sendList/{instance_name}", json=body)

    def send_buttons(
        self,
        instance_name: str,
        number: str,
        title: str = "",
        description: str = "",
        buttons: list[dict[str, Any]] | None = None,
        footer: str = "",
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "number": number,
            "options": {"delay": 1200},
        }
        button_message: dict[str, Any] = {}
        if title:
            button_message["title"] = title
        if description:
            button_message["description"] = description
        if footer:
            button_message["footerText"] = footer
        button_message["buttons"] = buttons or []
        body["buttonsMessage"] = button_message
        return self._request("POST", f"/message/sendButtons/{instance_name}", json=body)
