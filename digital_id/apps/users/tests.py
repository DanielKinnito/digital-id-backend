from django.test import TestCase
from .models import User

class UserModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(
            username='testuser',
            email='testuser@example.com',
            password='securepassword',
            # Add other fields as necessary
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_user_email(self):
        self.assertTrue('@' in self.user.email)

    # Add more tests as necessary for other functionalities