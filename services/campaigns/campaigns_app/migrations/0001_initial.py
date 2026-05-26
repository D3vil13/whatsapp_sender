import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Campaign",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("message_text", models.TextField()),
                ("media_url", models.URLField(blank=True, null=True)),
                ("group_id", models.UUIDField()),
                ("status", models.CharField(choices=[("queued", "Queued"), ("sending", "Sending"), ("completed", "Completed"), ("failed", "Failed")], default="queued", max_length=20)),
                ("scheduled_at", models.DateTimeField(blank=True, null=True)),
                ("total_count", models.IntegerField(default=0)),
                ("sent_count", models.IntegerField(default=0)),
                ("delivered_count", models.IntegerField(default=0)),
                ("read_count", models.IntegerField(default=0)),
                ("reply_count", models.IntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name="MessageLog",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("contact_id", models.UUIDField()),
                ("contact_name", models.CharField(max_length=255)),
                ("contact_phone", models.CharField(max_length=20)),
                ("wa_message_id", models.CharField(blank=True, default="", max_length=128)),
                ("status", models.CharField(choices=[("pending", "Pending"), ("sent", "Sent"), ("delivered", "Delivered"), ("read", "Read"), ("failed", "Failed")], default="pending", max_length=20)),
                ("status_updated_at", models.DateTimeField(blank=True, null=True)),
                ("task_index", models.IntegerField(default=0)),
                ("campaign", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="logs", to="campaigns_app.campaign")),
            ],
        ),
        migrations.AddIndex(
            model_name="messagelog",
            index=models.Index(fields=["wa_message_id"], name="campaigns_a_wa_mess_idx"),
        ),
    ]
