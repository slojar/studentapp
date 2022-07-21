from rest_framework import serializers
from .models import Profile, Hostel, Department


class HostelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hostel
        exclude = []


class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        exclude = []


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    hostel = serializers.SerializerMethodField()
    department = serializers.SerializerMethodField()

    def get_user_detail(self, obj):
        return obj.get_user_details()

    def get_profile_picture(self, obj):
        image = None
        request = self.context.get('request')
        if obj.profile_picture:
            image = obj.profile_picture.url
            if request:
                image = request.build_absolute_uri(obj.profile_picture.url)
        return image

    def get_hostel(self, obj):
        if obj.hostel:
            return obj.hostel.name
        return None

    def get_department(self, obj):
        if obj.department:
            return obj.department.name
        return None

    class Meta:
        model = Profile
        exclude = []


