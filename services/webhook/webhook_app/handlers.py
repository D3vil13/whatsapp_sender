from __future__ import annotations

import logging
from typing import Any

import httpx
from django.conf import settings

from bulkping_common.http import ServiceClient

logger = logging.getLogger(__name__)


def _client(base_url: str) -> ServiceClient:
    cfg = settings.BULKPING_CONFIG
    return ServiceClient(base_url, cfg.internal_service_token)


def _post_raw(url: str, json: dict) -> None:
    cfg = settings.BULKPING_CONFIG
    with httpx.Client(timeout=30.0) as client:
        client.post(
            url,
            json=json,
            headers={"X-Internal-Token": cfg.internal_service_token},
        )


def handle_connection_update(payload: dict[str, Any]) -> None:
    instance_name = payload.get("instance") or payload.get("instanceName")
    data = payload.get("data", payload)
    state = data.get("state") or data.get("connection")
    phone = ""
    if isinstance(data.get("wuid"), str):
        phone = data["wuid"].split("@")[0]
    cfg = settings.BULKPING_CONFIG
    _post_raw(
        f"{cfg.instance_service_url}/internal/instance/connection-update/",
        {"instance_name": instance_name, "state": state, "phone_number": phone},
    )


def handle_qrcode_updated(payload: dict[str, Any]) -> None:
    instance_name = payload.get("instance") or payload.get("instanceName")
    data = payload.get("data", {})
    qr = data.get("qrcode") or data.get("base64")
    if isinstance(qr, dict):
        qr = qr.get("base64")
    cfg = settings.BULKPING_CONFIG
    _post_raw(
        f"{cfg.instance_service_url}/internal/instance/qr-update/",
        {"instance_name": instance_name, "qr_base64": qr},
    )


def handle_messages_update(payload: dict[str, Any]) -> None:
    data = payload.get("data", {})
    for update in data if isinstance(data, list) else [data]:
        key = update.get("key", {})
        wa_id = key.get("id") or update.get("messageId")
        status = (update.get("status") or "").upper()
        status_map = {
            "DELIVERY_ACK": "delivered",
            "READ": "read",
            "SERVER_ACK": "sent",
        }
        mapped = status_map.get(status)
        if not wa_id or not mapped:
            continue
        if mapped in ("delivered", "read"):
            cfg = settings.BULKPING_CONFIG
            _post_raw(
                f"{cfg.campaigns_service_url}/internal/campaigns/logs/by-wa-id/update/",
                {"wa_message_id": wa_id, "status": mapped},
            )


def handle_messages_upsert(payload: dict[str, Any]) -> None:
    data = payload.get("data", {})
    messages = data if isinstance(data, list) else [data]
    instance_name = payload.get("instance") or payload.get("instanceName")
    cfg = settings.BULKPING_CONFIG

    instance_client = _client(cfg.instance_service_url)
    # Resolve user_id from instance_name via instance service DB lookup
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(
            f"{cfg.instance_service_url}/internal/instance/by-name/{instance_name}/",
            headers={"X-Internal-Token": cfg.internal_service_token},
        )
        if resp.status_code != 200:
            return
        user_id = resp.json().get("user_id")

    for message in messages:
        key = message.get("key", {})
        if key.get("fromMe"):
            continue
        text = ""
        msg_body = message.get("message", {})
        if "conversation" in msg_body:
            text = msg_body["conversation"]
        elif "extendedTextMessage" in msg_body:
            text = msg_body["extendedTextMessage"].get("text", "")
        sender = key.get("remoteJid", "").split("@")[0]
        if not sender.startswith("+"):
            sender = f"+{sender}"

        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{cfg.chatbot_service_url}/internal/chatbot/match/",
                json={
                    "user_id": user_id,
                    "sender_phone": sender,
                    "message_text": text,
                },
                headers={"X-Internal-Token": cfg.internal_service_token},
            )
            if resp.status_code != 200:
                continue
            match = resp.json()
        if not match.get("matched"):
            continue
        from celery import Celery

        app = Celery("bulkping")
        app.conf.broker_url = cfg.redis_url
        app.send_task(
            "worker.tasks.send_chatbot_reply",
            args=[user_id, sender, match["reply_text"]],
            queue="chatbot",
        )
