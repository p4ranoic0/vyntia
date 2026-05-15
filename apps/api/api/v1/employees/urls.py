"""URLs for employees bounded context — English paths per spec § 3.4 (flat).

B.9: extended with Selección Module 03.1 — 7 ViewSets covering candidates,
requisitions, postings, stages, applications, evaluations, and rankings.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.v1.rrhh.views import (
    CursosCertificacionesViewSet,
    DatosAcademicosViewSet,
    DatosFamiliaresViewSet,
    EmpleadoViewSet,
)

from .legajo_views import (
    JobHistoryViewSet,
    SwornDeclarationViewSet,
    WorkExperienceViewSet,
)
from .views import (
    CandidateEvaluationViewSet,
    CandidateViewSet,
    JobApplicationViewSet,
    JobPostingViewSet,
    MeritRankingViewSet,
    PersonnelRequisitionViewSet,
    SelectionStageViewSet,
)

app_name = "employees"

router = DefaultRouter()
router.register(r"employees", EmpleadoViewSet, basename="employee")
router.register(r"family-members", DatosFamiliaresViewSet, basename="family-member")
router.register(r"academic-records", DatosAcademicosViewSet, basename="academic-record")
router.register(r"certifications", CursosCertificacionesViewSet, basename="certification")

# B.9 — Selección (Module 03.1)
router.register(r"candidates", CandidateViewSet, basename="candidate")
router.register(r"personnel-requisitions", PersonnelRequisitionViewSet,
                basename="personnel-requisition")
router.register(r"job-postings", JobPostingViewSet, basename="job-posting")
router.register(r"selection-stages", SelectionStageViewSet, basename="selection-stage")
router.register(r"job-applications", JobApplicationViewSet, basename="job-application")
router.register(r"candidate-evaluations", CandidateEvaluationViewSet,
                basename="candidate-evaluation")
router.register(r"merit-rankings", MeritRankingViewSet, basename="merit-ranking")

# B.12 — Legajo content (Module 03.5)
router.register(r"work-experiences", WorkExperienceViewSet, basename="work-experience")
router.register(r"sworn-declarations", SwornDeclarationViewSet, basename="sworn-declaration")
router.register(r"job-histories", JobHistoryViewSet, basename="job-history")

urlpatterns = [
    path("", include(router.urls)),
]
