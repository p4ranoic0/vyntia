"""D.1a — legacy /api/v1/payroll/* surface must return structured 501, not 404."""

from django.urls import resolve
from rest_framework.test import APIRequestFactory

from api.v1.payroll.stub_views import PayrollUnavailableView


def test_stub_view_returns_501_for_every_verb():
    factory = APIRequestFactory()
    view = PayrollUnavailableView.as_view()
    for method in ("get", "post", "put", "patch", "delete"):
        request = getattr(factory, method)("/api/v1/payroll/monthly-runs/")
        response = view(request)
        assert response.status_code == 501, f"{method} returned {response.status_code}"
        assert response.data["success"] is False
        assert response.data["error_code"] == "payroll_rebuilding"


def test_all_legacy_payroll_paths_resolve_to_stub():
    paths = [
        "/api/v1/payroll/monthly-runs/",
        "/api/v1/payroll/monthly-runs/abc-123/calcular_planilla/",
        "/api/v1/payroll/tax-parameters/",
        "/api/v1/payroll/payslips/abc-123/pdf/",
        "/api/v1/payroll/mass-deductions/abc-123/anular/",
        "/api/v1/payroll/compensation-configurations/",
    ]
    for path in paths:
        match = resolve(path)
        assert getattr(match.func, "cls", None) is PayrollUnavailableView, path
