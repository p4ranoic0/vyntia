"""Smoke tests for B.10 contracts API — TRegistroDeclaration."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.contracts.models import Contract, TRegistroDeclaration
from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='RRHH', siglas_area='RH', estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='10101010', tipo_documento='DNI',
        nombres_empleado='Ana', apellido_paterno='Lopez',
        apellido_materno='Vega', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B10-API-001',
        tipo_documento='LEY_728_FIJO',
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=365),
        salario_bruto=Decimal('3000.00'),
        cargo='Analista', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b10_api', email='hr_b10_api@test.local',
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


def _make_declaration_payload(contract, employee):
    return {
        'contract': str(contract.id),
        'employee': str(employee.id),
        'employer_ruc': '20123456789',
        'employer_razon_social': 'ACME SAC',
        'worker_doc_type': '01',
        'worker_doc_number': '10101010',
        'worker_apellido_paterno': 'Lopez',
        'worker_apellido_materno': 'Vega',
        'worker_nombres': 'Ana',
        'worker_birth_date': '1990-01-01',
        'worker_gender': 'F',
        'worker_nationality_code': '604',
        'contract_start_date': str(date.today()),
        'contract_end_date': str(date.today() + timedelta(days=365)),
        'work_modality_code': 'SBT',
        'regimen_laboral_code': '728',
        'regimen_pensionario': 'snp',
        'regimen_salud': 'essalud',
        'remuneracion_basica': '3000.00',
        'jornada_horas_semanales': 48,
    }


@pytest.mark.django_db
class TestRouting:
    def test_endpoint_requires_auth(self):
        client = APIClient()
        r = client.get('/api/v1/t-registro-declarations/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists_declarations(self, auth_client):
        r = auth_client.get('/api/v1/t-registro-declarations/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestCreate:
    def test_create_alta(self, auth_client, contract, employee):
        r = auth_client.post(
            '/api/v1/t-registro-declarations/',
            _make_declaration_payload(contract, employee), format='json',
        )
        assert r.status_code in (200, 201), r.content
        data = r.json()
        # Backend wraps with APIResponse
        body = data.get('data', data)
        assert body['status'] == 'draft'
        assert body['declaration_type'] == 'alta'


@pytest.mark.django_db
class TestCustomActions:
    def _create(self, auth_client, contract, employee):
        r = auth_client.post(
            '/api/v1/t-registro-declarations/',
            _make_declaration_payload(contract, employee), format='json',
        )
        assert r.status_code in (200, 201)
        body = r.json().get('data', r.json())
        return body['id']

    def test_generate_anexo3_returns_txt_in_payload(
        self, auth_client, contract, employee,
    ):
        dec_id = self._create(auth_client, contract, employee)
        r = auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/generate-anexo3/',
        )
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert body['anexo3_txt'].startswith('H|TRREG|')

    def test_validate_pvs_clean_marks_validated(
        self, auth_client, contract, employee,
    ):
        dec_id = self._create(auth_client, contract, employee)
        r = auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/validate-pvs/',
        )
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert body['status'] == 'validated'

    def test_submit_after_validate(
        self, auth_client, contract, employee,
    ):
        dec_id = self._create(auth_client, contract, employee)
        auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/validate-pvs/',
        )
        r = auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/submit/',
            {'reference': 'REF-API'}, format='json',
        )
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert body['status'] == 'submitted'
        assert body['sunat_reference'] == 'REF-API'

    def test_submit_with_errors_400(self, auth_client, contract, employee):
        payload = _make_declaration_payload(contract, employee)
        payload['employer_ruc'] = '123'  # Invalid
        r = auth_client.post(
            '/api/v1/t-registro-declarations/', payload, format='json',
        )
        body = r.json().get('data', r.json())
        dec_id = body['id']
        r = auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/submit/',
        )
        assert r.status_code == 400

    def test_mark_rejected_requires_reason(self, auth_client, contract, employee):
        dec_id = self._create(auth_client, contract, employee)
        # Manually push to submitted via service
        from apps.contracts.services.tregistro_service import submit_declaration
        submit_declaration(dec_id, user=auth_client.handler._force_user, reference='') if False else None
        # Simpler: drive via API
        auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/validate-pvs/',
        )
        auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/submit/',
        )
        r = auth_client.post(
            f'/api/v1/t-registro-declarations/{dec_id}/mark-rejected/',
            {'reason': ''}, format='json',
        )
        assert r.status_code == 400

    def test_anexo3_txt_download(self, auth_client, contract, employee):
        dec_id = self._create(auth_client, contract, employee)
        r = auth_client.get(
            f'/api/v1/t-registro-declarations/{dec_id}/anexo3-txt/',
        )
        assert r.status_code == 200
        assert r['Content-Type'].startswith('text/plain')
        assert r['Content-Disposition'].startswith('attachment;')
        assert b'TRREG' in r.content
