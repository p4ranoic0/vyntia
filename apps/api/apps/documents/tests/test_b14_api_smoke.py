"""Smoke tests for B.14 WorkCertificate API."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.contracts.models import Contract, Termination
from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='93939393', tipo_documento='DNI',
        nombres_empleado='Pamela', apellido_paterno='Lozano',
        apellido_materno='Vega', fecha_nacimiento=date(1989, 3, 3),
        estado_empleado='activo',
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='LEG', siglas_area='LG', estado_area='activa',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14APIWC-001', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=400),
        salario_bruto=Decimal('3000.00'), cargo='Asistente', status='ACTIVO',
    )


@pytest.fixture
def termination(contract, employee):
    return Termination.objects.create(
        contract=contract, employee=employee,
        regimen='728', causal='renuncia',
        fecha_cese=date.today(),
        motivo='Renuncia voluntaria',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b14apiwc', email='hr_b14apiwc@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='WCB14',
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
    def test_requires_auth(self):
        client = APIClient()
        r = client.get('/api/v1/documents/work-certificates/')
        assert r.status_code in (401, 403)

    def test_authenticated_list(self, auth_client):
        r = auth_client.get('/api/v1/documents/work-certificates/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestGenerate:
    def test_generate_action(self, auth_client, termination):
        r = auth_client.post(
            '/api/v1/documents/work-certificates/generate/',
            {'termination': str(termination.id)},
            format='json',
        )
        assert r.status_code == 201, r.content
        body = r.json()
        assert body['data']['numero_constancia'].startswith('CTR-')
        assert body['data']['cargo_snapshot'] == 'Asistente'

    def test_generate_unknown_termination_returns_404(self, auth_client):
        import uuid
        r = auth_client.post(
            '/api/v1/documents/work-certificates/generate/',
            {'termination': str(uuid.uuid4())},
            format='json',
        )
        assert r.status_code == 404
