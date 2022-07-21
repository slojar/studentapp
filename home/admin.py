from django.contrib import admin
from .models import Hostel, Profile, Department


class ProfileModelAdmin(admin.ModelAdmin):
    list_display = ["user", "phone_number", "account_type"]


admin.site.register(Department)
admin.site.register(Hostel)
admin.site.register(Profile, ProfileModelAdmin)
