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


@pytest.mark.django_db
class TestAreaSerializerValidateSiglas:
    def test_two_tenants_can_have_same_siglas(self):
        """validate_siglas_area must scope to the current tenant (#55)."""
        from apps.tenancy.models import Tenant
        from apps.tenancy.context import tenant_context
        from apps.organization.models import Department
        from apps.identity.models import User
        from api.v1.rrhh.serializers import AreaSerializer

        # Create an admin user to own the tenants
        admin = User.objects.create_user(
            username="admin_55a",
            email="admin@test.com",
            password="test123",
            is_staff=True,
        )

        ta = Tenant.objects.create(
            name="VS TA",
            slug="vs-ta",
            ruc="20111111111",
            plan="starter",
            status="active",
            created_by=admin,
        )
        tb = Tenant.objects.create(
            name="VS TB",
            slug="vs-tb",
            ruc="20222222222",
            plan="starter",
            status="active",
            created_by=admin,
        )

        Department.objects.create(
            nombre_organo="A_55",
            nombre_unidad_organica="A_55",
            siglas_area="RRHH",
            estado_area="activo",
            tenant=ta,
        )

        # Same siglas in tenant B should be allowed
        with tenant_context(tb):
            serializer = AreaSerializer(data={
                "nombre_organo": "B_55",
                "nombre_unidad_organica": "B_55",
                "siglas_area": "RRHH",
                "estado_area": "activo",
            })
            assert serializer.is_valid(), serializer.errors

    def test_same_tenant_still_blocks_duplicate_siglas(self):
        """Within the same tenant, duplicate siglas must still be rejected (#55)."""
        from apps.tenancy.models import Tenant
        from apps.tenancy.context import tenant_context
        from apps.organization.models import Department
        from apps.identity.models import User
        from api.v1.rrhh.serializers import AreaSerializer

        # Create an admin user to own the tenant
        admin = User.objects.create_user(
            username="admin_55b",
            email="admin2@test.com",
            password="test123",
            is_staff=True,
        )

        tc = Tenant.objects.create(
            name="VS TC",
            slug="vs-tc",
            ruc="20333333333",
            plan="starter",
            status="active",
            created_by=admin,
        )

        Department.objects.create(
            nombre_organo="C_55",
            nombre_unidad_organica="C_55",
            siglas_area="DUPL",
            estado_area="activo",
            tenant=tc,
        )

        with tenant_context(tc):
            serializer = AreaSerializer(data={
                "nombre_organo": "C2_55",
                "nombre_unidad_organica": "C2_55",
                "siglas_area": "DUPL",
                "estado_area": "activo",
            })
            assert not serializer.is_valid()
            assert "siglas_area" in serializer.errors
