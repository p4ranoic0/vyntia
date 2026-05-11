"""Smoke tests for B.9 Selección API endpoints."""
from datetime import date
from decimal import Decimal

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employees.models import (
    Candidate,
    CandidateEvaluation,
    JobApplication,
    JobPosting,
    PersonnelRequisition,
    SelectionStage,
)
from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="T", nombre_unidad_organica="T", siglas_area="T",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(code="P", name="P", department=department)


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username="hr_b9", email="hr_b9@test.local",
        password="Test1234!",
        nombres_usuario="HR", apellidos_usuario="B9",
        tipo_usuario="rrhh", nivel_acceso="total",
    )
    role, _ = Role.objects.get_or_create(
        nombre_rol="Administrador RRHH",
        defaults={"estado_rol": "activo", "nivel_jerarquico": 2,
                  "es_rol_sistema": True},
    )
    UserRole.objects.get_or_create(
        usuario=user, rol=role,
        defaults={"estado_asignacion": "activo"},
    )
    return user


@pytest.fixture
def auth_client(hr_user):
    refresh = RefreshToken.for_user(hr_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token!s}")
    return client


@pytest.fixture
def requisition(department, position, hr_user):
    return PersonnelRequisition.objects.create(
        position=position, department=department,
        justification='replacement', requested_by=hr_user,
    )


@pytest.fixture
def approved_requisition(department, position, hr_user):
    req = PersonnelRequisition.objects.create(
        position=position, department=department,
        justification='replacement', requested_by=hr_user,
    )
    finance = User.objects.create(
        username='fin_b9', email='fin_b9@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )
    req.approve_hr(user=hr_user)
    req.approve_finance(user=finance)
    return req


@pytest.mark.django_db
class TestB9Routing:
    @pytest.mark.parametrize('path', [
        'candidates', 'personnel-requisitions', 'job-postings',
        'selection-stages', 'job-applications', 'candidate-evaluations',
        'merit-rankings',
    ])
    def test_endpoint_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/employees/{path}/')
        assert r.status_code in (401, 403)

    def test_authenticated_lists_candidates(self, auth_client):
        r = auth_client.get('/api/v1/candidates/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestB9Requisition:
    def test_submit_action(self, auth_client, requisition):
        url = f'/api/v1/personnel-requisitions/{requisition.id}/submit/'
        r = auth_client.post(url, {}, format='json')
        assert r.status_code == 200
        requisition.refresh_from_db()
        assert requisition.status == 'pending_approval'

    def test_approve_hr_then_finance_double_action(
        self, auth_client, requisition, hr_user,
    ):
        # First HR
        r1 = auth_client.post(
            f'/api/v1/personnel-requisitions/{requisition.id}/approve-hr/',
            {}, format='json',
        )
        assert r1.status_code == 200
        # Need a different user for finance — re-auth as a different RRHH user
        finance = User.objects.create_user(
            username='fin2_b9', email='fin2_b9@test.local',
            password='Test1234!',
            nombres_usuario='Fin', apellidos_usuario='B9',
            tipo_usuario='rrhh', nivel_acceso='total',
        )
        role, _ = Role.objects.get_or_create(
            nombre_rol='Administrador RRHH',
            defaults={'estado_rol': 'activo', 'nivel_jerarquico': 2,
                      'es_rol_sistema': True},
        )
        UserRole.objects.get_or_create(
            usuario=finance, rol=role,
            defaults={'estado_asignacion': 'activo'},
        )
        refresh = RefreshToken.for_user(finance)
        finance_client = APIClient()
        finance_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token!s}')
        r2 = finance_client.post(
            f'/api/v1/personnel-requisitions/{requisition.id}/approve-finance/',
            {}, format='json',
        )
        assert r2.status_code == 200
        requisition.refresh_from_db()
        assert requisition.status == 'approved'

    def test_reject_action_requires_reason(self, auth_client, requisition):
        url = f'/api/v1/personnel-requisitions/{requisition.id}/reject/'
        r = auth_client.post(url, {}, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestB9JobPosting:
    def test_publish_private_via_api(
        self, auth_client, approved_requisition, hr_user,
    ):
        posting = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='private',
        )
        url = f'/api/v1/job-postings/{posting.id}/publish/'
        r = auth_client.post(url, {}, format='json')
        assert r.status_code == 200
        posting.refresh_from_db()
        assert posting.status == 'published'

    def test_publish_servir_validates(self, auth_client, approved_requisition):
        posting = JobPosting.objects.create(
            requisition=approved_requisition, title='X',
            sector_mode='public_servir',
        )
        url = f'/api/v1/job-postings/{posting.id}/publish/'
        r = auth_client.post(url, {}, format='json')
        assert r.status_code == 400  # missing bases/plazos/transparency

    def test_compute_ranking_empty(self, auth_client, approved_requisition):
        posting = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='private',
        )
        url = f'/api/v1/job-postings/{posting.id}/compute-ranking/'
        r = auth_client.post(url, {}, format='json')
        assert r.status_code == 200


@pytest.mark.django_db
class TestB9Application:
    def test_create_application(self, auth_client, approved_requisition):
        posting = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='private',
        )
        cand = Candidate.objects.create(
            document_number='42424242',
            first_names='Z', last_names='Z', email='z@t.local',
        )
        r = auth_client.post(
            '/api/v1/job-applications/',
            {'posting': str(posting.id), 'candidate': str(cand.id)},
            format='json',
        )
        assert r.status_code == 201

    def test_advance_action(self, auth_client, approved_requisition):
        posting = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='private',
        )
        cand = Candidate.objects.create(
            document_number='42424241',
            first_names='Z', last_names='Z', email='zz@t.local',
        )
        app = JobApplication.objects.create(posting=posting, candidate=cand)
        url = f'/api/v1/job-applications/{app.id}/advance-to/'
        r = auth_client.post(url, {'new_status': 'reviewing'}, format='json')
        assert r.status_code == 200
        app.refresh_from_db()
        assert app.status == 'reviewing'

    def test_advance_illegal_returns_400(self, auth_client, approved_requisition):
        posting = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='private',
        )
        cand = Candidate.objects.create(
            document_number='42424240',
            first_names='Z', last_names='Z', email='zzz@t.local',
        )
        app = JobApplication.objects.create(posting=posting, candidate=cand)
        url = f'/api/v1/job-applications/{app.id}/advance-to/'
        r = auth_client.post(url, {'new_status': 'finalist'}, format='json')
        assert r.status_code == 400


@pytest.mark.django_db
class TestB9Evaluation:
    def test_create_evaluation_via_api(
        self, auth_client, approved_requisition, hr_user,
    ):
        posting = JobPosting.objects.create(
            requisition=approved_requisition, title='X', sector_mode='private',
        )
        stage = SelectionStage.objects.create(
            posting=posting, kind='knowledge', name='K',
            order=1, min_score=Decimal('14'), max_score=Decimal('20'),
        )
        cand = Candidate.objects.create(
            document_number='33333333',
            first_names='E', last_names='E', email='e@t.local',
        )
        app = JobApplication.objects.create(posting=posting, candidate=cand)
        r = auth_client.post(
            '/api/v1/candidate-evaluations/',
            {
                'application': str(app.id),
                'stage': str(stage.id),
                'score': '17.50',
                'notes': 'Buen desempeño',
            },
            format='json',
        )
        assert r.status_code == 201
        ev = CandidateEvaluation.objects.get(application=app, stage=stage)
        assert ev.passed is True
        assert ev.evaluator == hr_user  # auto-set by perform_create
