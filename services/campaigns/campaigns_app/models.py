import uuid
from django.db import models


class CampaignStatus(models.TextChoices):
    QUEUED = "queued", "Queued"
    SENDING = "sending", "Sending"
    COMPLETED = "completed", "Completed"
    FAILED = "failed", "Failed"
    STOPPED = "stopped", "Stopped"


class MessageStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    SENT = "sent", "Sent"
    DELIVERED = "delivered", "Delivered"
    READ = "read", "Read"
    FAILED = "failed", "Failed"


class Campaign(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(db_index=True)
    name = models.CharField(max_length=255)
    message_text = models.TextField()
    media_url = models.URLField(null=True, blank=True)
    group_id = models.UUIDField()
    status = models.CharField(
        max_length=20, choices=CampaignStatus.choices, default=CampaignStatus.QUEUED
    )
    scheduled_at = models.DateTimeField(null=True, blank=True)
    total_count = models.IntegerField(default=0)
    sent_count = models.IntegerField(default=0)
    delivered_count = models.IntegerField(default=0)
    read_count = models.IntegerField(default=0)
    reply_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)


class MessageLog(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name="logs")
    contact_id = models.UUIDField()
    contact_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    wa_message_id = models.CharField(max_length=128, blank=True, default="")
    status = models.CharField(
        max_length=20, choices=MessageStatus.choices, default=MessageStatus.PENDING
    )
    status_updated_at = models.DateTimeField(null=True, blank=True)
    task_index = models.IntegerField(default=0)

    class Meta:
        indexes = [models.Index(fields=["wa_message_id"])]
