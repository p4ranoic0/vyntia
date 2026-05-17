"""URLs principales para API v1.

Estructura (post-L3.11 — legacy /rrhh/ y /vacaciones/ removidos):
- /api/v1/auth/        - autenticación
- /api/v1/identity/    - English path per spec § 3.4
- /api/v1/organization/ - English path per spec § 3.4
- /api/v1/employees/, /family-members/, /academic-records/, /certifications/ - flat under /api/v1/
- /api/v1/contracts/, /contract-amendments/, /employment-data/ - flat under /api/v1/
- /api/v1/documents/   - English path per spec § 3.4
- /api/v1/payroll/     - English path per spec § 3.4
- /api/v1/time-off/    - English path per spec § 3.4
- /api/v1/onboarding/  - English path per spec § 3.4
"""

from django.urls import path, include

app_name = 'api_v1'

urlpatterns = [
    # Authentication
    path('auth/', include('api.v1.auth.urls')),

    # Workspaces (cross-tenant listing + exchange)
    path('workspaces/', include('api.v1.workspaces.urls')),

    # Canonical URLs (English paths) per spec § 3.4
    path('identity/', include('api.v1.identity.urls')),
    path('organization/', include('api.v1.organization.urls')),
    path('', include('api.v1.employees.urls')),     # /api/v1/employees/, /family-members/, /academic-records/, /certifications/
    path('', include('api.v1.contracts.urls')),     # /api/v1/contracts/, /contract-amendments/, /employment-data/
    path('documents/', include('api.v1.documents.urls')),
    path('payroll/', include('api.v1.payroll.urls')),
    path('time-off/', include('api.v1.time_off.urls')),
    path('onboarding/', include('api.v1.onboarding.urls')),
    path('compensation/', include('api.v1.compensation.urls')),
    path('', include('api.v1.policies.urls')),     # /api/v1/policies/, /policy-versions/, etc.
]
