from django.urls import path, include
from .views import RegisterView
from rest_framework.routers import DefaultRouter
from .views import PatientViewSet, DoctorViewSet, IssueViewSet, DocumentViewSet, CommentViewSet

router = DefaultRouter()
router.register(r'patients', PatientViewSet, basename='patient')
router.register(r'doctors', DoctorViewSet, basename='doctor')
router.register(r'issues', IssueViewSet, basename='issue')
router.register(r'documents', DocumentViewSet, basename='document')
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),  
]
