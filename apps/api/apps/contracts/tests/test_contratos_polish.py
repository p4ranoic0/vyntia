"""Tests for B.5 contracts polish bug fixes (#60-#67)."""

import inspect


# ---- #60 / #61 ----
class TestContratosAdendasViewSetGetQueryset:
    def test_distinct_query_params_for_empleado_and_area(self):
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet
        src = inspect.getsource(ContratosAdendasViewSet.get_queryset)
        # Bug: both empleado and area reading from "id"
        assert src.count('query_params.get("id")') < 2

    def test_filter_uses_status_not_estado(self):
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet
        src = inspect.getsource(ContratosAdendasViewSet.get_queryset)
        # Contract.estado was renamed to status
        assert "filter(estado=" not in src


class TestContratosAdendasViewSetEstadisticas:
    def test_uses_get_queryset_not_global(self):
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet
        src = inspect.getsource(ContratosAdendasViewSet.estadisticas)
        # Should not query Contract globally for tenant-scoped stats
        assert "Contract.objects.count()" not in src
        # Either uses self.get_queryset() or a local base assignment
        assert "self.get_queryset()" in src or "base = " in src or "qs = " in src


class TestAlertasVencimientoUsesStatus:
    def test_alertas_vencimiento_uses_status_not_estado(self):
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet
        src = inspect.getsource(ContratosAdendasViewSet.alertas_vencimiento)
        assert 'estado="ACTIVO"' not in src
        assert 'filter(estado=' not in src


class TestReporteContratosUsesStatus:
    def test_reporte_contratos_uses_status_not_estado(self):
        from api.v1.rrhh.contratos_views import ContratosAdendasViewSet
        src = inspect.getsource(ContratosAdendasViewSet.reporte_contratos)
        assert 'filter(estado=' not in src
        assert 'Q(estado=' not in src


# ---- #67 ----
class TestDatosLaboralesViewSetQuerysetSingleton:
    def test_class_declares_queryset_only_once(self):
        from api.v1.rrhh.views import DatosLaboralesViewSet
        src = inspect.getsource(DatosLaboralesViewSet)
        # Count class-body assignments (lines starting with "    queryset = ")
        class_level = sum(1 for line in src.split("\n") if line.startswith("    queryset = "))
        assert class_level == 1, f"Expected 1 queryset assignment, got {class_level}"


# ---- #63 ----
class TestDatosLaboralesViewSetSearchOrderingFields:
    def test_no_stale_search_fields(self):
        from api.v1.rrhh.views import DatosLaboralesViewSet
        # puesto_trabajo and categoria_laboral don't exist on EmploymentData
        stale = {"puesto_trabajo", "categoria_laboral"}
        actual = set(getattr(DatosLaboralesViewSet, "search_fields", []))
        overlap = stale & actual
        assert not overlap, f"Stale search_fields still present: {overlap}"

    def test_no_stale_ordering_fields(self):
        from api.v1.rrhh.views import DatosLaboralesViewSet
        # remuneracion_mensual doesn't exist on EmploymentData
        stale = {"remuneracion_mensual"}
        actual = set(getattr(DatosLaboralesViewSet, "ordering_fields", []))
        overlap = stale & actual
        assert not overlap, f"Stale ordering_fields still present: {overlap}"


# ---- #64 ----
class TestEstadisticasRemuneracionFieldRefs:
    def test_no_stale_field_refs(self):
        from api.v1.rrhh.views import DatosLaboralesViewSet
        if hasattr(DatosLaboralesViewSet, "estadisticas_remuneracion"):
            src = inspect.getsource(DatosLaboralesViewSet.estadisticas_remuneracion)
            assert "estado_laboral" not in src, "estado_laboral is stale; use estado_datos"
            assert "remuneracion_mensual" not in src, "remuneracion_mensual is stale; use sueldo_basico"


# ---- #65 ----
class TestDatosLaboralesFilterFieldPaths:
    def test_no_stale_field_paths(self):
        """No filter should reference non-existent EmploymentData fields as field_name."""
        from api.v1.rrhh.filters import DatosLaboralesFilter
        src = inspect.getsource(DatosLaboralesFilter)
        # These direct field names don't exist on EmploymentData
        # remuneracion as field_name is stale
        assert 'field_name="remuneracion"' not in src, "remuneracion is not a field on EmploymentData"

    def test_filter_is_importable(self):
        """The filter class must import without errors."""
        from api.v1.rrhh.filters import DatosLaboralesFilter
        assert DatosLaboralesFilter is not None


# ---- #66 ----
class TestDatosLaboralesSerializerProperties:
    def test_no_antiguedad_anos_with_tilde(self):
        """antiguedad_años (with tilde) is not a property on EmploymentData; must use antiguedad_anos."""
        from api.v1.rrhh.serializers import DatosLaboralesSerializer
        src = inspect.getsource(DatosLaboralesSerializer)
        assert "antiguedad_años" not in src, "Use antiguedad_anos (without tilde)"

    def test_no_tiempo_servicio(self):
        """tiempo_servicio does not exist on EmploymentData."""
        from api.v1.rrhh.serializers import DatosLaboralesSerializer
        src = inspect.getsource(DatosLaboralesSerializer)
        assert "tiempo_servicio" not in src, "tiempo_servicio is not a property on EmploymentData"

    def test_serializer_imports_without_error(self):
        """The serializer class must import without errors."""
        from api.v1.rrhh.serializers import DatosLaboralesSerializer
        assert DatosLaboralesSerializer is not None
