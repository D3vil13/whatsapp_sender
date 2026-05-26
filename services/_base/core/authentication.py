from __future__ import annotations

import uuid

from django.conf import settings
from rest_framework import authentication, exceptions

from bulkping_common.auth import JWTService, TokenPayload


class AuthenticatedUser:
    """Lightweight user object from JWT — no cross-service User FK."""

    def __init__(self, payload: TokenPayload) -> None:
        self.id = payload.user_id
        self.email = payload.email
        self.disclaimer_accepted = payload.disclaimer_accepted
        self.is_authenticated = True

    @property
    def pk(self) -> uuid.UUID:
        return self.id


class JWTAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        header = request.META.get("HTTP_AUTHORIZATION", "")
        if not header.startswith("Bearer "):
            return None
        token = header[7:]
        jwt_service = JWTService(
            settings.SECRET_KEY,
            access_minutes=settings.BULKPING_CONFIG.jwt_access_minutes,
            refresh_days=settings.BULKPING_CONFIG.jwt_refresh_days,
        )
        try:
            payload = jwt_service.decode(token, expected_type="access")
        except Exception as exc:
            raise exceptions.AuthenticationFailed("Invalid token") from exc
        return AuthenticatedUser(payload), token


class DisclaimerRequiredMixin:
    """Raise 403 when disclaimer not accepted."""

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        user = request.user
        if user and not getattr(user, "disclaimer_accepted", True):
            raise exceptions.PermissionDenied(
                "You must accept the disclaimer before using BulkPing."
            )


class InternalServiceUser:
    is_authenticated = True
    disclaimer_accepted = True
    id = None


class InternalServiceAuthentication(authentication.BaseAuthentication):
    """Service-to-service calls via X-Internal-Token + optional X-User-Id."""

    def authenticate(self, request):
        token = request.META.get("HTTP_X_INTERNAL_TOKEN", "")
        if not token:
            return None
        if token != settings.BULKPING_CONFIG.internal_service_token:
            raise exceptions.AuthenticationFailed("Invalid internal token")
        user_id = request.META.get("HTTP_X_USER_ID")
        if user_id:
            payload = TokenPayload(
                user_id=uuid.UUID(user_id),
                email="",
                disclaimer_accepted=True,
            )
            return AuthenticatedUser(payload), None
        return InternalServiceUser(), None
