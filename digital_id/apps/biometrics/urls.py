from django.urls import path
from .views import UserViewSet

urlpatterns = [
    path('register/', UserViewSet.as_view({'post': 'create'}), name='user-register'),
    path('profile/', UserViewSet.as_view({'get': 'retrieve'}), name='user-profile'),
    path('update/', UserViewSet.as_view({'put': 'update'}), name='user-update'),
    path('biometrics/', UserViewSet.as_view({'get': 'retrieve'}), name='user-biometrics'),
]