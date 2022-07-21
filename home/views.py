# 1. Default Admin should be able to register student and other admins
# 2. Admins should be able to create HOSTELS and assign to student when registering the student
# 3. Admins should be able to fetch all student based on hostels and other search field
from django.db.models import Q

from .models import Profile, Hostel
from .serializers import ProfileSerializer, HostelSerializer
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
        hostel = request.data.get("hostelID", "")
        department = request.data.get("departmentID", "")
        matric_no = request.data.get("matricNo", "")

        logged_in_user_acct_type = Profile.objects.get(user=request.user).account_type
        if logged_in_user_acct_type != "superadmin":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        if not (account_type == "student" or account_type == "admin"):
            return Response({"detail": f"You have selected a wrong account type: {account_type}"},
                            status=status.HTTP_400_BAD_REQUEST)

        if not all([first_name, last_name, email, password, gender, profile_picture, phone_number, account_type]):
            return Response({
                "detail": "All of the following are required fields: firstName, lastName, email, password, gender, "
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
            if not all([hostel, department, matric_no]):
                return Response({"detail": "Hostel, department, and matric number are required"},
                                status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            email=email, first_name=first_name, last_name=last_name, username=email, password=make_password(password)
        )

        user_profile, _ = Profile.objects.get_or_create(user=user)
        user_profile.phone_number = phone_number
        user_profile.profile_picture = profile_picture
        user_profile.gender = gender
        user_profile.account_type = account_type
        if account_type == "student":
            user_profile.hostel_id = hostel
            user_profile.department_id = department
            user_profile.matric_no = matric_no
        user_profile.save()

        data = ProfileSerializer(user_profile, context={"request": request}).data

        return Response(data)


class HostelAPIView(APIView):
    def post(self, request):
        profile = Profile.objects.get(user=request.user)
        if profile.account_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_400_BAD_REQUEST)

        hostel_name = request.data.get("hostelName")

        if not hostel_name:
            return Response({"detail": "hostelName is required"}, status=status.HTTP_400_BAD_REQUEST)

        hostel = Hostel.objects.get_or_create(name=hostel_name)
        data = HostelSerializer(hostel).data

        return Response(data)


class HostelListAPIView(generics.ListAPIView):
    permission_classes = []
    pagination_class = CustomPagination
    queryset = Hostel.objects.all().order_by("-id")
    serializer_class = HostelSerializer


class FetchStudentAPIView(APIView, CustomPagination):
    def get(self, request):
        acct_type = Profile.objects.get(user=request.user).account_type
        if acct_type == "student":
            return Response({"detail": "You are not permitted to perform this action"},
                            status=status.HTTP_401_UNAUTHORIZED)

        hostel = request.GET.get("hostelID")
        gender = request.GET.get("gender")
        department = request.GET.get("departmentID")
        search = request.GET.get("search")

        query = Q(account_type="student")
        if hostel:
            query &= Q(hostel__id=hostel)
        if gender:
            query &= Q(gender__iexact=gender)
        if department:
            query &= Q(department_id=department)
        if search:
            query &= Q(user__first_name__icontains=search) | Q(user__last_name__icontains=search) | \
                     Q(user__email=search) | Q(phone_number__icontains=search) | Q(matric_no__icontains=search)

        queryset = Profile.objects.filter(query).order_by("-id").distinct()

        data = self.paginate_queryset(queryset, request)
        serializer = self.get_paginated_response(
            ProfileSerializer(data, many=True, context={"request": request}).data
        ).data

        return Response(serializer)

