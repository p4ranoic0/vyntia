"""OnboardingService.reenviar_email_bienvenida + corregir_correo regression tests (B.5b #32)."""
import inspect


class TestReenviarEmailBienvenida:
    def test_uses_pk_lookup_not_legacy_onboarding_id_field(self):
        """OnboardingProcess PK is `id` UUID; legacy `onboarding_id=` lookup is FieldError."""
        from apps.onboarding.services.onboarding_service import OnboardingService

        src = inspect.getsource(OnboardingService.reenviar_email_bienvenida)
        assert "onboarding_id=onboarding_id" not in src
        # Must use pk= or id= lookup
        assert "pk=onboarding_id" in src or "id=onboarding_id" in src
