"""Tests for B.9 MeritRanking + ranking_service.compute_merit_ranking."""
from decimal import Decimal

import pytest

from apps.employees.models import (
    Candidate,
    CandidateEvaluation,
    JobApplication,
    JobPosting,
    MeritRanking,
    PersonnelRequisition,
    SelectionStage,
)
from apps.employees.services import compute_merit_ranking
from apps.identity.models import User
from apps.organization.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="T", nombre_unidad_organica="T", siglas_area="T",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(code="P", name="P", department=department)


@pytest.fixture
def admin(db):
    return User.objects.create(
        username="adm_mr", email="adm_mr@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def evaluator(db):
    return User.objects.create(
        username="ev_mr", email="ev_mr@test.local",
        tipo_usuario="administrador", estado_usuario="activo",
    )


@pytest.fixture
def posting(department, position, admin):
    req = PersonnelRequisition.objects.create(
        position=position, department=department,
        justification='replacement', requested_by=admin,
        requested_count=1,
    )
    return JobPosting.objects.create(
        requisition=req, title='Analista I', sector_mode='private',
    )


@pytest.fixture
def stages(posting):
    """2 stages: knowledge eliminatoria 60%, interview 40%."""
    s1 = SelectionStage.objects.create(
        posting=posting, kind='knowledge', name='Conocimientos',
        order=1, min_score=Decimal('14'), max_score=Decimal('20'),
        weight=Decimal('60'), is_eliminatoria=True,
    )
    s2 = SelectionStage.objects.create(
        posting=posting, kind='interview', name='Entrevista',
        order=2, min_score=Decimal('0'), max_score=Decimal('20'),
        weight=Decimal('40'), is_eliminatoria=False,
    )
    return s1, s2


def _candidate(n):
    return Candidate.objects.create(
        document_number=f'1000000{n}',
        first_names=f'Cand{n}', last_names='X',
        email=f'c{n}@test.local',
    )


def _eval(application, stage, score, evaluator):
    return CandidateEvaluation.objects.create(
        application=application, stage=stage, evaluator=evaluator,
        score=Decimal(str(score)),
    )


@pytest.mark.django_db
class TestRankingService:
    def test_three_qualified_ordered_by_score(self, posting, stages, evaluator):
        s_know, s_int = stages
        c_a = _candidate(1)
        c_b = _candidate(2)
        c_c = _candidate(3)
        a = JobApplication.objects.create(posting=posting, candidate=c_a)
        b = JobApplication.objects.create(posting=posting, candidate=c_b)
        c = JobApplication.objects.create(posting=posting, candidate=c_c)
        # A: 18 know × 0.6 + 16 int × 0.4 = 10.8 + 6.4 = 17.20
        _eval(a, s_know, 18, evaluator); _eval(a, s_int, 16, evaluator)
        # B: 17 × 0.6 + 18 × 0.4 = 10.2 + 7.2 = 17.40 → highest
        _eval(b, s_know, 17, evaluator); _eval(b, s_int, 18, evaluator)
        # C: 14 × 0.6 + 14 × 0.4 = 8.4 + 5.6 = 14.00
        _eval(c, s_know, 14, evaluator); _eval(c, s_int, 14, evaluator)

        rows = compute_merit_ranking(posting=posting)
        assert len(rows) == 3
        assert rows[0].application == b and rows[0].rank == 1 and rows[0].outcome == 'winner'
        assert rows[1].application == a and rows[1].outcome == 'waiting_list'
        assert rows[2].application == c
        assert rows[0].total_score == Decimal('17.40')

    def test_eliminatoria_failure_filters_out(self, posting, stages, evaluator):
        s_know, s_int = stages
        c_a = _candidate(10)
        c_b = _candidate(11)
        a = JobApplication.objects.create(posting=posting, candidate=c_a)
        b = JobApplication.objects.create(posting=posting, candidate=c_b)
        # A passes know (15) + int 18 → 15×0.6 + 18×0.4 = 9 + 7.2 = 16.20
        _eval(a, s_know, 15, evaluator); _eval(a, s_int, 18, evaluator)
        # B fails know (13.5 < 14) — eliminated regardless of high int
        _eval(b, s_know, 13.5, evaluator); _eval(b, s_int, 20, evaluator)

        rows = compute_merit_ranking(posting=posting)
        assert rows[0].application == a
        assert rows[0].outcome == 'winner'
        # B at end with eliminated outcome
        b_row = next(r for r in rows if r.application == b)
        assert b_row.outcome == 'eliminated'
        assert b_row.total_score == Decimal('0.00')

    def test_terminal_status_treated_as_eliminated(self, posting, stages, evaluator):
        s_know, s_int = stages
        c_a = _candidate(20)
        c_b = _candidate(21)
        a = JobApplication.objects.create(posting=posting, candidate=c_a)
        b = JobApplication.objects.create(posting=posting, candidate=c_b)
        _eval(a, s_know, 18, evaluator); _eval(a, s_int, 18, evaluator)
        _eval(b, s_know, 19, evaluator); _eval(b, s_int, 19, evaluator)
        b.withdraw()

        rows = compute_merit_ranking(posting=posting)
        # A wins because B withdrew despite higher score
        assert rows[0].application == a and rows[0].outcome == 'winner'
        b_row = next(r for r in rows if r.application == b)
        assert b_row.outcome == 'eliminated'

    def test_tie_broken_by_applied_at_oldest_first(self, posting, stages, evaluator):
        s_know, s_int = stages
        c_a = _candidate(30)
        c_b = _candidate(31)
        a = JobApplication.objects.create(posting=posting, candidate=c_a)
        b = JobApplication.objects.create(posting=posting, candidate=c_b)
        _eval(a, s_know, 17, evaluator); _eval(a, s_int, 17, evaluator)
        _eval(b, s_know, 17, evaluator); _eval(b, s_int, 17, evaluator)
        # A applied first (created earlier)
        rows = compute_merit_ranking(posting=posting)
        assert rows[0].application == a

    def test_idempotent_recompute(self, posting, stages, evaluator):
        s_know, s_int = stages
        c_a = _candidate(40)
        a = JobApplication.objects.create(posting=posting, candidate=c_a)
        _eval(a, s_know, 18, evaluator); _eval(a, s_int, 16, evaluator)

        compute_merit_ranking(posting=posting)
        compute_merit_ranking(posting=posting)
        assert MeritRanking.objects.filter(posting=posting).count() == 1

    def test_breakdown_includes_per_stage_detail(self, posting, stages, evaluator):
        s_know, s_int = stages
        c_a = _candidate(50)
        a = JobApplication.objects.create(posting=posting, candidate=c_a)
        _eval(a, s_know, 18, evaluator); _eval(a, s_int, 16, evaluator)

        rows = compute_merit_ranking(posting=posting)
        breakdown = rows[0].score_breakdown
        assert str(s_know.id) in breakdown
        assert str(s_int.id) in breakdown
        assert breakdown[str(s_know.id)]['weight'] == '60.00'
        assert breakdown[str(s_know.id)]['weighted'] == '10.80'
        assert breakdown[str(s_int.id)]['weighted'] == '6.40'

    def test_requested_count_2_creates_2_winners(
        self, posting, stages, evaluator,
    ):
        # Bump requested_count to 2
        posting.requisition.requested_count = 2
        posting.requisition.save()
        s_know, s_int = stages
        a = JobApplication.objects.create(posting=posting, candidate=_candidate(60))
        b = JobApplication.objects.create(posting=posting, candidate=_candidate(61))
        c = JobApplication.objects.create(posting=posting, candidate=_candidate(62))
        _eval(a, s_know, 18, evaluator); _eval(a, s_int, 18, evaluator)
        _eval(b, s_know, 16, evaluator); _eval(b, s_int, 16, evaluator)
        _eval(c, s_know, 14, evaluator); _eval(c, s_int, 14, evaluator)

        rows = compute_merit_ranking(posting=posting)
        assert rows[0].outcome == 'winner'
        assert rows[1].outcome == 'winner'
        assert rows[2].outcome == 'waiting_list'

    def test_unique_per_posting_application(self):
        names = {c.name for c in MeritRanking._meta.constraints}
        assert 'unique_ranking_per_posting_application' in names
