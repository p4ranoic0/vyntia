"""Smoke tests for B.15a policies API (routing + auth gating + happy paths)."""
from datetime import date, timedelta

import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from apps.policies.models import (
    Policy,
    PolicyApprovalFlow,
    PolicyApprovalStep,
    PolicyPublication,
    PolicyVersion,
)


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username='hr_b15a', email='hr_b15a@test.local',
        password='Test1234!',
        nombres_usuario='HR', apellidos_usuario='PolicyB15a',
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
def policy(hr_user):
    return Policy.objects.create(
        kind='codigo_etica', title='Código Smoke',
        owner_user=hr_user, status='draft',
    )


@pytest.mark.django_db
class TestRoutingAuth:
    @pytest.mark.parametrize('path', [
        'policies',
        'policy-versions',
        'policy-approval-flows',
        'policy-publications',
        'policy-acknowledgments',
    ])
    def test_requires_auth(self, path):
        client = APIClient()
        r = client.get(f'/api/v1/{path}/')
        assert r.status_code in (401, 403)

    @pytest.mark.parametrize('path', [
        'policies',
        'policy-versions',
        'policy-approval-flows',
        'policy-publications',
        'policy-acknowledgments',
    ])
    def test_authenticated_list_returns_200(self, auth_client, path):
        r = auth_client.get(f'/api/v1/{path}/')
        assert r.status_code == 200


@pytest.mark.django_db
class TestPolicyCRUD:
    def test_create_policy(self, auth_client, hr_user):
        r = auth_client.post(
            '/api/v1/policies/',
            {
                'kind': 'rit',
                'title': 'RIT API',
                'description': 'desc',
                'owner_user': str(hr_user.pk),
            },
            format='json',
        )
        assert r.status_code in (200, 201), r.content
        data = r.json().get('data') or r.json()
        assert data.get('title') == 'RIT API'

    def test_retire_action(self, auth_client, policy):
        r = auth_client.post(f'/api/v1/policies/{policy.pk}/retire/')
        assert r.status_code == 200, r.content
        policy.refresh_from_db()
        assert policy.status == 'retired'


@pytest.mark.django_db
class TestVersionLifecycleAPI:
    def test_submit_and_publish_chain(self, auth_client, hr_user, policy):
        # Create version directly (service-level path)
        v = PolicyVersion.objects.create(
            policy=policy, version_number=1, content_html='<p>v1</p>',
        )
        # Need a second user as approver — must have RRHH role to call decide
        approver = User.objects.create_user(
            username='approver_b15a', email='approver_b15a@test.local',
            password='Test1234!',
            nombres_usuario='Appr', apellidos_usuario='B15a',
            tipo_usuario='rrhh', nivel_acceso='total',
        )
        rrhh_role, _ = Role.objects.get_or_create(
            nombre_rol='Administrador RRHH',
            defaults={'estado_rol': 'activo', 'nivel_jerarquico': 2, 'es_rol_sistema': True},
        )
        UserRole.objects.get_or_create(
            usuario=approver, rol=rrhh_role, defaults={'estado_asignacion': 'activo'},
        )
        # submit-for-review
        r = auth_client.post(
            f'/api/v1/policy-versions/{v.pk}/submit-for-review/',
            {'approvers': [str(approver.pk)]},
            format='json',
        )
        assert r.status_code in (200, 201), r.content
        v.refresh_from_db()
        assert v.status == 'under_review'

        # Approve via decide
        flow = v.approval_flow
        # Switch to approver's token
        ref2 = RefreshToken.for_user(approver)
        approver_client = APIClient()
        approver_client.credentials(HTTP_AUTHORIZATION=f'Bearer {ref2.access_token!s}')
        r = approver_client.post(
            f'/api/v1/policy-approval-flows/{flow.pk}/decide/',
            {'step_order': 1, 'decision': 'approved'},
            format='json',
        )
        assert r.status_code == 200, r.content
        v.refresh_from_db()
        assert v.status == 'approved'

        # Publish
        r = auth_client.post(
            f'/api/v1/policy-versions/{v.pk}/publish/',
            {'target_audience': 'all', 'requires_acknowledgment': False},
            format='json',
        )
        assert r.status_code in (200, 201), r.content
        v.refresh_from_db()
        assert v.status == 'published'


@pytest.mark.django_db
class TestAcknowledgeAPI:
    def test_acknowledge_action(self, auth_client, hr_user, policy):
        v = PolicyVersion.objects.create(
            policy=policy, version_number=1, status='approved',
        )
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=hr_user, target_audience='all',
            requires_acknowledgment=True,
            acknowledgment_deadline=date.today() + timedelta(days=5),
        )
        emp = Employee.objects.create(
            numero_documento='90909090', tipo_documento='DNI',
            nombres_empleado='Yo', apellido_paterno='Mismo',
            apellido_materno='Test', fecha_nacimiento=date(1990, 1, 1),
            estado_empleado='activo',
        )
        from apps.policies.models import PolicyAcknowledgment
        ack = PolicyAcknowledgment.objects.create(
            publication=pub, employee=emp,
        )
        r = auth_client.post(
            f'/api/v1/policy-acknowledgments/{ack.pk}/acknowledge/',
            {'signature_kind': 'checkbox', 'signature_payload': 'true'},
            format='json',
        )
        assert r.status_code == 200, r.content
        ack.refresh_from_db()
        assert ack.status == 'acknowledged'

    def test_decline_action(self, auth_client, hr_user, policy):
        v = PolicyVersion.objects.create(
            policy=policy, version_number=1, status='approved',
        )
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=hr_user, target_audience='all',
            requires_acknowledgment=True,
        )
        emp = Employee.objects.create(
            numero_documento='80808080', tipo_documento='DNI',
            nombres_empleado='Otro', apellido_paterno='Yo',
            apellido_materno='Demo', fecha_nacimiento=date(1990, 1, 1),
            estado_empleado='activo',
        )
        from apps.policies.models import PolicyAcknowledgment
        ack = PolicyAcknowledgment.objects.create(
            publication=pub, employee=emp,
        )
        r = auth_client.post(
            f'/api/v1/policy-acknowledgments/{ack.pk}/decline/',
            {'reason': 'No estoy de acuerdo'},
            format='json',
        )
        assert r.status_code == 200, r.content
        ack.refresh_from_db()
        assert ack.status == 'declined'

    def test_expire_overdue_collection_action(self, auth_client):
        r = auth_client.post('/api/v1/policy-acknowledgments/expire-overdue/')
        assert r.status_code == 200, r.content
        body = r.json()
        data = body.get('data') or body
        assert 'expired' in data
