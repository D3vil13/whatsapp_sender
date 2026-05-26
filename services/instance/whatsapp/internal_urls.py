from django.urls import path

from whatsapp.scheduled_views import HealthCheckView, IncrementWarmupView, ResetDailyCountsView
from whatsapp.views import (
    InternalConnectionUpdateView,
    InternalIncrementSentView,
    InternalInstanceByNameView,
    InternalInstanceByUserView,
    InternalQrUpdateView,
)

urlpatterns = [
    path("by-name/<str:instance_name>/", InternalInstanceByNameView.as_view()),
    path("users/<uuid:user_id>/", InternalInstanceByUserView.as_view()),
    path("users/<uuid:user_id>/increment-sent/", InternalIncrementSentView.as_view()),
    path("connection-update/", InternalConnectionUpdateView.as_view()),
    path("qr-update/", InternalQrUpdateView.as_view()),
    path("reset-daily-counts/", ResetDailyCountsView.as_view()),
    path("increment-warmup/", IncrementWarmupView.as_view()),
    path("health-check/", HealthCheckView.as_view()),
]
