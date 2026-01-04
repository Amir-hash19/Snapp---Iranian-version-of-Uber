from django.db import transaction
from rest_framework import status
from rest_framework.generics import (
    CreateAPIView,
    GenericAPIView,
    RetrieveAPIView,
    UpdateAPIView,
)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.utils.timezone import now
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    ChangeUserToDriverSerializer,
    LoginSerializer,
    RegisterSerializer,
    UserBaseSerializer,
)
from .throttling import UserBaseThrottle


class testJWTView(APIView):
    """this endpoint test jwt token and decode it"""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": request.user.username, "iser_id": request.user.id})


class TestHeaderView(APIView):
    """
    This endpoint is useful for testing headers sent by client
    It returns the received headers in the response.
    """

    def get(self, request):

        print("Request headers:", request.headers)
        print("User:", request.user)

        return Response({"received_headers": dict(request.headers)})


class RegisterView(CreateAPIView):
    """
    This endpoint allows users to register by providing necessary details.
    Upon successful registration, it returns the user ID and JWT tokens.
    args:
        wallet_balance (decimal): Initial wallet balance for the user
        full_name (str): Full name of the user
        phone_number (str): Phone number of the user
        email (str): Email address of the user
        password (str): Password for the user account
        password2 (str): Confirmation of the password
    returns:
        This endpoint returns: a dictionary containing user ID and JWT tokens
    exceptions:
        Raises ValidationError if the provided data is invalid or passwords do not match.
    example out put:
        {
            "user": {
                "id": 1,
                "email": "test@test.com",
                "full_name": "John Doe",
                "phone_number": "09123456789",
                "wallet_balance": 1000
            },
            "tokens": {
                "refresh": "refresh_token_string",
    """

    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            tokens = {"refresh": str(refresh), "access": str(refresh.access_token)}
            return Response(
                {"user": {"id": user.id, "email": user.email}, "tokens": tokens},
                status=status.HTTP_201_CREATED,
            )


class LoginView(GenericAPIView):
    """
    In this endpoint, users can log in by providing their email and password.
    Upon successful authentication, it returns JWT tokens for the user.
    args:
        email (str): email of the user
        password (str): password of the user
    returns:
        This endpoint returns: a dictionary containing refresh and access tokens
    exceptions:
        Raises ValidationError if the provided credentials are invalid.
    example out put:
        {
            "refresh": "refresh_token_string",
            "access": "access_token_string"
        }
    """

    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.save()
        return Response(tokens, status=status.HTTP_200_OK)


class RetrieveUserView(RetrieveAPIView):
    """
    In this endpoint, authenticated users can retrieve their own user details.
    args:
        None
    returns:
        This endpoint returns: User object of the authenticated user
        exceptions:
        Raises PermissionDenied if the user is not authenticated.
    example out put:
        {
            "id": 1,
            "email": "test@test.com",
            "full_name": "John Doe",
            "phone_number": "09123456789",
            "wallet_balance": 1000
        }
    """

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
    """endpoint for authenticated users to update their own user details.
    args:
        wallet_balance (decimal, optional): Updated wallet balance for the user
        full_name (str, optional): Updated full name of the user
        phone_number (str, optional): Updated phone number of the user
        email (str, optional): Updated email address of the user
    returns:
        This endpoint returns: Updated User object of the authenticated user
    exceptions:
        Raises PermissionDenied if the user is not authenticated.
    example out put:
        {
            "id": 1,
            "email":    "test@test.com",}
            "full_name": "John Doe",
            "phone_number": "09123456789",
            "wallet_balance": 1000
        }
    """

    permission_classes = [IsAuthenticated]
    serializer_class = UserBaseSerializer
    throttle_classes = [UserBaseThrottle]

    def get_object(self):
        return self.request.user


class EditUserToDriverView(APIView):
    """endpoint for authenticated users to change their role to driver.
    args:
        vehicle_type (str): Type of the vehicle
        vehicle_plate (str): Vehicle plate number
    returns:
        This endpoint returns: a DriverProfile object
    exceptions:
        Raises PermissionDenied if the user is not authenticated or is already a driver.
    example out put:
        {
            "status": "success",
            "message": "You Are now a driver",
            "driver_profile": {
                "vehicle": "Car",
                "vehicle_plate": "ABC123"
            }
        }
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [UserBaseThrottle]

    def post(self, request):
        with transaction.atomic():
            serializer = ChangeUserToDriverSerializer(
                data=request.data, context={"request": request}
            )
            if serializer.is_valid():
                driver_profile = serializer.save()
                return Response(
                    {
                        "status": "success",
                        "message": "You Are now a driver",
                        "driver_profile": {
                            "vehicle": driver_profile.vehicle_type,
                            "vehicle_plate": driver_profile.vehicle_plate,
                        },
                    },
                    status=status.HTTP_201_CREATED,
                )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def health_check(request):
    """this endpoint is just a health checker"""

    return Response(
        {
            "status": "Ok",
            "service": "django-rest-api",
            "version": "1.0.0",
            "timestamp": now(),
        },
        status=status.HTTP_200_OK,
    )
