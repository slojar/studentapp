from rest_framework import serializers
from .models import Profile, Hostel, Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        exclude = []


class HostelSerializer(serializers.ModelSerializer):
    rooms = serializers.SerializerMethodField()

    def get_rooms(self, obj):
        if Room.objects.filter(hostel=obj).exists():
            return RoomSerializer(Room.objects.filter(hostel=obj), many=True).data
        return None

    class Meta:
        model = Hostel
        exclude = []


class ProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.SerializerMethodField()
    user_detail = serializers.SerializerMethodField()
    room = serializers.SerializerMethodField()

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

    def get_room(self, obj):
        if obj.room:
            data = {
                "room_id": obj.room.id,
                "room_name": obj.room.name,
                "hostel_name": obj.room.hostel.name
            }
            return data
        return None

    class Meta:
        model = Profile
        exclude = []


