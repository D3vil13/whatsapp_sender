import uuid

from django.db import models


class InstanceStatus(models.TextChoices):
    CONNECTED = "connected", "Connected"
    DISCONNECTED = "disconnected", "Disconnected"
    QR_PENDING = "qr_pending", "QR Pending"


class WAInstance(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_id = models.UUIDField(unique=True, db_index=True)
    instance_name = models.CharField(max_length=128, unique=True)
    status = models.CharField(
        max_length=20,
        choices=InstanceStatus.choices,
        default=InstanceStatus.QR_PENDING,
    )
    phone_number = models.CharField(max_length=20, blank=True, default="")
    daily_sent_count = models.IntegerField(default=0)
    daily_cap = models.IntegerField(default=50)
    warmup_day = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "wa_instances"
