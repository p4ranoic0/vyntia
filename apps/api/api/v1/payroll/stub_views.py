"""Stub for the legacy payroll API surface during the Vyntia Pay migration.

The legacy `apps.payroll` models + services are dropped in D.1b and rebuilt
greenfield across D.2-D.6. During the transition every legacy
`/api/v1/payroll/*` URL must keep returning a structured HTTP 501 (not a 404)
so existing frontend consumers degrade gracefully.

This module imports NOTHING from `apps.payroll` — that is what lets D.1b drop
those models without breaking the URL conf.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from apps.core.responses import APIResponse

_MESSAGE = (
    "El módulo de planilla está en reconstrucción (Vyntia Pay). "
    "Este endpoint estará disponible en una próxima fase."
)


class PayrollUnavailableView(APIView):
    """Catch-all 501 for every legacy /api/v1/payroll/* route + verb."""

    permission_classes = [AllowAny]

    def _gone(self, request, *args, **kwargs):
        return APIResponse.error(
            message=_MESSAGE,
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            error_code="payroll_rebuilding",
        )

    get = _gone
    post = _gone
    put = _gone
    patch = _gone
    delete = _gone
