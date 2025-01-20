from django.urls import path, include

urlpatterns = [
    path('users/', include('digital_id.apps.users.urls')),
    path('ids/', include('digital_id.apps.ids.urls')),
    path('biometrics/', include('digital_id.apps.biometrics.urls')),
]