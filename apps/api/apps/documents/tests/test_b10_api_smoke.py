"""Smoke tests for B.10 documents API — signatures + hiring-bundles."""
from datetime import date

import pytest
from django.core.files.base import ContentFile
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.documents.models import (
    DigitalDocument,
    DocumentSignature,
    HiringDocumentBundle,
)
from apps.documents.services import bundle_service, signature_service
from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='22334455', tipo_documento='DNI',
        nombres_empleado='Carla', apellido_paterno='Ramos',
        apellido_materno='Cruz', fecha_nacimiento=date(1995, 7, 7),
        estado_empleado='activo',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_doc_b10', email='hr_doc_b10@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='B10',
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


@pytest.fixture
def document(employee):
    content = ContentFile(b'%PDF-1.4 test', name='rit.pdf')
    doc = DigitalDocument(
        empleado=employee, tipo_documento='reglamento_interno',
        categoria='normativa', nombre_documento='RIT 2026',
        estado_documento='vigente', es_version_actual=True, version='1.0',
        nombre_archivo_original='rit.pdf', formato_archivo='pdf',
        tamano_archivo=12, nivel_acceso='restringido',
    )
    doc.archivo.save('rit.pdf', content, save=False)
    doc.save()
    return doc


@pytest.fixture
def signature(document):
    return signature_service.request_signature(
        document=document,
        signer_name='Carla',
        signer_doc_number='22334455',
        kind='typed',
    )


@pytest.mark.django_db
class TestSignatureRouting:
    @pytest.mark.parametrize('path', [
        'signatures', 'hiring-bundles', 'hiring-bundle-items',
    ])
    def test_endpoint_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/documents/{path}/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists_signatures(self, auth_client):
        r = auth_client.get('/api/v1/documents/signatures/')
        assert r.status_code == 200

    def test_authenticated_lists_hiring_bundles(self, auth_client):
        r = auth_client.get('/api/v1/documents/hiring-bundles/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestSignatureCustomActions:
    def test_capture_typed_signature(self, auth_client, signature):
        r = auth_client.post(
            f'/api/v1/documents/signatures/{signature.id}/capture/',
            {'typed_name': 'Carla Ramos Cruz'}, format='json',
        )
        assert r.status_code == 200
        signature.refresh_from_db()
        assert signature.status == 'signed'

    def test_capture_canvas_requires_payload(self, auth_client, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='X',
            kind='canvas',
        )
        r = auth_client.post(
            f'/api/v1/documents/signatures/{sig.id}/capture/', {}, format='json',
        )
        assert r.status_code == 400

    def test_reject_signature(self, auth_client, signature):
        r = auth_client.post(
            f'/api/v1/documents/signatures/{signature.id}/reject/',
            {'reason': 'No conforme'}, format='json',
        )
        assert r.status_code == 200
        signature.refresh_from_db()
        assert signature.status == 'rejected'

    def test_expire_overdue_collection_action(self, auth_client):
        r = auth_client.post(
            '/api/v1/documents/signatures/expire-overdue/',
        )
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert 'expired_count' in body


@pytest.mark.django_db
class TestHiringBundleCRUDActions:
    def test_create_bundle_scaffolds_items(self, auth_client, employee):
        r = auth_client.post(
            '/api/v1/documents/hiring-bundles/',
            {
                'employee': str(employee.id),
                'item_kinds': ['contrato', 'rit'],
                'title': 'Bundle B10 Smoke',
            },
            format='json',
        )
        assert r.status_code in (200, 201), r.content
        body = r.json().get('data', r.json())
        assert len(body['items']) == 2

    def test_create_default_six_items(self, auth_client, employee):
        r = auth_client.post(
            '/api/v1/documents/hiring-bundles/',
            {'employee': str(employee.id)}, format='json',
        )
        body = r.json().get('data', r.json())
        assert len(body['items']) == 6

    def test_send_requires_documents(self, auth_client, employee):
        r = auth_client.post(
            '/api/v1/documents/hiring-bundles/',
            {'employee': str(employee.id), 'item_kinds': ['contrato']},
            format='json',
        )
        bundle_id = r.json().get('data', r.json())['id']
        r = auth_client.post(
            f'/api/v1/documents/hiring-bundles/{bundle_id}/send/',
        )
        assert r.status_code == 400

    def test_acknowledge_when_incomplete_400(self, auth_client, employee, document):
        r = auth_client.post(
            '/api/v1/documents/hiring-bundles/',
            {'employee': str(employee.id), 'item_kinds': ['contrato']},
            format='json',
        )
        bundle_id = r.json().get('data', r.json())['id']
        bundle = HiringDocumentBundle.objects.get(pk=bundle_id)
        item = bundle.items.first()
        # Attach doc and send first
        r = auth_client.post(
            f'/api/v1/documents/hiring-bundle-items/{item.id}/attach-document/',
            {'document_id': str(document.id)}, format='json',
        )
        assert r.status_code == 200
        auth_client.post(f'/api/v1/documents/hiring-bundles/{bundle_id}/send/')
        r = auth_client.post(
            f'/api/v1/documents/hiring-bundles/{bundle_id}/acknowledge/',
        )
        assert r.status_code == 400


@pytest.mark.django_db
class TestHiringBundleItemActions:
    def test_attach_document(self, auth_client, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['rit'],
        )
        item = bundle.items.first()
        r = auth_client.post(
            f'/api/v1/documents/hiring-bundle-items/{item.id}/attach-document/',
            {'document_id': str(document.id)}, format='json',
        )
        assert r.status_code == 200
        item.refresh_from_db()
        assert item.document_id == document.id

    def test_attach_document_404_on_missing(self, auth_client, employee):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['rit'],
        )
        item = bundle.items.first()
        r = auth_client.post(
            f'/api/v1/documents/hiring-bundle-items/{item.id}/attach-document/',
            {'document_id': '00000000-0000-0000-0000-000000000000'},
            format='json',
        )
        assert r.status_code == 404

    def test_attach_acuse(self, auth_client, employee, document, signature):
        # Sign the signature first
        signature_service.capture_signature(
            signature_id=signature.id, typed_name='Carla',
        )
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['rit'],
        )
        item = bundle.items.first()
        r = auth_client.post(
            f'/api/v1/documents/hiring-bundle-items/{item.id}/attach-acuse/',
            {'signature_id': str(signature.id)}, format='json',
        )
        assert r.status_code == 200
        item.refresh_from_db()
        assert item.signature_id == signature.id
