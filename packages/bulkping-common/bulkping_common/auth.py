from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt


@dataclass(frozen=True)
class TokenPayload:
    user_id: uuid.UUID
    email: str
    disclaimer_accepted: bool


class JWTService:
    def __init__(
        self,
        secret_key: str,
        access_minutes: int = 60,
        refresh_days: int = 7,
        algorithm: str = "HS256",
    ) -> None:
        self.secret_key = secret_key
        self.access_minutes = access_minutes
        self.refresh_days = refresh_days
        self.algorithm = algorithm

    def create_access_token(self, payload: TokenPayload) -> str:
        return self._encode(
            {
                "sub": str(payload.user_id),
                "email": payload.email,
                "disclaimer_accepted": payload.disclaimer_accepted,
                "type": "access",
            },
            timedelta(minutes=self.access_minutes),
        )

    def create_refresh_token(self, payload: TokenPayload) -> str:
        return self._encode(
            {
                "sub": str(payload.user_id),
                "email": payload.email,
                "disclaimer_accepted": payload.disclaimer_accepted,
                "type": "refresh",
            },
            timedelta(days=self.refresh_days),
        )

    def decode(self, token: str, *, expected_type: str | None = None) -> TokenPayload:
        data = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        if expected_type and data.get("type") != expected_type:
            raise jwt.InvalidTokenError("Unexpected token type")
        return TokenPayload(
            user_id=uuid.UUID(data["sub"]),
            email=data.get("email", ""),
            disclaimer_accepted=bool(data.get("disclaimer_accepted", False)),
        )

    def _encode(self, claims: dict[str, Any], delta: timedelta) -> str:
        now = datetime.now(timezone.utc)
        claims = {
            **claims,
            "iat": now,
            "exp": now + delta,
        }
        return jwt.encode(claims, self.secret_key, algorithm=self.algorithm)
