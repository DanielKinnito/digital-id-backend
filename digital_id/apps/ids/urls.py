from django.urls import path
from . import views

urlpatterns = [
    path('ids/', views.IDListView.as_view(), name='id-list'),
    path('ids/<int:pk>/', views.IDDetailView.as_view(), name='id-detail'),
    path('ids/renew/<int:pk>/', views.IDRenewView.as_view(), name='id-renew'),
]