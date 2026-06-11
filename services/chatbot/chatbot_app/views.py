import re
from datetime import datetime, timedelta, timezone

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from core.authentication import DisclaimerRequiredMixin, InternalServiceAuthentication

from chatbot_app.models import (
    ChatbotBranch,
    ChatbotFlow,
    ChatbotMatchLog,
    ChatbotRule,
    ChatbotSession,
)
from chatbot_app.serializers import (
    ChatbotFlowDetailSerializer,
    ChatbotFlowSerializer,
    ChatbotMatchLogSerializer,
    ChatbotRuleCreateSerializer,
    ChatbotRuleSerializer,
    ChatbotSessionSerializer,
)


# ---------------------------------------------------------------------------
# Flows
# ---------------------------------------------------------------------------

class ChatbotFlowListCreateView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        flows = ChatbotFlow.objects.filter(user_id=request.user.id)
        return Response(ChatbotFlowSerializer(flows, many=True).data)

    def post(self, request):
        data = {**request.data, "user_id": request.user.id}
        serializer = ChatbotFlowSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        flow = ChatbotFlow.objects.create(user_id=request.user.id, **serializer.validated_data)
        return Response(ChatbotFlowDetailSerializer(flow).data, status=201)


class ChatbotFlowDetailView(DisclaimerRequiredMixin, APIView):
    def get(self, request, flow_id):
        try:
            flow = ChatbotFlow.objects.get(id=flow_id, user_id=request.user.id)
        except ChatbotFlow.DoesNotExist:
            return Response(status=404)
        return Response(ChatbotFlowDetailSerializer(flow).data)

    def patch(self, request, flow_id):
        try:
            flow = ChatbotFlow.objects.get(id=flow_id, user_id=request.user.id)
        except ChatbotFlow.DoesNotExist:
            return Response(status=404)
        for field in ("name", "is_active", "welcome_message"):
            if field in request.data:
                setattr(flow, field, request.data[field])
        flow.save()
        return Response(ChatbotFlowDetailSerializer(flow).data)

    def delete(self, request, flow_id):
        deleted, _ = ChatbotFlow.objects.filter(id=flow_id, user_id=request.user.id).delete()
        if not deleted:
            return Response(status=404)
        return Response(status=204)


# ---------------------------------------------------------------------------
# Rules
# ---------------------------------------------------------------------------

class ChatbotRuleListCreateView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        rules = ChatbotRule.objects.filter(user_id=request.user.id)
        flow_id = request.query_params.get("flow_id")
        if flow_id:
            rules = rules.filter(flow_id=flow_id)
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
        writable = (
            "flow", "match_type", "keyword", "reply_text",
            "response_type", "menu_config", "attachment_url",
            "is_active", "is_fallback", "priority", "cooldown_seconds",
        )
        for field in writable:
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


# ---------------------------------------------------------------------------
# Branches
# ---------------------------------------------------------------------------

class ChatbotBranchListCreateView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        rule_id = request.query_params.get("rule_id")
        if not rule_id:
            return Response({"detail": "rule_id query param required"}, status=400)
        branches = ChatbotBranch.objects.filter(rule__user_id=request.user.id, rule_id=rule_id)
        from chatbot_app.serializers import ChatbotBranchSerializer
        return Response(ChatbotBranchSerializer(branches, many=True).data)

    def post(self, request):
        rule_id = request.data.get("rule")
        if not rule_id:
            return Response({"detail": "rule is required"}, status=400)
        try:
            rule = ChatbotRule.objects.get(id=rule_id, user_id=request.user.id)
        except ChatbotRule.DoesNotExist:
            return Response({"detail": "Rule not found"}, status=404)
        branch = ChatbotBranch.objects.create(rule=rule, **{
            k: request.data[k] for k in ("match_type", "match_value", "next_rule", "next_flow")
            if k in request.data
        })
        from chatbot_app.serializers import ChatbotBranchSerializer
        return Response(ChatbotBranchSerializer(branch).data, status=201)


