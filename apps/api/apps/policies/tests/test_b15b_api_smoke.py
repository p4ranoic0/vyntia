"""Smoke tests for B.15b strategic/workforce/compliance API."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department, Position
from apps.policies.models import (
    ComplianceMatrix,
    ComplianceObligation,
    HRStrategicPlan,
    StrategicObjective,
    KPI,
    WorkforcePlan,
    SuccessionPlan,
    KeyPosition,
)


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b15b', email='hr_b15b@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='B15b',
        tipo_usuario='rrhh', nivel_acceso='total',
    )
    role, _ = Role.objects.get_or_create(
        nombre_rol='Administrador RRHH',
        defaults={'estado_rol': 'activo', 'nivel_jerarquico': 2, 'es_rol_sistema': True},
    )
    UserRole.objects.get_or_create(
        usuario=user, rol=role, defaults={'estado_asignacion': 'activo'},
    )
    return user


@pytest.fixture
def auth_client(hr_user):
    refresh = RefreshToken.for_user(hr_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token!s}')
    return client


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Operaciones', siglas_area='OPS', estado_area='activa',
    )


@pytest.fixture
def position(db, department):
    return Position.objects.create(
        code='POS-API', name='API Tester', department=department,
    )


@pytest.mark.django_db
class TestRoutingAuth:
    @pytest.mark.parametrize('path', [
        'strategic-plans',
        'strategic-objectives',
        'kpis',
        'workforce-plans',
        'headcount-projections',
        'succession-plans',
        'key-positions',
        'successor-candidates',
        'compliance-matrices',
        'compliance-obligations',
        'evidences',
    ])
    def test_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/{path}/')
        assert r.status_code in (401, 403)

    @pytest.mark.parametrize('path', [
        'strategic-plans',
        'workforce-plans',
        'succession-plans',
        'compliance-matrices',
        'kpis',
    ])
    def test_authenticated_list_returns_200(self, auth_client, path):
        r = auth_client.get(f'/api/v1/{path}/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestStrategicPlanAPI:
    def test_create_plan_and_activate(self, auth_client, hr_user):
        r = auth_client.post(
            '/api/v1/strategic-plans/',
            {
                'name': 'Plan API', 'fiscal_year': 2026,
                'period_start': '2026-01-01', 'period_end': '2026-12-31',
                'owner_user': str(hr_user.pk),
            }, format='json',
        )
        assert r.status_code in (200, 201), r.content
        body = r.json().get('data') or r.json()
        plan_id = body['id']

        r = auth_client.post(f'/api/v1/strategic-plans/{plan_id}/activate/')
        assert r.status_code == 200, r.content

    def test_progress_action(self, auth_client, hr_user):
        plan = HRStrategicPlan.objects.create(
            name='Plan-progress', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=hr_user,
        )
        obj = StrategicObjective.objects.create(
            plan=plan, code='OE-X', title='X', weight=Decimal('100'),
        )
        KPI.objects.create(
            objective=obj, name='K', target=Decimal('100'), actual=Decimal('40'),
        )
        r = auth_client.get(f'/api/v1/strategic-plans/{plan.pk}/progress/')
        assert r.status_code == 200, r.content
        body = r.json().get('data') or r.json()
        assert 'overall_pct' in body

    def test_kpi_update_actual(self, auth_client, hr_user):
        plan = HRStrategicPlan.objects.create(
            name='Plan-K', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=hr_user,
        )
        obj = StrategicObjective.objects.create(
            plan=plan, code='OE-K', title='X', weight=Decimal('100'),
        )
        kpi = KPI.objects.create(
            objective=obj, name='K', target=Decimal('100'),
        )
        r = auth_client.post(
            f'/api/v1/kpis/{kpi.pk}/update-actual/',
            {'actual': '85'}, format='json',
        )
        assert r.status_code == 200, r.content
        kpi.refresh_from_db()
        assert kpi.actual == Decimal('85')


@pytest.mark.django_db
class TestWorkforceAPI:
    def test_create_workforce_plan(self, auth_client, hr_user):
        r = auth_client.post(
            '/api/v1/workforce-plans/',
            {
                'name': 'Dotación API', 'fiscal_year': 2026,
                'period_start': '2026-01-01', 'period_end': '2026-12-31',
                'owner_user': str(hr_user.pk),
            }, format='json',
        )
        assert r.status_code in (200, 201), r.content

    def test_create_succession_chain(self, auth_client, hr_user, position):
        sp = SuccessionPlan.objects.create(
            name='Suc API', fiscal_year=2026, owner_user=hr_user,
        )
        r = auth_client.post(
            '/api/v1/key-positions/',
            {
                'plan': str(sp.pk),
                'position': str(position.pk),
                'criticality': 'alta',
            }, format='json',
        )
        assert r.status_code in (200, 201), r.content


@pytest.mark.django_db
class TestComplianceAPI:
    def test_create_matrix(self, auth_client, hr_user):
        r = auth_client.post(
            '/api/v1/compliance-matrices/',
            {
                'name': 'Matriz API', 'fiscal_year': 2026,
                'owner_user': str(hr_user.pk),
            }, format='json',
        )
        assert r.status_code in (200, 201), r.content

    def test_mark_completed_action(self, auth_client, hr_user):
        m = ComplianceMatrix.objects.create(
            name='M', fiscal_year=2026, owner_user=hr_user,
        )
        o = ComplianceObligation.objects.create(
            matrix=m, code='SUNAT-API', title='PDT 601',
            source='sunat', frequency='mensual',
            next_due_date=date.today() - timedelta(days=2),
        )
        r = auth_client.post(
            f'/api/v1/compliance-obligations/{o.pk}/mark-completed/',
            {}, format='json',
        )
        assert r.status_code == 200, r.content
        o.refresh_from_db()
        assert o.last_completed_at is not None

    def test_alertas_collection(self, auth_client, hr_user):
        m = ComplianceMatrix.objects.create(
            name='M-alert', fiscal_year=2026, owner_user=hr_user,
        )
        ComplianceObligation.objects.create(
            matrix=m, code='OD-1', title='Vencido',
            source='sunat', frequency='mensual',
            next_due_date=date.today() - timedelta(days=10),
        )
        r = auth_client.get('/api/v1/compliance-obligations/alertas/?days_ahead=30')
        assert r.status_code == 200, r.content
        body = r.json().get('data') or r.json()
        assert 'overdue' in body
        assert 'due_soon' in body
        assert any(item['code'] == 'OD-1' for item in body['overdue'])

    def test_mark_overdue_action(self, auth_client, hr_user):
        m = ComplianceMatrix.objects.create(
            name='M-mo', fiscal_year=2026, owner_user=hr_user,
        )
        o = ComplianceObligation.objects.create(
            matrix=m, code='OD-2', title='V',
            source='sunat', frequency='mensual',
            next_due_date=date.today() - timedelta(days=5),
        )
        r = auth_client.post('/api/v1/compliance-obligations/mark-overdue/')
        assert r.status_code == 200, r.content
        o.refresh_from_db()
        assert o.status == 'vencido'
