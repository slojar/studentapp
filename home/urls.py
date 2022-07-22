from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name="register"),
    path('hostels/', views.HostelListCreateAPIView.as_view(), name="department"),
    path('student/', views.FetchStudentAPIView.as_view(), name="student"),
]

