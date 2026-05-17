"""URLs for onboarding bounded context — English paths per spec § 3.4.

B.11: induction-plans + induction-tasks + induction-materials routers added
(Module 03.3 backlog #114, #115).
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.onboarding.exit_flow_views import (
    ExitFlowScaffoldView,
    ExitInterviewViewSet,
    HandoverChecklistViewSet,
    HandoverItemViewSet,
    SystemsOffboardingViewSet,
)
from api.v1.onboarding.induction_views import (
    InductionMaterialViewSet,
    InductionPlanViewSet,
    InductionTaskViewSet,
)
from api.v1.onboarding.views import OnboardingViewSet

app_name = "onboarding"

router = DefaultRouter()
router.register(r"processes", OnboardingViewSet, basename="onboarding-process")
router.register(r"induction-plans", InductionPlanViewSet, basename="induction-plan")
router.register(r"induction-tasks", InductionTaskViewSet, basename="induction-task")
router.register(r"induction-materials", InductionMaterialViewSet, basename="induction-material")
# B.14 — Exit flow (Module 03.7)
router.register(r"exit-interviews", ExitInterviewViewSet, basename="exit-interview")
router.register(r"handover-checklists", HandoverChecklistViewSet, basename="handover-checklist")
router.register(r"handover-items", HandoverItemViewSet, basename="handover-item")
router.register(r"systems-offboardings", SystemsOffboardingViewSet, basename="systems-offboarding")
router.register(r"exit-flow-scaffold", ExitFlowScaffoldView, basename="exit-flow-scaffold")

urlpatterns = [
    path("", include(router.urls)),
]
