from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterAPIView.as_view(), name="register"),
    path('hostels/', views.HostelListCreateAPIView.as_view(), name="hostels"),
    path('hostels/<int:pk>/', views.DeleteHostelView.as_view(), name="delete-hostel"),
    path('student/', views.FetchStudentAPIView.as_view(), name="student"),
    path('student/<int:pk>/', views.FetchStudentAPIView.as_view(), name="student-detail"),
    path('login/', views.LoginAPIView.as_view(), name="login"),
    path('analysis/', views.AnalysisAPIView.as_view(), name="analysis"),

    path('admins/', views.FetchAdminListView.as_view(), name="admin"),
    path('admins/<int:pk>/', views.ViewDeleteAdminView.as_view(), name="admin-detail"),
]

