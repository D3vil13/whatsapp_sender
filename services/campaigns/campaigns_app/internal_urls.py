from django.urls import path
from campaigns_app.views import (
    InternalMessageLogView,
    InternalMessageUpdateByWaIdView,
    InternalReplyIncrementView,
)

urlpatterns = [
    path("logs/<uuid:log_id>/", InternalMessageLogView.as_view()),
    path("logs/by-wa-id/update/", InternalMessageUpdateByWaIdView.as_view()),
    path("<uuid:campaign_id>/reply/", InternalReplyIncrementView.as_view()),
]
