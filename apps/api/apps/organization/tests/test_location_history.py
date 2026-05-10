"""Tests for LocationHistory property fixes (B.3 #53)."""

from datetime import date

import pytest


@pytest.mark.django_db
class TestLocationHistoryProperties:
    def _setup(self):
        from apps.organization.models import Department
        from apps.employees.models import Employee
        from apps.organization.models.location_history import LocationHistory

        dept_origin = Department.objects.create(
            nombre_organo="OrgIn53",
            nombre_unidad_organica="UnidadIn53",
            siglas_area="ORI",
            estado_area="activo",
        )
        dept_dest = Department.objects.create(
            nombre_organo="OrgOut53",
            nombre_unidad_organica="UnidadOut53",
            siglas_area="DST",
            estado_area="activo",
        )
        emp = Employee.objects.create(
            nombres_empleado="TestLH",
            apellido_paterno="User",
            apellido_materno="Test",
            numero_documento="55512345",
            tipo_documento="DNI",
            correo_personal="testlh53@example.com",
            estado_empleado="activo",
        )
        loc = LocationHistory.objects.create(
            empleado=emp,
            area_origen=dept_origin,
            area_destino=dept_dest,
            tipo_movimiento="rotacion",
            estado_ubicacion="activo",
            fecha_inicio=date.today(),
        )
        return loc, dept_origin, dept_dest

    def test_movimiento_completo_uses_existing_field(self):
        """movimiento_completo must NOT raise AttributeError on nombre_area (#53)."""
        loc, dept_origin, dept_dest = self._setup()
        # Must not raise
        result = loc.movimiento_completo
        # Should reference origin and destination by some real Department field
        assert dept_origin.nombre_unidad_organica in result or dept_origin.siglas_area in result
        assert dept_dest.nombre_unidad_organica in result or dept_dest.siglas_area in result

    def test_codigo_movimiento_uses_existing_field(self):
        """codigo_movimiento must NOT raise AttributeError on codigo_area (#53)."""
        loc, _, dept_dest = self._setup()
        result = loc.codigo_movimiento
        assert isinstance(result, str)
        assert len(result) > 0
