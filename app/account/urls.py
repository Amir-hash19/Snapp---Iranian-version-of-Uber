from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView
from .views import RegisterView, LoginView

urlpatterns = [
    path("sign-up/", RegisterView.as_view(), name="register-user"),
    path("login/", LoginView.as_view(), name="login-user"),
    path("refresh-token/", TokenRefreshView.as_view(), name="token-refresh")

]

