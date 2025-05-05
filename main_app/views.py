from rest_framework import viewsets, permissions
from .models import Patient, Doctor, Issue, Document, Comment
from .serializers import (PatientSerializer, DoctorSerializer,IssueSerializer, DocumentSerializer, CommentSerializer)
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer



class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            role = request.data.get('role', '').upper()
            
            if role == 'PATIENT':
                Patient.objects.create(user=user)
            elif role == 'DOCTOR':
                Doctor.objects.create(user=user)
            
            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def index(request):
    return HttpResponse("Welcome to the YaqeenMed API!")


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

# Permission: allow read access to anyone, but edits only to owners
class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

# --- PATIENT VIEWSET ---
class PatientViewSet(viewsets.ModelViewSet):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Patient.objects.filter(user=user)
        return Patient.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# --- DOCTOR VIEWSET ---
class DoctorViewSet(viewsets.ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Doctor.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Doctor.objects.filter(user=user)
        return Doctor.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

# --- ISSUE VIEWSET ---
class IssueViewSet(viewsets.ModelViewSet):
    serializer_class = IssueSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Issue.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Issue.objects.filter(patient__user=user)
        elif user.role == 'DOCTOR':
            return Issue.objects.filter(doctor__user=user)
        return Issue.objects.all()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient)

# --- DOCUMENT VIEWSET ---
class DocumentViewSet(viewsets.ModelViewSet):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.all()

# --- COMMENT VIEWSET ---
class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()
