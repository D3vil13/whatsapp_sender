from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="google_sub",
            field=models.CharField(
                max_length=128,
                unique=True,
                null=True,
                blank=True,
                default=None,
            ),
        ),
    ]
