"""URLs principales para API v1."""

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    path('auth/', include('api.v1.auth.urls')),
    path('rrhh/', include('api.v1.rrhh.urls')),
    path('vacaciones/', include('api.v1.vacaciones.urls')),
]