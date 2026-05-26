from django.urls import include, path
urlpatterns = [
    path("webhooks/", include("webhook_app.urls")),
]
