from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegisterView.as_view(), name='user-register'),
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('update/', views.UserUpdateView.as_view(), name='user-update'),
    path('biometrics/', views.UserBiometricsView.as_view(), name='user-biometrics'),
]