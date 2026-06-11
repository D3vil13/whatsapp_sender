import uuid
from django.db import migrations, models
import django.db.models.deletion


def update_rule_ordering(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("chatbot_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChatbotFlow",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField(db_index=True)),
                ("name", models.CharField(max_length=255)),
                ("is_active", models.BooleanField(default=True)),
                ("welcome_message", models.TextField(blank=True, default="")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ChatbotBranch",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("match_type", models.CharField(
                    choices=[
                        ("keyword_contains", "Keyword Contains"),
                        ("keyword_exact", "Keyword Exact"),
                        ("keyword_regex", "Keyword Regex"),
                        ("button_id", "Button ID"),
                        ("list_selection", "List Selection"),
                        ("always", "Always"),
                    ],
                    default="button_id",
                    max_length=50,
                )),
                ("match_value", models.CharField(blank=True, default="", max_length=255)),
                ("next_rule", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="incoming_branches",
                    to="chatbot_app.chatbotrule",
                )),
                ("next_flow", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name="entry_branches",
                    to="chatbot_app.chatbotflow",
                )),
                ("rule", models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name="branches",
                    to="chatbot_app.chatbotrule",
                )),
            ],
            options={"ordering": ["match_value"]},
        ),
        migrations.CreateModel(
            name="ChatbotSession",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ("user_id", models.UUIDField(db_index=True)),
                ("sender_phone", models.CharField(db_index=True, max_length=20)),
                ("variables", models.JSONField(blank=True, default=dict)),
                ("last_interaction", models.DateTimeField(auto_now=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("current_flow", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to="chatbot_app.chatbotflow",
                )),
                ("current_rule", models.ForeignKey(
                    blank=True, null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to="chatbot_app.chatbotrule",
                )),
            ],
            options={"ordering": ["-last_interaction"]},
        ),
        migrations.AlterUniqueTogether(
            name="chatbotsession",
            unique_together={("user_id", "sender_phone")},
        ),
        # Add new fields to ChatbotRule
        migrations.AddField(
            model_name="chatbotrule",
            name="flow",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="rules",
                to="chatbot_app.chatbotflow",
            ),
        ),
        migrations.AddField(
            model_name="chatbotrule",
            name="match_type",
            field=models.CharField(
                choices=[
                    ("keyword_contains", "Keyword Contains"),
                    ("keyword_exact", "Keyword Exact"),
                    ("keyword_regex", "Keyword Regex"),
                    ("button_id", "Button ID"),
                    ("list_selection", "List Selection"),
                    ("always", "Always"),
                ],
                default="keyword_contains",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="chatbotrule",
            name="response_type",
            field=models.CharField(
                choices=[
                    ("text", "Text"),
                    ("list_menu", "List Menu"),
                    ("buttons", "Buttons"),
                    ("image", "Image"),
                    ("document", "Document"),
                    ("audio", "Audio"),
                    ("video", "Video"),
                ],
                default="text",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="chatbotrule",
            name="menu_config",
            field=models.JSONField(blank=True, null=True, default=dict),
        ),
        migrations.AddField(
            model_name="chatbotrule",
            name="attachment_url",
            field=models.URLField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="chatbotrule",
            name="priority",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="chatbotrule",
            name="cooldown_seconds",
            field=models.IntegerField(default=0),
        ),
        # Update ordering on ChatbotRule
        migrations.AlterModelOptions(
            name="chatbotrule",
            options={"ordering": ["priority", "-created_at"]},
        ),
        # Add new fields to ChatbotMatchLog
        migrations.AddField(
            model_name="chatbotmatchlog",
            name="matched_rule",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="chatbot_app.chatbotrule",
            ),
        ),
        migrations.AddField(
            model_name="chatbotmatchlog",
            name="matched_flow",
            field=models.ForeignKey(
                blank=True, null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to="chatbot_app.chatbotflow",
            ),
        ),
    ]
