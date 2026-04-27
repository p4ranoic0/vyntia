# -*- coding: utf-8 -*-
"""
Tests para la API de Onboarding — Wave 0 RED scaffold.

Estos tests deben FALLAR (RED) hasta que Wave 1 implemente los endpoints.
Cubre: ONBD-01 (corregir-correo), ONBD-03 (foto), ONBD-08 (last_login en lista).
"""

import pytest
import io

from rest_framework.test import APIClient

from apps.onboarding.models import OnboardingProcess
from apps.documents.models import DigitalDocument
from apps.employees.models import Employee


@pytest.mark.django_db
class TestCorregirCorreo:
    """ONBD-01: POST /api/v1/rrhh/onboarding/{id}/corregir-correo/ — no existe todavía."""

    def test_corregir_correo_updates_email(self, hr_client, onboarding_factory):
        """El endpoint corregir-correo debe actualizar Employee.correo_personal.

        DEBE FALLAR en RED — el endpoint no existe aún (404 o 405).
        El test espera HTTP 2xx, que no ocurrirá hasta Wave 1.
        """
        onboarding = onboarding_factory()
        nuevo_correo = "nuevo.correo@test.com"
        url = f"/api/v1/rrhh/onboarding/{onboarding.onboarding_id}/corregir-correo/"

        response = hr_client.post(url, {"correo_personal": nuevo_correo}, format="json")

        # Este assert falla en RED porque el endpoint no existe (404/405)
        assert response.status_code in (200, 201), (
            f"Se esperaba 200/201 pero se obtuvo {response.status_code}. "
            "El endpoint corregir-correo no existe todavía (Wave 1 lo implementará)."
        )

        # Verificar que el correo fue actualizado en DB
        onboarding.empleado.refresh_from_db()
        assert onboarding.empleado.correo_personal == nuevo_correo, (
            f"El correo en DB es '{onboarding.empleado.correo_personal}', "
            f"se esperaba '{nuevo_correo}'"
        )


@pytest.mark.django_db
class TestPhotoUpload:
    """ONBD-03: Subida de foto de perfil crea DigitalDocument con tipo_documento='foto'."""

    def test_photo_upload_creates_documento(self, onboarding_client):
        """POST /api/v1/rrhh/onboarding/subir-foto/ crea DigitalDocument con tipo='foto'
        y actualiza ruta_fotografia en el Employee.
        """
        onboarding = onboarding_client._onboarding
        empleado_id = onboarding.empleado.empleado_id

        # Simular archivo de imagen pequeño (PNG header)
        imagen = io.BytesIO(b"\x89PNG\r\n\x1a\n" + b"\x00" * 100)
        imagen.name = "foto_perfil.png"

        url = "/api/v1/rrhh/onboarding/subir-foto/"
        response = onboarding_client.post(
            url,
            {"archivo": imagen},
            format="multipart",
        )

        assert response.status_code in (200, 201), (
            f"Se esperaba 200/201 pero se obtuvo {response.status_code}. "
            f"Respuesta: {response.data}"
        )

        # Verificar que se creó el documento con tipo foto
        existe_foto = DigitalDocument.objects.filter(
            empleado_id=empleado_id,
            tipo_documento="foto",
        ).exists()
        assert existe_foto, (
            "No se encontró DigitalDocument con tipo_documento='foto' "
            "para el empleado tras el upload."
        )

        # Verificar que se actualizó ruta_fotografia
        onboarding.empleado.refresh_from_db()
        assert onboarding.empleado.ruta_fotografia, (
            "ruta_fotografia del empleado no fue actualizada tras subir la foto."
        )


@pytest.mark.django_db
class TestOnboardingList:
    """ONBD-08: GET /api/v1/rrhh/onboarding/ incluye campo 'last_login' en cada item."""

    def test_list_includes_last_login(self, hr_client, onboarding_factory):
        """El listado de onboardings debe incluir 'last_login' en cada elemento.

        DEBE FALLAR en RED — el serializer actual no expone 'last_login'.
        """
        # Crear al menos un onboarding
        onboarding_factory()

        url = "/api/v1/rrhh/onboarding/"
        response = hr_client.get(url)

        assert response.status_code == 200, (
            f"GET {url} devolvió {response.status_code}, se esperaba 200"
        )

        # Extraer resultados (paginado o no)
        data = response.data
        if isinstance(data, dict):
            results = data.get("results", data.get("data", []))
        else:
            results = data

        assert len(results) > 0, "No hay onboardings en la lista — el factory no creó datos"

        first_item = results[0]
        assert "last_login" in first_item, (
            f"El campo 'last_login' no está en la respuesta. "
            f"Campos disponibles: {list(first_item.keys())}"
        )


# --- Wave 5 stubs: per-document approval endpoints ---

class TestPerDocumentApproval:
    def test_aprobar_documento_stub(self):
        """Stub — full test in plan 01-09 execution. Verifies endpoint exists."""
        pass

    def test_rechazar_documento_requires_motivo(self):
        """Stub — rechazar without motivo returns 400."""
        pass

    def test_cursos_certificaciones_employee_create(self):
        """Stub — employee can create their own curso record."""
        pass

    def test_familiar_employee_create_own_record(self):
        """Stub — employee can create FamilyMember for own empleado_id."""
        pass
