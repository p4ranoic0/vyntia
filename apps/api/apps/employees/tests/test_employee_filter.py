"""Tests for EmpleadoFilter path/choice fixes (B.4 #18, #41)."""

import inspect


class TestEmpleadoFilterArea:
    def test_filter_area_uses_real_path(self):
        from api.v1.rrhh.filters import EmpleadoFilter

        src = inspect.getsource(EmpleadoFilter.filter_area)
        assert "ubicaciones_destino__area_id" not in src


class TestEmpleadoFilterTieneConyuge:
    def test_uses_conyuge_choice_not_legacy_esposo_esposa(self):
        from api.v1.rrhh.filters import EmpleadoFilter

        src = inspect.getsource(EmpleadoFilter.filter_tiene_conyuge)
        assert '"esposo"' not in src
        assert '"esposa"' not in src
        assert '"conyuge"' in src or "'conyuge'" in src
