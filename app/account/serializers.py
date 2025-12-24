from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import DriverProfile, User


class RegisterSerializer(serializers.ModelSerializer):

    """
    endpoint for user registration
    args:
        wallet_balance (decimal): Initial wallet balance for the user
        full_name (str): Full name of the user
        phone_number (str): Phone number of the user
        email (str): Email address of the user
        password (str): Password for the user account
        password2 (str): Confirmation of the password
    returns:    
        This endpoint returns: a User object
    exceptions:
        Raises ValidationError if the password fields do not match.
    example out put:
        {
            "wallet_balance": "100.00", 
            "full_name": "John Doe",
            "phone_number": "1234567890",
            "email": "john@example.com",
            "password": "securepassword",
            "password2": "securepassword"
        }
    """
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = (
            "wallet_balance",
            "full_name",
            "phone_number",
            "email",
            "password",
            "password2",
        )

    def validate(self, attrs):
        if attrs["password"] != attrs["password2"]:
            raise serializers.ValidationError(
                {"password": "password fields did not match."}
            )
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data["email"],
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            wallet_balance=validated_data["wallet_balance"],
        )
        user.set_password(validated_data["password"])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """endpoint for user login using email and password
    args:
        email (str): email of the user
        password (str): password of the user
    returns:    
        This endpoint returns: a dictionary containing JWT tokens and success message
    exceptions:
        Raises ValidationError if the provided credentials are invalid.
    example out put:
        {
            "refresh": "refresh_token_string",
            "access": "access_token_string",
            "message": "Login Successfully",
            "status": 200
        }        
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(username=email, password=password)
            if not user:
                raise serializers.ValidationError("Invalid email or password")
        else:
            raise serializers.ValidationError("Email and password required")

        attrs["user"] = user
        return attrs

    def create(self, validated_data):
        user = validated_data["user"]
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "message": "Login Successfully",
        }


class UserBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "phone_number",
            "full_name",
            "date_joined",
            "wallet_balance",
        ]


class UserDriverSerializer(serializers.ModelSerializer):

    """endpoint to retrieve user details along with role field"""

    class Meta:
        model = User
        fields = [
            "email",
            "password",
            "phone_number",
            "full_name",
            "date_joined",
            "wallet_balance",
            "role",
        ]


class ChangeUserToDriverSerializer(serializers.Serializer):
    """
    This serializer is used to change a user to a driver.
    It requires vehicle_type and vehicle_plate fields.
    args:
        vehicle_type (str): Type of the vehicle
        vehicle_plate (str): Vehicle plate number
    returns:    
        This endpoint returns: a DriverProfile object
    exceptions:
        Raises ValidationError if the user is already a driver or if a DriverProfile already exists for the user.

    """
    vehicle_type = serializers.CharField(max_length=225)
    vehicle_plate = serializers.CharField(max_length=20)

    def validate(self, data):
        user = self.context["request"].user
        if user.role == User.DRIVER:
            raise serializers.ValidationError("User is already a driver.")
        if DriverProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError("Driver profile already exists.")
        return data

    def create(self, validated_data):
        user = self.context["request"].user
        user.role = User.DRIVER
        user.save()
        driver_profile = DriverProfile.objects.create(
            user=user,
            vehicle_type=validated_data["vehicle_type"],
            vehicle_plate=validated_data["vehicle_plate"],
        )
        return driver_profile
