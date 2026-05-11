"""ranking_service — algoritmo de cuadro de méritos para Selección (B.9).

Algoritmo:
1. Para cada JobApplication de la posting:
   a. Si la app está en estado terminal 'eliminated'/'rejected'/'withdrawn',
      o falló alguna stage eliminatoria (passed=False en eliminatoria),
      → outcome='eliminated', total_score=0.
   b. En otro caso:
      total_score = sum(eval.score × stage.weight / 100) sobre todas las
      evaluaciones existentes. Stages sin evaluación cuentan como 0.
2. Ordena por total_score DESC, desempata por applied_at ASC (más antiguo
   primero).
3. Asigna rank = 1..N. outcome:
   - rank == 1 → 'winner' (limitado a posting.requisition.requested_count;
     si requested_count > 1, los primeros K son winners).
   - resto sin eliminar → 'waiting_list'.
   - eliminados → 'eliminated' (rank al final, ordenados por applied_at).
4. Atómico: borra rankings previos del posting y crea nuevos.
"""
from decimal import Decimal

from django.db import transaction


def _is_failed_in_eliminatoria(application, evaluations_by_app_stage):
    """Did this application fail any eliminatoria stage it was evaluated in?"""
    for stage in application.posting.stages.filter(is_eliminatoria=True):
        ev = evaluations_by_app_stage.get((application.id, stage.id))
        if ev is not None and not ev.passed:
            return True
    return False


def _compute_weighted_total(application, stages, evaluations_by_app_stage):
    """Sum eval.score × stage.weight / 100 across all stages."""
    total = Decimal('0.00')
    breakdown = {}
    for stage in stages:
        ev = evaluations_by_app_stage.get((application.id, stage.id))
        score = ev.score if ev else Decimal('0.00')
        weighted = (score * stage.weight) / Decimal('100')
        total += weighted
        breakdown[str(stage.id)] = {
            'name': stage.name or stage.get_kind_display(),
            'order': stage.order,
            'score': str(score),
            'weight': str(stage.weight),
            'weighted': str(weighted.quantize(Decimal('0.01'))),
            'passed': bool(ev.passed) if ev else None,
        }
    return total.quantize(Decimal('0.01')), breakdown


@transaction.atomic
def compute_merit_ranking(*, posting):
    """(Re)compute MeritRanking rows for a posting.

    Args:
        posting: JobPosting instance to rank.

    Returns:
        List of MeritRanking rows (in rank order) just persisted.
    """
    from apps.employees.models import (
        CandidateEvaluation,
        JobApplication,
        MeritRanking,
    )

    stages = list(posting.stages.all().order_by('order'))
    applications = list(
        posting.applications.select_related('candidate').order_by('applied_at'),
    )
    evaluations = CandidateEvaluation.objects.filter(
        application__posting=posting,
    ).select_related('stage')
    evaluations_by_app_stage = {
        (e.application_id, e.stage_id): e for e in evaluations
    }

    qualified = []  # [(application, total_score, breakdown), ...]
    eliminated = []  # [(application, breakdown), ...]

    for app in applications:
        terminal_eliminated = app.status in (
            'eliminated', 'rejected', 'withdrawn',
        )
        failed_eliminatoria = _is_failed_in_eliminatoria(
            app, evaluations_by_app_stage,
        )
        total, breakdown = _compute_weighted_total(
            app, stages, evaluations_by_app_stage,
        )
        if terminal_eliminated or failed_eliminatoria:
            eliminated.append((app, breakdown))
        else:
            qualified.append((app, total, breakdown))

    # Sort qualified by score DESC, applied_at ASC (already pre-ordered by applied_at)
    qualified.sort(key=lambda t: t[1], reverse=True)

    # Wipe and rewrite
    MeritRanking.objects.filter(posting=posting).delete()

    requested = posting.requisition.requested_count or 1

    rows = []
    rank = 1
    for app, total, breakdown in qualified:
        outcome = 'winner' if rank <= requested else 'waiting_list'
        rows.append(MeritRanking(
            posting=posting,
            application=app,
            rank=rank,
            total_score=total,
            outcome=outcome,
            score_breakdown=breakdown,
        ))
        rank += 1

    for app, breakdown in eliminated:
        rows.append(MeritRanking(
            posting=posting,
            application=app,
            rank=rank,
            total_score=Decimal('0.00'),
            outcome='eliminated',
            score_breakdown=breakdown,
        ))
        rank += 1

    MeritRanking.objects.bulk_create(rows)
    return list(MeritRanking.objects.filter(posting=posting).order_by('rank'))
