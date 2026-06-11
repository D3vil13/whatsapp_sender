from rest_framework import serializers
from chatbot_app.models import (
    ChatbotBranch,
    ChatbotFlow,
    ChatbotMatchLog,
    ChatbotRule,
    ChatbotSession,
)

MAX_RULES_PER_FLOW = 50


class ChatbotFlowSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotFlow
        fields = ["id", "name", "is_active", "welcome_message", "created_at"]
        read_only_fields = ["id", "created_at"]


class ChatbotBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotBranch
        fields = [
            "id", "rule", "match_type", "match_value",
            "next_rule", "next_flow",
        ]


class ChatbotRuleSerializer(serializers.ModelSerializer):
    branches = ChatbotBranchSerializer(many=True, read_only=True)

    class Meta:
        model = ChatbotRule
        fields = [
            "id", "flow", "match_type", "keyword", "reply_text",
            "response_type", "menu_config", "attachment_url",
            "is_active", "is_fallback", "priority", "cooldown_seconds",
            "created_at", "branches",
        ]
        read_only_fields = ["id", "created_at"]


class ChatbotFlowDetailSerializer(serializers.ModelSerializer):
    rules = ChatbotRuleSerializer(many=True, read_only=True)

    class Meta:
        model = ChatbotFlow
        fields = ["id", "name", "is_active", "welcome_message", "created_at", "rules"]
        read_only_fields = ["id", "created_at"]


class ChatbotRuleCreateSerializer(serializers.Serializer):
    flow = serializers.UUIDField(required=False, allow_null=True)
    match_type = serializers.ChoiceField(choices=[
        "keyword_contains", "keyword_exact", "keyword_regex",
        "button_id", "list_selection", "always",
    ], default="keyword_contains")
    keyword = serializers.CharField(max_length=255, required=False, allow_blank=True)
    reply_text = serializers.CharField(required=False, allow_blank=True)
    response_type = serializers.ChoiceField(choices=[
        "text", "list_menu", "buttons", "image", "document", "audio", "video",
    ], default="text")
    menu_config = serializers.JSONField(required=False, default=dict)
    attachment_url = serializers.URLField(required=False, allow_blank=True, default="")
    is_fallback = serializers.BooleanField(default=False)
    priority = serializers.IntegerField(default=0, required=False)
    cooldown_seconds = serializers.IntegerField(default=0, required=False)

    def validate(self, attrs):
        user_id = self.context["user_id"]
        flow_id = attrs.get("flow")

        flow_rules_count = ChatbotRule.objects.filter(user_id=user_id)
        if flow_id:
            flow_rules_count = flow_rules_count.filter(flow_id=flow_id)
        if flow_rules_count.count() >= MAX_RULES_PER_FLOW:
            raise serializers.ValidationError(
                f"Maximum {MAX_RULES_PER_FLOW} rules per flow."
            )

        if attrs.get("is_fallback"):
            if ChatbotRule.objects.filter(user_id=user_id, is_fallback=True).exists():
                raise serializers.ValidationError("Only one fallback rule allowed per user.")
        elif attrs["match_type"] in ("keyword_contains", "keyword_exact", "keyword_regex"):
            if not attrs.get("keyword"):
                raise serializers.ValidationError("Keyword is required for this match type.")
        elif attrs["match_type"] in ("button_id", "list_selection"):
            pass

        if attrs.get("response_type") in ("list_menu", "buttons") and not attrs.get("menu_config"):
            raise serializers.ValidationError("menu_config is required for list/button response types.")

        if attrs["response_type"] in ("image", "document", "audio", "video") and not attrs.get("attachment_url"):
            raise serializers.ValidationError("attachment_url is required for media response types.")

        if not attrs.get("reply_text") and attrs["response_type"] not in ("list_menu", "buttons"):
            raise serializers.ValidationError("reply_text is required for non-menu response types.")

        return attrs


class ChatbotSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotSession
        fields = [
            "id", "sender_phone", "current_flow", "current_rule",
            "variables", "last_interaction", "created_at",
        ]
        read_only_fields = ["id", "last_interaction", "created_at"]


class ChatbotMatchLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatbotMatchLog
        fields = [
            "id", "sender_phone", "matched_keyword",
            "matched_rule", "matched_flow",
            "is_fallback", "created_at",
        ]
        read_only_fields = ["id", "created_at"]
