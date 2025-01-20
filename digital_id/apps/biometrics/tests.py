from django.test import TestCase
from .models import UserBiometric

class UserBiometricModelTest(TestCase):
    def setUp(self):
        self.user_biometric = UserBiometric.objects.create(
            user_id=1,
            fingerprint=b'sample_fingerprint_data',
            photo='sample_photo_url'
        )

    def test_user_biometric_creation(self):
        self.assertEqual(self.user_biometric.user_id, 1)
        self.assertEqual(self.user_biometric.fingerprint, b'sample_fingerprint_data')
        self.assertEqual(self.user_biometric.photo, 'sample_photo_url')

    def test_user_biometric_str(self):
        self.assertEqual(str(self.user_biometric), 'Biometric data for user 1')