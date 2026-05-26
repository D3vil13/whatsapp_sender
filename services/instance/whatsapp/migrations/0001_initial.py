import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="WAInstance",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField(db_index=True, unique=True)),
                ("instance_name", models.CharField(max_length=128, unique=True)),
                ("status", models.CharField(choices=[("connected", "Connected"), ("disconnected", "Disconnected"), ("qr_pending", "QR Pending")], default="qr_pending", max_length=20)),
                ("phone_number", models.CharField(blank=True, default="", max_length=20)),
                ("daily_sent_count", models.IntegerField(default=0)),
                ("daily_cap", models.IntegerField(default=50)),
                ("warmup_day", models.IntegerField(default=1)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"db_table": "wa_instances"},
        ),
    ]
