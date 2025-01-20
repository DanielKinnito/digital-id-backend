from django.urls import path
from .views import IDViewSet

urlpatterns = [
    path('', IDViewSet.as_view({'get': 'list'}), name='id-list'),
    path('<int:pk>/', IDViewSet.as_view({'get': 'retrieve'}), name='id-detail'),
    path('renew/<int:pk>/', IDViewSet.as_view({'put': 'update'}), name='id-renew'),
]