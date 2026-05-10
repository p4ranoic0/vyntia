"""Compensation services — scoring, audit, Excel import/export."""
from .audit_service import compute_salary_gap_by_category, summarize_gap
from .scoring_service import recompute_category_total

__all__ = [
    "compute_salary_gap_by_category",
    "recompute_category_total",
    "summarize_gap",
]
