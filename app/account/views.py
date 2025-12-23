from rest_framework import  status
from rest_framework.views import APIView
from rest_framework.generics import GenericAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .throttling import UserBaseThrottle

from .serializers import RegisterSerializer, LoginSerializer, UserBaseSerializer


class testJWTView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response({
            "user": request.user.username,
            "iser_id": request.user.id
        })



class TestHeaderView(APIView):
    def get(self, request):
        
        print("Request headers:", request.headers)
        print("User:", request.user)

        return Response({
            "received_headers": dict(request.headers)
        })



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





class RetrieveUserView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBaseSerializer
    throttle_classes = [UserBaseThrottle]

    def get_queryset(self):
        return User.objects.filter(is_active=True)

    def get_object(self):
        queryset = self.get_queryset()
        obj = queryset.get(pk=self.request.user.pk)
        return obj




class UpdateUserView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserBaseSerializer
    throttle_classes = [UserBaseThrottle]

    def get_object(self):
        return self.request.user
