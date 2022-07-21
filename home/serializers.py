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
    profile_picture = serializers.SerializerMethodField()

    def get_profile_picture(self, obj):
        image = None
        request = self.context.get('request')
        if obj.image:
            image = obj.image.url
            if request:
                image = request.build_absolute_uri(obj.image.url)
        return image

    class Meta:
        model = Profile
        exclude = []


