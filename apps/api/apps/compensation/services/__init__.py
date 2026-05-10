"""Compensation services — scoring, audit, Excel import/export."""
from .audit_service import compute_salary_gap_by_category, summarize_gap
from .ccf_excel_service import CCFImportResult, export_template, import_ccf
from .scoring_service import recompute_category_total

__all__ = [
    "CCFImportResult",
    "compute_salary_gap_by_category",
    "export_template",
    "import_ccf",
    "recompute_category_total",
    "summarize_gap",
]
