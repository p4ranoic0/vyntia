# -*- coding: utf-8 -*-
"""
Tests for ONBD-16: EmpleadoUpdateSerializer extension.

Verifies that PATCH /api/v1/rrhh/empleados/{id}/ correctly saves and returns
the 8 new personal/banking/pension fields added in plan 01.1-01.

Response shape note:
  - PATCH partial_update returns super().partial_update() -> Response(serializer.data)
  - GET retrieve returns super().retrieve() -> Response(serializer.data)
  Both return the serializer data directly (no APIResponse envelope).
"""

import pytest


@pytest.mark.django_db
class TestEmpleadoUpdateV2:
    """Test suite for ONBD-16 serializer extensions."""

    def _empleado_url(self, empleado_id):
        return f"/api/v1/rrhh/empleados/{empleado_id}/"

    def test_patch_saves_pension_fields(self, hr_client, onboarding_factory):
        """PATCH with sistema_pensiones+codigo_cuspp+tipo_comision saves all three fields."""
        onboarding = onboarding_factory()
        empleado = onboarding.empleado
        url = self._empleado_url(empleado.empleado_id)

        patch_data = {
            "sistema_pensiones": "AFP PRIMA",
            "codigo_cuspp": "ABCD1234",
            "tipo_comision": "FLUJO",
        }
        response = hr_client.patch(url, patch_data, format="json")
        assert response.status_code == 200, f"PATCH failed: {response.data}"

        get_response = hr_client.get(url)
        assert get_response.status_code == 200
        # retrieve returns serializer.data directly (no APIResponse envelope)
        data = get_response.data
        assert data["sistema_pensiones"] == "AFP PRIMA"
        assert data["codigo_cuspp"] == "ABCD1234"
        assert data["tipo_comision"] == "FLUJO"

    def test_patch_saves_banking_fields(self, hr_client, onboarding_factory):
        """PATCH with numero_cci saves the field; GET confirms saved value."""
        onboarding = onboarding_factory()
        empleado = onboarding.empleado
        url = self._empleado_url(empleado.empleado_id)

        patch_data = {"numero_cci": "00219300060156893091"}
        response = hr_client.patch(url, patch_data, format="json")
        assert response.status_code == 200, f"PATCH failed: {response.data}"

        get_response = hr_client.get(url)
        assert get_response.status_code == 200
        data = get_response.data
        assert data["numero_cci"] == "00219300060156893091"

    def test_patch_accepts_sin_pension(self, hr_client, onboarding_factory):
        """PATCH with sistema_pensiones='SIN PENSION' returns 200 (not 400 validation error)."""
        onboarding = onboarding_factory()
        empleado = onboarding.empleado
        url = self._empleado_url(empleado.empleado_id)

        patch_data = {"sistema_pensiones": "SIN PENSION"}
        response = hr_client.patch(url, patch_data, format="json")
        assert response.status_code == 200, (
            f"Expected 200 for 'SIN PENSION', got {response.status_code}: {response.data}"
        )

    def test_patch_saves_domicile_fields(self, hr_client, onboarding_factory):
        """PATCH with provincia_domicilio+departamento_domicilio saves both; GET confirms."""
        onboarding = onboarding_factory()
        empleado = onboarding.empleado
        url = self._empleado_url(empleado.empleado_id)

        patch_data = {
            "provincia_domicilio": "Arequipa",
            "departamento_domicilio": "Arequipa",
        }
        response = hr_client.patch(url, patch_data, format="json")
        assert response.status_code == 200, f"PATCH failed: {response.data}"

        get_response = hr_client.get(url)
        assert get_response.status_code == 200
        data = get_response.data
        assert data["provincia_domicilio"] == "Arequipa"
        assert data["departamento_domicilio"] == "Arequipa"

    def test_read_serializer_includes_new_fields(self, hr_client, onboarding_factory):
        """GET /api/v1/rrhh/empleados/{id}/ response keys include sistema_pensiones, numero_cci, codigo_cuspp."""
        onboarding = onboarding_factory()
        empleado = onboarding.empleado
        url = self._empleado_url(empleado.empleado_id)

        get_response = hr_client.get(url)
        assert get_response.status_code == 200
        # retrieve returns serializer.data directly (no APIResponse envelope)
        data = get_response.data
        assert "sistema_pensiones" in data, "sistema_pensiones not in GET response"
        assert "numero_cci" in data, "numero_cci not in GET response"
        assert "codigo_cuspp" in data, "codigo_cuspp not in GET response"
        assert "tipo_comision" in data, "tipo_comision not in GET response"
        assert "numero_ruc" in data, "numero_ruc not in GET response"
        assert "provincia_domicilio" in data, "provincia_domicilio not in GET response"
        assert "departamento_domicilio" in data, "departamento_domicilio not in GET response"
