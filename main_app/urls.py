from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('users/login/', views.LoginView.as_view(), name='login'),
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  
    path('patients/', views.PatientList.as_view(), name='patient-list'),
    path('patients/<int:pk>/', views.PatientDetail.as_view(), name='patient-detail'),
    path('doctors/', views.DoctorList.as_view(), name='doctor-list'),
    path('doctors/<int:pk>/', views.DoctorDetail.as_view(), name='doctor-detail'),
    path('issues/', views.IssueList.as_view(), name='issue-list'),
    path('issues/<int:pk>/', views.IssueDetail.as_view(), name='issue-detail'),
    path('documents/', views.DocumentList.as_view(), name='document-list'),
    path('documents/<int:pk>/', views.DocumentDetail.as_view(), name='document-detail'),
    path('comments/', views.CommentList.as_view(), name='comment-list'),
    path('comments/<int:pk>/', views.CommentDetail.as_view(), name='comment-detail'),
    path('patient-requests/', views.PatientRequestCreate.as_view(), name='patient-request-create'),
    path('api/patient-requests/', views.PatientRequestAction.as_view(), name='get_patient_requests'),  # To get the list of patient requests
    path('api/patient-requests/<int:request_id>/action/', views.PatientRequestAction.as_view(), name='handle_patient_request'),  # To handle actions (accept/decline) for a specific request
]
