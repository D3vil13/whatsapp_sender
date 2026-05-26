from django.urls import path
from chatbot_app.views import ChatbotRuleDetailView, ChatbotRuleListCreateView

urlpatterns = [
    path("rules/", ChatbotRuleListCreateView.as_view()),
    path("rules/<uuid:rule_id>/", ChatbotRuleDetailView.as_view()),
]
