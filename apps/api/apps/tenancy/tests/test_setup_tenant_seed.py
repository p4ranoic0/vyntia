"""Tests for setup_tenant_seed()."""

import pytest

from apps.organization.models import Company
from apps.tenancy.admin_helpers.seed import setup_tenant_seed
from apps.tenancy.models import Tenant


@pytest.fixture
def staff_user(django_user_model):
    return django_user_model.objects.create_user(
        username="staff", email="staff@vyntia.pe", password="x"
    )


@pytest.fixture
def tenant(staff_user):
    return Tenant.objects.create(
        slug="acme", name="Acme Corp", ruc="20123456789",
        plan="starter", status="trial", created_by=staff_user,
    )


@pytest.mark.django_db
class TestSetupTenantSeed:
    def test_creates_company_for_tenant(self, tenant):
        result = setup_tenant_seed(tenant)
        assert result["company_created"] is True
        company = Company.objects.get(tenant=tenant)
        assert company.ruc == "20123456789"

    def test_idempotent(self, tenant):
        setup_tenant_seed(tenant)
        result = setup_tenant_seed(tenant)
        # Second call should not duplicate
        assert result["company_created"] is False
        assert Company.objects.filter(tenant=tenant).count() == 1
