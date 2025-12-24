from django.contrib import admin

from .models import DriverProfile, User

admin.site.register(User)
admin.site.register(DriverProfile)
