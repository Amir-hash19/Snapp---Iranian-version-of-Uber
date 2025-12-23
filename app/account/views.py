from rest_framework import viewsets, status
from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import SessionAuthentication
from rest_framework.response import Response
from django.shortcuts import redirect
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction


from .serializers import RegisterSerializer, LoginSerializer



class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            tokens = {
                "refresh": str(refresh),
                "access": str(refresh.access_token)
            }
            return Response({
                "user": {
                    "id":user.id,
                    "email":user.email
                },
                "tokens": tokens
            }, status=status.HTTP_201_CREATED)
        


class LoginView(GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(tokens, status=status.HTTP_200_OK)

