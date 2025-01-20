from django.urls import path, include

urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('users/', include('digital_id.apps.users.urls')),
    path('ids/', include('digital_id.apps.ids.urls')),
    path('biometrics/', include('digital_id.apps.biometrics.urls')),
]