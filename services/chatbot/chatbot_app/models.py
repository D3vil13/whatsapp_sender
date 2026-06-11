import uuid
from django.db import models


MATCH_TYPE_CHOICES = [
    ("keyword_contains", "Keyword Contains"),
    ("keyword_exact", "Keyword Exact"),
    ("keyword_regex", "Keyword Regex"),
    ("button_id", "Button ID"),
    ("list_selection", "List Selection"),
    ("always", "Always"),
]

RESPONSE_TYPE_CHOICES = [
    ("text", "Text"),
    ("list_menu", "List Menu"),
    ("buttons", "Buttons"),
    ("image", "Image"),
    ("document", "Document"),
    ("audio", "Audio"),
    ("video", "Video"),
]


class ChatbotFlow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    welcome_message = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ChatbotRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    flow = models.ForeignKey(
        ChatbotFlow, on_delete=models.SET_NULL, null=True, blank=True, related_name="rules"
    )
    match_type = models.CharField(
        max_length=50, choices=MATCH_TYPE_CHOICES, default="keyword_contains"
    )
    keyword = models.CharField(max_length=255, blank=True, default="")
    reply_text = models.TextField(blank=True, default="")
    response_type = models.CharField(
        max_length=50, choices=RESPONSE_TYPE_CHOICES, default="text"
    )
    menu_config = models.JSONField(blank=True, null=True, default=dict)
    attachment_url = models.URLField(blank=True, default="")
    is_active = models.BooleanField(default=True)
    is_fallback = models.BooleanField(default=False)
    priority = models.IntegerField(default=0)
    cooldown_seconds = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority", "-created_at"]


class ChatbotBranch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    rule = models.ForeignKey(
        ChatbotRule, on_delete=models.CASCADE, related_name="branches"
    )
    match_type = models.CharField(
        max_length=50, choices=MATCH_TYPE_CHOICES, default="button_id"
    )
    match_value = models.CharField(max_length=255, blank=True, default="")
    next_rule = models.ForeignKey(
        ChatbotRule, on_delete=models.SET_NULL, null=True, blank=True, related_name="incoming_branches"
    )
    next_flow = models.ForeignKey(
        ChatbotFlow, on_delete=models.SET_NULL, null=True, blank=True, related_name="entry_branches"
    )

    class Meta:
        ordering = ["match_value"]


class ChatbotSession(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    sender_phone = models.CharField(max_length=20, db_index=True)
    current_flow = models.ForeignKey(
        ChatbotFlow, on_delete=models.SET_NULL, null=True, blank=True
    )
    current_rule = models.ForeignKey(
        ChatbotRule, on_delete=models.SET_NULL, null=True, blank=True
    )
    variables = models.JSONField(blank=True, default=dict)
    last_interaction = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user_id", "sender_phone")]
        ordering = ["-last_interaction"]


class ChatbotMatchLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    sender_phone = models.CharField(max_length=20)
    matched_keyword = models.CharField(max_length=255, blank=True, default="")
    matched_rule = models.ForeignKey(
        ChatbotRule, on_delete=models.SET_NULL, null=True, blank=True
    )
    matched_flow = models.ForeignKey(
        ChatbotFlow, on_delete=models.SET_NULL, null=True, blank=True
    )
    is_fallback = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
