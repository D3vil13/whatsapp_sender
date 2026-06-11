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
        resp = client.post(
            url,
            json=json,
            headers={"X-Internal-Token": cfg.internal_service_token},
        )
        if resp.status_code >= 400:
            logger.error("_post_raw to %s returned %s: %s", url, resp.status_code, resp.text[:500])


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
    event = payload.get("event", "")
    logger.info("handle_messages_update: event=%s data_keys=%s", event, list(data.keys()) if isinstance(data, dict) else f"list({len(data)})")
    for update in data if isinstance(data, list) else [data]:
        key = update.get("key", {})
        wa_id = key.get("id") or update.get("keyId") or update.get("messageId")
        # Evolution API v2 nests status inside "update" object, some versions at top level
        status = (update.get("status") or update.get("update", {}).get("status") or "").upper()
        if not status and event in ("send.message", "send_message", "SEND_MESSAGE"):
            status = (data.get("status") or data.get("messageStatus") or "").upper()
            wa_id = wa_id or data.get("messageId")
        logger.info("WA_DEBUG: wa_id=%s status=%s event=%s update_keys=%s", wa_id, status, event, list(update.keys())[:10])
        status_map = {
            "DELIVERY_ACK": "delivered",
            "READ": "read",
            "SERVER_ACK": "sent",
            "SENT": "sent",
        }
        mapped = status_map.get(status)
        if not wa_id or not mapped:
            logger.debug("messages.update skipped: wa_id=%s status=%s", wa_id, status)
            continue
        if mapped in ("delivered", "read"):
            cfg = settings.BULKPING_CONFIG
            logger.info("Processing %s for wa_message_id=%s", mapped, wa_id)
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
        elif "interactiveResponseMessage" in msg_body:
            interactive = msg_body["interactiveResponseMessage"]
            list_resp = interactive.get("listResponseMessage", {}) or \
                        interactive.get("list_reply_responseMessage", {})
            if list_resp:
                row_id = list_resp.get("singleSelectReply", {}).get("selectedRowId", "")
                display = list_resp.get("title", "") or list_resp.get("description", "")
                text = f"__interactive_list__:{row_id}:{display}"
            else:
                button_resp = interactive.get("buttonResponseMessage", {}) or \
                              interactive.get("button_reply_responseMessage", {})
                if button_resp:
                    btn_id = button_resp.get("id", "")
                    btn_text = button_resp.get("text", "") or button_resp.get("displayText", "")
                    text = f"__interactive_button__:{btn_id}:{btn_text}"
        elif "buttonsResponseMessage" in msg_body:
            btn_resp = msg_body["buttonsResponseMessage"]
            btn_id = btn_resp.get("id", "")
            btn_text = btn_resp.get("text", "") or btn_resp.get("displayText", "")
            text = f"__interactive_button__:{btn_id}:{btn_text}"
        elif "listResponseMessage" in msg_body:
            list_resp = msg_body["listResponseMessage"]
            row_id = list_resp.get("singleSelectReply", {}).get("selectedRowId", "")
            display = list_resp.get("title", "")
            text = f"__interactive_list__:{row_id}:{display}"

        sender = key.get("remoteJid", "").split("@")[0]
        if not sender.startswith("+"):
            sender = f"+{sender}"

        # Track reply count — every incoming message from a campaign recipient counts
        _post_raw(
            f"{cfg.campaigns_service_url}/internal/campaigns/logs/by-phone/reply/",
            {"sender_phone": sender},
        )

        # Check chatbot rules for auto-reply
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
            kwargs={
                "user_id": user_id,
                "sender_phone": sender,
                "reply_text": match.get("reply_text", ""),
                "response_type": match.get("response_type", "text"),
                "menu_config": match.get("menu_config"),
                "attachment_url": match.get("attachment_url", ""),
                "rule_id": match.get("rule_id"),
                "flow_id": match.get("flow_id"),
                "branches": match.get("branches"),
            },
            queue="chatbot",
        )
