# -*- coding: utf-8 -*-
"""
Tests for DocumentosDigitales endpoint behavior for onboarding employees.
Covers GAP-02 (archivo_url missing from response) and GAP-05 (permission issues).

All tests pass against the fixed code from plans 01.1-05 and 01.1-06.
"""
import io
import pytest
from django.core.files.base import ContentFile

from app_rrhh.models import DocumentosDigitales


def _make_doc(empleado, tipo='dni', categoria='personal', nombre='Doc Test',
              es_version_actual=True, version='1.0', estado='pendiente_revision'):
    """
    Create a DocumentosDigitales record with a minimal in-memory file.
    Provides all mandatory fields so save() does not raise ValidationError.
    """
    content = ContentFile(b'%PDF-1.4 fake content', name='test.pdf')
    doc = DocumentosDigitales(
        empleado=empleado,
        tipo_documento=tipo,
        categoria=categoria,
        nombre_documento=nombre,
        estado_documento=estado,
        es_version_actual=es_version_actual,
        version=version,
        nombre_archivo_original='test.pdf',
        formato_archivo='pdf',
        tamano_archivo=len(b'%PDF-1.4 fake content'),
        nivel_acceso='restringido',
    )
    doc.archivo.save('test.pdf', content, save=False)
    doc.save()
    return doc


@pytest.mark.django_db
class TestDocumentosDigitalesOnboardingEmployee:
    """Onboarding employee can list their own documents."""

    def test_employee_can_list_own_documents(self, onboarding_client):
        """GET documentos-digitales/?empleado=X returns 200 for authenticated employee."""
        onboarding = onboarding_client._onboarding
        empleado = onboarding.empleado

        _make_doc(empleado, tipo='dni', nombre='DNI del empleado', version='1.0')

        url = f'/api/v1/rrhh/documentos-digitales/?empleado={empleado.empleado_id}'
        response = onboarding_client.get(url)
        assert response.status_code == 200, (
            f'Expected 200, got {response.status_code}: {response.data}'
        )

    def test_response_includes_archivo_url_field(self, onboarding_client):
        """Response must include archivo_url field in each document record."""
        onboarding = onboarding_client._onboarding
        empleado = onboarding.empleado

        _make_doc(empleado, tipo='foto', nombre='Foto del empleado', version='1.0')

        url = f'/api/v1/rrhh/documentos-digitales/?empleado={empleado.empleado_id}'
        response = onboarding_client.get(url)
        assert response.status_code == 200

        # Unwrap the APIResponse envelope
        raw = response.data
        data = raw.get('data') or raw.get('results') or []
        if isinstance(data, dict):
            data = data.get('results', [])

        assert len(data) > 0, 'Expected at least one document in response'

        first_doc = data[0]
        assert 'archivo_url' in first_doc, (
            f'archivo_url field missing from response. Got keys: {list(first_doc.keys())}'
        )

    def test_employee_cannot_see_other_employee_documents(self, onboarding_client):
        """Requesting another employee's documents returns 0 results (filtered to own).

        Creates a second employee directly (not via factory) to avoid email uniqueness clash.
        """
        from app_rrhh.models import Empleado
        other_empleado = Empleado.objects.create(
            nombres_empleado='Otro',
            apellido_paterno='Empleado',
            apellido_materno='Prueba',
            numero_documento='11223344',
            tipo_documento='DNI',
            correo_personal='otro.empleado@test.com',
            telefono_celular='988777666',
            fecha_nacimiento='1990-01-01',
            estado_civil='soltero',
            genero_empleado='femenino',
            direccion_domicilio='Av. Otra 123',
            distrito_domicilio='Miraflores',
            provincia_domicilio='Lima',
            departamento_domicilio='Lima',
            estado_empleado='activo',
        )
        _make_doc(other_empleado, tipo='dni', nombre='DNI del otro', version='1.0')

        # Request the OTHER employee's documents — must return 0 results
        url = f'/api/v1/rrhh/documentos-digitales/?empleado={other_empleado.empleado_id}'
        response = onboarding_client.get(url)
        assert response.status_code == 200

        raw = response.data
        data = raw.get('data') or raw.get('results') or []
        if isinstance(data, dict):
            data = data.get('results', [])

        assert len(data) == 0, (
            f'Employee should not see other employee documents, but got {len(data)} records'
        )

    def test_es_version_actual_filter(self, onboarding_client):
        """?es_version_actual=true excludes old versions and includes current ones."""
        onboarding = onboarding_client._onboarding
        empleado = onboarding.empleado

        # Create current and old version — use distinct version strings to avoid unique_together clash
        _make_doc(empleado, tipo='dni', nombre='DNI v2', es_version_actual=True, version='2.0')
        _make_doc(empleado, tipo='dni', nombre='DNI v1', es_version_actual=False, version='1.0')

        url = (
            f'/api/v1/rrhh/documentos-digitales/'
            f'?empleado={empleado.empleado_id}&es_version_actual=true'
        )
        response = onboarding_client.get(url)
        assert response.status_code == 200

        raw = response.data
        data = raw.get('data') or raw.get('results') or []
        if isinstance(data, dict):
            data = data.get('results', [])

        names = [d.get('nombre_documento') for d in data]
        assert 'DNI v1' not in names, 'Old version should be excluded by es_version_actual=true filter'
        assert 'DNI v2' in names, 'Current version should be included by es_version_actual=true filter'
