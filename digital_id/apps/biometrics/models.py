from django.db import models

class UserBiometric(models.Model):
    user_id = models.OneToOneField('users.User', on_delete=models.CASCADE)
    fingerprint = models.BinaryField()
    photo = models.ImageField(upload_to='biometrics/photos/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Biometric data for {self.user_id.username}"