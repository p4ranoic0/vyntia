"""termination_service — Termination lifecycle helpers (B.14).

Encapsula la transición del Termination + las invariantes alrededor del
Contract (flip a TERMINADO en `complete_termination`) y la búsqueda de SLAs
de baja T-Registro (48 horas según el lineamiento operacional B.10).

See Module 03.7 of docs/modulos/03_gestion_empleo.md and BACKLOG #123 + #127.
"""
from __future__ import annotations

from datetime import date, timedelta

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.contracts.models import Contract, Termination


@transaction.atomic
def initiate_termination(
    *,
    contract: Contract,
    causal: str,
    fecha_cese: date,
    regimen: str = '728',
    last_day_worked: date | None = None,
    motivo: str = '',
    user=None,
    tenant=None,
) -> Termination:
    """Create a Termination header on top of an active Contract.

    Refuses if Contract.status is not ACTIVO/PENDIENTE (defensive — UI also gates).
    """
    if contract.status not in ('ACTIVO', 'PENDIENTE'):
        raise ValidationError(
            f'Cannot initiate termination for contract in status={contract.status}'
        )
    if hasattr(contract, 'termination'):
        raise ValidationError(
            'Este contrato ya tiene un cese registrado'
        )
    if tenant is None:
        tenant = getattr(contract, 'tenant', None)
    termination = Termination.objects.create(
        tenant=tenant,
        contract=contract,
        employee=contract.empleado,
        regimen=regimen,
        causal=causal,
        fecha_cese=fecha_cese,
        last_day_worked=last_day_worked or fecha_cese,
        motivo=motivo,
        status='draft',
    )
    termination.mark_in_progress(user=user)
    return termination


@transaction.atomic
def complete_termination(termination: Termination, *, user) -> Termination:
    """Promote in_progress → completed and flip Contract.status → TERMINADO."""
    termination.mark_completed(user=user)
    contract = termination.contract
    if contract.status != 'TERMINADO':
        contract.status = 'TERMINADO'
        # Save sin full_clean para no chocar con la validación fecha_fin de Contract.
        Contract.objects.filter(pk=contract.pk).update(status='TERMINADO')
    return termination


def liquidate(termination: Termination, *, user) -> Termination:
    """Promote completed → liquidated (requires settlement.paid_at)."""
    settlement = getattr(termination, 'settlement', None)
    if settlement is None or settlement.status != 'paid':
        raise ValidationError(
            'Cannot liquidate: settlement must be marked paid first'
        )
    termination.mark_liquidated(user=user)
    return termination


def mark_baja_tregistro_done(
    termination: Termination, *, declaration,
) -> Termination:
    """Link a TRegistroDeclaration(declaration_type='baja') and transition."""
    if declaration.declaration_type != 'baja':
        raise ValidationError('declaration must be of type baja')
    if declaration.contract_id != termination.contract_id:
        raise ValidationError(
            'declaration.contract does not match termination.contract'
        )
    termination.mark_baja_tregistro_done(declaration=declaration)
    return termination


def list_pending_baja_tregistro_48h(tenant=None):
    """Terminations completadas hace >48h sin baja T-Registro adjunta.

    Indicador operativo: el plazo legal para informar baja a T-Registro es
    dentro del primer día hábil después del cese (D.S. 018-2007-TR). El umbral
    de 48 horas le da al equipo RRHH una ventana razonable antes de alertar.
    """
    cutoff = timezone.now() - timedelta(hours=48)
    qs = Termination.objects.filter(
        status__in=['completed', 'liquidated'],
        completed_at__lt=cutoff,
        baja_t_registro__isnull=True,
    )
    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    return qs


def cancel_termination(termination: Termination, *, reason: str, user) -> Termination:
    termination.cancel(reason=reason, user=user)
    return termination
