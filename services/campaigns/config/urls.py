from django.urls import include, path
urlpatterns = [
    path("api/campaigns/", include("campaigns_app.urls")),
    path("internal/campaigns/", include("campaigns_app.internal_urls")),
]
