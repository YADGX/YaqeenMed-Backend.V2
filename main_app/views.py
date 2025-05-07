from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView
from django.http import HttpResponse
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken




from .models import *
from .serializers import *

# from django.http import JsonResponse

# def index(request):
#     return JsonResponse({"message": "Welcome to YaqeenMed API!"})


# Home View
class HomeView(APIView):
    def get(self, request):
        return Response({"message": "Welcome to the YaqeenMed API!"})

# Register View with Nested User Creation
class RegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            role = request.data.get('role', '').upper()

            # Automatically creating Patient or Doctor after user creation
            if role == 'PATIENT':
                Patient.objects.create(user=user)
            elif role == 'DOCTOR':
                Doctor.objects.create(user=user)

            return Response({'message': 'User registered successfully!'}, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):

  def post(self, request):
    try:
      username = request.data.get('username')
      password = request.data.get('password')
      user = authenticate(username=username, password=password)
      if user:
        refresh = RefreshToken.for_user(user)
        content = {'refresh': str(refresh), 'access': str(refresh.access_token),'user': UserSerializer(user).data}
        return Response(content, status=status.HTTP_200_OK)
      return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    except Exception as err:
        print(err)
        return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class VerifyUserView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user

class PatientList(generics.ListCreateAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Patient.objects.filter(user=user)
        return Patient.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class PatientDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PatientSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Patient.objects.all()

class DoctorList(generics.ListCreateAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'DOCTOR':
            return Doctor.objects.filter(user=user)
        return Doctor.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class DoctorDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Doctor.objects.all()

class IssueList(generics.ListCreateAPIView):
    serializer_class = IssueSerializer  
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return Issue.objects.filter(patient__user=user)
        elif user.role == 'DOCTOR':
            return Issue.objects.filter(doctor__user=user)
        return Issue.objects.all()

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user.patient)

class IssueDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = IssueSerializer  
    permission_classes = [permissions.IsAuthenticated]
    queryset = Issue.objects.all()

class DocumentList(generics.ListCreateAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.all()

class DocumentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Document.objects.all()

# --- COMMENT Views ---
class CommentList(generics.ListCreateAPIView):
    serializer_class = CommentListSerializer  
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()


class CommentCreate(generics.CreateAPIView):
    serializer_class = CommentCreateSerializer  
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()
    

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CommentListSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()



class PatientRequestCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all patient requests associated with the current user
        patient_requests = PatientRequest.objects.filter(patient=request.user.patient)
        serializer = PatientRequestSerializer(patient_requests, many=True)
        return Response(serializer.data)

    def post(self, request):
        try:
            print("REQUEST DATA:   ", request.data)
            # Serialize the data sent by the user
            patient = Patient.objects.get(user=request.user)
            serializer = PatientRequestSerializer(data=request.data)
            if serializer.is_valid():
                # Attach the patient to the request directly (done in the serializer)
                serializer.save(patient=patient)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            # Print serializer errors for debugging
            print("SERIALIZER ERRORS:   ", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            print("EXCEPTION:   ", err)
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
