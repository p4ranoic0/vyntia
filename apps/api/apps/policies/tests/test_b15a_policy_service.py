"""Tests for B.15a policy_service flows."""
from datetime import date

import pytest
from django.core.exceptions import ValidationError

from apps.identity.models import User
from apps.policies.models import Policy, PolicyApprovalFlow, PolicyApprovalStep, PolicyVersion
from apps.policies.services import policy_service


@pytest.fixture
def owner(db):
    return User.objects.create(
        username='owner_svc', email='owner_svc@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def approver_a(db):
    return User.objects.create(
        username='appA', email='appA@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def approver_b(db):
    return User.objects.create(
        username='appB', email='appB@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestCreate:
    def test_create_policy(self, owner):
        p = policy_service.create_policy(
            tenant=None, kind='codigo_etica', title='Ética',
            owner_user=owner, user=owner,
        )
        assert p.pk is not None
        assert p.status == 'draft'

    def test_create_version_increments_number(self, owner):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT', owner_user=owner)
        v1 = policy_service.create_version(policy=p, content_html='<p>v1</p>', user=owner)
        v2 = policy_service.create_version(policy=p, content_html='<p>v2</p>', user=owner)
        assert v1.version_number == 1
        assert v2.version_number == 2

    def test_create_version_refused_on_retired_policy(self, owner):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-2', owner_user=owner)
        p.status = 'retired'
        p.save()
        with pytest.raises(ValidationError):
            policy_service.create_version(policy=p, content_html='<p>x</p>')


@pytest.mark.django_db
class TestApprovalFlow:
    def test_submit_creates_flow_with_steps(self, owner, approver_a, approver_b):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-3', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow = policy_service.submit_for_review(version=v, approvers=[approver_a, approver_b])
        assert flow.steps.count() == 2
        v.refresh_from_db()
        assert v.status == 'under_review'
        p.refresh_from_db()
        assert p.status == 'in_review'

    def test_submit_with_no_approvers_raises(self, owner):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-4', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        with pytest.raises(ValidationError):
            policy_service.submit_for_review(version=v, approvers=[])

    def test_resubmit_replaces_previous_flow(self, owner, approver_a):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-5', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow1 = policy_service.submit_for_review(version=v, approvers=[approver_a])
        # reject + resubmit
        policy_service.register_approval_decision(
            flow=flow1, step_order=1, approver=approver_a, decision='rejected', comment='no',
        )
        flow2 = policy_service.submit_for_review(version=v, approvers=[approver_a])
        assert flow2.pk != flow1.pk
        assert not PolicyApprovalFlow.objects.filter(pk=flow1.pk).exists()

    def test_full_approve_path_marks_version_approved(self, owner, approver_a):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-6', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow = policy_service.submit_for_review(version=v, approvers=[approver_a])
        policy_service.register_approval_decision(
            flow=flow, step_order=1, approver=approver_a, decision='approved',
        )
        v.refresh_from_db()
        assert v.status == 'approved'
        p.refresh_from_db()
        assert p.status == 'approved'

    def test_reject_reverts_to_draft(self, owner, approver_a):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-7', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow = policy_service.submit_for_review(version=v, approvers=[approver_a])
        policy_service.register_approval_decision(
            flow=flow, step_order=1, approver=approver_a, decision='rejected', comment='nope',
        )
        v.refresh_from_db()
        assert v.status == 'draft'
        p.refresh_from_db()
        assert p.status == 'draft'

    def test_wrong_approver_refused(self, owner, approver_a, approver_b):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-8', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow = policy_service.submit_for_review(version=v, approvers=[approver_a])
        with pytest.raises(ValidationError):
            policy_service.register_approval_decision(
                flow=flow, step_order=1, approver=approver_b, decision='approved',
            )


@pytest.mark.django_db
class TestPublishAndRetire:
    def test_publish_requires_approved(self, owner):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-9', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        with pytest.raises(ValidationError):
            policy_service.publish(version=v, user=owner)

    def test_publish_sets_current_version(self, owner, approver_a):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-10', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow = policy_service.submit_for_review(version=v, approvers=[approver_a])
        policy_service.register_approval_decision(
            flow=flow, step_order=1, approver=approver_a, decision='approved',
        )
        pub = policy_service.publish(version=v, target_audience='all', user=owner)
        v.refresh_from_db()
        assert v.status == 'published'
        p.refresh_from_db()
        assert p.status == 'published'
        assert p.current_version_id == v.pk
        assert pub.target_audience == 'all'

    def test_retire_marks_policy_and_current_version_retired(self, owner, approver_a):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-11', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow = policy_service.submit_for_review(version=v, approvers=[approver_a])
        policy_service.register_approval_decision(
            flow=flow, step_order=1, approver=approver_a, decision='approved',
        )
        policy_service.publish(version=v, user=owner)
        policy_service.retire(p, user=owner)
        p.refresh_from_db()
        v.refresh_from_db()
        assert p.status == 'retired'
        assert v.status == 'retired'

    def test_publish_role_requires_target_role(self, owner, approver_a):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-12', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        flow = policy_service.submit_for_review(version=v, approvers=[approver_a])
        policy_service.register_approval_decision(
            flow=flow, step_order=1, approver=approver_a, decision='approved',
        )
        with pytest.raises(ValidationError):
            policy_service.publish(version=v, target_audience='role', user=owner)


@pytest.mark.django_db
class TestListPending:
    def test_list_pending_approvals_for_user(self, owner, approver_a):
        p = policy_service.create_policy(tenant=None, kind='rit', title='RIT-13', owner_user=owner)
        v = policy_service.create_version(policy=p, content_html='<p>v</p>')
        policy_service.submit_for_review(version=v, approvers=[approver_a])
        pending = list(policy_service.list_pending_approvals_for_user(approver_a))
        assert len(pending) == 1
        assert pending[0].approver_user_id == approver_a.pk
