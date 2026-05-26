from django.urls import path
from campaigns_app.views import (
    CampaignAnalyticsView,
    CampaignExportView,
    CampaignListCreateView,
    CampaignStatsView,
    CampaignStopView,
    QuickSendView,
)

urlpatterns = [
    path("", CampaignListCreateView.as_view()),
    path("analytics/", CampaignAnalyticsView.as_view()),
    path("quick-send/", QuickSendView.as_view()),
    path("<uuid:campaign_id>/stats/", CampaignStatsView.as_view()),
    path("<uuid:campaign_id>/stop/", CampaignStopView.as_view()),
    path("<uuid:campaign_id>/export/", CampaignExportView.as_view()),
]
