# -*- coding: utf-8 -*-
"""
Tests for onboarding self-service fixes (UAT round 2):

- Fix 1: Employee can PATCH their own personal/banking/pension fields
- Fix 2: Employee cannot PATCH restricted fields (nombres_empleado, etc.)
- Fix 3: FamilyMember — 'hijo' accepted, 'hija' rejected by backend
- Fix 4: Employee can DELETE their own dependents
- Fix 5: Employee cannot delete another employee's dependents
"""

import pytest
from django.core.cache import cache

from apps.employees.models import FamilyMember, Employee


@pytest.fixture(autouse=True)
def clear_cache():
    cache.clear()
    yield
    cache.clear()


def _empleado_url(empleado_id):
    return f"/api/v1/rrhh/empleados/{empleado_id}/"


def _familiares_url(pk=None):
    if pk:
        return f"/api/v1/rrhh/datos-familiares/{pk}/"
    return "/api/v1/rrhh/datos-familiares/"


@pytest.mark.django_db
class TestEmpleadoSelfUpdate:
    """Employee can PATCH their own personal/banking/pension fields (Fix 1)."""

    def test_employee_can_patch_own_personal_fields(self, onboarding_client):
        onboarding = onboarding_client._onboarding
        empleado = onboarding.empleado
        url = _empleado_url(empleado.pk)

        payload = {
            "telefono_celular": "987654321",
            "direccion_domicilio": "Av. Nueva 999",
            "genero_empleado": "masculino",
            "estado_civil": "soltero",
        }
        response = onboarding_client.patch(url, payload, format="json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"

        empleado.refresh_from_db()
        assert empleado.telefono_celular == "987654321"
        assert empleado.direccion_domicilio == "Av. Nueva 999"

    def test_employee_can_patch_own_banking_fields(self, onboarding_client):
        onboarding = onboarding_client._onboarding
        empleado = onboarding.empleado
        url = _empleado_url(empleado.pk)

        payload = {
            "entidad_bancaria": "BCP - Banco de Crédito del Perú",
            "numero_cuenta_bancaria": "19412345678901",
            "numero_cci": "00219412345678901234",
        }
        response = onboarding_client.patch(url, payload, format="json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"

        empleado.refresh_from_db()
        assert empleado.entidad_bancaria == "BCP - Banco de Crédito del Perú"
        assert empleado.numero_cci == "00219412345678901234"

    def test_employee_can_patch_own_pension_fields(self, onboarding_client):
        onboarding = onboarding_client._onboarding
        empleado = onboarding.empleado
        url = _empleado_url(empleado.pk)

        payload = {
            "sistema_pensiones": "AFP PRIMA",
            "tipo_comision": "FLUJO",
            "codigo_cuspp": "TEST20001231",
        }
        response = onboarding_client.patch(url, payload, format="json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"

        empleado.refresh_from_db()
        assert empleado.sistema_pensiones == "AFP PRIMA"

    def test_employee_cannot_patch_restricted_fields(self, onboarding_client):
        """Employee sending nombres_empleado must be blocked (403)."""
        onboarding = onboarding_client._onboarding
        empleado = onboarding.empleado
        url = _empleado_url(empleado.pk)

        payload = {"nombres_empleado": "Hacker", "apellido_paterno": "Hack"}
        response = onboarding_client.patch(url, payload, format="json")
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"

    def test_employee_cannot_patch_another_employees_record(self, onboarding_client):
        """Employee cannot PATCH another employee's record even with allowed fields."""
        other_empleado = Employee.objects.create(
            nombres_empleado="Otro",
            apellido_paterno="Employee",
            apellido_materno="Dos",
            numero_documento="88776655",
            tipo_documento="DNI",
            correo_personal="otro.empleado2@test.com",
            estado_empleado="activo",
        )
        url = _empleado_url(other_empleado.pk)

        payload = {"telefono_celular": "111222333"}
        response = onboarding_client.patch(url, payload, format="json")
        assert response.status_code in (403, 404), (
            f"Expected 403 or 404, got {response.status_code}"
        )

    def test_hr_can_patch_any_field(self, hr_client, onboarding_factory):
        """RRHH can still PATCH any field including restricted ones."""
        onboarding = onboarding_factory()
        empleado = onboarding.empleado
        url = _empleado_url(empleado.pk)

        payload = {"numero_ruc": "10123456789"}
        response = hr_client.patch(url, payload, format="json")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.data}"


@pytest.mark.django_db
class TestDatosFamiliaresParentesco:
    """Parentesco choices: 'hijo' accepted, 'hija' rejected by backend (Fix 3 frontend)."""

    def _base_familiar_payload(self, empleado_id, **overrides):
        payload = {
            "empleado": empleado_id,
            "nombres_familiar": "Juan",
            "apellido_paterno": "García",
            "apellido_materno": "López",
            "parentesco": "hijo",
            "fecha_nacimiento": "2010-01-15",
            "genero_familiar": "masculino",
            "numero_documento": "12345678",
        }
        payload.update(overrides)
        return payload

    def test_create_familiar_hijo_accepted(self, onboarding_client):
        onboarding = onboarding_client._onboarding
        payload = self._base_familiar_payload(onboarding.empleado.pk)
        response = onboarding_client.post(_familiares_url(), payload, format="json")
        assert response.status_code in (200, 201), f"Expected 201, got {response.status_code}: {response.data}"

    def test_create_familiar_hija_rejected_by_backend(self, onboarding_client):
        """'hija' is NOT a valid backend choice — backend must reject it (hence frontend fix)."""
        onboarding = onboarding_client._onboarding
        payload = self._base_familiar_payload(
            onboarding.empleado.pk,
            parentesco="hija",
            nombres_familiar="María",
            numero_documento="87654321",
        )
        response = onboarding_client.post(_familiares_url(), payload, format="json")
        assert response.status_code == 400, (
            f"'hija' should be rejected by backend (invalid choice), got {response.status_code}"
        )

    def test_create_familiar_conyuge_accepted(self, onboarding_client):
        onboarding = onboarding_client._onboarding
        payload = self._base_familiar_payload(
            onboarding.empleado.pk,
            parentesco="conyuge",
            nombres_familiar="Ana",
            apellido_paterno="Torres",
            numero_documento="11223344",
        )
        response = onboarding_client.post(_familiares_url(), payload, format="json")
        assert response.status_code in (200, 201), f"Expected 201, got {response.status_code}: {response.data}"


@pytest.mark.django_db
class TestDatosFamiliaresDestroy:
    """Employee can delete their own dependents but not another's (Fix 4)."""

    def _create_familiar(self, empleado, parentesco="hijo"):
        return FamilyMember.objects.create(
            empleado=empleado,
            nombres_familiar="Test",
            apellido_paterno="Familiar",
            apellido_materno="X",
            parentesco=parentesco,
            fecha_nacimiento="2010-05-20",
            genero_familiar="masculino",
            numero_documento="00000001",
        )

    def test_employee_can_delete_own_familiar(self, onboarding_client):
        onboarding = onboarding_client._onboarding
        familiar = self._create_familiar(onboarding.empleado)

        response = onboarding_client.delete(_familiares_url(familiar.pk))
        assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.data}"
        assert not FamilyMember.objects.filter(pk=familiar.pk).exists()

    def test_employee_cannot_delete_other_employees_familiar(self, onboarding_client):
        other_empleado = Employee.objects.create(
            nombres_empleado="Otro",
            apellido_paterno="Employee",
            apellido_materno="X",
            numero_documento="77665544",
            tipo_documento="DNI",
            correo_personal="otro.empleado3@test.com",
            estado_empleado="activo",
        )
        other_familiar = self._create_familiar(other_empleado)

        response = onboarding_client.delete(_familiares_url(other_familiar.pk))
        assert response.status_code in (403, 404), (
            f"Expected 403 or 404, got {response.status_code}"
        )
        assert FamilyMember.objects.filter(pk=other_familiar.pk).exists()

    def test_hr_can_delete_any_familiar(self, hr_client, onboarding_factory):
        onboarding = onboarding_factory()
        familiar = self._create_familiar(onboarding.empleado)

        response = hr_client.delete(_familiares_url(familiar.pk))
        assert response.status_code == 204, f"Expected 204, got {response.status_code}: {response.data}"
