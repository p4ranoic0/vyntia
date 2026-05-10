"""URLs for onboarding bounded context — English paths per spec § 3.4."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.onboarding.views import OnboardingViewSet

app_name = "onboarding"

router = DefaultRouter()
router.register(r"processes", OnboardingViewSet, basename="onboarding-process")

urlpatterns = [
    path("", include(router.urls)),
]
