from django.urls import path
from accounts.views import UserRegistration, UserLoginView, TokenRefreshView

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("register/", UserRegistration.as_view(), name="register"),
]
