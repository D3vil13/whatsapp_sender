from django.urls import path
from contacts_app.views import InternalGroupContactsView

urlpatterns = [
    path("groups/<uuid:group_id>/contacts/", InternalGroupContactsView.as_view()),
]
