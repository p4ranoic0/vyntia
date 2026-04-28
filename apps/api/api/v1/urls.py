"""URLs principales para API v1.

Estructura:
- /api/v1/auth/        - autenticación (legacy + canonical)
- /api/v1/rrhh/...     - LEGACY URLs (preservadas hasta L3.11)
- /api/v1/vacaciones/  - LEGACY URLs (preservadas hasta L3.11)
- /api/v1/identity/    - NUEVO (English path) per spec § 3.4
- /api/v1/organization/ - NUEVO
- /api/v1/employees/, /family-members/, /academic-records/, /certifications/ - NUEVO (flat under /api/v1/)
- /api/v1/contracts/, /contract-amendments/, /employment-data/ - NUEVO (flat under /api/v1/)
- /api/v1/documents/   - NUEVO
- /api/v1/payroll/     - NUEVO
- /api/v1/time-off/    - NUEVO
- /api/v1/onboarding/  - NUEVO
"""

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Authentication
    path('auth/', include('api.v1.auth.urls')),

    # Legacy URLs (Spanish paths) — preserved until L3.11 cleanup
    path('rrhh/', include('api.v1.rrhh.urls')),
    path('vacaciones/', include('api.v1.vacaciones.urls')),

    # New canonical URLs (English paths) per spec § 3.4
    path('identity/', include('api.v1.identity.urls')),
    path('organization/', include('api.v1.organization.urls')),
    path('', include('api.v1.employees.urls')),     # /api/v1/employees/, /family-members/, /academic-records/, /certifications/
    path('', include('api.v1.contracts.urls')),     # /api/v1/contracts/, /contract-amendments/, /employment-data/
    path('documents/', include('api.v1.documents.urls')),
    path('payroll/', include('api.v1.payroll.urls')),
    path('time-off/', include('api.v1.time_off.urls')),
    path('onboarding/', include('api.v1.onboarding.urls')),
]
