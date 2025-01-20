from django.urls import path
from .views import UserBiometricViewSet

urlpatterns = [
    path('register/', UserBiometricViewSet.as_view({'post': 'create'}), name='user-register'),
    path('profile/', UserBiometricViewSet.as_view({'get': 'retrieve'}), name='user-profile'),
    path('update/', UserBiometricViewSet.as_view({'put': 'update'}), name='user-update'),
    path('biometrics/', UserBiometricViewSet.as_view({'get': 'retrieve'}), name='user-biometrics'),
]