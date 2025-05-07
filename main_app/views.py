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



from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PatientRequest
from .serializers import PatientRequestSerializer

class PatientRequestCreate(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        try:
            # Check if the user is a doctor
            if request.user.role == 'doctor':
                # If the user is a doctor, fetch all requests
                patient_requests = PatientRequest.objects.all()
            else:
                # If the user is a patient, fetch only the requests for that patient
                patient_requests = PatientRequest.objects.filter(patient=request.user.patient)

            serializer = PatientRequestSerializer(patient_requests, many=True)
            return Response(serializer.data)

        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            # Handle patient request creation logic here
            serializer = PatientRequestSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(patient=request.user.patient)  # Assign the logged-in user as the patient
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as err:
            return Response({'error': str(err)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class PatientRequestAction(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch all pending patient requests associated with the current doctor
        patient_requests = PatientRequest.objects.filter(issue__doctor=request.user.doctor, status=PatientRequest.STATUS_PENDING)
        serializer = PatientRequestSerializer(patient_requests, many=True)
        return Response(serializer.data)

    def post(self, request, request_id):
        try:
            # Fetch the patient request by ID
            patient_request = PatientRequest.objects.get(id=request_id)

            # Ensure that the doctor can only handle the request (only accept/decline)
            if patient_request.status != PatientRequest.STATUS_PENDING:
                return Response({'error': 'This request has already been handled.'}, status=status.HTTP_400_BAD_REQUEST)

            # Check the action to perform (Accept or Decline)
            action = request.data.get('action')

            if action == 'accept':
                patient_request.status = PatientRequest.STATUS_ACCEPTED
                patient_request.doctor = request.user.doctor  # Assign doctor to the request
                patient_request.save()

                return Response({'message': 'Request accepted successfully.'}, status=status.HTTP_200_OK)

            elif action == 'decline':
                patient_request.status = PatientRequest.STATUS_DECLINED
                patient_request.save()

                return Response({'message': 'Request declined successfully.'}, status=status.HTTP_200_OK)

            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

        except PatientRequest.DoesNotExist:
            return Response({'error': 'Request not found.'}, status=status.HTTP_404_NOT_FOUND)
