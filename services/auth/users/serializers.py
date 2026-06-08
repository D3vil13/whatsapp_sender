from django.utils import timezone
from rest_framework import serializers

from users.models import User


class SignupSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(min_length=8, write_only=True)
    disclaimer_accepted = serializers.BooleanField()

    def validate_disclaimer_accepted(self, value: bool) -> bool:
        if not value:
            raise serializers.ValidationError(
                "You must accept the disclaimer to use BulkPing."
            )
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            disclaimer_accepted=True,
            disclaimer_accepted_at=timezone.now(),
        )


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class GoogleAuthSerializer(serializers.Serializer):
    credential = serializers.CharField()

    def validate_credential(self, value: str) -> dict:
        from django.conf import settings
        cfg = settings.BULKPING_CONFIG
        if not cfg.google_client_id:
            raise serializers.ValidationError("Google OAuth is not configured.")
        try:
            from google.oauth2 import id_token
            from google.auth.transport import requests
            info = id_token.verify_oauth2_token(
                value, requests.Request(), cfg.google_client_id
            )
        except ValueError as exc:
            raise serializers.ValidationError(f"Invalid Google token: {exc}")
        if info.get("email_verified") is not True:
            raise serializers.ValidationError("Google email not verified.")
        return info
