from django.test import TestCase
from .models import BiometricData

class BiometricDataModelTest(TestCase):
    def setUp(self):
        self.biometric_data = BiometricData.objects.create(
            user_id=1,
            fingerprint='sample_fingerprint_data',
            photo='sample_photo_url'
        )

    def test_biometric_data_creation(self):
        self.assertEqual(self.biometric_data.user_id, 1)
        self.assertEqual(self.biometric_data.fingerprint, 'sample_fingerprint_data')
        self.assertEqual(self.biometric_data.photo, 'sample_photo_url')

    def test_biometric_data_str(self):
        self.assertEqual(str(self.biometric_data), 'BiometricData for user 1')