class ChatbotBranchDetailView(DisclaimerRequiredMixin, APIView):
    def patch(self, request, branch_id):
        try:
            branch = ChatbotBranch.objects.get(id=branch_id, rule__user_id=request.user.id)
        except ChatbotBranch.DoesNotExist:
            return Response(status=404)
        for field in ("match_type", "match_value", "next_rule", "next_flow"):
            if field in request.data:
                setattr(branch, field, request.data[field])
        branch.save()
        from chatbot_app.serializers import ChatbotBranchSerializer
        return Response(ChatbotBranchSerializer(branch).data)

    def delete(self, request, branch_id):
        deleted, _ = ChatbotBranch.objects.filter(
            id=branch_id, rule__user_id=request.user.id
        ).delete()
        if not deleted:
            return Response(status=404)
        return Response(status=204)


# ---------------------------------------------------------------------------
# Sessions
# ---------------------------------------------------------------------------

class ChatbotSessionListView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        sessions = ChatbotSession.objects.filter(user_id=request.user.id)
        return Response(ChatbotSessionSerializer(sessions, many=True).data)

    def delete(self, request, session_id):
        deleted, _ = ChatbotSession.objects.filter(
            id=session_id, user_id=request.user.id
        ).delete()
        if not deleted:
            return Response(status=404)
        return Response(status=204)


# ---------------------------------------------------------------------------
# Match Logs
# ---------------------------------------------------------------------------

class ChatbotMatchLogListView(DisclaimerRequiredMixin, APIView):
    def get(self, request):
        logs = ChatbotMatchLog.objects.filter(user_id=request.user.id)[:200]
        return Response(ChatbotMatchLogSerializer(logs, many=True).data)


# ---------------------------------------------------------------------------
# Internal: enhanced message matching
# ---------------------------------------------------------------------------

class InternalMatchMessageView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        user_id = request.data.get("user_id")
        sender_phone = request.data.get("sender_phone")
        message_text = request.data.get("message_text") or ""

        if not user_id or not sender_phone:
            return Response({"matched": False})

        match_type, match_value = self._parse_interactive(message_text)
        message_lower = message_text.lower().strip()

        matched_rule = None

        # 1. Check if user has an active session -> continue from that flow/rule
        session = ChatbotSession.objects.filter(
            user_id=user_id, sender_phone=sender_phone
        ).first()

        if session and session.current_rule:
            # Check branches on the current rule
            branch_rules = self._match_branch(
                session.current_rule, match_type, match_value, message_lower
            )
            if branch_rules:
                matched_rule = branch_rules
            else:
                # If no branch matches, fall through to normal matching
                pass

        # 2. Normal matching (if no session or no branch match)
        if not matched_rule:
            matched_rule = self._match_normal(
                user_id, match_type, match_value, message_lower
            )

        if not matched_rule:
            # 3. Fallback rule
            matched_rule = ChatbotRule.objects.filter(
                user_id=user_id, is_active=True, is_fallback=True
            ).first()
            if not matched_rule:
                return Response({"matched": False})

            self._log_match(user_id, sender_phone, matched_rule, "", is_fallback=True)
            return self._build_reply(matched_rule, user_id, sender_phone, "", is_fallback=True)

        self._log_match(
            user_id, sender_phone, matched_rule,
            matched_rule.keyword if matched_rule.match_type in (
                "keyword_contains", "keyword_exact", "keyword_regex"
            ) else match_value or "",
        )
        return self._build_reply(matched_rule, user_id, sender_phone, match_value or "")

    def _parse_interactive(self, text):
        if text.startswith("__interactive_list__:"):
            parts = text.split(":", 3)
            return ("list_selection", parts[2] if len(parts) >= 3 else "")
        if text.startswith("__interactive_button__:"):
            parts = text.split(":", 3)
            return ("button_id", parts[2] if len(parts) >= 3 else "")
        return ("keyword_contains", "")

    def _match_branch(self, rule, match_type, match_value, message_lower):
        branches = ChatbotBranch.objects.filter(rule=rule)
        for branch in branches:
            if branch.match_type == match_type and branch.match_value == match_value:
                if branch.next_rule:
                    return branch.next_rule
                if branch.next_flow:
                    first = ChatbotRule.objects.filter(
                        flow=branch.next_flow, is_active=True
                    ).order_by("priority", "created_at").first()
                    return first
        return None

    def _match_normal(self, user_id, match_type, match_value, message_lower):
        rules = ChatbotRule.objects.filter(
            user_id=user_id, is_active=True, is_fallback=False
        ).order_by("priority", "created_at")

        for rule in rules:
            if match_type == "button_id" and rule.match_type == "button_id":
                if rule.keyword.lower() == match_value.lower():
                    return rule
            elif match_type == "list_selection" and rule.match_type == "list_selection":
                if rule.keyword.lower() == match_value.lower():
                    return rule
            elif rule.match_type == "keyword_contains":
                if rule.keyword.lower() in message_lower:
                    return rule
            elif rule.match_type == "keyword_exact":
                if message_lower == rule.keyword.lower():
                    return rule
            elif rule.match_type == "keyword_regex":
                try:
                    if re.search(rule.keyword, message_lower):
                        return rule
                except re.error:
                    pass
            elif rule.match_type == "always":
                return rule
        return None

    def _log_match(self, user_id, sender_phone, rule, matched_keyword, is_fallback=False):
        ChatbotMatchLog.objects.create(
            user_id=user_id,
            sender_phone=sender_phone,
            matched_keyword=matched_keyword,
            matched_rule=rule,
            matched_flow=rule.flow if hasattr(rule, "flow") and rule.flow_id else None,
            is_fallback=is_fallback,
        )

    def _build_reply(self, rule, user_id, sender_phone, matched_value, is_fallback=False):
        reply_data = {
            "matched": True,
            "reply_text": rule.reply_text,
            "response_type": rule.response_type,
            "matched_keyword": rule.keyword if not is_fallback else "",
            "is_fallback": is_fallback,
            "rule_id": str(rule.id),
            "flow_id": str(rule.flow_id) if rule.flow_id else None,
        }

        if rule.response_type in ("list_menu", "buttons") and rule.menu_config:
            reply_data["menu_config"] = rule.menu_config
        if rule.attachment_url:
            reply_data["attachment_url"] = rule.attachment_url

        # Check for branch routing
        if rule.response_type in ("list_menu", "buttons"):
            branches = ChatbotBranch.objects.filter(rule=rule).values(
                "match_value", "next_rule", "next_flow"
            )
            branch_map = {b["match_value"]: b for b in branches}
            if branch_map:
                reply_data["branches"] = branch_map

        # Update or create session
        if rule.flow_id:
            ChatbotSession.objects.update_or_create(
                user_id=user_id,
                sender_phone=sender_phone,
                defaults={
                    "current_flow_id": rule.flow_id,
                    "current_rule": rule,
                    "variables": {},
                },
            )

        return Response(reply_data)


