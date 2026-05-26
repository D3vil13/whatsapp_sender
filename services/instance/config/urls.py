from django.urls import include, path

urlpatterns = [
    path("api/instance/", include("whatsapp.urls")),
    path("internal/instance/", include("whatsapp.internal_urls")),
]
