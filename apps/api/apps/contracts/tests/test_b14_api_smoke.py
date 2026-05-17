"""Smoke tests for B.14 Termination + SeveranceSettlement API."""
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
        numero_documento='92929292', tipo_documento='DNI',
        nombres_empleado='Renzo', apellido_paterno='Acosta',
        apellido_materno='Bravo', fecha_nacimiento=date(1991, 2, 2),
        estado_empleado='activo',
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Ops', siglas_area='OP', estado_area='activa',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14API-001', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=400),
        salario_bruto=Decimal('3500.00'), cargo='Analista', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b14api', email='hr_b14api@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='B14',
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
        'terminations',
        'severance-settlements',
    ])
    def test_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/{path}/')
        assert r.status_code in (401, 403)

    def test_lists_terminations_authenticated(self, auth_client):
        r = auth_client.get('/api/v1/terminations/')
        assert r.status_code == 200

    def test_lists_settlements_authenticated(self, auth_client):
        r = auth_client.get('/api/v1/severance-settlements/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestTerminationCreate:
    def test_initiate_via_endpoint(self, auth_client, contract):
        r = auth_client.post(
            '/api/v1/terminations/',
            {
                'contract': str(contract.id),
                'causal': 'renuncia',
                'regimen': '728',
                'fecha_cese': date.today().isoformat(),
                'motivo': 'Mejor oportunidad',
            },
            format='json',
        )
        assert r.status_code == 201, r.content
        body = r.json()
        assert body['data']['status'] == 'in_progress'
        assert body['data']['causal'] == 'renuncia'

    def test_alertas_48h_sla_returns_collection(self, auth_client):
        r = auth_client.get('/api/v1/terminations/alertas-48h-sla/')
        assert r.status_code == 200
        body = r.json()
        assert 'data' in body


@pytest.mark.django_db
class TestSeveranceActions:
    def test_compute_endpoint(self, auth_client, contract, employee):
        from apps.contracts.models import SeveranceSettlement

        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia', fecha_cese=date.today(),
        )
        s = SeveranceSettlement.objects.create(
            termination=t, sueldo_base=Decimal('3500.00'),
        )
        r = auth_client.post(
            f'/api/v1/severance-settlements/{s.id}/compute/',
            {}, format='json',
        )
        assert r.status_code == 200, r.content
        body = r.json()
        assert body['data']['status'] == 'computed'
        assert len(body['data']['lines']) == 4