class InternalProcessInteractiveView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        user_id = request.data.get("user_id")
        sender_phone = request.data.get("sender_phone")
        match_type = request.data.get("match_type", "button_id")
        match_value = request.data.get("match_value", "")

        if not user_id or not sender_phone or not match_value:
            return Response({"matched": False})

        rule = ChatbotRule.objects.filter(
            user_id=user_id, is_active=True,
            match_type=match_type, keyword__iexact=match_value,
        ).first()

        if not rule:
            return Response({"matched": False})

        ChatbotMatchLog.objects.create(
            user_id=user_id,
            sender_phone=sender_phone,
            matched_keyword=match_value,
            matched_rule=rule,
            matched_flow=rule.flow,
        )

        reply_data = {
            "matched": True,
            "reply_text": rule.reply_text,
            "response_type": rule.response_type,
            "rule_id": str(rule.id),
            "flow_id": str(rule.flow_id) if rule.flow_id else None,
        }
        if rule.response_type in ("list_menu", "buttons") and rule.menu_config:
            reply_data["menu_config"] = rule.menu_config
        if rule.attachment_url:
            reply_data["attachment_url"] = rule.attachment_url

        return Response(reply_data)


class InternalSessionCreateView(APIView):
    authentication_classes = [InternalServiceAuthentication]

    def post(self, request):
        user_id = request.data.get("user_id")
        sender_phone = request.data.get("sender_phone")
        flow_id = request.data.get("flow_id")
        rule_id = request.data.get("rule_id")

        if not user_id or not sender_phone:
            return Response({"error": "user_id and sender_phone required"}, status=400)

        session, created = ChatbotSession.objects.update_or_create(
            user_id=user_id,
            sender_phone=sender_phone,
            defaults={
                "current_flow_id": flow_id,
                "current_rule_id": rule_id,
            },
        )
        return Response(ChatbotSessionSerializer(session).data)
