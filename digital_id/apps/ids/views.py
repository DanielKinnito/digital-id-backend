from rest_framework import viewsets
from rest_framework.response import Response
from .models import ID
from .serializers import IDSerializer

class IDViewSet(viewsets.ModelViewSet):
    queryset = ID.objects.all()
    serializer_class = IDSerializer

    def list(self, request):
        ids = self.get_queryset()
        serializer = self.get_serializer(ids, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        id_instance = self.get_object()
        serializer = self.get_serializer(id_instance)
        return Response(serializer.data)

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        id_instance = serializer.save()
        return Response(serializer.data, status=201)

    def update(self, request, pk=None):
        id_instance = self.get_object()
        serializer = self.get_serializer(id_instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        id_instance = serializer.save()
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        id_instance = self.get_object()
        id_instance.delete()
        return Response(status=204)