"""Enqueue Celery tasks on the worker service via Redis."""

from __future__ import annotations

import random
import uuid

from celery import Celery
from django.conf import settings


def get_celery() -> Celery:
    app = Celery("bulkping")
    app.conf.broker_url = settings.CELERY_BROKER_URL
    app.conf.result_backend = settings.CELERY_RESULT_BACKEND
    app.conf.task_routes = {
        "worker.tasks.send_broadcast_message": {"queue": "broadcast"},
        "worker.tasks.send_chatbot_reply": {"queue": "chatbot"},
        "worker.tasks.reset_daily_sent_counts": {"queue": "scheduled"},
        "worker.tasks.increment_warmup_day": {"queue": "scheduled"},
        "worker.tasks.check_instance_health": {"queue": "scheduled"},
    }
    return app


def enqueue_broadcast_messages(campaign_id: uuid.UUID, log_ids: list[uuid.UUID]) -> None:
    app = get_celery()
    for index, log_id in enumerate(log_ids):
        countdown = random.uniform(3, 8) * (index + 1)
        app.send_task(
            "worker.tasks.send_broadcast_message",
            args=[str(log_id)],
            countdown=countdown,
            queue="broadcast",
        )


def enqueue_single_message(log_id: str) -> None:
    app = get_celery()
    app.send_task(
        "worker.tasks.send_broadcast_message",
        args=[log_id],
        countdown=random.uniform(3, 8),
        queue="broadcast",
    )
