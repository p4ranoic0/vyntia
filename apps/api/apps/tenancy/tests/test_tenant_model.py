"""Tests for the Tenant model."""

from datetime import timedelta

import pytest
from django.db import IntegrityError
from django.utils import timezone

from apps.tenancy.models import Tenant


@pytest.fixture
def staff_user(django_user_model):
    """A Vyntia staff user used as `created_by` for tenants."""
    return django_user_model.objects.create_user(
        username="vyntia_staff",
        email="staff@vyntia.pe",
        password="testpass123",
    )


@pytest.mark.django_db
class TestTenantModel:
    def test_create_tenant_with_required_fields(self, staff_user):
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme Corp S.A.C.",
            ruc="20123456789",
            plan="starter",
            status="trial",
            trial_ends_at=timezone.now() + timedelta(days=30),
            created_by=staff_user,
        )
        assert tenant.id is not None
        assert tenant.slug == "acme"
        assert tenant.name == "Acme Corp S.A.C."
        assert tenant.ruc == "20123456789"
        assert tenant.plan == "starter"
        assert tenant.status == "trial"
        assert tenant.max_users == 10
        assert tenant.created_at is not None
        assert tenant.updated_at is not None
        assert tenant.cancelled_at is None
        assert tenant.created_by == staff_user

    def test_slug_must_be_unique(self, staff_user):
        Tenant.objects.create(
            slug="acme",
            name="Acme",
            ruc="20123456789",
            plan="starter",
            status="trial",
            created_by=staff_user,
        )
        with pytest.raises(IntegrityError):
            Tenant.objects.create(
                slug="acme",
                name="Other Acme",
                ruc="20999999999",
                plan="pro",
                status="active",
                created_by=staff_user,
            )

    def test_str_representation(self, staff_user):
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme Corp",
            ruc="20123456789",
            plan="starter",
            status="active",
            created_by=staff_user,
        )
        assert str(tenant) == "Acme Corp (acme)"

    def test_default_max_users_is_ten(self, staff_user):
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme",
            ruc="20123456789",
            plan="starter",
            status="trial",
            created_by=staff_user,
        )
        assert tenant.max_users == 10

    def test_uuid_primary_key(self, staff_user):
        import uuid
        tenant = Tenant.objects.create(
            slug="acme",
            name="Acme",
            ruc="20123456789",
            plan="starter",
            status="trial",
            created_by=staff_user,
        )
        assert isinstance(tenant.id, uuid.UUID)
