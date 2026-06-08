from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from bulkping_common.evolution import EvolutionAPIClient, extract_qr_base64

from core.authentication import DisclaimerRequiredMixin, InternalServiceAuthentication

from whatsapp.models import InstanceStatus, WAInstance
from whatsapp.serializers import InstanceStatusSerializer
from whatsapp import services


def _fetch_qr(client: EvolutionAPIClient, instance_name: str) -> str | None:
    """Create or reconnect instance and return QR base64 if available."""
    qr = None
    try:
        created = client.create_instance(instance_name)
        qr = extract_qr_base64(created)
    except Exception as exc:
        err = str(exc).lower()
        if "403" in err or "already" in err or "in use" in err:
            pass
        else:
            raise
    if not qr:
        connect = client.connect_instance(instance_name)
        qr = extract_qr_base64(connect)
    return qr


class InstanceCreateView(DisclaimerRequiredMixin, APIView):
    def post(self, request):
        instance = services.get_or_create_instance(request.user.id)
        client = services.evolution_client()
        try:
            # Check current Evolution state
            state_resp = client.connection_state(instance.instance_name)
            evo_state = state_resp.get("state") or state_resp.get("instance", {}).get("state")
            if evo_state == "open":
                return Response(
                    {"detail": "Instance is already connected. Disconnect first to get a new QR."},
                    status=status.HTTP_409_CONFLICT,
                )
            if evo_state == "close":
                try:
                    client.delete_instance(instance.instance_name)
                except Exception:
                    pass
        except Exception:
            pass

        try:
            qr = _fetch_qr(client, instance.instance_name)
            if qr:
                services.store_qr_cache(instance.instance_name, qr)
            instance.status = InstanceStatus.QR_PENDING
            instance.save(update_fields=["status"])
        except Exception as exc:
            return Response(
                {"detail": f"Failed to create WhatsApp instance: {exc}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )
        return Response(
            {
                "qr_base64": qr or "",
                "instance_name": instance.instance_name,
                "hint": "Open WhatsApp → Linked devices → Link a device → scan this QR",
            }
        )


class InstanceStatusView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        try:
            instance = WAInstance.objects.get(user_id=request.user.id)
        except WAInstance.DoesNotExist:
            return Response(
                {
                    "status": "disconnected",
                    "phone_number": "",
                    "daily_sent_count": 0,
                    "daily_cap": 50,
                    "qr_base64": None,
                },
            )
        client = services.evolution_client()
        data = InstanceStatusSerializer(instance).data

        # Always check actual state from Evolution API
        try:
            state_resp = client.connection_state(instance.instance_name)
            evo_state = state_resp.get("state") or state_resp.get("instance", {}).get("state")

            if evo_state == "open":
                wuid = state_resp.get("wuid", "")
                phone = wuid.split("@")[0] if wuid else ""
                needs_update = False
                if instance.status != InstanceStatus.CONNECTED:
                    instance.status = InstanceStatus.CONNECTED
                    needs_update = True
                if phone and instance.phone_number != phone:
                    instance.phone_number = phone
                    needs_update = True
                if needs_update:
                    instance.save(update_fields=["status", "phone_number"])
                data = InstanceStatusSerializer(instance).data
            elif evo_state == "close":
                if instance.status != InstanceStatus.DISCONNECTED:
                    instance.status = InstanceStatus.DISCONNECTED
                    instance.save(update_fields=["status"])
                data = InstanceStatusSerializer(instance).data
        except Exception:
            pass

        # Attempt to get/refresh QR if still not connected and no cached QR
        if instance.status != InstanceStatus.CONNECTED and not data.get("qr_base64"):
            try:
                connect = client.connect_instance(instance.instance_name)
                qr = extract_qr_base64(connect)
                if qr:
                    services.store_qr_cache(instance.instance_name, qr)
                    data["qr_base64"] = qr
            except Exception:
                pass

        return Response(data)


class InstanceDisconnectView(DisclaimerRequiredMixin, APIView):
    def delete(self, request):
        try:
            instance = WAInstance.objects.get(user_id=request.user.id)
        except WAInstance.DoesNotExist:
            return Response(status=status.HTTP_204_NO_CONTENT)
        try:
            services.evolution_client().delete_instance(instance.instance_name)
        except Exception:
            pass
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class InternalInstanceByNameView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def get(self, request, instance_name):
        try:
            instance = WAInstance.objects.get(instance_name=instance_name)
        except WAInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response({"user_id": str(instance.user_id), "instance_name": instance.instance_name})


class InternalInstanceByUserView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def get(self, request, user_id):
        try:
            instance = WAInstance.objects.get(user_id=user_id)
        except WAInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(
            {
                "instance_name": instance.instance_name,
                "status": instance.status,
                "phone_number": instance.phone_number,
                "daily_sent_count": instance.daily_sent_count,
                "daily_cap": instance.daily_cap,
            }
        )


class InternalIncrementSentView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request, user_id):
        try:
            instance = WAInstance.objects.get(user_id=user_id)
        except WAInstance.DoesNotExist:
            return Response({"allowed": False, "reason": "no_instance"}, status=404)
        if instance.daily_sent_count >= instance.daily_cap:
            return Response({"allowed": False, "reason": "daily_cap_exceeded"})
        instance.daily_sent_count += 1
        instance.save(update_fields=["daily_sent_count"])
        return Response({"allowed": True, "daily_sent_count": instance.daily_sent_count})


class InternalConnectionUpdateView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        instance_name = request.data.get("instance_name")
        state = request.data.get("state")
        phone = request.data.get("phone_number", "")
        try:
            instance = WAInstance.objects.get(instance_name=instance_name)
        except WAInstance.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        if state == "open":
            instance.status = InstanceStatus.CONNECTED
            if phone:
                instance.phone_number = phone
        elif state == "close":
            instance.status = InstanceStatus.DISCONNECTED
        instance.save()
        return Response({"ok": True})


class InternalQrUpdateView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        instance_name = request.data.get("instance_name")
        qr_base64 = request.data.get("qr_base64")
        if instance_name and qr_base64:
            services.store_qr_cache(instance_name, qr_base64)
        return Response({"ok": True})
