from rest_framework import serializers
from .models import UserBiometric

class UserBiometricSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBiometric
        fields = ['id', 'user_id', 'fingerprint', 'photo', 'created_at', 'updated_at']