from __future__ import annotations

import uuid
from typing import Any

import httpx


class ServiceClient:
    def __init__(self, base_url: str, internal_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.internal_token = internal_token

    def _headers(self, user_id: uuid.UUID | None = None) -> dict[str, str]:
        headers = {"X-Internal-Token": self.internal_token}
        if user_id:
            headers["X-User-Id"] = str(user_id)
        return headers

    def get(self, path: str, *, user_id: uuid.UUID | None = None) -> Any:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(
                f"{self.base_url}{path}",
                headers=self._headers(user_id),
            )
            response.raise_for_status()
            return response.json()

    def post(
        self,
        path: str,
        *,
        user_id: uuid.UUID | None = None,
        json: dict[str, Any] | None = None,
        extra_headers: dict[str, str] | None = None,
    ) -> Any:
        headers = self._headers(user_id)
        if extra_headers:
            headers.update(extra_headers)
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{self.base_url}{path}",
                headers=headers,
                json=json or {},
            )
            response.raise_for_status()
            return response.json()
