"""Smoke tests for B.13 Displacement + LocationHistory API."""
from datetime import date, timedelta

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department, Displacement


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='91919191', tipo_documento='DNI',
        nombres_empleado='Rocío', apellido_paterno='Vera',
        apellido_materno='Sosa', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def origen(db):
    return Department.objects.create(
        nombre_unidad_organica='Origen', siglas_area='OR', estado_area='activa',
    )


@pytest.fixture
def destino(db):
    return Department.objects.create(
        nombre_unidad_organica='Destino', siglas_area='DE', estado_area='activa',
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b13_api', email='hr_b13_api@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='B13',
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
        'displacements', 'displacement-extensions', 'location-histories',
    ])
    def test_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/organization/{path}/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists(self, auth_client):
        r = auth_client.get('/api/v1/organization/displacements/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestDisplacementCRUDActions:
    def test_create_persists_kind(self, auth_client, employee, origen, destino):
        r = auth_client.post(
            '/api/v1/organization/displacements/',
            {
                'employee': str(employee.id),
                'kind': 'encargatura',
                'origen_department': str(origen.id),
                'destino_department': str(destino.id),
                'start_date': str(date.today()),
                'end_date': str(date.today() + timedelta(days=180)),
            },
            format='json',
        )
        assert r.status_code in (200, 201), r.content
        body = r.json().get('data', r.json())
        assert body['kind'] == 'encargatura'
        assert body['status'] == 'draft'

    def test_submit_action(self, auth_client, employee, origen, destino):
        d = Displacement.objects.create(
            employee=employee, kind='rotacion',
            origen_department=origen, destino_department=destino,
            start_date=date.today(),
        )
        r = auth_client.post(f'/api/v1/organization/displacements/{d.id}/submit/')
        assert r.status_code == 200
        d.refresh_from_db()
        assert d.status == 'pending_supervisor'

    def test_full_approval_chain_via_api(self, auth_client, employee, origen, destino):
        d = Displacement.objects.create(
            employee=employee, kind='destaque',
            origen_department=origen, destino_department=destino,
            start_date=date.today(),
        )
        auth_client.post(f'/api/v1/organization/displacements/{d.id}/submit/')
        auth_client.post(f'/api/v1/organization/displacements/{d.id}/approve-supervisor/')
        auth_client.post(f'/api/v1/organization/displacements/{d.id}/approve-hr/')
        r = auth_client.post(f'/api/v1/organization/displacements/{d.id}/approve-titular/')
        assert r.status_code == 200
        d.refresh_from_db()
        assert d.status == 'approved'

    def test_cancel_requires_reason(self, auth_client, employee, origen, destino):
        d = Displacement.objects.create(
            employee=employee, kind='rotacion',
            origen_department=origen, destino_department=destino,
            start_date=date.today(),
        )
        r = auth_client.post(
            f'/api/v1/organization/displacements/{d.id}/cancel/',
            {'reason': ''}, format='json',
        )
        assert r.status_code == 400
        r = auth_client.post(
            f'/api/v1/organization/displacements/{d.id}/cancel/',
            {'reason': 'Cambio de plan'}, format='json',
        )
        assert r.status_code == 200

    def test_extend_only_active(self, auth_client, employee, origen, destino):
        d = Displacement.objects.create(
            employee=employee, kind='encargatura',
            origen_department=origen, destino_department=destino,
            start_date=date.today(), end_date=date.today() + timedelta(days=90),
        )
        # Drive to active via API
        for path in ('submit', 'approve-supervisor', 'approve-hr',
                     'approve-titular', 'activate'):
            auth_client.post(f'/api/v1/organization/displacements/{d.id}/{path}/')
        r = auth_client.post(
            f'/api/v1/organization/displacements/{d.id}/extend/',
            {
                'new_end_date': str(date.today() + timedelta(days=200)),
                'reason': 'Prórroga necesaria',
            },
            format='json',
        )
        assert r.status_code in (200, 201)

    def test_resolution_pdf_download(self, auth_client, employee, origen, destino):
        d = Displacement.objects.create(
            employee=employee, kind='comision',
            origen_department=origen, destino_department=destino,
            start_date=date.today(),
        )
        r = auth_client.get(
            f'/api/v1/organization/displacements/{d.id}/resolution-pdf/',
        )
        assert r.status_code == 200
        assert r['Content-Type'].startswith('application/pdf')


@pytest.mark.django_db
class TestLocationHistory:
    def test_create(self, auth_client, employee, origen, destino):
        r = auth_client.post(
            '/api/v1/organization/location-histories/',
            {
                'empleado': str(employee.id),
                'area_origen': str(origen.id),
                'area_destino': str(destino.id),
                'tipo_movimiento': 'rotacion',
                'fecha_inicio': str(date.today()),
            },
            format='json',
        )
        assert r.status_code in (200, 201), r.content
