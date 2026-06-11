from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0002_add_google_sub"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="clerk_user_id",
            field=models.CharField(
                max_length=128,
                unique=True,
                null=True,
                blank=True,
                default=None,
            ),
        ),
    ]
