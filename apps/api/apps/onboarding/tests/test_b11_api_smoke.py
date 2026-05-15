"""Smoke tests for B.11 Induction API endpoints."""
from datetime import date

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from apps.onboarding.models import InductionPlan
from apps.onboarding.services import induction_service


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='55555555', tipo_documento='DNI',
        nombres_empleado='Rosa', apellido_paterno='Vega',
        apellido_materno='Pino', fecha_nacimiento=date(1993, 9, 9),
        estado_empleado='activo',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b11_api', email='hr_b11_api@test.local',
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
    @pytest.mark.parametrize('path', [
        'induction-plans', 'induction-tasks', 'induction-materials',
    ])
    def test_endpoint_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/onboarding/{path}/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists_plans(self, auth_client):
        r = auth_client.get('/api/v1/onboarding/induction-plans/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestPlanCRUDActions:
    def test_create_scaffolds_default_tasks(self, auth_client, employee):
        r = auth_client.post(
            '/api/v1/onboarding/induction-plans/',
            {'employee': str(employee.id), 'kind': 'general',
             'title': 'Plan smoke'},
            format='json',
        )
        assert r.status_code in (200, 201), r.content
        body = r.json().get('data', r.json())
        assert len(body['tasks']) > 0

    def test_start_complete_certify_lifecycle(self, auth_client, employee):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=None,
        )
        r = auth_client.post(f'/api/v1/onboarding/induction-plans/{plan.id}/start/')
        assert r.status_code == 200
        r = auth_client.post(f'/api/v1/onboarding/induction-plans/{plan.id}/complete/')
        assert r.status_code == 200
        r = auth_client.post(f'/api/v1/onboarding/induction-plans/{plan.id}/certify/')
        assert r.status_code == 200
        plan.refresh_from_db()
        assert plan.status == 'certified'

    def test_record_evaluation(self, auth_client, employee):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=None,
        )
        r = auth_client.post(
            f'/api/v1/onboarding/induction-plans/{plan.id}/record-evaluation/',
            {'score': 85, 'comments': 'Excelente'}, format='json',
        )
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert body['evaluation']['score'] == 85
        assert body['evaluation']['passed'] is True

    def test_assign_mentor(self, auth_client, employee, hr_user):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=None,
        )
        r = auth_client.post(
            f'/api/v1/onboarding/induction-plans/{plan.id}/assign-mentor/',
            {'mentor': str(hr_user.id)}, format='json',
        )
        assert r.status_code == 200

    def test_assign_mentor_404_on_missing(self, auth_client, employee):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=None,
        )
        r = auth_client.post(
            f'/api/v1/onboarding/induction-plans/{plan.id}/assign-mentor/',
            {'mentor': '00000000-0000-0000-0000-000000000000'}, format='json',
        )
        assert r.status_code == 404


@pytest.mark.django_db
class TestTaskActions:
    def test_mark_done(self, auth_client, employee):
        plan = induction_service.build_plan_for_employee(
            employee=employee, kind='general', created_by=None,
        )
        task = plan.tasks.first()
        r = auth_client.post(
            f'/api/v1/onboarding/induction-tasks/{task.id}/mark-done/',
        )
        assert r.status_code == 200
        body = r.json().get('data', r.json())
        assert body['is_done'] is True
