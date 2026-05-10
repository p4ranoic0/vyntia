"""Scoring service — recomputes Category.total_score from factor scores.

Per Ley 30709 / R.M. 243-2018-TR: total puntaje = sum(score × factor.weight/100)
across all CategoryFactorScore rows attached to the Category.
"""
from decimal import Decimal


def recompute_category_total(category):
    """Recompute and persist Category.total_score.

    Args:
        category: Category instance.

    Returns:
        Decimal: the new total_score (also written to category.total_score).
    """
    from apps.compensation.models import CategoryFactorScore

    scores = (
        CategoryFactorScore.objects.select_related('subfactor', 'subfactor__factor')
        .filter(category=category)
    )
    total = Decimal('0.00')
    for s in scores:
        # subfactor.factor.weight is a % (0..100); convert to multiplier.
        weight_multiplier = s.subfactor.factor.weight / Decimal('100.00')
        total += Decimal(s.score) * weight_multiplier
    # Quantize to 2 decimal places to match field precision
    total = total.quantize(Decimal('0.01'))
    category.total_score = total
    category.save(update_fields=['total_score', 'updated_at'])
    return total
