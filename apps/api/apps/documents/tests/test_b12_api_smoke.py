"""Smoke tests for B.12 documents API — DigitalDossier + sections + access logs."""
from datetime import date

import pytest
from django.core.files.base import ContentFile
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.documents.models import (
    DigitalDocument,
    DigitalDossier,
    DocumentAccessLog,
)
from apps.documents.services import access_service, dossier_service
from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='12121212', tipo_documento='DNI',
        nombres_empleado='Luis', apellido_paterno='Mora',
        apellido_materno='Vega', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b12_api', email='hr_b12_api@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='B12',
        tipo_usuario='rrhh', nivel_acceso='total',
    )
    role, _ = Role.objects.get_or_create(
        nombre_rol='Administrador RRHH',
        defaults={
            'estado_rol': 'activo', 'nivel_jerarquico': 2,
            'es_rol_sistema': True,
        },
    )
    UserRole.objects.get_or_create(
        usuario=user, rol=role,
        defaults={'estado_asignacion': 'activo'},
    )
    return user


@pytest.fixture
def auth_client(hr_user):
    refresh = RefreshToken.for_user(hr_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token!s}')
    return client


@pytest.mark.django_db
class TestRouting:
    @pytest.mark.parametrize('path', [
        'digital-dossiers', 'dossier-sections', 'document-access-logs',
    ])
    def test_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/documents/{path}/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists(self, auth_client):
        r = auth_client.get('/api/v1/documents/digital-dossiers/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestDossierActions:
    def test_create_provisions_15_sections(self, auth_client, employee):
        r = auth_client.post(
            '/api/v1/documents/digital-dossiers/',
            {'employee': str(employee.id)}, format='json',
        )
        assert r.status_code in (200, 201), r.content
        body = r.json().get('data', r.json())
        assert len(body['sections']) == 15

    def test_create_404_missing_employee(self, auth_client):
        r = auth_client.post(
            '/api/v1/documents/digital-dossiers/',
            {'employee': '00000000-0000-0000-0000-000000000000'},
            format='json',
        )
        assert r.status_code == 404

    def test_build_is_idempotent(self, auth_client, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        r = auth_client.post(
            f'/api/v1/documents/digital-dossiers/{dossier.id}/build/',
        )
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert len(body['sections']) == 15

    def test_consolidated_pdf_download(self, auth_client, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        r = auth_client.get(
            f'/api/v1/documents/digital-dossiers/{dossier.id}/consolidated-pdf/',
        )
        assert r.status_code == 200
        assert r['Content-Type'].startswith('application/pdf')
        assert r['Content-Disposition'].startswith('attachment;')


@pytest.mark.django_db
class TestAccessLogs:
    def test_logs_listable(self, auth_client, employee):
        # Generate a log via service
        content = ContentFile(b'test', name='x.pdf')
        doc = DigitalDocument(
            empleado=employee, tipo_documento='dni',
            categoria='personal', nombre_documento='X',
            estado_documento='vigente', es_version_actual=True, version='1.0',
            nombre_archivo_original='x.pdf', formato_archivo='pdf',
            tamano_archivo=4, nivel_acceso='restringido', permission_level=3,
        )
        doc.archivo.save('x.pdf', content, save=False)
        doc.save()
        access_service.log_access(document=doc, user=None, action='view')
        r = auth_client.get(f'/api/v1/documents/document-access-logs/?document={doc.id}')
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        # Body may be either {'results': [...]} or just a list, depending on pagination
        if isinstance(body, dict):
            results = body.get('results', [])
        else:
            results = body
        assert isinstance(results, list)
        assert len(results) >= 1
