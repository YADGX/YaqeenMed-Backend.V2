from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator

class User(AbstractUser):
    ROLE_CHOICES = [
        ('PATIENT', 'Patient'),
        ('DOCTOR', 'Doctor'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    profile_picture = models.ImageField(
        upload_to='profiles/',
        null=True,
        blank=True,
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])]
    )
    
    # Add these to resolve conflicts
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # Changed
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # Changed
        related_query_name='user',
    )
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

class Patient(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='patient'
    )
    age = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user'], name='unique_patient_user')
        ]

    def __str__(self):
        return f"Patient {self.id} ({self.user.username})"

class Doctor(models.Model):
    SPECIALTY_CHOICES = [
        ('RADIOLOGY', 'Radiology'),
        ('PATHOLOGY', 'Pathology'),
        ('CARDIOLOGY', 'Cardiology'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    specialty = models.CharField(max_length=20, choices=SPECIALTY_CHOICES)
    license_number = models.CharField(max_length=50, unique=True)
    years_experience = models.PositiveIntegerField()
    
    def __str__(self):
        return f"Dr. {self.user.get_full_name()}"

class Issue(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ACCEPTED', 'Accepted'),
        ('DECLINED', 'Declined'),
        ('COMPLETED', 'Completed'),
    ]
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Issue #{self.id} - {self.title}"

class Document(models.Model):
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE, related_name='documents')
    file = models.FileField(
        upload_to='issue_documents/',
        validators=[FileExtensionValidator(['pdf', 'jpg', 'jpeg', 'png'])]
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
        if self.issue.status == 'COMPLETED':
            raise ValueError("Cannot modify comments on completed issues")
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"Comment by {self.author} on Issue #{self.issue.id}"