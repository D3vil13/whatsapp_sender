from django.urls import path

from users.views import LoginView, SignupView, TokenRefreshView, UserProfileInternalView

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("login/", LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("internal/users/<uuid:user_id>/", UserProfileInternalView.as_view()),
]
