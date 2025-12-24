import logging

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


class IsDriverPermission(BasePermission):
    """
    Permission that allows access only to authenticated users who are drivers
    and have an available driver profile.
    Logs detailed reasons for permission denial.
    """

    def has_permission(self, request, view):
        user = getattr(request, "user", None)

        if not user:
            logger.warning("No user in request.")
            return False

        if not getattr(user, "is_authenticated", False):
            logger.warning("User is not authenticated.")
            return False

        role = getattr(user, "role", None)
        if not role:
            logger.warning(f"User {user} has no role attribute.")
            return False

        if role.upper() != "DRIVER":
            logger.warning(f"User {user} role is not DRIVER: {role}")
            return False

        driver_profile = getattr(user, "driver_profile", None)
        if not driver_profile:
            logger.warning(f"User {user} does not have a driver_profile.")
            return False

        is_available = getattr(driver_profile, "is_available", False)
        if not is_available:
            logger.warning(f"DriverProfile for user {user} is not available.")
            return False

        return True


class IsAssignedDriverPermission(BasePermission):

    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if getattr(user, "role", "").upper() != "DRIVER":
            return False

        return obj.driver == user
