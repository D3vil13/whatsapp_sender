from __future__ import annotations

import logging
import os
import uuid

import httpx
from celery import shared_task

from bulkping_common.evolution import EvolutionAPIClient
from bulkping_common.http import ServiceClient

logger = logging.getLogger(__name__)


def _cfg() -> dict[str, str]:
    return {
        "internal_token": os.environ["INTERNAL_SERVICE_TOKEN"],
        "instance_url": os.environ.get("INSTANCE_SERVICE_URL", "http://instance-service:8002"),
        "campaigns_url": os.environ.get("CAMPAIGNS_SERVICE_URL", "http://campaigns-service:8004"),
        "evolution_url": os.environ.get("EVOLUTION_API_URL", "http://evolution-api:8080"),
        "evolution_key": os.environ.get("EVOLUTION_API_KEY", ""),
    }


def _headers(cfg: dict) -> dict[str, str]:
    return {"X-Internal-Token": cfg["internal_token"]}


def _patch_log(cfg: dict, log_id: str, wa_message_id: str, status: str) -> None:
    with httpx.Client(timeout=30.0) as client:
        resp = client.patch(
            f"{cfg['campaigns_url']}/internal/campaigns/logs/{log_id}/",
            json={"wa_message_id": wa_message_id, "status": status},
            headers=_headers(cfg),
        )
        if resp.status_code != 200:
            logger.error("Patch log %s to %s failed with status %s", log_id, status, resp.status_code)


@shared_task(name="worker.tasks.send_broadcast_message", bind=True, max_retries=3)
def send_broadcast_message(self, log_id: str) -> None:
    cfg = _cfg()
    instance_svc = ServiceClient(cfg["instance_url"], cfg["internal_token"])
    logger.info("Processing broadcast log %s", log_id)

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.get(
                f"{cfg['campaigns_url']}/internal/campaigns/logs/{log_id}/",
                headers=_headers(cfg),
            )
            if resp.status_code != 200:
                logger.error("Log %s not found (status %s)", log_id, resp.status_code)
                return
            log_data = resp.json()
    except Exception as exc:
        logger.error("Failed to fetch log %s: %s", log_id, exc)
        raise self.retry(exc=exc, countdown=30) from exc

    user_id = uuid.UUID(log_data["user_id"])
    try:
        cap_check = instance_svc.post(
            f"/internal/instance/users/{user_id}/increment-sent/",
            user_id=user_id,
        )
        if not cap_check.get("allowed"):
            logger.warning("Cap check rejected for user %s", user_id)
            _patch_log(cfg, log_id, "", "failed")
            return
    except Exception as exc:
        logger.error("Cap check failed for user %s: %s", user_id, exc)
        raise self.retry(exc=exc, countdown=30) from exc

    try:
        instance = instance_svc.get(f"/internal/instance/users/{user_id}/", user_id=user_id)
        logger.info("Instance %s status: %s", instance.get("instance_name"), instance.get("status"))
    except Exception as exc:
        logger.error("Instance lookup failed for user %s: %s", user_id, exc)
        _patch_log(cfg, log_id, "", "failed")
        return

    evolution = EvolutionAPIClient(cfg["evolution_url"], cfg["evolution_key"])
    phone = log_data["contact_phone"].lstrip("+")
    try:
        if log_data.get("media_url"):
            result = evolution.send_media(
                instance["instance_name"],
                phone,
                log_data["media_url"],
                log_data["message_text"],
            )
        else:
            result = evolution.send_text(
                instance["instance_name"],
                phone,
                log_data["message_text"],
            )
        logger.info("Evolution API send response: %s", result)
        wa_id = ""
        if isinstance(result, dict):
            wa_id = result.get("key", {}).get("id") or result.get("messageId") or ""
        _patch_log(cfg, log_id, wa_id, "sent")
        logger.info("Message sent, log %s updated", log_id)
    except Exception as exc:
        logger.error("Send failed for log %s: %s", log_id, exc)
        _patch_log(cfg, log_id, "", "failed")
        raise self.retry(exc=exc, countdown=60) from exc


@shared_task(name="worker.tasks.send_chatbot_reply")
def send_chatbot_reply(user_id: str, sender_phone: str, reply_text: str) -> None:
    cfg = _cfg()
    uid = uuid.UUID(user_id)
    instance_svc = ServiceClient(cfg["instance_url"], cfg["internal_token"])
    try:
        instance = instance_svc.get(f"/internal/instance/users/{uid}/", user_id=uid)
    except Exception as exc:
        logger.error("No instance for chatbot reply: %s", exc)
        return
    evolution = EvolutionAPIClient(cfg["evolution_url"], cfg["evolution_key"])
    phone = sender_phone.lstrip("+")
    try:
        evolution.send_text(instance["instance_name"], phone, reply_text)
        instance_svc.post(f"/internal/instance/users/{uid}/increment-sent/", user_id=uid)
    except Exception as exc:
        logger.error("Chatbot reply failed: %s", exc)


@shared_task(name="worker.tasks.reset_daily_sent_counts")
def reset_daily_sent_counts() -> None:
    cfg = _cfg()
    with httpx.Client(timeout=60.0) as client:
        client.post(
            f"{cfg['instance_url']}/internal/instance/reset-daily-counts/",
            headers=_headers(cfg),
        )


@shared_task(name="worker.tasks.increment_warmup_day")
def increment_warmup_day() -> None:
    cfg = _cfg()
    with httpx.Client(timeout=60.0) as client:
        client.post(
            f"{cfg['instance_url']}/internal/instance/increment-warmup/",
            headers=_headers(cfg),
        )


@shared_task(name="worker.tasks.check_instance_health")
def check_instance_health() -> None:
    cfg = _cfg()
    with httpx.Client(timeout=120.0) as client:
        client.post(
            f"{cfg['instance_url']}/internal/instance/health-check/",
            headers=_headers(cfg),
            json={
                "evolution_url": cfg["evolution_url"],
                "evolution_key": cfg["evolution_key"],
            },
        )
