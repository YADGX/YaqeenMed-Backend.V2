from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError



def validate_file_size(value):
    max_size_mb = 5
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"File size must be under {max_size_mb}MB")

class User(AbstractUser):
    ROLE_PATIENT = 'patient'
    ROLE_DOCTOR = 'doctor'

    ROLE_CHOICES = [
        (ROLE_PATIENT, "patient"),
        (ROLE_DOCTOR, "doctor"),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_PATIENT)
    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions', 
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"




class Patient(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient'
    )
    age = models.PositiveIntegerField(null=True, blank=True)

    def clean(self):
        if not (0 < self.age <= 120):
            raise ValidationError("Age must be between 1 and 120.")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_patient_user')
        ]

    def __str__(self):
        return f"Patient {self.id} ({self.user.username})"


class Doctor(models.Model):
    SPECIALTY_RADIOLOGY = 'RADIOLOGY'
    SPECIALTY_PATHOLOGY = 'PATHOLOGY'
    SPECIALTY_CARDIOLOGY = 'CARDIOLOGY'

    SPECIALTY_CHOICES = [
        (SPECIALTY_RADIOLOGY, 'Radiology'),
        (SPECIALTY_PATHOLOGY, 'Pathology'),
        (SPECIALTY_CARDIOLOGY, 'Cardiology'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES)
    license_number = models.CharField(max_length=50, unique=True)
    years_experience = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"


class Issue(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_DECLINED = 'DECLINED'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Issue #{self.id} - {self.title}"



class PatientRequest(models.Model):
    STATUS_PENDING = 'PENDING'
    STATUS_ACCEPTED = 'ACCEPTED'
    STATUS_DECLINED = 'DECLINED'
    STATUS_COMPLETED = 'COMPLETED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_DECLINED, 'Declined'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='patient_requests', null=True, blank=True)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='patient_requests', null=True, blank=True)
    title = models.CharField(max_length=200)  
    detailed_comment = models.TextField()
    summary_comment = models.CharField(max_length=255)
    document = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Patient Request #{self.id} - {self.title} - {self.status}"

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['created_at']),
        ]



class Document(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(
        upload_to='issue_documents/',
        validators=[
            FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png']),
            validate_file_size
        ]
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Document for Issue #{self.issue.id}"


class Comment(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if self.issue.status == Issue.STATUS_COMPLETED:
            raise ValidationError("Cannot modify comments on completed issues.")
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Comment by {self.author} on Issue #{self.issue.id}"
