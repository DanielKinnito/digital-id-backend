from rest_framework import serializers
from .models import BiometricData

class BiometricDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = BiometricData
        fields = ['id', 'user', 'fingerprint', 'photo', 'created_at', 'updated_at']