"""Tests for TenantManager and UnsafeManager.

These tests use the existing TenantMembership model (which is tenant-scoped)
to exercise both manager classes without needing a fixture model.
"""

import pytest

from apps.tenancy.context import tenant_context
from apps.tenancy.managers import TenantManager, UnsafeManager
from apps.tenancy.models import Tenant, TenantMembership


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant_a(staff_user):
    return Tenant.objects.create(
        slug="alpha", name="Alpha", ruc="20111111111",
        plan="starter", status="active", created_by=staff_user,
    )


@pytest.fixture
def tenant_b(staff_user):
    return Tenant.objects.create(
        slug="beta", name="Beta", ruc="20222222222",
        plan="pro", status="active", created_by=staff_user,
    )


@pytest.fixture
def member_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.mark.django_db
class TestTenantManagerLenient:
    """TenantManager filters by tenant when context is set, returns all otherwise."""

    def test_no_context_returns_all_rows(self, tenant_a, tenant_b, member_user):
        TenantMembership.objects.create(
            tenant=tenant_a, user=member_user, role="admin", status="active"
        )
        TenantMembership.objects.create(
            tenant=tenant_b, user=member_user, role="member", status="active"
        )
        # No tenant_context active → manager is lenient → returns all rows
        qs = TenantManager()._lenient_queryset_for_test(TenantMembership)
        assert qs.count() == 2  # both rows visible

    def test_with_context_filters_to_tenant(self, tenant_a, tenant_b, member_user):
        TenantMembership.objects.create(
            tenant=tenant_a, user=member_user, role="admin", status="active"
        )
        TenantMembership.objects.create(
            tenant=tenant_b, user=member_user, role="member", status="active"
        )
        with tenant_context(tenant_a):
            qs = TenantManager()._lenient_queryset_for_test(TenantMembership)
            assert qs.count() == 1
            assert qs.first().tenant_id == tenant_a.id


@pytest.mark.django_db
class TestUnsafeManager:
    """UnsafeManager always returns all rows, regardless of context."""

    def test_returns_all_even_with_tenant_context(self, tenant_a, tenant_b, member_user):
        TenantMembership.objects.create(
            tenant=tenant_a, user=member_user, role="admin", status="active"
        )
        TenantMembership.objects.create(
            tenant=tenant_b, user=member_user, role="member", status="active"
        )
        with tenant_context(tenant_a):
            qs = UnsafeManager()._lenient_queryset_for_test(TenantMembership)
            assert qs.count() == 2  # ignores context
