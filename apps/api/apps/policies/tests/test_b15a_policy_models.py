"""Tests for B.15a Policy + PolicyVersion + Approval + Publication + Acknowledgment models."""
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department
from apps.policies.models import (
    Policy,
    PolicyAcknowledgment,
    PolicyApprovalFlow,
    PolicyApprovalStep,
    PolicyPublication,
    PolicyVersion,
)


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='RRHH', siglas_area='RRHH', estado_area='activa',
    )


@pytest.fixture
def owner_user(db):
    return User.objects.create(
        username='policy_owner', email='owner@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='10101010', tipo_documento='DNI',
        nombres_empleado='Pol', apellido_paterno='Acuser',
        apellido_materno='Demo', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def policy(owner_user, department):
    return Policy.objects.create(
        kind='rit', title='Reglamento Interno', description='RIT base',
        owner_user=owner_user, owner_area=department, status='draft',
    )


@pytest.mark.django_db
class TestPolicyModel:
    def test_create_and_str(self, policy):
        assert 'Reglamento Interno' in str(policy)
        assert policy.is_active is False  # draft

    def test_unique_title_per_kind_per_tenant(self, owner_user):
        from apps.tenancy.models import Tenant
        t = Tenant.objects.create(
            slug='acme', name='ACME', ruc='20100000001',
            plan='starter', status='active', created_by=owner_user,
        )
        Policy.objects.create(tenant=t, kind='codigo_etica', title='Código', owner_user=owner_user)
        with pytest.raises(Exception):
            Policy.objects.create(tenant=t, kind='codigo_etica', title='Código', owner_user=owner_user)

    def test_latest_version_with_two_versions(self, policy):
        v1 = PolicyVersion.objects.create(policy=policy, version_number=1)
        v2 = PolicyVersion.objects.create(policy=policy, version_number=2)
        assert policy.latest_version().pk == v2.pk


@pytest.mark.django_db
class TestPolicyVersionLifecycle:
    def test_draft_to_under_review_to_approved_to_published(self, policy, owner_user):
        v = PolicyVersion.objects.create(policy=policy, version_number=1)
        v.mark_under_review(user=owner_user)
        assert v.status == 'under_review'
        assert v.submitted_by == owner_user
        v.mark_approved()
        assert v.status == 'approved'
        assert v.approved_at is not None
        v.mark_published()
        assert v.status == 'published'

    def test_revert_to_draft_from_under_review(self, policy):
        v = PolicyVersion.objects.create(policy=policy, version_number=1)
        v.mark_under_review()
        v.revert_to_draft()
        assert v.status == 'draft'
        assert v.submitted_at is None

    def test_cannot_publish_from_draft(self, policy):
        v = PolicyVersion.objects.create(policy=policy, version_number=1)
        with pytest.raises(ValidationError):
            v.mark_published()

    def test_version_number_unique_per_policy(self, policy):
        PolicyVersion.objects.create(policy=policy, version_number=1)
        with pytest.raises(Exception):
            PolicyVersion.objects.create(policy=policy, version_number=1)


@pytest.mark.django_db
class TestApprovalFlow:
    def test_step_record_decision(self, policy, owner_user):
        v = PolicyVersion.objects.create(policy=policy, version_number=1)
        flow = PolicyApprovalFlow.objects.create(policy_version=v)
        step = PolicyApprovalStep.objects.create(flow=flow, order=1, approver_user=owner_user)
        step.record_decision(decision='approved', user=owner_user, comment='ok')
        assert step.decision == 'approved'
        assert step.decided_by == owner_user

    def test_recompute_status_approved(self, policy, owner_user):
        v = PolicyVersion.objects.create(policy=policy, version_number=1)
        flow = PolicyApprovalFlow.objects.create(policy_version=v)
        s1 = PolicyApprovalStep.objects.create(flow=flow, order=1, approver_user=owner_user)
        s1.record_decision(decision='approved', user=owner_user)
        flow.recompute_status()
        flow.refresh_from_db()
        assert flow.status == 'approved'

    def test_recompute_status_rejected_on_any_rejection(self, policy, owner_user):
        v = PolicyVersion.objects.create(policy=policy, version_number=1)
        flow = PolicyApprovalFlow.objects.create(policy_version=v)
        u2 = User.objects.create(username='u2', email='u2@x.local', tipo_usuario='administrador')
        s1 = PolicyApprovalStep.objects.create(flow=flow, order=1, approver_user=owner_user)
        s2 = PolicyApprovalStep.objects.create(flow=flow, order=2, approver_user=u2)
        s1.record_decision(decision='approved', user=owner_user)
        s2.record_decision(decision='rejected', user=u2, comment='no')
        flow.recompute_status()
        flow.refresh_from_db()
        assert flow.status == 'rejected'

    def test_cannot_decide_twice(self, policy, owner_user):
        v = PolicyVersion.objects.create(policy=policy, version_number=1)
        flow = PolicyApprovalFlow.objects.create(policy_version=v)
        s = PolicyApprovalStep.objects.create(flow=flow, order=1, approver_user=owner_user)
        s.record_decision(decision='approved', user=owner_user)
        with pytest.raises(ValidationError):
            s.record_decision(decision='rejected', user=owner_user)


@pytest.mark.django_db
class TestPublication:
    def test_expand_target_employees_all(self, policy, owner_user, employee):
        v = PolicyVersion.objects.create(policy=policy, version_number=1, status='approved')
        from django.utils import timezone
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=owner_user, target_audience='all',
        )
        emps = list(pub.expand_target_employees())
        assert employee in emps


@pytest.mark.django_db
class TestAcknowledgment:
    def test_mark_acknowledged_records_audit(self, policy, owner_user, employee):
        v = PolicyVersion.objects.create(policy=policy, version_number=1, status='approved')
        from django.utils import timezone
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=owner_user, target_audience='all',
        )
        ack = PolicyAcknowledgment.objects.create(publication=pub, employee=employee)
        ack.mark_acknowledged(
            signature_kind='checkbox', signature_payload='true',
            ip='10.0.0.1', user_agent='Mozilla/5.0',
        )
        assert ack.status == 'acknowledged'
        assert ack.signature_kind == 'checkbox'
        assert ack.ip == '10.0.0.1'
        assert ack.acknowledged_at is not None

    def test_decline_requires_reason(self, policy, owner_user, employee):
        v = PolicyVersion.objects.create(policy=policy, version_number=1, status='approved')
        from django.utils import timezone
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=owner_user, target_audience='all',
        )
        ack = PolicyAcknowledgment.objects.create(publication=pub, employee=employee)
        with pytest.raises(ValidationError):
            ack.mark_declined(reason='')

    def test_unique_per_publication_employee(self, policy, owner_user, employee):
        v = PolicyVersion.objects.create(policy=policy, version_number=1, status='approved')
        from django.utils import timezone
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=owner_user, target_audience='all',
        )
        PolicyAcknowledgment.objects.create(publication=pub, employee=employee)
        with pytest.raises(Exception):
            PolicyAcknowledgment.objects.create(publication=pub, employee=employee)

    def test_is_overdue(self, policy, owner_user, employee):
        from django.utils import timezone
        v = PolicyVersion.objects.create(policy=policy, version_number=1, status='approved')
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=owner_user, target_audience='all',
            acknowledgment_deadline=date.today() - timedelta(days=1),
        )
        ack = PolicyAcknowledgment.objects.create(publication=pub, employee=employee)
        assert ack.is_overdue() is True
