"""URLs for policies bounded context — B.15a Module 01 + B.15b strategic/workforce/compliance."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.policies.b15b_views import (
    ComplianceMatrixViewSet,
    ComplianceObligationViewSet,
    EvidenceViewSet,
    HeadcountProjectionViewSet,
    HRStrategicPlanViewSet,
    KPIViewSet,
    KeyPositionViewSet,
    StrategicObjectiveViewSet,
    SuccessionPlanViewSet,
    SuccessorCandidateViewSet,
    WorkforcePlanViewSet,
)
from api.v1.policies.views import (
    PolicyAcknowledgmentViewSet,
    PolicyApprovalFlowViewSet,
    PolicyPublicationViewSet,
    PolicyVersionViewSet,
    PolicyViewSet,
)

app_name = "policies"

router = DefaultRouter()
# B.15a — Policy gestor
router.register(r"policies", PolicyViewSet, basename="policy")
router.register(r"policy-versions", PolicyVersionViewSet, basename="policy-version")
router.register(r"policy-approval-flows", PolicyApprovalFlowViewSet, basename="policy-approval-flow")
router.register(r"policy-publications", PolicyPublicationViewSet, basename="policy-publication")
router.register(r"policy-acknowledgments", PolicyAcknowledgmentViewSet, basename="policy-acknowledgment")
# B.15b — Strategic plan
router.register(r"strategic-plans", HRStrategicPlanViewSet, basename="strategic-plan")
router.register(r"strategic-objectives", StrategicObjectiveViewSet, basename="strategic-objective")
router.register(r"kpis", KPIViewSet, basename="kpi")
# B.15b — Workforce + succession
router.register(r"workforce-plans", WorkforcePlanViewSet, basename="workforce-plan")
router.register(r"headcount-projections", HeadcountProjectionViewSet, basename="headcount-projection")
router.register(r"succession-plans", SuccessionPlanViewSet, basename="succession-plan")
router.register(r"key-positions", KeyPositionViewSet, basename="key-position")
router.register(r"successor-candidates", SuccessorCandidateViewSet, basename="successor-candidate")
# B.15b — Compliance
router.register(r"compliance-matrices", ComplianceMatrixViewSet, basename="compliance-matrix")
router.register(r"compliance-obligations", ComplianceObligationViewSet, basename="compliance-obligation")
router.register(r"evidences", EvidenceViewSet, basename="evidence")

urlpatterns = [
    path("", include(router.urls)),
]
