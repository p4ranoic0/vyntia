"""Tests for audit_lite domain audit events (ADR-B.2)."""

import pytest

from apps.audit_lite.models import AuditEvent
from apps.audit_lite.services import record_event


@pytest.mark.django_db
class TestAuditEvent:
    def test_audit_event_can_be_created(self, tenant_a, admin_user):
        event = AuditEvent.objects.create(
            tenant=tenant_a,
            actor_user=admin_user,
            action="employee.terminated",
            target_model="employees.Employee",
            target_id="some-uuid",
            payload_json={"reason": "voluntary"},
        )
        assert event.pk is not None
        assert event.created_at is not None
        assert event.payload_json == {"reason": "voluntary"}

    def test_record_event_helper_persists_event(self, tenant_a, admin_user):
        event = record_event(
            tenant=tenant_a,
            actor_user=admin_user,
            action="contract.amended",
            target_model="contracts.Contract",
            target_id="contract-uuid",
            payload={"old_salary": 1000, "new_salary": 1500},
        )
        assert event.pk is not None
        assert event.action == "contract.amended"
        assert event.payload_json["old_salary"] == 1000
        assert AuditEvent.objects.filter(action="contract.amended").count() == 1

    def test_record_event_accepts_string_target_id(self, tenant_a, admin_user):
        event = record_event(
            tenant=tenant_a,
            actor_user=admin_user,
            action="user.password_reset",
            target_model="identity.User",
            target_id="42",
            payload={},
        )
        assert event.target_id == "42"

    def test_record_event_actor_user_can_be_none(self, tenant_a):
        event = record_event(
            tenant=tenant_a,
            actor_user=None,
            action="system.cleanup",
            target_model="documents.Document",
            target_id="doc-uuid",
            payload={"reason": "retention"},
        )
        assert event.actor_user is None
        assert event.action == "system.cleanup"
