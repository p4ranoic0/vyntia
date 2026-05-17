"""Smoke tests for B.14 ExitInterview + HandoverChecklist + SystemsOffboarding API."""
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
        numero_documento='94949494', tipo_documento='DNI',
        nombres_empleado='Tania', apellido_paterno='Mejía',
        apellido_materno='Soto', fecha_nacimiento=date(1988, 4, 4),
        estado_empleado='activo',
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='TI', siglas_area='TI', estado_area='activa',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14APIEX-001', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=400),
        salario_bruto=Decimal('3500.00'), cargo='Dev', status='ACTIVO',
    )


@pytest.fixture
def termination(contract, employee):
    return Termination.objects.create(
        contract=contract, employee=employee,
        regimen='728', causal='renuncia',
        fecha_cese=date.today(),
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b14apiex', email='hr_b14apiex@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='ExitB14',
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
        'exit-interviews',
        'handover-checklists',
        'handover-items',
        'systems-offboardings',
    ])
    def test_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/onboarding/{path}/')
        assert r.status_code in (401, 403)

    def test_authenticated_list(self, auth_client):
        r = auth_client.get('/api/v1/onboarding/exit-interviews/')
        assert r.status_code == 200
        r = auth_client.get('/api/v1/onboarding/handover-checklists/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestScaffold:
    def test_scaffold_endpoint(self, auth_client, termination):
        r = auth_client.post(
            '/api/v1/onboarding/exit-flow-scaffold/',
            {'termination': str(termination.id)},
            format='json',
        )
        assert r.status_code == 201, r.content
        body = r.json()
        assert 'interview' in body['data']
        assert 'checklist' in body['data']
        assert 'systems_offboarding' in body['data']

    def test_scaffold_unknown_termination_returns_404(self, auth_client):
        import uuid
        r = auth_client.post(
            '/api/v1/onboarding/exit-flow-scaffold/',
            {'termination': str(uuid.uuid4())},
            format='json',
        )
        assert r.status_code == 404
