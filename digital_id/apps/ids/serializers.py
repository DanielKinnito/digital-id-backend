from .models import ID  # Adjust the import based on your actual model location
from rest_framework import serializers

class IDSerializer(serializers.ModelSerializer):
    class Meta:
        model = ID
        fields = '__all__'  # Specify the fields you want to include in the serialization

    def create(self, validated_data):
        return ID.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.field_name = validated_data.get('field_name', instance.field_name)  # Update fields as necessary
        instance.save()
        return instance