from django.urls import path

from whatsapp.views import InstanceCreateView, InstanceDisconnectView, InstanceStatusView

urlpatterns = [
    path("create/", InstanceCreateView.as_view()),
    path("status/", InstanceStatusView.as_view()),
    path("disconnect/", InstanceDisconnectView.as_view()),
]
