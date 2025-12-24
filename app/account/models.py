from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """
    This class manager provides methods to create user and superuser
    """

    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        """this function creates and saves a User with the given email and password

        Args:
            email (str): email of the user
            password (str, optional): password of the user. Defaults to None.

        This endpoint returns: a User object
        """

        if not email:
            raise ValueError("Email field is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """this function creates and saves a superuser with the given email and password

        Args:
            email (str): email of the superuser
            password (str, optional): password of the superuser. Defaults to None.

        This endpoint returns: a SuperUser object
        """

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    This class represents a custom user model that uses email as the username field.
    It includes fields for email, password, is_active, is_staff, is_superuser, and date_joined.
    It also includes a property method full_name that returns the user's full name
    if a UserProfile exists for the user, otherwise it returns the email.
    """

    USER = "user"
    DRIVER = "driver"
    ADMIN = "admin"

    ROLE_CHOICES = (
        (USER, "Normal User"),
        (DRIVER, "Driver"),
        (ADMIN, "Admin"),
    )

    role = models.CharField(
        max_length=10, choices=ROLE_CHOICES, default=USER, db_index=True
    )
    wallet_balance = models.PositiveIntegerField(default=0)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255, null=False, blank=False)
    phone_number = models.CharField(unique=True, max_length=15, null=False, blank=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    @property
    def get_full_name(self):
        return f"{self.full_name}"

    def __str__(self):
        return f"{self.email} and {self.id}"


class DriverProfile(models.Model):
    user = models.OneToOneField(
        to=User, on_delete=models.CASCADE, related_name="driver_profile"
    )
    vehicle_type = models.CharField(max_length=225)
    vehicle_plate = models.CharField(max_length=20)

    is_available = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Driver Profile - {self.user.email}"
