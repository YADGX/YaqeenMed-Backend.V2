from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


from .models import User, Patient, Doctor, Issue, Document, Comment, PatientRequest

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all(), message="Username already exists.")]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=role
        )
        if role == 'PATIENT':
            Patient.objects.create(user=user, age=0)  
        elif role == 'DOCTOR':
            Doctor.objects.create(user=user, specialty='', license_number='', years_experience=0)  
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data['role'] = self.user.role
        return data

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'profile_picture']
        extra_kwargs = {'password': {'write_only': True}}

class PatientSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Patient
        fields = ['id', 'user', 'age']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        return Patient.objects.create(user=user, **validated_data)

class DoctorSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Doctor
        fields = ['id', 'user', 'specialty', 'license_number', 'years_experience']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create_user(**user_data)
        return Doctor.objects.create(user=user, **validated_data)

class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'file', 'uploaded_at']
        read_only_fields = ['uploaded_at']

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'content']

class CommentListSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'author', 'content', 'created_at', 'updated_at']
        read_only_fields = ['author', 'created_at', 'updated_at']

class IssueSerializer(serializers.ModelSerializer):
    documents = DocumentSerializer(many=True, read_only=True)
    comments = CommentListSerializer(many=True, read_only=True)
    patient = serializers.StringRelatedField()
    doctor = serializers.StringRelatedField()

    class Meta:
        model = Issue
        fields = [
            'id', 'patient', 'doctor', 'title', 'description',
            'status', 'created_at', 'updated_at', 'documents', 'comments'
        ]
        read_only_fields = ['patient', 'created_at', 'updated_at']


class PatientRequestSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    issue = serializers.PrimaryKeyRelatedField(queryset=Issue.objects.all(), required=False)
    
    class Meta:
        model = PatientRequest
        fields = ['id', 'title', 'detailed_comment', 'summary_comment', 'document', 'patient', 'issue'] 

    # def create(self, validated_data):
    #     user = self.data.user 
    #     patient = user.patient  
    #     validated_data['patient'] = patient  

    #     # Directly access issue_id from self.data
    #     issue_id = validated_data.get('issue_id')
    #     if not issue_id:
    #         raise serializers.ValidationError("Issue ID is required.")
        
    #     try:
    #         # Get the issue object using the provided issue_id
    #         issue = Issue.objects.get(id=issue_id)
    #     except Issue.DoesNotExist:
    #         raise serializers.ValidationError(f"Issue with ID {issue_id} does not exist.")
        
    #     validated_data['issue'] = issue  # Assign the issue to the validated data
        
    #     return PatientRequest.objects.create(**validated_data)  # Create and return the PatientRequest object


