import uuid
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Contact",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("phone", models.CharField(max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("user_id", "phone")}},
        ),
        migrations.CreateModel(
            name="ContactGroup",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("contacts", models.ManyToManyField(blank=True, related_name="groups", to="contacts_app.contact")),
            ],
            options={"ordering": ["-created_at"], "unique_together": {("user_id", "name")}},
        ),
    ]
