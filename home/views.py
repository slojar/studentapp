# 1. Default Admin should be able to register student and other admins
# 2. Admins should be able to create HOSTELS and assign to student when registering the student
# 3. Admins should be able to fetch all student based on hostels and other search field
from django.contrib.auth import authenticate
from django.db.models import Q
from rest_framework.authtoken.models import Token

from .models import Profile, Hostel, Room
from .serializers import ProfileSerializer, HostelSerializer, RoomSerializer
from .pagination import CustomPagination
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics


class RegisterAPIView(APIView):
    def post(self, request):
        first_name = request.data.get("firstName")
        last_name = request.data.get("lastName")
        email = request.data.get("email")
        password = request.data.get("password")
        gender = request.data.get("gender")
        profile_picture = request.data.get("profilePicture")
        phone_number = request.data.get("phoneNumber")
        account_type = request.data.get("accountType")
        room = request.data.get("roomID", "")
        department = request.data.get("department", "")
        matric_no = request.data.get("matricNo", "")
        school = request.data.get("school", "")
        level = request.data.get("level", "")

        print(request.data)

        logged_in_user_acct_type = Profile.objects.get(user=request.user).account_type
        if logged_in_user_acct_type != "superadmin":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not (account_type == "student" or account_type == "admin"):
            return Response({"detail": f"You have selected a wrong account type: {account_type}"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not all([first_name, last_name, email, gender, profile_picture, phone_number, account_type]):
            return Response({
                "detail": "All of the following are required fields: firstName, lastName, email, gender, "
                          "profilePicture, phoneNumber, and accountType"
            }, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email=email).exists():
            return Response({"detail": "User with this email already exist. Please change email or contact admin"},
                            status=status.HTTP_400_BAD_REQUEST)

        if Profile.objects.filter(phone_number=phone_number).exists():
            return Response({
                "detail": "User with this phone number already exist. Please change phone number or contact admin"
            }, status=status.HTTP_400_BAD_REQUEST)

        if account_type == "student":
            password = email
            if not all([room, department, matric_no, school, level]):
                return Response({"detail": "room, department, school, level, and matric number are required"},
                                status=status.HTTP_400_BAD_REQUEST)

        if account_type == "admin":
            if not password:
                return Response({"detail": "Password is required to create admin"})

        user = User.objects.create(
            email=email, first_name=first_name, last_name=last_name, username=email, password=make_password(password)
        )

        user_profile, _ = Profile.objects.get_or_create(user=user)
        user_profile.phone_number = phone_number
        user_profile.profile_picture = profile_picture
        user_profile.gender = gender
        user_profile.account_type = account_type
        if account_type == "student":
            user_profile.room_id = room
            user_profile.department = department
            user_profile.matric_no = matric_no
            user_profile.school = school
            user_profile.level = level
        user_profile.save()

        data = ProfileSerializer(user_profile, context={"request": request}).data

        return Response(data)


class HostelListCreateAPIView(generics.ListCreateAPIView):
    pagination_class = CustomPagination
    serializer_class = HostelSerializer

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        if profile.account_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_400_BAD_REQUEST)

        queryset = Hostel.objects.all().order_by("-id")
        return queryset


class UpdateDeleteHostelView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = HostelSerializer
    lookup_field = 'pk'

    def get_queryset(self):
        profile = Profile.objects.get(user=self.request.user)
        if profile.account_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_400_BAD_REQUEST)

        queryset = Hostel.objects.all().order_by("-id")
        return queryset


class FetchStudentAPIView(APIView, CustomPagination):
    def get(self, request):
        acct_type = Profile.objects.get(user=request.user).account_type
        if acct_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        hostel = request.GET.get("hostelID")
        gender = request.GET.get("gender")
        department = request.GET.get("department")
        school = request.GET.get("school")
        level = request.GET.get("level")
        search = request.GET.get("search")
        try:

            query = Q(account_type="student")
            if hostel:
                hostel = Hostel.objects.get(id=hostel).id
                print(hostel)
                query &= Q(room__hostel_id=hostel)

            # if gender:
            #     query &= Q(gender__iexact=gender)
            # if department:
            #     query &= Q(department__iexact=department)
            # if school:
            #     query &= Q(school__iexact=school)
            # if level:
            #     query &= Q(level__iexact=level)
            # if search:
            #     query &= Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | \
            #              Q(user__email=search) | Q(phone_number__icontains=search) | Q(matric_no__iexact=search)

            queryset = Profile.objects.filter(query).order_by("-id").distinct()
            print(queryset)

            data = self.paginate_queryset(queryset, request)
            serializer = self.get_paginated_response(
                ProfileSerializer(data, many=True, context={"request": request}).data
            ).data
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer)

    def put(self, request, pk):
        acct_type = Profile.objects.get(user=request.user).account_type
        if acct_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(id=pk, account_type="student")
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        last_name = request.data.get("lastName")
        first_name = request.data.get("firstName")
        email = request.data.get("email")
        gender = request.data.get("gender")
        profile_picture = request.data.get("profilePicture")
        phone_number = request.data.get("phoneNumber")
        department = request.data.get("department", "")
        room = request.data.get("roomID", "")
        matric_no = request.data.get("matricNo", "")
        school = request.data.get("school", "")
        level = request.data.get("level", "")

        if profile_picture:
            profile.profile_picture = request.data.get("profilePicture")
        if first_name:
            profile.user.first_name = first_name
        if last_name:
            profile.user.last_name = last_name
        if email:
            profile.user.email = email
            profile.user.username = email
        if gender:
            profile.gender = gender
        if phone_number:
            profile.phone_number = phone_number
        if room:
            profile.room_id = room
        if department:
            profile.department = department
        if matric_no:
            profile.matric_no = matric_no
        if school:
            profile.school = school
        if level:
            profile.level = level
        profile.user.save()
        profile.save()

        return Response({"detail": "Profile updated successfully"})

    def delete(self, request, pk):

        acct_ = Profile.objects.get(user=request.user).account_type
        if acct_ == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(id=pk, account_type="student").user
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        profile.delete()
        return Response({"detail": "Profile deleted successfully"})


