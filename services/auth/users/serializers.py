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
