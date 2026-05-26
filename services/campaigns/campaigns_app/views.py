import csv
import io
import uuid

from django.db.models import F
from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import DisclaimerRequiredMixin, InternalServiceAuthentication

from campaigns_app.models import Campaign, CampaignStatus, MessageLog, MessageStatus
from campaigns_app.serializers import (
    CampaignCreateSerializer,
    CampaignListSerializer,
    MessageLogSerializer,
    QuickSendSerializer,
)
from campaigns_app import services as campaign_services
from campaigns_app.tasks_client import enqueue_broadcast_messages, enqueue_single_message


class CampaignListCreateView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        campaigns = Campaign.objects.filter(user_id=request.user.id).order_by("-created_at")
        return Response(CampaignListSerializer(campaigns, many=True).data)

    def post(self, request):
        serializer = CampaignCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        contacts = campaign_services.fetch_group_contacts(
            request.user.id, data["group_id"]
        )
        if not contacts:
            return Response({"detail": "Group has no contacts"}, status=400)

        campaign = Campaign.objects.create(
            user_id=request.user.id,
            name=data["name"],
            message_text=data["message_text"],
            media_url=data.get("media_url") or None,
            group_id=data["group_id"],
            status=CampaignStatus.SENDING,
            scheduled_at=data.get("scheduled_at"),
            total_count=len(contacts),
        )
        logs = []
        for contact in contacts:
            logs.append(
                MessageLog(
                    campaign=campaign,
                    contact_id=contact["id"],
                    contact_name=contact["name"],
                    contact_phone=contact["phone"],
                )
            )
        MessageLog.objects.bulk_create(logs)
        log_ids = list(
            MessageLog.objects.filter(campaign=campaign).values_list("id", flat=True)
        )
        for i, log in enumerate(MessageLog.objects.filter(campaign=campaign).order_by("id")):
            log.task_index = i
            log.save(update_fields=["task_index"])

        enqueue_broadcast_messages(campaign.id, log_ids)

        warning = campaign_services.broadcast_hours_warning(data.get("scheduled_at"))
        response_data = CampaignListSerializer(campaign).data
        if warning:
            response_data["warning"] = warning
        return Response(response_data, status=201)


def _campaign_analytics(campaign: Campaign) -> dict:
    logs = campaign.logs.all()
    failed_count = logs.filter(status=MessageStatus.FAILED).count()
    pending_count = logs.filter(status=MessageStatus.PENDING).count()
    ignored_count = campaign.delivered_count - campaign.read_count
    open_rate = round((campaign.read_count / campaign.delivered_count * 100), 1) if campaign.delivered_count else 0.0
    return {
        "id": str(campaign.id),
        "name": campaign.name,
        "status": campaign.status,
        "total_count": campaign.total_count,
        "queued_processing": pending_count,
        "sent_count": campaign.sent_count,
        "delivered_count": campaign.delivered_count,
        "read_count": campaign.read_count,
        "ignored_count": max(ignored_count, 0),
        "failed_count": failed_count,
        "reply_count": campaign.reply_count,
        "open_rate": open_rate,
        "stopped": campaign.status == CampaignStatus.STOPPED,
    }


class CampaignStatsView(DisclaimerRequiredMixin, APIView):
    def get(self, request, campaign_id):
        try:
            campaign = Campaign.objects.get(id=campaign_id, user_id=request.user.id)
        except Campaign.DoesNotExist:
            return Response(status=404)
        data = _campaign_analytics(campaign)
        data["logs"] = MessageLogSerializer(campaign.logs.all().order_by("contact_name"), many=True).data
        return Response(data)


class CampaignAnalyticsView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        campaigns = Campaign.objects.filter(user_id=request.user.id)
        totals = {
            "total_campaigns": campaigns.count(),
            "total_recipients": sum(c.total_count for c in campaigns),
            "total_sent": sum(c.sent_count for c in campaigns),
            "total_delivered": sum(c.delivered_count for c in campaigns),
            "total_read": sum(c.read_count for c in campaigns),
            "total_failed": sum(c.logs.filter(status=MessageStatus.FAILED).count() for c in campaigns),
            "total_pending": sum(c.logs.filter(status=MessageStatus.PENDING).count() for c in campaigns),
            "total_replied": sum(c.reply_count for c in campaigns),
            "total_stopped": campaigns.filter(status=CampaignStatus.STOPPED).count(),
            "campaigns": [_campaign_analytics(c) for c in campaigns.order_by("-created_at")],
        }
        return Response(totals)


