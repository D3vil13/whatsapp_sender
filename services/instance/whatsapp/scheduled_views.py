from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView

from bulkping_common.evolution import EvolutionAPIClient
from bulkping_common.warmup import daily_cap_for_warmup_day

from core.authentication import InternalServiceAuthentication
from whatsapp.models import InstanceStatus, WAInstance


class ResetDailyCountsView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        WAInstance.objects.all().update(daily_sent_count=0)
        return Response({"ok": True})


class IncrementWarmupView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        for instance in WAInstance.objects.all():
            instance.warmup_day += 1
            instance.daily_cap = daily_cap_for_warmup_day(instance.warmup_day)
            instance.save(update_fields=["warmup_day", "daily_cap"])
        return Response({"ok": True})


class HealthCheckView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        evolution_url = request.data.get("evolution_url") or settings.BULKPING_CONFIG.evolution_api_url
        evolution_key = request.data.get("evolution_key") or settings.BULKPING_CONFIG.evolution_api_key
        client = EvolutionAPIClient(evolution_url, evolution_key)
        updated = 0
        for instance in WAInstance.objects.filter(status=InstanceStatus.CONNECTED):
            try:
                state = client.connection_state(instance.instance_name)
                if state.get("state") != "open" and state.get("instance", {}).get("state") != "open":
                    instance.status = InstanceStatus.DISCONNECTED
                    instance.save(update_fields=["status"])
                    updated += 1
            except Exception:
                instance.status = InstanceStatus.DISCONNECTED
                instance.save(update_fields=["status"])
                updated += 1
        return Response({"checked": True, "disconnected": updated})
