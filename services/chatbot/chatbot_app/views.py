from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import DisclaimerRequiredMixin, InternalServiceAuthentication

from chatbot_app.models import ChatbotMatchLog, ChatbotRule
from chatbot_app.serializers import ChatbotRuleCreateSerializer, ChatbotRuleSerializer


class ChatbotRuleListCreateView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        rules = ChatbotRule.objects.filter(user_id=request.user.id)
        return Response(ChatbotRuleSerializer(rules, many=True).data)

    def post(self, request):
        serializer = ChatbotRuleCreateSerializer(
            data=request.data,
            context={"user_id": request.user.id},
        )
        serializer.is_valid(raise_exception=True)
        rule = ChatbotRule.objects.create(
            user_id=request.user.id,
            **serializer.validated_data,
        )
        return Response(ChatbotRuleSerializer(rule).data, status=201)


class ChatbotRuleDetailView(DisclaimerRequiredMixin, APIView):
    def patch(self, request, rule_id):
        try:
            rule = ChatbotRule.objects.get(id=rule_id, user_id=request.user.id)
        except ChatbotRule.DoesNotExist:
            return Response(status=404)
        for field in ("keyword", "reply_text", "is_active"):
            if field in request.data:
                setattr(rule, field, request.data[field])
        rule.save()
        return Response(ChatbotRuleSerializer(rule).data)

    def delete(self, request, rule_id):
        deleted, _ = ChatbotRule.objects.filter(
            id=rule_id, user_id=request.user.id
        ).delete()
        if not deleted:
            return Response(status=404)
        return Response(status=204)


class InternalMatchMessageView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        user_id = request.data.get("user_id")
        sender_phone = request.data.get("sender_phone")
        message_text = (request.data.get("message_text") or "").lower()
        if not user_id or not sender_phone:
            return Response({"matched": False})

        rules = ChatbotRule.objects.filter(user_id=user_id, is_active=True, is_fallback=False)
        matched_rule = None
        for rule in rules:
            if rule.keyword.lower() in message_text:
                matched_rule = rule
                break
        if not matched_rule:
            matched_rule = ChatbotRule.objects.filter(
                user_id=user_id, is_active=True, is_fallback=True
            ).first()
            if matched_rule:
                ChatbotMatchLog.objects.create(
                    user_id=user_id,
                    sender_phone=sender_phone,
                    matched_keyword="",
                    is_fallback=True,
                )
                return Response(
                    {
                        "matched": True,
                        "reply_text": matched_rule.reply_text,
                        "matched_keyword": "",
                        "is_fallback": True,
                    }
                )
            return Response({"matched": False})

        ChatbotMatchLog.objects.create(
            user_id=user_id,
            sender_phone=sender_phone,
            matched_keyword=matched_rule.keyword,
            is_fallback=False,
        )
        return Response(
            {
                "matched": True,
                "reply_text": matched_rule.reply_text,
                "matched_keyword": matched_rule.keyword,
                "is_fallback": False,
            }
        )