class CampaignExportView(DisclaimerRequiredMixin, APIView):
    def get(self, request, campaign_id):
        try:
            campaign = Campaign.objects.get(id=campaign_id, user_id=request.user.id)
        except Campaign.DoesNotExist:
            return Response(status=404)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["name", "phone", "status", "status_updated_at"])
        for log in campaign.logs.all():
            writer.writerow([
                log.contact_name,
                log.contact_phone,
                log.status,
                log.status_updated_at.isoformat() if log.status_updated_at else "",
            ])
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="campaign_{campaign_id}.csv"'
        return response


class CampaignStopView(DisclaimerRequiredMixin, APIView):
    def post(self, request, campaign_id):
        updated = Campaign.objects.filter(id=campaign_id, user_id=request.user.id).update(
            status=CampaignStatus.STOPPED
        )
        if not updated:
            return Response(status=404)
        return Response({"ok": True})


class QuickSendView(DisclaimerRequiredMixin, APIView):
    def post(self, request):
        serializer = QuickSendSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        campaign = Campaign.objects.create(
            user_id=request.user.id,
            name=f"Quick: {data['name']}",
            message_text=data["message_text"],
            media_url=data.get("media_url") or None,
            group_id=uuid.uuid4(),
            status=CampaignStatus.SENDING,
            total_count=1,
        )
        log = MessageLog.objects.create(
            campaign=campaign,
            contact_id=uuid.uuid4(),
            contact_name=data["name"],
            contact_phone=data["phone"],
        )
        enqueue_single_message(str(log.id))
        return Response(CampaignListSerializer(campaign).data, status=201)


class InternalMessageLogView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def patch(self, request, log_id):
        try:
            log = MessageLog.objects.select_related("campaign").get(id=log_id)
        except MessageLog.DoesNotExist:
            return Response(status=404)
        wa_message_id = request.data.get("wa_message_id")
        new_status = request.data.get("status")
        if wa_message_id is not None:
            log.wa_message_id = wa_message_id
        if new_status:
            log.status = new_status
            log.status_updated_at = timezone.now()
        log.save()
        campaign = log.campaign
        if new_status == MessageStatus.SENT:
            Campaign.objects.filter(id=campaign.id).update(sent_count=F("sent_count") + 1)
        elif new_status == MessageStatus.FAILED:
            pass
        return Response({"ok": True})

    def get(self, request, log_id):
        try:
            log = MessageLog.objects.select_related("campaign").get(id=log_id)
        except MessageLog.DoesNotExist:
            return Response(status=404)
        campaign = log.campaign
        return Response(
            {
                "log_id": str(log.id),
                "campaign_id": str(campaign.id),
                "user_id": str(campaign.user_id),
                "contact_phone": log.contact_phone,
                "message_text": campaign.message_text,
                "media_url": campaign.media_url,
                "status": log.status,
            }
        )

class InternalMessageUpdateByWaIdView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        wa_message_id = request.data.get("wa_message_id")
        new_status = request.data.get("status")
        try:
            log = MessageLog.objects.select_related("campaign").get(wa_message_id=wa_message_id)
        except MessageLog.DoesNotExist:
            return Response(status=404)
        log.status = new_status
        log.status_updated_at = timezone.now()
        log.save(update_fields=["status", "status_updated_at"])
        campaign = log.campaign
        counter_field = None
        if new_status == MessageStatus.DELIVERED:
            counter_field = "delivered_count"
        elif new_status == MessageStatus.READ:
            counter_field = "read_count"
        if counter_field:
            Campaign.objects.filter(id=campaign.id).update(
                **{counter_field: F(counter_field) + 1}
            )
        return Response({"ok": True})


class InternalReplyIncrementView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request, campaign_id):
        updated = Campaign.objects.filter(id=campaign_id).update(
            reply_count=F("reply_count") + 1
        )
        return Response({"ok": bool(updated)})
