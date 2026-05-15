"""Smoke tests for B.12 employees API — WorkExperience + SwornDeclaration + JobHistory."""
from datetime import date

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='13131313', tipo_documento='DNI',
        nombres_empleado='Ana', apellido_paterno='Ríos',
        apellido_materno='Pino', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b12_emp_api', email='hr_b12_emp_api@test.local',
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
        'work-experiences', 'sworn-declarations', 'job-histories',
    ])
    def test_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/{path}/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists(self, auth_client):
        r = auth_client.get('/api/v1/work-experiences/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestWorkExperienceCRUD:
    def test_create(self, auth_client, employee):
        r = auth_client.post(
            '/api/v1/work-experiences/',
            {
                'employee': str(employee.id),
                'employer': 'ACME',
                'position_title': 'Analista',
                'sector': 'privado',
                'start_date': '2020-01-01',
                'end_date': '2022-12-31',
            },
            format='json',
        )
        assert r.status_code in (200, 201), r.content


@pytest.mark.django_db
class TestSwornDeclarationCRUD:
    def test_create_4_kinds(self, auth_client, employee):
        for kind in ('no_parentesco', 'no_incompatibilidad', 'intereses', 'impedimentos'):
            r = auth_client.post(
                '/api/v1/sworn-declarations/',
                {
                    'employee': str(employee.id),
                    'kind': kind,
                    'declared_at': str(date.today()),
                },
                format='json',
            )
            assert r.status_code in (200, 201), r.content


@pytest.mark.django_db
class TestJobHistoryCRUD:
    def test_create(self, auth_client, employee):
        r = auth_client.post(
            '/api/v1/job-histories/',
            {
                'employee': str(employee.id),
                'position_label': 'Analista',
                'department_label': 'RRHH',
                'start_date': '2024-01-01',
                'motive': 'hiring',
            },
            format='json',
        )
        assert r.status_code in (200, 201), r.content
