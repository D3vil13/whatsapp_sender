from django.urls import path
from chatbot_app.views import InternalMatchMessageView

urlpatterns = [
    path("match/", InternalMatchMessageView.as_view()),
]
