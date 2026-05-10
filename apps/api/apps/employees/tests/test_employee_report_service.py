"""Tests for EmpleadoReportService PK lookup fix (B.4 #16)."""

import inspect


class TestEmpleadoReportServicePKLookup:
    def test_uses_id_not_empleado_id(self):
        from apps.employees.services.employee_report_service import EmpleadoReportService

        src = inspect.getsource(EmpleadoReportService)
        assert "Employee.objects.get(empleado_id=" not in src
        assert "Employee.objects.get(empleado_id =" not in src
        assert "Employee.objects.get(id=" in src or "Employee.objects.get(pk=" in src
