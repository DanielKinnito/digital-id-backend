from django.db import models
from django.contrib.auth.models import User

class ID(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    id_type = models.CharField(max_length=50)  # e.g., 'Driver's License', 'Work ID', etc.
    issue_date = models.DateField()
    expiration_date = models.DateField()
    id_number = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.id_type} - {self.id_number} ({self.user.username})"