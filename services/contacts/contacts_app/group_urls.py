from django.urls import path
from contacts_app.views import GroupListCreateView, GroupMembersView

urlpatterns = [
    path("", GroupListCreateView.as_view()),
    path("<uuid:group_id>/members/", GroupMembersView.as_view()),
]
