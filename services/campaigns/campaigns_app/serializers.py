from rest_framework import serializers
from campaigns_app.models import Campaign, MessageLog


class CampaignCreateSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    message_text = serializers.CharField()
    group_id = serializers.UUIDField()
    media_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    scheduled_at = serializers.DateTimeField(required=False, allow_null=True)


class QuickSendSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)
    message_text = serializers.CharField()
    media_url = serializers.URLField(required=False, allow_null=True, allow_blank=True)


class CampaignListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campaign
        fields = [
            "id", "name", "status", "total_count", "sent_count",
            "delivered_count", "read_count", "reply_count", "created_at",
        ]


class MessageLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = MessageLog
        fields = [
            "id", "contact_id", "contact_name", "contact_phone",
            "status", "status_updated_at",
        ]
