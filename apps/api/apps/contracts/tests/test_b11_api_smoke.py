"""Smoke tests for B.11 ProbationPeriod API endpoints."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.contracts.models import Contract, ProbationPeriod
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
        numero_documento='44444444', tipo_documento='DNI',
        nombres_empleado='Tomás', apellido_paterno='Lara',
        apellido_materno='Bravo', fecha_nacimiento=date(1991, 11, 11),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B11api-001', tipo_documento='LEY_728_FIJO',
        fecha_inicio=date.today(), fecha_fin=date.today() + timedelta(days=365),
        salario_bruto=Decimal('3000.00'), cargo='Analista', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b11_pap', email='hr_b11_pap@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='B11',
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
    def test_endpoint_requires_auth(self):
        client = APIClient()
        r = client.get('/api/v1/probation-periods/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists(self, auth_client):
        r = auth_client.get('/api/v1/probation-periods/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestLifecycleActions:
    def _create(self, auth_client, contract):
        r = auth_client.post(
            '/api/v1/probation-periods/',
            {'contract': str(contract.id), 'regimen': '728_comun',
             'start_date': str(date.today())},
            format='json',
        )
        assert r.status_code in (200, 201), r.content
        body = r.json().get('data', r.json())
        return body['id']

    def test_create_persists_regimen(self, auth_client, contract):
        period_id = self._create(auth_client, contract)
        p = ProbationPeriod.objects.get(pk=period_id)
        assert p.regimen == '728_comun'
        assert p.plazo_dias == 90

    def test_evaluate_promotes(self, auth_client, contract):
        period_id = self._create(auth_client, contract)
        r = auth_client.post(
            f'/api/v1/probation-periods/{period_id}/evaluate/',
            {'score': 85}, format='json',
        )
        assert r.status_code == 200
        p = ProbationPeriod.objects.get(pk=period_id)
        assert p.status == 'evaluated'
        assert p.evaluation_score == 85

    def test_ratify_only_from_evaluated(self, auth_client, contract):
        period_id = self._create(auth_client, contract)
        r = auth_client.post(f'/api/v1/probation-periods/{period_id}/ratify/')
        assert r.status_code == 400
        auth_client.post(
            f'/api/v1/probation-periods/{period_id}/evaluate/',
            {'score': 85}, format='json',
        )
        r = auth_client.post(f'/api/v1/probation-periods/{period_id}/ratify/')
        assert r.status_code == 200
        p = ProbationPeriod.objects.get(pk=period_id)
        assert p.status == 'ratified'

    def test_not_renew_requires_reason(self, auth_client, contract):
        period_id = self._create(auth_client, contract)
        auth_client.post(
            f'/api/v1/probation-periods/{period_id}/evaluate/',
            {'score': 40}, format='json',
        )
        r = auth_client.post(
            f'/api/v1/probation-periods/{period_id}/not-renew/',
            {'reason': ''}, format='json',
        )
        assert r.status_code == 400
        r = auth_client.post(
            f'/api/v1/probation-periods/{period_id}/not-renew/',
            {'reason': 'Bajo desempeño'}, format='json',
        )
        assert r.status_code == 200


@pytest.mark.django_db
class TestAlertasAction:
    def test_alertas_collection_endpoint(self, auth_client, contract):
        # Create a period inside the 15d window
        ProbationPeriod.objects.create(
            contract=contract, regimen='728_comun',
            start_date=date.today() - timedelta(days=80),
        )
        r = auth_client.get('/api/v1/probation-periods/alertas/')
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert 'within_30_days' in body
        assert 'within_15_days' in body
        assert len(body['within_30_days']) >= 1
