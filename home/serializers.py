from rest_framework import serializers
from .models import Profile, Hostel


class HostelSerializer(serializers.ModelSerializer):

    user_detail = serializers.SerializerMethodField()

    def get_user_detail(self, obj):
        return obj.get_user_details()

    class Meta:
        model = Hostel
        exclude = []


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        exclude = []


