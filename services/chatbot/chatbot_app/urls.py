from django.urls import path
from chatbot_app.views import (
    ChatbotBranchDetailView,
    ChatbotBranchListCreateView,
    ChatbotFlowDetailView,
    ChatbotFlowListCreateView,
    ChatbotMatchLogListView,
    ChatbotRuleDetailView,
    ChatbotRuleListCreateView,
    ChatbotSessionListView,
)

urlpatterns = [
    path("rules/", ChatbotRuleListCreateView.as_view()),
    path("rules/<uuid:rule_id>/", ChatbotRuleDetailView.as_view()),
    path("flows/", ChatbotFlowListCreateView.as_view()),
    path("flows/<uuid:flow_id>/", ChatbotFlowDetailView.as_view()),
    path("branches/", ChatbotBranchListCreateView.as_view()),
    path("branches/<uuid:branch_id>/", ChatbotBranchDetailView.as_view()),
    path("sessions/", ChatbotSessionListView.as_view()),
    path("sessions/<uuid:session_id>/", ChatbotSessionListView.as_view()),
    path("logs/", ChatbotMatchLogListView.as_view()),
]
