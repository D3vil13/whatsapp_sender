from django.urls import path
from webhook_app.views import EvolutionWebhookView

urlpatterns = [
    path("evolution/", EvolutionWebhookView.as_view()),
]
