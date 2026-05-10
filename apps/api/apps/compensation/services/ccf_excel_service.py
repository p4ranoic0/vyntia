"""CCF Excel import + template export service (Ley 30709)."""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation
from io import BytesIO
from typing import Optional

from django.db import transaction
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill

from apps.compensation.models import (
    Category,
    CategoryFactorScore,
    CategoryFunctionTable,
    JobSubfactor,
    SalaryBand,
)
from apps.compensation.services.scoring_service import recompute_category_total


# Fixed columns (per category row); subfactor columns appended dynamically.
FIXED_COLUMNS = [
    "code",
    "name",
    "description",
    "functions_summary",
    "min_education",
    "min_experience_years",
    "salary_min",
    "salary_mid",
    "salary_max",
]


def export_template() -> BytesIO:
    """Export a blank .xlsx template for CCF import.

    Headers: fixed columns + one column per active JobSubfactor (named by code).
    The template includes a single helper row commented out (just hints in the
    first data row using gray fill) so users see expected formats.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "CCF"

    subfactors = list(
        JobSubfactor.objects.filter(is_active=True).order_by("factor__kind", "code")
    )
    headers = list(FIXED_COLUMNS) + [f"factor_{s.code}" for s in subfactors]

    # Header row with styling
    header_font = Font(bold=True, color="FFFFFFFF")
    header_fill = PatternFill(start_color="FF2563EB", end_color="FF2563EB",
                              fill_type="solid")
    for col_idx, name in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx, value=name)
        cell.font = header_font
        cell.fill = header_fill

    # Hint row with sample values (greyed out, optional — user can delete)
    hint_fill = PatternFill(start_color="FFF3F4F6", end_color="FFF3F4F6",
                            fill_type="solid")
    sample_fixed = [
        "CAT-001", "Analista I",
        "Categoría para analistas junior",
        "Análisis de datos, soporte a usuarios, generación de reportes.",
        "Universitario titulado", 2,
        2000, 3000, 4000,
    ]
    sample_scores = [50] * len(subfactors)
    sample_row = sample_fixed + sample_scores
    for col_idx, val in enumerate(sample_row, start=1):
        cell = ws.cell(row=2, column=col_idx, value=val)
        cell.fill = hint_fill

    # Reasonable column widths
    for col_idx in range(1, len(headers) + 1):
        ws.column_dimensions[ws.cell(row=1, column=col_idx).column_letter].width = 22

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


@dataclass
class CCFImportResult:
    """Outcome of an Excel CCF import attempt."""
    success: bool
    ccf_id: Optional[str] = None
    categories_created: int = 0
    bands_created: int = 0
    scores_created: int = 0
    row_errors: list[dict] = field(default_factory=list)
    fatal_error: Optional[str] = None


def import_ccf(*, file, tenant=None, ccf_title: str, user=None) -> CCFImportResult:
    """Import a CCF from an uploaded .xlsx file.

    All-or-nothing: any row error rolls back the entire import. Errors are
    collected per-row and returned in `row_errors`.

    Args:
        file: file-like object (or Django UploadedFile).
        tenant: Tenant instance for the new CCF + Category rows.
        ccf_title: Title for the new CategoryFunctionTable.
        user: User who triggered the import (set as created_by).

    Returns:
        CCFImportResult with success flag, IDs, counts, and row_errors list.
    """
    result = CCFImportResult(success=False)

    try:
        wb = load_workbook(filename=file, data_only=True)
        ws = wb.active
    except Exception as e:
        result.fatal_error = f"No se pudo abrir el archivo: {e}"
        return result

    # Parse headers (row 1)
    raw_headers = [str(c.value or "").strip() for c in ws[1]]
    if not raw_headers or raw_headers[0] != "code":
        result.fatal_error = (
            "El archivo no tiene la cabecera esperada. La primera columna "
            "debe ser 'code'. Descargue la plantilla y vuelva a intentar."
        )
        return result

    # Map subfactor code → JobSubfactor (subfactor columns start after FIXED_COLUMNS)
    subfactor_columns: list[tuple[int, JobSubfactor]] = []
    for col_idx, header in enumerate(raw_headers[len(FIXED_COLUMNS):], start=len(FIXED_COLUMNS)):
        if not header.startswith("factor_"):
            continue
        code = header.replace("factor_", "", 1)
        sub = JobSubfactor.objects.filter(code=code, is_active=True).first()
        if sub is not None:
            subfactor_columns.append((col_idx, sub))

    # Parse rows
    parsed_rows: list[dict] = []
    row_errors: list[dict] = []
    for row_num, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
        if not any(c is not None and str(c).strip() != "" for c in row):
            continue  # blank row

        code = (row[0] or "").strip() if row[0] else ""
        if not code:
            row_errors.append({"row": row_num, "error": "'code' es requerido."})
            continue

        try:
            min_exp = int(row[5] or 0)
            if min_exp < 0:
                raise ValueError("min_experience_years debe ser >= 0")
            salary_min = _to_decimal(row[6], "salary_min")
            salary_mid = _to_decimal(row[7], "salary_mid")
            salary_max = _to_decimal(row[8], "salary_max")
            if not (salary_min < salary_mid < salary_max):
                raise ValueError("salary_min < salary_mid < salary_max requerido")
        except ValueError as e:
            row_errors.append({"row": row_num, "code": code, "error": str(e)})
            continue

        scores: list[tuple[JobSubfactor, int]] = []
        score_error = None
        for col_idx, sub in subfactor_columns:
            raw_score = row[col_idx] if col_idx < len(row) else None
            if raw_score is None or str(raw_score).strip() == "":
                continue
            try:
                score_int = int(raw_score)
            except (TypeError, ValueError):
                score_error = f"factor_{sub.code} no es entero válido: {raw_score!r}"
                break
            if score_int < 0 or score_int > sub.max_score:
                score_error = (
                    f"factor_{sub.code}={score_int} fuera de rango "
                    f"[0..{sub.max_score}]"
                )
                break
            scores.append((sub, score_int))
        if score_error:
            row_errors.append({"row": row_num, "code": code, "error": score_error})
            continue

        parsed_rows.append({
            "row": row_num,
            "code": code,
            "name": (row[1] or "").strip() if row[1] else "",
            "description": (row[2] or "").strip() if row[2] else "",
            "functions_summary": (row[3] or "").strip() if row[3] else "",
            "min_education": (row[4] or "").strip() if row[4] else "",
            "min_experience_years": min_exp,
            "salary_min": salary_min,
            "salary_mid": salary_mid,
            "salary_max": salary_max,
            "scores": scores,
        })

    if row_errors:
        # All-or-nothing: any error fails the import
        result.row_errors = row_errors
        return result

    if not parsed_rows:
        result.fatal_error = "El archivo no contiene categorías a importar."
        return result

    # Commit transactionally
    try:
        with transaction.atomic():
            ccf = CategoryFunctionTable.objects.create(
                tenant=tenant,
                title=ccf_title,
                created_by=user,
            )
            result.ccf_id = str(ccf.id)
            for pr in parsed_rows:
                cat = Category.objects.create(
                    tenant=tenant,
                    ccf=ccf,
                    code=pr["code"],
                    name=pr["name"],
                    description=pr["description"],
                    functions_summary=pr["functions_summary"],
                    min_education=pr["min_education"],
                    min_experience_years=pr["min_experience_years"],
                )
                result.categories_created += 1
                SalaryBand.objects.create(
                    category=cat,
                    min_salary=pr["salary_min"],
                    mid_salary=pr["salary_mid"],
                    max_salary=pr["salary_max"],
                )
                result.bands_created += 1
                for sub, score_int in pr["scores"]:
                    CategoryFactorScore.objects.create(
                        category=cat, subfactor=sub, score=score_int,
                    )
                    result.scores_created += 1
                # Recompute total_score after all scores are in
                recompute_category_total(cat)
    except Exception as e:
        result.fatal_error = f"Error al guardar: {e}"
        return result

    result.success = True
    return result


def _to_decimal(value, field_name: str) -> Decimal:
    if value is None or str(value).strip() == "":
        raise ValueError(f"{field_name} es requerido")
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError):
        raise ValueError(f"{field_name} no es un decimal válido: {value!r}")
    if d <= 0:
        raise ValueError(f"{field_name} debe ser > 0")
    return d
