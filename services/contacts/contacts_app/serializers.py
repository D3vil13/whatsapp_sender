from rest_framework import serializers
from contacts_app.models import Contact, ContactGroup


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ["id", "name", "phone", "created_at"]
        read_only_fields = ["id", "created_at"]


class ContactCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)

    def validate_phone(self, value):
        from contacts_app.utils import normalize_phone
        normalized = normalize_phone(value)
        if not normalized:
            raise serializers.ValidationError("Invalid phone number. Use E.164 or valid local format.")
        return normalized


class GroupSerializer(serializers.ModelSerializer):
    member_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = ContactGroup
        fields = ["id", "name", "member_count", "created_at"]
        read_only_fields = ["id", "created_at"]


class GroupCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)


class GroupMembersSerializer(serializers.Serializer):
    contact_ids = serializers.ListField(child=serializers.UUIDField())