class LoginAPIView(APIView):
    permission_classes = []

    def post(self, request):

        email = request.data.get("email")
        password = request.data.get("password")

        if not all([email, password]):
            return Response({"detail": "email and password are required fields"}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(username=email, password=password)

        if not user:
            return Response({"detail": "User with these credentials not found"}, status=status.HTTP_400_BAD_REQUEST)

        acct_type = Profile.objects.get(user=user).account_type
        if acct_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        user_auth = Token.objects.get(user=user).key
        serializer = ProfileSerializer(Profile.objects.get(user=user), context={"request": request}).data

        return Response({
            "detail": "Login Successful",
            "token": str(user_auth),
            "data": serializer
        })


class AnalysisAPIView(APIView):
    def get(self, request):

        hostels = Hostel.objects.all().count()
        admins = Profile.objects.filter(account_type="admin").count()
        students = Profile.objects.filter(account_type="student").count()

        return Response({
            "total_hostel": hostels,
            "total_admin": admins,
            "total_student": students
        })


# class FetchAdminListView(generics.ListAPIView):
#     serializer_class = ProfileSerializer
#     queryset = Profile.objects.filter(account_type="admin").order_by('-id')
#     pagination_class = CustomPagination


class FetchAdminAPIView(APIView, CustomPagination):
    def get(self, request, pk=None):
        try:
            acct_type = Profile.objects.get(user=request.user).account_type
            if acct_type == "student":
                return Response({"detail": "You are not permitted to perform this action"},
                                status=status.HTTP_401_UNAUTHORIZED)

            if pk:
                serializer = ProfileSerializer(
                    Profile.objects.get(account_type="admin", id=pk), context={"request": request}
                ).data
            else:
                queryset = Profile.objects.filter(account_type="admin").order_by("-id").distinct()

                data = self.paginate_queryset(queryset, request)
                serializer = self.get_paginated_response(
                    ProfileSerializer(data, many=True, context={"request": request}).data
                ).data
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer)

    def put(self, request, pk):
        acct_type = Profile.objects.get(user=request.user).account_type
        if acct_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(id=pk, account_type="admin")
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        first_name = request.data.get("firstName")
        email = request.data.get("email")
        last_name = request.data.get("lastName")
        password = request.data.get("password")
        gender = request.data.get("gender")
        profile_picture = request.data.get("profilePicture")
        phone_number = request.data.get("phoneNumber")

        if first_name:
            profile.user.first_name = request.data.get("firstName")
        if profile_picture:
            profile.profile_picture = profile_picture
        if email:
            profile.user.email = email
            profile.user.username = email
        if last_name:
            profile.user.last_name = last_name
        if phone_number:
            profile.phone_number = phone_number
        if gender:
            profile.gender = gender
        if password:
            profile.user.password = make_password(password)
        profile.user.save()
        profile.save()

        return Response({"detail": "Profile updated successfully"})

    def delete(self, request, pk):

        acct_ = Profile.objects.get(user=request.user).account_type
        if acct_ == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        try:
            profile = Profile.objects.get(id=pk, account_type="admin").user
        except Exception as err:
            return Response({"detail": "An error has occurred", "error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        profile.delete()
        return Response({"detail": "Admin Profile deleted successfully"})


class ListCreateRoomView(generics.ListCreateAPIView):
    pagination_class = CustomPagination
    serializer_class = RoomSerializer
    queryset = Room.objects.all().order_by("-id")


class UpdateDeleteRoomView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RoomSerializer
    queryset = Room.objects.all()
    lookup_field = "pk"


# class ViewDeleteAdminView(generics.RetrieveDestroyAPIView):
#     serializer_class = ProfileSerializer
#     queryset = User.objects.filter(profile__account_type="admin")
#     # queryset = Profile.objects.filter(account_type="admin")
#     lookup_field = "pk"





