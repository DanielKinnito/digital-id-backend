from django.test import TestCase
from .models import ID

class IDModelTest(TestCase):
    def setUp(self):
        ID.objects.create(type="Driver's License", expiration_date="2025-12-31")
        ID.objects.create(type="Work ID", expiration_date="2024-06-30")

    def test_id_creation(self):
        id_instance = ID.objects.get(type="Driver's License")
        self.assertEqual(id_instance.expiration_date, "2025-12-31")

    def test_id_expiration(self):
        id_instance = ID.objects.get(type="Work ID")
        self.assertEqual(id_instance.expiration_date, "2024-06-30")