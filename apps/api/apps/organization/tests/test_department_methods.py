"""Tests for organization bug fixes (B.3 #50, #51, #52, #56)."""

import inspect

import pytest


@pytest.mark.django_db
class TestAreaSerializerEmpleadosCount:
    def test_serializer_resolves_empleados_activos_count(self):
        """AreaSerializer.get_empleados_activos_count must call the real method,
        not the non-existent get_empleados_activos_count() (#50)."""
        from apps.organization.models import Department
        from api.v1.rrhh.serializers import AreaSerializer

        dept = Department.objects.create(
            nombre_organo="Test50",
            nombre_unidad_organica="Test Org 50",
            siglas_area="T50",
            estado_area="activo",
        )
        serializer = AreaSerializer(dept)
        # This must NOT raise AttributeError
        data = serializer.data
        assert "empleados_activos_count" in data
        assert isinstance(data["empleados_activos_count"], int)


class TestAreaViewSetEmpleados:
    def test_empleados_action_uses_real_method_name(self):
        """AreaViewSet.empleados must call empleados_activos (which exists),
        NOT empleados_actuales (which doesn't) (#51)."""
        from api.v1.rrhh.views import AreaViewSet

        source = inspect.getsource(AreaViewSet.empleados)
        assert "empleados_activos" in source
        assert "empleados_actuales" not in source


class TestAreaViewSetActivas:
    def test_activas_filters_estado_area_field(self):
        """AreaViewSet.activas must filter by estado_area='activo' — NOT
        estado='activa' (#52)."""
        from api.v1.rrhh.views import AreaViewSet

        source = inspect.getsource(AreaViewSet.activas)
        assert 'estado="activa"' not in source
        assert "estado='activa'" not in source
        assert "estado_area" in source


class TestAreaViewSetPerformDestroy:
    def test_perform_destroy_uses_valid_inactivo_choice(self):
        """AreaViewSet.perform_destroy must set estado_area='inactivo' — the
        valid choice value (#56). 'inactiva' is not in ESTADO_AREA_CHOICES."""
        from api.v1.rrhh.views import AreaViewSet

        source = inspect.getsource(AreaViewSet.perform_destroy)
        assert 'estado_area = "inactiva"' not in source
        assert "estado_area = 'inactiva'" not in source
        assert '"inactivo"' in source or "'inactivo'" in source
