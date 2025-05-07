from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Patient, Doctor, Issue, Comment, Document
from django.urls import reverse
import tempfile

User = get_user_model()

class YaqeenMedAPITestCase(APITestCase):

    def setUp(self):
        # Create a user for tests
        self.patient_user = User.objects.create_user(
            username="test_patient", email="test_patient@example.com", password="password123", role="PATIENT"
        )
        self.doctor_user = User.objects.create_user(
            username="test_doctor", email="test_doctor@example.com", password="password123", role="DOCTOR"
        )
        self.patient = Patient.objects.create(user=self.patient_user, age=30)
        self.doctor = Doctor.objects.create(user=self.doctor_user, specialty='CARDIOLOGY', license_number='123456', years_experience=10)

    def test_register_patient(self):
        data = {
            'username': 'new_patient',
            'email': 'new_patient@example.com',
            'password': 'password123',
            'role': 'PATIENT',
            'age': 25,  # Ensure age is included
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='new_patient').exists())

    def test_register_doctor(self):
        data = {
            'username': 'new_doctor',
            'email': 'new_doctor@example.com',
            'password': 'password123',
            'role': 'DOCTOR',
            'specialty': 'CARDIOLOGY',  # Ensure specialty is included
            'license_number': '654321',  # Ensure license_number is included
            'years_experience': 5,  # Ensure years_experience is included
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='new_doctor').exists())

    def test_login(self):
        data = {
            'username': 'test_patient',
            'password': 'password123',
        }
        response = self.client.post(reverse('login'), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_create_issue_patient(self):
        self.client.login(username='test_patient', password='password123')
        data = {
            'title': 'Heart issue',
            'description': 'Severe chest pain',
            'doctor': self.doctor.id
        }
        response = self.client.post(reverse('issue-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Issue.objects.filter(title='Heart issue').exists())

    def test_create_issue_doctor(self):
        self.client.login(username='test_doctor', password='password123')
        data = {
            'title': 'Checkup request',
            'description': 'Annual health checkup',
            'patient': self.patient.id
        }
        response = self.client.post(reverse('issue-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Issue.objects.filter(title='Checkup request').exists())

    def test_create_comment_on_issue(self):
        self.client.login(username='test_doctor', password='password123')
        issue = Issue.objects.create(
            patient=self.patient, doctor=self.doctor, title='Initial consultation', description='Consultation for health issues'
        )
        data = {'content': 'Initial comment on the issue'}
        response = self.client.post(reverse('comment-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Comment.objects.filter(content='Initial comment on the issue').exists())

    def test_create_document_for_issue(self):
        self.client.login(username='test_doctor', password='password123')
        issue = Issue.objects.create(
            patient=self.patient, doctor=self.doctor, title='Health check', description='General health check'
        )
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_file:
            temp_file.write(b'This is a test document.')
            temp_file.seek(0)
            data = {'file': temp_file}
            response = self.client.post(reverse('document-list'), data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Document.objects.filter(issue=issue).exists())

    def test_patient_detail(self):
        self.client.login(username='test_patient', password='password123')
        response = self.client.get(reverse('patient-detail', args=[self.patient.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'test_patient')

    def test_doctor_detail(self):
        self.client.login(username='test_doctor', password='password123')
        response = self.client.get(reverse('doctor-detail', args=[self.doctor.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['username'], 'test_doctor')

    def test_permissions_patient(self):
        self.client.login(username='test_doctor', password='password123')
        response = self.client.get(reverse('patient-detail', args=[self.patient.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_permissions_doctor(self):
        self.client.login(username='test_patient', password='password123')
        response = self.client.get(reverse('doctor-detail', args=[self.doctor.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_patient(self):
        self.client.login(username='test_patient', password='password123')
        data = {'age': 35}
        response = self.client.put(reverse('patient-detail', args=[self.patient.id]), data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Patient.objects.get(id=self.patient.id).age, 35)

    def test_delete_issue(self):
        self.client.login(username='test_doctor', password='password123')
        issue = Issue.objects.create(
            patient=self.patient, doctor=self.doctor, title='Test issue', description='Test description'
        )
        response = self.client.delete(reverse('issue-detail', args=[issue.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Issue.objects.filter(id=issue.id).exists())

    def test_create_patient_with_invalid_age(self):
        data = {
            'username': 'invalid_patient',
            'email': 'invalid_patient@example.com',
            'password': 'password123',
            'role': 'PATIENT',
            # 'age' is intentionally missing to test validation
        }
        response = self.client.post(reverse('register'), data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('age', response.data)
