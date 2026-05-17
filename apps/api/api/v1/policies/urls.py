"""URLs for policies bounded context — B.15a Module 01."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.policies.views import (
    PolicyAcknowledgmentViewSet,
    PolicyApprovalFlowViewSet,
    PolicyPublicationViewSet,
    PolicyVersionViewSet,
    PolicyViewSet,
)

app_name = "policies"

router = DefaultRouter()
router.register(r"policies", PolicyViewSet, basename="policy")
router.register(r"policy-versions", PolicyVersionViewSet, basename="policy-version")
router.register(r"policy-approval-flows", PolicyApprovalFlowViewSet, basename="policy-approval-flow")
router.register(r"policy-publications", PolicyPublicationViewSet, basename="policy-publication")
router.register(r"policy-acknowledgments", PolicyAcknowledgmentViewSet, basename="policy-acknowledgment")

urlpatterns = [
    path("", include(router.urls)),
]
