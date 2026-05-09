"""Tests for the TenantMembership model."""

import pytest
from django.db import IntegrityError

from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
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


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@acme.com", password="x"
    )


@pytest.mark.django_db
class TestTenantMembershipModel:
    def test_create_membership(self, tenant, member_user):
        membership = TenantMembership.objects.create(
            tenant=tenant,
            user=member_user,
            role="admin",
            status="active",
        )
        assert membership.id is not None
        assert membership.tenant == tenant
        assert membership.user == member_user
        assert membership.role == "admin"
        assert membership.status == "active"
        assert membership.invited_at is not None
        assert membership.joined_at is None
        assert membership.invited_by is None

    def test_unique_constraint_tenant_user(self, tenant, member_user):
        TenantMembership.objects.create(
            tenant=tenant, user=member_user, role="admin", status="active"
        )
        with pytest.raises(IntegrityError):
            TenantMembership.objects.create(
                tenant=tenant,
                user=member_user,
                role="member",
                status="active",
            )

    def test_same_user_different_tenants_allowed(self, tenant, member_user, staff_user):
        """A user can be member of multiple tenants — the unique is composite."""
        TenantMembership.objects.create(
            tenant=tenant, user=member_user, role="admin", status="active"
        )
        other_tenant = Tenant.objects.create(
            slug="beta",
            name="Beta",
            ruc="20999999999",
            plan="pro",
            status="active",
            created_by=staff_user,
        )
        m2 = TenantMembership.objects.create(
            tenant=other_tenant,
            user=member_user,
            role="member",
            status="active",
        )
        assert m2.id is not None

    def test_str_representation(self, tenant, member_user):
        membership = TenantMembership.objects.create(
            tenant=tenant, user=member_user, role="admin", status="active"
        )
        assert str(membership) == f"{member_user.username} @ acme (admin)"
