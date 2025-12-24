from rest_framework.throttling import UserRateThrottle


class UserBaseThrottle(UserRateThrottle):
    scope = "user_base"
