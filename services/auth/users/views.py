from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bulkping_common.auth import JWTService, TokenPayload

from users.serializers import LoginSerializer, SignupSerializer


def _jwt_service() -> JWTService:
    cfg = settings.BULKPING_CONFIG
    return JWTService(
        settings.SECRET_KEY,
        access_minutes=cfg.jwt_access_minutes,
        refresh_days=cfg.jwt_refresh_days,
    )


def _token_response(user) -> Response:
    payload = TokenPayload(
        user_id=user.id,
        email=user.email,
        disclaimer_accepted=user.disclaimer_accepted,
    )
    jwt_service = _jwt_service()
    return Response(
        {
            "access": jwt_service.create_access_token(payload),
            "refresh": jwt_service.create_refresh_token(payload),
        }
    )


class SignupView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        from users.models import User

        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if User.objects.filter(email=serializer.validated_data["email"]).exists():
            return Response(
                {"email": ["A user with this email already exists."]},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user = serializer.save()
        return _token_response(user)


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        from users.models import User

        try:
            user = User.objects.get(email=serializer.validated_data["email"])
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        if not user.check_password(serializer.validated_data["password"]):
            return Response(
                {"detail": "Invalid credentials."},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return _token_response(user)


class TokenRefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        refresh = request.data.get("refresh")
        if not refresh:
            return Response(
                {"detail": "refresh token required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        jwt_service = _jwt_service()
        try:
            payload = jwt_service.decode(refresh, expected_type="refresh")
        except Exception:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        from users.models import User

        try:
            user = User.objects.get(id=payload.user_id)
        except User.DoesNotExist:
            return Response(
                {"detail": "User not found"},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        return _token_response(user)


class UserProfileInternalView(APIView):
    """Internal endpoint for other services to verify disclaimer status."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id):
        token = request.META.get("HTTP_X_INTERNAL_TOKEN", "")
        if token != settings.BULKPING_CONFIG.internal_service_token:
            return Response(status=status.HTTP_403_FORBIDDEN)
        from users.models import User

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "id": str(user.id),
                "email": user.email,
                "disclaimer_accepted": user.disclaimer_accepted,
            }
        )
