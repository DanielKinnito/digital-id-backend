from django.urls import path
from .views import UserBiometricViewSet

urlpatterns = [
    path('register/', UserBiometricViewSet.as_view({'post': 'create'}), name='register_biometrics'),
    path('retrieve/', UserBiometricViewSet.as_view({'get': 'retrieve'}), name='retrieve_biometrics'),
    path('update/', UserBiometricViewSet.as_view({'put': 'update'}), name='update_biometrics'),
]