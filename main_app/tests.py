from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

class PatientAPITests(APITestCase):
    def test_patient_creation(self):
        response = self.client.post('/api/patients/', {  # Add trailing slash
            'user': {
                'username': 'testuser',
                'password': 'testpass123',
                'email': 'test@example.com',
                'role': 'PATIENT'
            },
            'age': 30
        }, format='json')
        print(response.data)  # Add this to debug
        self.assertEqual(response.status_code, 201)