"""OnboardingViewSet routing migration (B.5b #82)."""


class TestOnboardingRouting:
    def test_view_set_lives_in_onboarding_module(self):
        """Module migration smoke test (#82 — moved from rrhh/views.py to onboarding/views.py)."""
        from api.v1.onboarding import views as ob_views

        assert hasattr(ob_views, "OnboardingViewSet")

    def test_view_set_is_no_longer_in_rrhh_views(self):
        """rrhh/views.py must no longer expose OnboardingViewSet."""
        from api.v1.rrhh import views as rrhh_views

        assert not hasattr(rrhh_views, "OnboardingViewSet"), (
            "OnboardingViewSet still in api.v1.rrhh.views — migration incomplete"
        )

    def test_url_routing_imports_from_local(self):
        """The urls.py must import the ViewSet from local module."""
        from pathlib import Path

        urls_path = Path(__file__).resolve().parents[3] / "api" / "v1" / "onboarding" / "urls.py"
        content = urls_path.read_text(encoding="utf-8")
        assert "from api.v1.onboarding.views import OnboardingViewSet" in content
        assert "from api.v1.rrhh.views import OnboardingViewSet" not in content
