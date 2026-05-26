import os
from typing import Any

import requests

API_BASE = os.environ.get("API_BASE_URL", "http://localhost:8000")


class BulkPingAPI:
    def __init__(self) -> None:
        self.base = API_BASE.rstrip("/")
        self.token: str | None = None

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def signup(self, email: str, password: str, disclaimer: bool) -> dict:
        resp = requests.post(
            f"{self.base}/api/auth/signup/",
            json={"email": email, "password": password, "disclaimer_accepted": disclaimer},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access"]
        return data

    def login(self, email: str, password: str) -> dict:
        resp = requests.post(
            f"{self.base}/api/auth/login/",
            json={"email": email, "password": password},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        self.token = data["access"]
        return data

    def get(self, path: str) -> Any:
        resp = requests.get(f"{self.base}{path}", headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, json: dict | None = None, files=None) -> Any:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        if files:
            resp = requests.post(
                f"{self.base}{path}",
                headers=headers,
                files=files,
                timeout=60,
            )
        else:
            headers["Content-Type"] = "application/json"
            resp = requests.post(
                f"{self.base}{path}",
                headers=headers,
                json=json,
                timeout=60,
            )
        resp.raise_for_status()
        if resp.content:
            return resp.json()
        return {}

    def patch(self, path: str, json: dict) -> Any:
        resp = requests.patch(
            f"{self.base}{path}", headers=self._headers(), json=json, timeout=30
        )
        resp.raise_for_status()
        return resp.json()

    def delete(self, path: str, json: dict | None = None) -> None:
        headers = self._headers()
        if json is None:
            resp = requests.delete(f"{self.base}{path}", headers=headers, timeout=30)
        else:
            resp = requests.delete(f"{self.base}{path}", headers=headers, json=json, timeout=30)
        resp.raise_for_status()
