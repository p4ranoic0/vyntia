"""CategoryFactorScore — Category × JobSubfactor → score (Ley 30709)."""
import uuid

from django.core.exceptions import ValidationError
from django.db import models


class CategoryFactorScore(models.Model):
    """Score for one (Category, JobSubfactor) pair.

    Drives Ley 30709 audit + R.M. 243-2018-TR methodology. The weighted
    sum of all scores (subfactor.score × subfactor.factor.weight) produces
    Category.total_score (recomputed by scoring_service.recompute_category_total).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(
        'compensation.Category',
        on_delete=models.CASCADE,
        related_name='factor_scores',
    )
    subfactor = models.ForeignKey(
        'compensation.JobSubfactor',
        on_delete=models.PROTECT,
        related_name='+',
    )
    score = models.PositiveIntegerField(
        default=0,
        help_text='Score 0..subfactor.max_score.',
    )
    notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'category_factor_score'
        ordering = ['category', 'subfactor']
        constraints = [
            models.UniqueConstraint(
                fields=['category', 'subfactor'],
                name='unique_factor_score_per_category_subfactor',
            ),
        ]

    def __str__(self):
        return f"{self.category.code} × {self.subfactor.code} = {self.score}"

    def clean(self):
        if self.score > self.subfactor.max_score:
            raise ValidationError(
                f"Score {self.score} excede max {self.subfactor.max_score} "
                f"para subfactor {self.subfactor.code}."
            )
