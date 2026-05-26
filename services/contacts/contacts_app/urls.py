from django.urls import path
from contacts_app.views import ContactDeleteView, ContactImportView, ContactListCreateView

urlpatterns = [
    path("import/", ContactImportView.as_view()),
    path("", ContactListCreateView.as_view()),
    path("<uuid:contact_id>/", ContactDeleteView.as_view()),
]
