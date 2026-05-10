"""OnboardingService.crear_onboarding_completo Role tenant scoping (B.5b #81)."""
import inspect


class TestRoleLookupTenantScoped:
    def test_role_lookup_filters_by_tenant_when_available(self):
        """Role.objects.filter() must apply tenant filter when tenant arg present."""
        from apps.onboarding.services.onboarding_service import OnboardingService

        src = inspect.getsource(OnboardingService.crear_onboarding_completo)
        # The fix wraps the role lookup in a `if tenant is not None: filter(tenant=...)`
        assert "Role.objects.filter" in src
        assert "filter(tenant=tenant)" in src
