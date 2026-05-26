from django.urls import include, path
urlpatterns = [
    path("api/contacts/", include("contacts_app.urls")),
    path("api/groups/", include("contacts_app.group_urls")),
    path("internal/", include("contacts_app.internal_urls")),
]
