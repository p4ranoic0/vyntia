"""Salary-gap audit service per Ley 30709 § 8.

For each Category, groups active employees by sex (via Position.category and
EmploymentData → Employee.genero_empleado), computes average salary, and
returns the brecha % = (male_avg - female_avg) / male_avg * 100. Alert flag
fires when |brecha| > 5%.
"""
from decimal import Decimal
from typing import Optional


def compute_salary_gap_by_category(*, tenant=None, ccf_id=None):
    """Return list of audit rows per Category.

    Args:
        tenant: optional Tenant instance to scope the audit.
        ccf_id: optional CCF UUID to limit the audit to one CCF.

    Returns:
        list[dict] — one entry per Category with:
            category_id, category_code, category_name,
            group_male: {count, avg_salary},
            group_female: {count, avg_salary},
            brecha_pct,
            alert (bool).
    """
    from apps.compensation.models import Category
    from apps.contracts.models import EmploymentData
    from apps.organization.models import Position

    qs = Category.objects.filter(is_active=True).order_by('code')
    if tenant is not None:
        qs = qs.filter(tenant=tenant)
    if ccf_id is not None:
        qs = qs.filter(ccf_id=ccf_id)

    rows: list[dict] = []
    for cat in qs:
        positions = Position.objects.filter(category=cat, is_current=True)
        emp_data = (
            EmploymentData.objects.filter(
                position__in=positions,
                estado_datos='activo',
            )
            .select_related('empleado')
        )

        male: list[EmploymentData] = []
        female: list[EmploymentData] = []
        for e in emp_data:
            gen = getattr(e.empleado, 'genero_empleado', '') or ''
            gen = gen.lower()
            if gen.startswith('m'):
                male.append(e)
            elif gen.startswith('f'):
                female.append(e)

        m_avg = _avg_salary(male)
        f_avg = _avg_salary(female)
        brecha = _compute_brecha(m_avg, f_avg)

        rows.append({
            'category_id': str(cat.id),
            'category_code': cat.code,
            'category_name': cat.name,
            'group_male': {'count': len(male), 'avg_salary': m_avg},
            'group_female': {'count': len(female), 'avg_salary': f_avg},
            'brecha_pct': brecha,
            'alert': abs(brecha) > Decimal('5.00'),
        })
    return rows


def _avg_salary(group) -> Decimal:
    if not group:
        return Decimal('0.00')
    total = Decimal('0.00')
    for g in group:
        salary = g.sueldo_basico or Decimal('0.00')
        total += Decimal(salary)
    return (total / len(group)).quantize(Decimal('0.01'))


def _compute_brecha(male_avg: Decimal, female_avg: Decimal) -> Decimal:
    """Brecha % = (male_avg - female_avg) / male_avg * 100. Quantized 2dp."""
    if male_avg <= 0:
        return Decimal('0.00')
    return ((male_avg - female_avg) / male_avg * 100).quantize(Decimal('0.01'))


def summarize_gap(rows: list[dict]) -> dict:
    """Aggregate audit rows into headline metrics for dashboard display."""
    total_categories = len(rows)
    alerted = sum(1 for r in rows if r['alert'])
    total_male = sum(r['group_male']['count'] for r in rows)
    total_female = sum(r['group_female']['count'] for r in rows)

    # Population-weighted average brecha across categories with employees of both sexes
    weighted_sum = Decimal('0.00')
    total_weight = 0
    for r in rows:
        if r['group_male']['count'] > 0 and r['group_female']['count'] > 0:
            weight = r['group_male']['count'] + r['group_female']['count']
            weighted_sum += r['brecha_pct'] * weight
            total_weight += weight
    overall_brecha = (
        (weighted_sum / total_weight).quantize(Decimal('0.01'))
        if total_weight > 0
        else Decimal('0.00')
    )

    return {
        'total_categories': total_categories,
        'alerted_categories': alerted,
        'total_male_employees': total_male,
        'total_female_employees': total_female,
        'overall_brecha_pct': overall_brecha,
    }
