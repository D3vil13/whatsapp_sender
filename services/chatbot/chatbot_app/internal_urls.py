from django.urls import path
from chatbot_app.views import (
    InternalMatchMessageView,
    InternalProcessInteractiveView,
    InternalSessionCreateView,
)

urlpatterns = [
    path("match/", InternalMatchMessageView.as_view()),
    path("process-interactive/", InternalProcessInteractiveView.as_view()),
    path("sessions/create/", InternalSessionCreateView.as_view()),
]
