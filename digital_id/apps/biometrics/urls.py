from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_biometrics, name='register_biometrics'),
    path('retrieve/', views.retrieve_biometrics, name='retrieve_biometrics'),
    path('update/', views.update_biometrics, name='update_biometrics'),
]