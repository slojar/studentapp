# Admin Fields: first_name, last_name, email, phone_number, profile_picture, gender,
# Student Fields: first_name, last_name, email, phone_number, profile_picture, gender, department, matric_number, hostel
# Hostel Field: name
# Department Field: name

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token

GENDER_CHOICES = (
    ("male", "Male"), ("female", "Female")
)

ROLE_CHOICES = (
    ("student", "Student"), ("admin", "Admin"), ("superadmin", "Superadmin")
)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Hostel(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Department(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    hostel = models.ForeignKey(Hostel, on_delete=models.SET_NULL, null=True, blank=True)
    phone_number = models.CharField(max_length=11, default="")
    profile_picture = models.ImageField(upload_to="profile_pictures", blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default="male")
    account_type = models.CharField(max_length=20, choices=ROLE_CHOICES, default="student")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True)
    matric_no = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"ID: {self.pk}, user: {self.user}"

    def get_user_details(self):
        data = dict()
        data["first_name"] = self.user.first_name
        data["last_name"] = self.user.last_name
        data["email"] = self.user.email
        data["date_joined"] = self.user.date_joined
        data["last_visited"] = self.user.last_login
        return data






