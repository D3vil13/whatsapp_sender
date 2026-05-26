from django.urls import include, path
urlpatterns = [
    path("api/chatbot/", include("chatbot_app.urls")),
    path("internal/chatbot/", include("chatbot_app.internal_urls")),
]
