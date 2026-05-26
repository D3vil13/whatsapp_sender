import uuid

from django.db.models import Count
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import DisclaimerRequiredMixin, InternalServiceAuthentication

from contacts_app.models import Contact, ContactGroup
from contacts_app.serializers import (
    ContactCreateSerializer,
    ContactSerializer,
    GroupCreateSerializer,
    GroupMembersSerializer,
    GroupSerializer,
)
from contacts_app.utils import parse_contacts_csv


class ContactImportView(DisclaimerRequiredMixin, APIView):
    def post(self, request):
        file = request.FILES.get("file")
        if not file:
            return Response({"detail": "CSV file required"}, status=400)
        rows = parse_contacts_csv(file)
        imported = skipped = 0
        errors = []
        for i, row in enumerate(rows, start=1):
            if Contact.objects.filter(user_id=request.user.id, phone=row["phone"]).exists():
                skipped += 1
                continue
            try:
                Contact.objects.create(
                    user_id=request.user.id,
                    name=row["name"],
                    phone=row["phone"],
                )
                imported += 1
            except Exception as exc:
                errors.append({"row": i, "error": str(exc)})
        return Response(
            {
                "total": len(rows),
                "imported": imported,
                "skipped": skipped,
                "errors": errors,
                "disclaimer": "Only import contacts who opted in to receive WhatsApp messages from you.",
            }
        )


class ContactListCreateView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        contacts = Contact.objects.filter(user_id=request.user.id).order_by("-created_at")
        return Response(ContactSerializer(contacts, many=True).data)

    def post(self, request):
        serializer = ContactCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contact, created = Contact.objects.get_or_create(
            user_id=request.user.id,
            phone=serializer.validated_data["phone"],
            defaults={"name": serializer.validated_data["name"]},
        )
        if not created:
            return Response({"detail": "Contact already exists"}, status=400)
        return Response(ContactSerializer(contact).data, status=201)


class ContactDeleteView(DisclaimerRequiredMixin, APIView):
    def delete(self, request, contact_id):
        deleted, _ = Contact.objects.filter(
            id=contact_id, user_id=request.user.id
        ).delete()
        if not deleted:
            return Response(status=404)
        return Response(status=204)


class GroupListCreateView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        groups = (
            ContactGroup.objects.filter(user_id=request.user.id)
            .annotate(member_count=Count("contacts"))
            .order_by("-created_at")
        )
        return Response(GroupSerializer(groups, many=True).data)

    def post(self, request):
        serializer = GroupCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        group = ContactGroup.objects.create(
            user_id=request.user.id,
            name=serializer.validated_data["name"],
        )
        group.member_count = 0
        return Response(GroupSerializer(group).data, status=201)


class GroupMembersView(DisclaimerRequiredMixin, APIView):
    def get(self, request, group_id):
        try:
            group = ContactGroup.objects.get(id=group_id, user_id=request.user.id)
        except ContactGroup.DoesNotExist:
            return Response(status=404)
        contacts = group.contacts.all().order_by("name")
        return Response(ContactSerializer(contacts, many=True).data)

    def post(self, request, group_id):
        return self._modify(request, group_id, add=True)

    def delete(self, request, group_id):
        return self._modify(request, group_id, add=False)

    def _modify(self, request, group_id, add: bool):
        try:
            group = ContactGroup.objects.get(id=group_id, user_id=request.user.id)
        except ContactGroup.DoesNotExist:
            return Response(status=404)
        serializer = GroupMembersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        contacts = Contact.objects.filter(
            id__in=serializer.validated_data["contact_ids"],
            user_id=request.user.id,
        )
        if add:
            group.contacts.add(*contacts)
        else:
            group.contacts.remove(*contacts)
        return Response({"updated": contacts.count()})


class InternalGroupContactsView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def get(self, request, group_id):
        user_id = uuid.UUID(request.META["HTTP_X_USER_ID"])
        try:
            group = ContactGroup.objects.get(id=group_id, user_id=user_id)
        except ContactGroup.DoesNotExist:
            return Response(status=404)
        contacts = group.contacts.all().values("id", "name", "phone")
        return Response({"contacts": list(contacts)})
