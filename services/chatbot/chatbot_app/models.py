import uuid
from django.db import models


class ChatbotRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    keyword = models.CharField(max_length=255, blank=True, default="")
    reply_text = models.TextField()
    is_active = models.BooleanField(default=True)
    is_fallback = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ChatbotMatchLog(models.Model):
    """Metadata only — no message content stored."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    sender_phone = models.CharField(max_length=20)
    matched_keyword = models.CharField(max_length=255, blank=True, default="")
    is_fallback = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
