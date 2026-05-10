"""Tests for B.7 CCF Excel import + template export."""
from decimal import Decimal
from io import BytesIO

import pytest
from django.core.management import call_command
from openpyxl import load_workbook

from apps.compensation.models import (
    Category,
    CategoryFactorScore,
    CategoryFunctionTable,
    SalaryBand,
)
from apps.compensation.services import export_template, import_ccf


@pytest.fixture
def seeded_factors(db):
    call_command("seed_job_factors")


@pytest.mark.django_db
class TestExportTemplate:
    def test_export_returns_xlsx_bytes(self, seeded_factors):
        buf = export_template()
        assert isinstance(buf, BytesIO)
        wb = load_workbook(buf)
        assert wb.active.title == "CCF"

    def test_template_includes_fixed_columns(self, seeded_factors):
        buf = export_template()
        wb = load_workbook(buf)
        ws = wb.active
        headers = [c.value for c in ws[1]]
        assert "code" in headers
        assert "name" in headers
        assert "salary_min" in headers
        assert "salary_mid" in headers
        assert "salary_max" in headers

    def test_template_includes_subfactor_columns(self, seeded_factors):
        buf = export_template()
        wb = load_workbook(buf)
        ws = wb.active
        headers = [c.value for c in ws[1]]
        # Expect at least one factor_<subfactor_code> column (14 subfactors seeded)
        factor_columns = [h for h in headers if h and h.startswith("factor_")]
        assert len(factor_columns) == 14


def _build_test_xlsx(rows: list[dict], subfactor_codes: list[str]) -> BytesIO:
    """Helper to construct a CCF Excel file for import tests."""
    from openpyxl import Workbook

    wb = Workbook()
    ws = wb.active
    headers = [
        "code", "name", "description", "functions_summary",
        "min_education", "min_experience_years",
        "salary_min", "salary_mid", "salary_max",
    ] + [f"factor_{c}" for c in subfactor_codes]
    ws.append(headers)
    for r in rows:
        row_values = [
            r.get("code", ""),
            r.get("name", ""),
            r.get("description", ""),
            r.get("functions_summary", ""),
            r.get("min_education", ""),
            r.get("min_experience_years", 0),
            r.get("salary_min", 0),
            r.get("salary_mid", 0),
            r.get("salary_max", 0),
        ]
        scores = r.get("scores", {})
        for code in subfactor_codes:
            row_values.append(scores.get(code, ""))
        ws.append(row_values)
    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


@pytest.mark.django_db
class TestImportCCF:
    def test_valid_import_creates_ccf_categories_bands(self, seeded_factors):
        rows = [
            {
                "code": "CAT-001", "name": "Analista I",
                "description": "Junior",
                "min_education": "Universitario",
                "min_experience_years": 2,
                "salary_min": 2000, "salary_mid": 3000, "salary_max": 4000,
                "scores": {"COMP_CONOC": 50, "RESP_PERS": 40},
            },
            {
                "code": "CAT-002", "name": "Analista II",
                "description": "Mid",
                "min_education": "Universitario",
                "min_experience_years": 4,
                "salary_min": 3500, "salary_mid": 4500, "salary_max": 5500,
                "scores": {"COMP_CONOC": 70, "RESP_PERS": 60},
            },
        ]
        buf = _build_test_xlsx(rows, ["COMP_CONOC", "RESP_PERS"])
        result = import_ccf(file=buf, ccf_title="CCF 2026")

        assert result.success is True
        assert result.categories_created == 2
        assert result.bands_created == 2
        assert result.scores_created == 4
        assert result.row_errors == []
        assert CategoryFunctionTable.objects.count() == 1
        assert Category.objects.count() == 2
        assert SalaryBand.objects.count() == 2
        assert CategoryFactorScore.objects.count() == 4

        # total_score recomputed: 50*0.25 + 40*0.30 = 12.5 + 12 = 24.5
        cat1 = Category.objects.get(code="CAT-001")
        assert cat1.total_score == Decimal("24.50")

    def test_invalid_score_rolls_back_entire_import(self, seeded_factors):
        rows = [
            {
                "code": "CAT-001", "name": "Good",
                "salary_min": 2000, "salary_mid": 3000, "salary_max": 4000,
                "scores": {"COMP_CONOC": 50},
            },
            {
                "code": "CAT-002", "name": "Bad score",
                "salary_min": 3000, "salary_mid": 4000, "salary_max": 5000,
                "scores": {"COMP_CONOC": 999},  # exceeds max 100
            },
        ]
        buf = _build_test_xlsx(rows, ["COMP_CONOC"])
        result = import_ccf(file=buf, ccf_title="CCF Bad")

        assert result.success is False
        assert any("fuera de rango" in e["error"] for e in result.row_errors)
        # Rollback: no rows committed
        assert CategoryFunctionTable.objects.count() == 0
        assert Category.objects.count() == 0
        assert SalaryBand.objects.count() == 0

    def test_invalid_salary_band_ordering_fails(self, seeded_factors):
        rows = [
            {
                "code": "CAT-X", "name": "Bad band",
                "salary_min": 4000, "salary_mid": 3000, "salary_max": 5000,
                "scores": {},
            },
        ]
        buf = _build_test_xlsx(rows, ["COMP_CONOC"])
        result = import_ccf(file=buf, ccf_title="Bad CCF")
        assert result.success is False
        assert any("salary_min < salary_mid" in e["error"] for e in result.row_errors)

    def test_empty_code_skips_with_error(self, seeded_factors):
        rows = [
            {
                "code": "", "name": "No code",
                "salary_min": 1000, "salary_mid": 2000, "salary_max": 3000,
                "scores": {},
            },
        ]
        buf = _build_test_xlsx(rows, ["COMP_CONOC"])
        result = import_ccf(file=buf, ccf_title="CCF Empty Code")
        assert result.success is False
        assert any("'code' es requerido" in e["error"] for e in result.row_errors)

    def test_missing_header_returns_fatal(self, seeded_factors):
        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.append(["NOT_CODE", "garbage"])
        ws.append(["data", "row"])
        buf = BytesIO()
        wb.save(buf)
        buf.seek(0)
        result = import_ccf(file=buf, ccf_title="CCF Bad Headers")
        assert result.success is False
        assert result.fatal_error is not None
        assert "cabecera" in result.fatal_error.lower()

    def test_round_trip_via_template(self, seeded_factors):
        """Export template → fill in 1 row → import succeeds."""
        from openpyxl import load_workbook as lw
        buf = export_template()
        wb = lw(buf)
        ws = wb.active
        # Wipe the hint row at row 2 and write a real entry
        for col_idx in range(1, ws.max_column + 1):
            ws.cell(row=2, column=col_idx, value=None)
        headers = [c.value for c in ws[1]]
        # Build row dict
        row_data = {
            "code": "RT-001", "name": "Round trip",
            "description": "test", "functions_summary": "",
            "min_education": "Universitario",
            "min_experience_years": 1,
            "salary_min": 1500, "salary_mid": 2500, "salary_max": 3500,
        }
        for col_idx, header in enumerate(headers, start=1):
            if header in row_data:
                ws.cell(row=2, column=col_idx, value=row_data[header])
            elif header and header.startswith("factor_"):
                ws.cell(row=2, column=col_idx, value=30)

        out_buf = BytesIO()
        wb.save(out_buf)
        out_buf.seek(0)
        result = import_ccf(file=out_buf, ccf_title="Round Trip CCF")
        assert result.success is True
        assert result.categories_created == 1
