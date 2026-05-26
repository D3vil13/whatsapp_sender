import logging

from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from webhook_app import handlers

logger = logging.getLogger(__name__)


class EvolutionWebhookView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        secret = request.META.get("HTTP_X_WEBHOOK_SECRET", "")
        if secret != settings.BULKPING_CONFIG.webhook_secret:
            logger.warning("Webhook rejected: invalid secret")
            return Response({"detail": "Forbidden"}, status=403)

        event = request.data.get("event") or request.data.get("type", "")
        payload = request.data

        try:
            if event in ("messages.upsert", "MESSAGES_UPSERT"):
                handlers.handle_messages_upsert(payload)
            elif event in ("messages.update", "MESSAGES_UPDATE"):
                handlers.handle_messages_update(payload)
            elif event in ("connection.update", "CONNECTION_UPDATE"):
                handlers.handle_connection_update(payload)
            elif event in ("qrcode.updated", "QRCODE_UPDATED"):
                handlers.handle_qrcode_updated(payload)
            else:
                logger.debug("Unhandled event type: %s", event)
        except Exception as exc:
            logger.error("Webhook handler error for event %s: %s", event, exc, exc_info=True)

        return Response({"ok": True})
