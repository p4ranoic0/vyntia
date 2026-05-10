"""Tests for Company.get_config tenant safety (B.3 #54)."""

import pytest

from apps.tenancy.context import tenant_context


def _make_staff_user(username):
    """Create a minimal staff user required by Tenant.created_by FK."""
    from apps.identity.models import User
    return User.objects.create_user(
        username=username,
        email=f"{username}@vyntia.pe",
        password="testpass123",
    )


def _make_tenant(slug, name, staff_user):
    """Create a Tenant with the required created_by field."""
    from apps.tenancy.models import Tenant
    return Tenant.objects.create(
        slug=slug,
        name=name,
        ruc=f"20{slug.replace('-', '')[:9]:0<9}",
        plan="starter",
        status="active",
        created_by=staff_user,
    )


@pytest.mark.django_db
class TestCompanyGetConfig:
    def _make_company(self, tenant, suffix):
        from apps.organization.models import Company
        # All non-id fields have defaults; create with minimal overrides.
        return Company.objects.create(
            tenant=tenant,
            nombre=f"Company {suffix}",
        )

    def test_get_config_with_explicit_tenant(self):
        from apps.organization.models import Company

        staff = _make_staff_user("gc_staff_a")
        ta = _make_tenant("gc-ta", "GC TA", staff)
        company = self._make_company(ta, "A")
        result = Company.get_config(tenant=ta)
        assert result == company

    def test_get_config_resolves_tenant_from_context_when_arg_none(self):
        """When tenant arg is None, Company.get_config should resolve from
        get_current_tenant() — not fall back to pk=1 singleton (#54).

        We create an earlier Company (for ta) so that tb's company is NOT
        pk=1 — this makes the pk=1 fallback visibly return the wrong record.
        """
        from apps.organization.models import Company

        staff = _make_staff_user("gc_staff_b")
        # ta and its company are created first so tb's company is NOT pk=1
        ta = _make_tenant("gc-tb-ta", "GC TB TA", staff)
        self._make_company(ta, "B-decoy")  # occupies lower pk

        tb = _make_tenant("gc-tb-tb", "GC TB TB", staff)
        company_b = self._make_company(tb, "B-real")

        with tenant_context(tb):
            result = Company.get_config()
        assert result == company_b

    def test_get_config_returns_none_when_no_tenant_resolvable(self):
        """When neither arg nor context provides a tenant, return None — do NOT
        fall back to pk=1 (which would leak the wrong tenant's config) (#54)."""
        from apps.organization.models import Company

        # No tenant context, no arg — must return None, not a singleton
        result = Company.get_config()
        assert result is None
