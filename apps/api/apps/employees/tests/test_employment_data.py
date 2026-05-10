"""Tests for EmploymentData.generar_codigo_empleado fix (B.4 #59)."""

import inspect


class TestGenerarCodigoEmpleado:
    def test_uses_id_not_stale_empleado_id(self):
        from apps.contracts.models import EmploymentData

        src = inspect.getsource(EmploymentData.generar_codigo_empleado)
        assert "empleado.empleado_id" not in src
        assert "empleado.id" in src or "empleado.pk" in src
