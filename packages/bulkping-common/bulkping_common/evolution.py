from __future__ import annotations

from typing import Any

import httpx


def extract_qr_base64(payload: dict[str, Any]) -> str | None:
    """Extract QR image base64 from Evolution API create/connect responses."""
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
    """Thin HTTP client for Evolution API v2.3.7."""

    def __init__(self, base_url: str, api_key: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = {"apikey": api_key, "Content-Type": "application/json"}

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        with httpx.Client(timeout=kwargs.pop("timeout", 30.0)) as client:
            response = client.request(method, url, headers=self.headers, **kwargs)
            response.raise_for_status()
            if response.content:
                data = response.json()
                return data if isinstance(data, dict) else {}
            return {}

    def create_instance(self, instance_name: str) -> dict[str, Any]:
        """Create instance. Webhook is configured via Evolution env (WEBHOOK_GLOBAL_URL)."""
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
            json={"number": number, "text": text},
        )

    def send_media(
        self,
        instance_name: str,
        number: str,
        media_url: str,
        caption: str,
        mimetype: str = "image/jpeg",
    ) -> dict[str, Any]:
        return self._request(
            "POST",
            f"/message/sendMedia/{instance_name}",
            json={
                "number": number,
                "mediatype": "image",
                "mimetype": mimetype,
                "media": media_url,
                "caption": caption,
            },
        )
