from rest_framework import serializers

from whatsapp.models import WAInstance


class InstanceStatusSerializer(serializers.ModelSerializer):
    qr_base64 = serializers.SerializerMethodField()

    class Meta:
        model = WAInstance
        fields = [
            "status",
            "phone_number",
            "daily_sent_count",
            "daily_cap",
            "qr_base64",
        ]

    def get_qr_base64(self, obj: WAInstance) -> str | None:
        from whatsapp.services import get_qr_cache

        return get_qr_cache(obj.instance_name)
