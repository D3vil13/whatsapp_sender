from django.db import migrations, models
from django.utils import timezone


def set_created_at(apps, schema_editor):
    MessageLog = apps.get_model("campaigns_app", "MessageLog")
    now = timezone.now()
    MessageLog.objects.filter(created_at__isnull=True).update(created_at=now)


class Migration(migrations.Migration):
    dependencies = [
        ("campaigns_app", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="messagelog",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.RunPython(set_created_at, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="messagelog",
            name="created_at",
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
