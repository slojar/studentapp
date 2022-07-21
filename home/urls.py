from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name="register"),
    path('hostel/', views.HostelAPIView.as_view(), name="hostel"),
    path('hostel/<int:id>/', views.HostelListAPIView.as_view(), name="hostel-detail"),
    path('student/', views.FetchStudentAPIView.as_view(), name="student"),
]
