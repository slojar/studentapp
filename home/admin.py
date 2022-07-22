from django.contrib import admin
from .models import Hostel, Profile


class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number", "account_type"]


admin.site.register(Hostel)
admin.site.register(Profile, ProfileModelAdmin)
