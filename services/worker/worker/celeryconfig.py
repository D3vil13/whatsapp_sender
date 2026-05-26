import os

from celery.schedules import crontab

broker_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
result_backend = broker_url
accept_content = ["json"]
task_serializer = "json"
result_serializer = "json"
timezone = os.environ.get("CELERY_TIMEZONE", "Asia/Kolkata")
enable_utc = True

task_routes = {
    "worker.tasks.send_broadcast_message": {"queue": "broadcast"},
    "worker.tasks.send_chatbot_reply": {"queue": "chatbot"},
    "worker.tasks.reset_daily_sent_counts": {"queue": "scheduled"},
    "worker.tasks.increment_warmup_day": {"queue": "scheduled"},
    "worker.tasks.check_instance_health": {"queue": "scheduled"},
}

beat_schedule = {
    "reset-daily-sent-counts": {
        "task": "worker.tasks.reset_daily_sent_counts",
        "schedule": crontab(hour=0, minute=0),
    },
    "increment-warmup-day": {
        "task": "worker.tasks.increment_warmup_day",
        "schedule": crontab(hour=0, minute=5),
    },
    "check-instance-health": {
        "task": "worker.tasks.check_instance_health",
        "schedule": crontab(minute="*/5"),
    },
}
