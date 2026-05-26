from rest_framework import serializers
from chatbot_app.models import ChatbotRule

MAX_RULES = 20


class ChatbotRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotRule
        fields = [
            "id", "keyword", "reply_text", "is_active", "is_fallback", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class ChatbotRuleCreateSerializer(serializers.Serializer):
    keyword = serializers.CharField(max_length=255, required=False, allow_blank=True)
    reply_text = serializers.CharField()
    is_fallback = serializers.BooleanField(default=False)

    def validate(self, attrs):
        user_id = self.context["user_id"]
        if ChatbotRule.objects.filter(user_id=user_id).count() >= MAX_RULES:
            raise serializers.ValidationError("Maximum 20 chatbot rules allowed.")
        if attrs.get("is_fallback"):
            if ChatbotRule.objects.filter(user_id=user_id, is_fallback=True).exists():
                raise serializers.ValidationError("Only one fallback rule allowed per user.")
        elif not attrs.get("keyword"):
            raise serializers.ValidationError("Keyword is required for non-fallback rules.")
        return attrs
