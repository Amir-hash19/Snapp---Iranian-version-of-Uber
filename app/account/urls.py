from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView, TokenObtainPairView
from .views import RegisterView, LoginView, RetrieveUserView, TestHeaderView, testJWTView, UpdateUserView

urlpatterns = [
    path("sign-up/", RegisterView.as_view(), name="register-user"),
    path("login/", LoginView.as_view(), name="login-user"),
    path("you/", RetrieveUserView.as_view(), name="retrieve-user"),
    path("you/edit/", UpdateUserView.as_view(), name="edit-user"),

    #this two endpoints is useful for testing headers and jwt tokens
    path("test/", TestHeaderView.as_view()),
    path("test-jwt/", testJWTView.as_view()),

    path("refresh-token/", TokenRefreshView.as_view(), name="token-refresh"),
    path("token-get/", TokenObtainPairView.as_view()),
    path("verify-token/", TokenVerifyView.as_view(), name="token-verify")

]

