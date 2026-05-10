"""Tests for EmpleadoViewSet path/scope fixes (B.4 #19, #20, #42)."""

import inspect


class TestGetQuerysetFilterByArea:
    def test_no_stale_area_destino_chain_in_get_queryset(self):
        """get_queryset must NOT chain ...__area_destino__area_id (#42)."""
        from api.v1.rrhh.views import EmpleadoViewSet

        src = inspect.getsource(EmpleadoViewSet.get_queryset)
        assert "area_destino__area_id" not in src


class TestEstadisticasTenantScope:
    def test_estadisticas_does_not_use_global_employee_objects_count(self):
        """estadisticas must scope counts to the current tenant via self.get_queryset() (#20)."""
        from api.v1.rrhh.views import EmpleadoViewSet

        src = inspect.getsource(EmpleadoViewSet.estadisticas)
        assert "Employee.objects.count()" not in src
        assert "Employee.objects.filter" not in src or "self.get_queryset()" in src
