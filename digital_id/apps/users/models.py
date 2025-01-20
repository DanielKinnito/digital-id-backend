from django.db import models

class User(models.Model):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    date_of_birth = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class BiometricData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    fingerprint = models.BinaryField()
    photo = models.ImageField(upload_to='biometric_photos/')

    def __str__(self):
        return f"Biometric data for {self.user.first_name} {self.user.last_name}"