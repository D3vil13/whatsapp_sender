import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("SECRET_KEY", os.environ.get("SECRET_KEY", "dev-secret"))
os.environ.setdefault("REDIS_URL", os.environ.get("REDIS_URL", "redis://localhost:6379/0"))

app = Celery("bulkping")
app.config_from_object("worker.celeryconfig")
app.autodiscover_tasks(["worker.tasks"])
