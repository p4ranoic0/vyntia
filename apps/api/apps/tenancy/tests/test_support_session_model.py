"""Tests for the SupportSession model.

SupportSession audits Vyntia staff impersonating tenant users for support.
Every action taken during the session bumps actions_count.
"""

from datetime import timedelta

import pytest
from django.utils import timezone

from apps.tenancy.models import SupportSession, Tenant


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def target_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme",
        name="Acme",
        ruc="20123456789",
        plan="starter",
        status="active",
        created_by=staff_user,
    )


@pytest.mark.django_db
class TestSupportSessionModel:
    def test_create_session(self, staff_user, target_user, tenant):
        expires = timezone.now() + timedelta(hours=2)
        session = SupportSession.objects.create(
            staff_user=staff_user,
            target_user=target_user,
            tenant=tenant,
            reason="Ticket #1234 — error generating boletas",
            expires_at=expires,
        )
        assert session.id is not None
        assert session.staff_user == staff_user
        assert session.target_user == target_user
        assert session.tenant == tenant
        assert session.reason == "Ticket #1234 — error generating boletas"
        assert session.started_at is not None
        assert session.expires_at == expires
        assert session.ended_at is None
        assert session.actions_count == 0

    def test_actions_count_increments(self, staff_user, target_user, tenant):
        session = SupportSession.objects.create(
            staff_user=staff_user,
            target_user=target_user,
            tenant=tenant,
            reason="x",
            expires_at=timezone.now() + timedelta(hours=2),
        )
        session.actions_count += 1
        session.save()
        session.refresh_from_db()
        assert session.actions_count == 1

    def test_str_representation(self, staff_user, target_user, tenant):
        session = SupportSession.objects.create(
            staff_user=staff_user,
            target_user=target_user,
            tenant=tenant,
            reason="x",
            expires_at=timezone.now() + timedelta(hours=2),
        )
        assert str(session) == f"staff impersonating maria @ acme"
