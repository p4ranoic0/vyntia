"""severance_service — minimum legal severance calculation (B.14, ADR-B.9).

4 componentes obligatorios (LCT 728 + base aplicable a 276/CAS con caveats):
- CTS proporcional del semestre en curso
- Vacaciones truncas por días no gozados
- Gratificación trunca del semestre en curso
- Indemnización por despido arbitrario / indirecto (cuando aplica)

Ámbito explícito (ADR-B.9): no incluye AFP/ONP, Renta 5ta, saldos depositados
de CTS anteriores, multi-régimen variantes. El motor de planilla completo vive
en sub-proyecto D (Vyntia Pay).

Fuentes: D.S. 003-97-TR (LPCL consolidado), D.S. 001-97-TR (CTS), Ley 27735
(Gratificaciones).
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from apps.contracts.models import (
    SeveranceLine,
    SeveranceSettlement,
    Termination,
)


TWOPLACES = Decimal('0.01')
CAUSALES_INDEMNIZACION = {'despido_arbitrario', 'despido_indirecto'}


def _quantize(value) -> Decimal:
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(TWOPLACES, rounding=ROUND_HALF_UP)


def _months_between(start: date, end: date) -> int:
    """Whole months between two dates (inclusive end)."""
    if end < start:
        return 0
    months = (end.year - start.year) * 12 + (end.month - start.month)
    if end.day >= start.day:
        months += 1
    return max(months, 0)


def _current_semester_start(reference: date) -> date:
    """Inicio del semestre en curso para CTS (mayo-octubre / noviembre-abril).

    Convención CTS peruana: depósitos en mayo (semestre noviembre-abril) y
    noviembre (semestre mayo-octubre). El "semestre en curso" depende del mes
    del cese.
    """
    if 5 <= reference.month <= 10:
        return date(reference.year, 5, 1)
    if reference.month >= 11:
        return date(reference.year, 11, 1)
    # Enero-abril: semestre noviembre-abril del año pasado.
    return date(reference.year - 1, 11, 1)


def _current_gratification_semester_start(reference: date) -> date:
    """Inicio del semestre vigente para gratificación (enero-junio / julio-diciembre)."""
    if reference.month <= 6:
        return date(reference.year, 1, 1)
    return date(reference.year, 7, 1)


# ---------------------------- Component calculators ----------------------------

def _compute_cts(sueldo: Decimal, fecha_inicio: date, fecha_cese: date) -> tuple[Decimal, dict, str]:
    """CTS proporcional del semestre en curso."""
    semestre_inicio = _current_semester_start(fecha_cese)
    inicio = max(fecha_inicio, semestre_inicio)
    meses = _months_between(inicio, fecha_cese)
    meses = min(meses, 6)
    # Fórmula simplificada (ADR-B.9 minimum legal): sueldo/12 × meses + 1/6 grati
    # se aproxima a (sueldo × meses) / 6 cuando no hay grati histórica disponible.
    amount = (sueldo * Decimal(meses)) / Decimal('6')
    # Cap defensivo: no exceder un sueldo completo en el semestre.
    if amount > sueldo:
        amount = sueldo
    base = {
        'sueldo': str(sueldo),
        'semestre_inicio': semestre_inicio.isoformat(),
        'meses_semestre': meses,
        'formula': '(sueldo × meses_semestre) / 6, capped at sueldo',
    }
    return _quantize(amount), base, 'CTS proporcional D.S. 001-97-TR'


def _compute_vac_truncas(
    sueldo: Decimal, fecha_inicio: date, fecha_cese: date,
    dias_acumulados_no_gozados: Decimal | None = None,
) -> tuple[Decimal, dict, str]:
    """Vacaciones truncas: días por mes trabajado del último año × jornal."""
    inicio_año = date(fecha_cese.year, fecha_cese.month, fecha_cese.day)
    inicio_año = max(
        fecha_inicio,
        date(fecha_cese.year - 1, fecha_cese.month, fecha_cese.day)
        if fecha_cese >= date(fecha_cese.year, fecha_cese.month, 1)
        else fecha_inicio,
    )
    meses = _months_between(inicio_año, fecha_cese)
    meses = min(meses, 12)
    dias_proporcionales = Decimal(meses) * Decimal('2.5')
    if dias_acumulados_no_gozados is not None and dias_acumulados_no_gozados > 0:
        dias_proporcionales = max(dias_proporcionales, dias_acumulados_no_gozados)
    jornal = sueldo / Decimal('30')
    amount = jornal * dias_proporcionales
    base = {
        'sueldo': str(sueldo),
        'jornal': str(_quantize(jornal)),
        'meses_año': meses,
        'dias_proporcionales': str(dias_proporcionales),
        'dias_acumulados_input': str(dias_acumulados_no_gozados or 0),
        'formula': 'jornal × (meses_año × 2.5 días)',
    }
    return _quantize(amount), base, 'Vacaciones truncas D.S. 012-92-TR'


def _compute_grat_trunca(sueldo: Decimal, fecha_inicio: date, fecha_cese: date) -> tuple[Decimal, dict, str]:
    """Gratificación trunca del semestre vigente."""
    semestre_inicio = _current_gratification_semester_start(fecha_cese)
    inicio = max(fecha_inicio, semestre_inicio)
    meses = _months_between(inicio, fecha_cese)
    meses = min(meses, 6)
    amount = (sueldo * Decimal(meses)) / Decimal('6')
    base = {
        'sueldo': str(sueldo),
        'semestre_inicio': semestre_inicio.isoformat(),
        'meses_semestre': meses,
        'formula': '(sueldo × meses_semestre) / 6',
    }
    return _quantize(amount), base, 'Gratificación trunca Ley 27735'


def _compute_indemnizacion(
    sueldo: Decimal, fecha_inicio: date, fecha_cese: date, causal: str,
) -> tuple[Decimal, dict, str]:
    """Indemnización despido arbitrario: 1.5 sueldos/año, capped 12 sueldos.

    Años se calcula como (fecha_cese - fecha_inicio).days / 365 (no usamos
    _months_between para evitar +1 inclusivo que infla el resultado en plazos
    redondos como 730 días).
    """
    if causal not in CAUSALES_INDEMNIZACION:
        return Decimal('0'), {
            'aplicable': False,
            'causal': causal,
        }, 'No aplica (causal sin derecho a indemnización)'
    dias = max((fecha_cese - fecha_inicio).days, 0)
    años = Decimal(dias) / Decimal('365')
    monto = sueldo * Decimal('1.5') * años
    cap = sueldo * Decimal('12')
    if monto > cap:
        monto = cap
    base = {
        'sueldo': str(sueldo),
        'dias_servicio': dias,
        'años': str(_quantize(años)),
        'cap_sueldos': 12,
        'aplicable': True,
        'causal': causal,
        'formula': 'sueldo × 1.5 × (días_servicio / 365), capped at 12 sueldos',
    }
    return _quantize(monto), base, 'Indemnización por despido arbitrario LPCL Art. 38'


# ---------------------------- Public API ----------------------------

@transaction.atomic
def compute_settlement(
    termination: Termination,
    *,
    user=None,
    dias_acumulados_no_gozados: Decimal | None = None,
) -> SeveranceSettlement:
    """Compute the 4 minimum-legal severance lines + persist totals.

    Idempotente: si ya existe un settlement para este termination, recalcula
    las líneas (delete + recreate) y refresca total.
    """
    contract = termination.contract
    sueldo = Decimal(contract.salario_bruto or 0)
    fecha_inicio = contract.fecha_inicio
    fecha_cese = termination.fecha_cese

    settlement, _ = SeveranceSettlement.objects.get_or_create(
        termination=termination,
        defaults={
            'tenant': termination.tenant,
            'sueldo_base': sueldo,
            'fecha_inicio_contrato': fecha_inicio,
            'fecha_cese': fecha_cese,
        },
    )
    # Refresh snapshot fields (en caso de re-compute con datos actualizados).
    settlement.sueldo_base = sueldo
    settlement.fecha_inicio_contrato = fecha_inicio
    settlement.fecha_cese = fecha_cese

    # Wipe existing lines to recompute cleanly.
    settlement.lines.all().delete()

    components = [
        ('cts', _compute_cts(sueldo, fecha_inicio, fecha_cese)),
        ('vac_truncas', _compute_vac_truncas(
            sueldo, fecha_inicio, fecha_cese, dias_acumulados_no_gozados,
        )),
        ('grat_trunca', _compute_grat_trunca(sueldo, fecha_inicio, fecha_cese)),
        ('indemnizacion', _compute_indemnizacion(
            sueldo, fecha_inicio, fecha_cese, termination.causal,
        )),
    ]
    for component_code, (amount, base, note) in components:
        SeveranceLine.objects.create(
            settlement=settlement,
            component=component_code,
            amount=amount,
            base_calculation=base,
            formula_note=note,
        )

    settlement.recompute_total()
    settlement.mark_computed(user=user)
    return settlement


def mark_paid(
    settlement: SeveranceSettlement, *, paid_total, user=None, paid_at=None,
) -> SeveranceSettlement:
    settlement.mark_paid(paid_total=paid_total, user=user, paid_at=paid_at)
    return settlement
