"""Seed the vendor regulatory catalog (TaxParameter + PayrollConcept + RegimenConfig).

Idempotent: upserts by the model's natural key. Values cite Peruvian normativa
(INVENTORY § 5 N06/N07/N09). NOT a regulatory sign-off gate — D.4's golden
cartilla validates the numbers downstream.
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.payroll.models import PayrollConcept, RegimenConfig, TaxParameter

D = Decimal

# (code, value, unit, valid_from, valid_to, source_law, metadata)
# UIT/RMV/asig: latest known year (2026) has valid_to=None so forward dates resolve
# until the next D.S. is published and seeded (ADR-D.6).
TAX_PARAMETERS = [
    ("UIT", D("5150"), "PEN", date(2024, 1, 1), date(2024, 12, 31), "D.S. 309-2023-EF", {}),
    ("UIT", D("5350"), "PEN", date(2025, 1, 1), date(2025, 12, 31), "D.S. 260-2024-EF", {}),
    ("UIT", D("5500"), "PEN", date(2026, 1, 1), None, "D.S. 2026 (pending cite)", {}),
    ("RMV", D("1025"), "PEN", date(2024, 1, 1), date(2024, 12, 31), "D.S. 003-2022-TR", {}),
    ("RMV", D("1130"), "PEN", date(2025, 1, 1), None, "D.S. 2024-TR", {}),
    ("ASIG_FAMILIAR", D("102.50"), "PEN", date(2024, 1, 1), date(2024, 12, 31), "10% RMV (N08-33)", {}),
    ("ASIG_FAMILIAR", D("113.00"), "PEN", date(2025, 1, 1), None, "10% RMV (N08-33)", {}),
    ("ONP_RATE", D("0.1300"), "RATE", date(2024, 1, 1), None, "N07-10", {}),
    ("ESSALUD_RATE", D("0.0900"), "RATE", date(2024, 1, 1), None, "N07-13", {}),
    ("EPS_CREDIT_RATE", D("0.0225"), "RATE", date(2024, 1, 1), None, "N07-19", {}),
    ("AFP_FONDO_RATE", D("0.1000"), "RATE", date(2024, 1, 1), None, "N07-01", {}),
    ("PRIMA_SISCO_RATE", D("0.0137"), "RATE", date(2026, 1, 1), None, "N07-02", {}),
    ("RMA_SISCO", D("12598.91"), "PEN", date(2026, 4, 1), date(2026, 6, 30), "SBS Abr-Jun 2026 (N07-03)", {}),
    # AFP commission rates (flujo) — N07-04
    ("AFP_INTEGRA_FLUJO", D("0.0155"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    ("AFP_PRIMA_FLUJO", D("0.0160"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    ("AFP_PROFUTURO_FLUJO", D("0.0169"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    ("AFP_HABITAT_FLUJO", D("0.0147"), "RATE", date(2024, 1, 1), None, "N07-04", {}),
    # Renta 5ta progressive brackets 2026 (N09-04/05) — metadata holds soles bounds
    ("RENTA_5TA_TRAMO_1", D("0.08"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_max": 5}),
    ("RENTA_5TA_TRAMO_2", D("0.14"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 5, "uit_max": 20}),
    ("RENTA_5TA_TRAMO_3", D("0.17"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 20, "uit_max": 35}),
    ("RENTA_5TA_TRAMO_4", D("0.20"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 35, "uit_max": 45}),
    ("RENTA_5TA_TRAMO_5", D("0.30"), "RATE", date(2024, 1, 1), None, "N09-04", {"uit_min": 45}),
    ("RENTA_5TA_DEDUCCION_UIT", D("7"), "UIT", date(2024, 1, 1), None, "N09-02", {}),
]

# (code, sunat_code, name, category, subcategory, IT, AFP, ES, CTS, GRA, remun, variable)
# Flags per INVENTORY § 5 N06-20..N06-39 + Ley 30334 (grati no EsSalud).
CONCEPTS = [
    ("BASIC_SALARY", "0101", "Remuneración básica", "INCOME", "BASIC", 1, 1, 1, 1, 1, 1, 0),
    ("ALIMENTACION_ESPECIE", "0102", "Alimentación principal en especie", "INCOME", "BASIC", 1, 1, 1, 1, 1, 1, 0),
    ("COMISIONES", "0103", "Comisiones regulares", "INCOME", "VARIABLE", 1, 1, 1, 1, 1, 1, 1),
    ("ASIG_FAMILIAR", "0104", "Asignación familiar", "INCOME", "BASIC", 1, 1, 1, 1, 1, 1, 0),
    ("OVERTIME", "0106", "Horas extras", "INCOME", "VARIABLE", 1, 1, 1, 1, 1, 1, 1),
    ("VACATION_PAY", "0107", "Vacaciones", "INCOME", "BASIC", 1, 1, 1, 0, 1, 1, 0),
    ("REINTEGROS", "0108", "Reintegros", "INCOME", "VARIABLE", 1, 1, 1, 0, 1, 1, 1),
    ("GRATI_FP", "0109", "Gratificación Fiestas Patrias", "INCOME", "EXTRAORDINARY", 1, 1, 0, 0, 0, 1, 0),
    ("GRATI_NAV", "0110", "Gratificación Navidad", "INCOME", "EXTRAORDINARY", 1, 1, 0, 0, 0, 1, 0),
    ("GRATI_TRUNCA", "0111", "Gratificación trunca", "INCOME", "EXTRAORDINARY", 1, 1, 0, 0, 0, 1, 0),
    ("BONIF_EXTRA_30334", "0121", "Bonificación extraordinaria Ley 30334", "INCOME", "EXTRAORDINARY", 1, 0, 0, 0, 0, 0, 0),
    ("MOVILIDAD_SUPEDITADA", "0115", "Movilidad supeditada a asistencia", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("REFRIGERIO", "0116", "Refrigerio no principal", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("CTS", "0120", "Compensación por Tiempo de Servicios", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("INDEM_VAC_NO_GOZADAS", "0501", "Indemnización vacaciones no gozadas", "INCOME", "EXTRAORDINARY", 1, 0, 0, 0, 0, 0, 0),
    ("INDEM_DESPIDO", "0503", "Indemnización por despido arbitrario", "INCOME", "EXTRAORDINARY", 0, 0, 0, 0, 0, 0, 0),
    ("AFP_FONDO", "0601", "Aporte obligatorio AFP (fondo)", "DEDUCTION", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("RENTA_5TA", "0605", "Retención Renta 5ta categoría", "TAX", "INCOME_TAX", 0, 0, 0, 0, 0, 0, 0),
    ("AFP_COMISION_PRIMA", "0606", "Comisión + Prima AFP", "DEDUCTION", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("AFP_VOLUNTARIO", "0607", "Aporte voluntario AFP", "DEDUCTION", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("ESSALUD", "0801", "Aporte EsSalud 9%", "CONTRIBUTION_EMPLOYER", "HEALTH", 0, 0, 0, 0, 0, 0, 0),
    # Present but not applicable for MVP 728 oficinas (#24, #25) — is_active=False handled below
    ("SCTR_SALUD", "0803", "SCTR Salud", "CONTRIBUTION_EMPLOYER", "HEALTH", 0, 0, 0, 0, 0, 0, 0),
    ("SCTR_PENSION", "0804", "SCTR Pensiones", "CONTRIBUTION_EMPLOYER", "PENSION", 0, 0, 0, 0, 0, 0, 0),
    ("SENATI", "0805", "SENATI", "CONTRIBUTION_EMPLOYER", "BASIC", 0, 0, 0, 0, 0, 0, 0),
    ("SENCICO", "0806", "SENCICO", "CONTRIBUTION_EMPLOYER", "BASIC", 0, 0, 0, 0, 0, 0, 0),
]
_INACTIVE_CODES = {"SCTR_SALUD", "SCTR_PENSION", "SENATI", "SENCICO"}  # #24, #25

REGIMEN_728 = dict(
    regimen_code="728", valid_from=date(2024, 1, 1), valid_to=None,
    vacation_days_annual=30, applies_asignacion_familiar=True,
    applies_cts=True, applies_gratification=True,
    cts_deposit_months=[5, 11], gratification_months=[7, 12],
    severance_indemnization_formula="1_5_SALARIES_PER_YEAR_CAPPED_12",
    policy_notes="Régimen laboral privado D.Leg. 728 (N01).",
)


class Command(BaseCommand):
    help = "Seed the vendor regulatory catalog (idempotent)."

    @transaction.atomic
    def handle(self, *args, **options):
        tp = self._seed_tax_parameters()
        pc = self._seed_concepts()
        rc = self._seed_regimen()
        self.stdout.write(self.style.SUCCESS(
            f"Catalog seeded: {tp} tax params, {pc} concepts, {rc} régimen configs."
        ))

    def _seed_tax_parameters(self):
        n = 0
        for code, value, unit, vfrom, vto, law, meta in TAX_PARAMETERS:
            TaxParameter.objects.update_or_create(
                code=code, valid_from=vfrom,
                defaults=dict(value=value, unit=unit, valid_to=vto, source_law=law, metadata=meta),
            )
            n += 1
        return n

    def _seed_concepts(self):
        n = 0
        for code, sunat, name, cat, sub, it, afp, es, cts, gra, remun, var in CONCEPTS:
            PayrollConcept.objects.update_or_create(
                tenant=None, code=code,
                defaults=dict(
                    sunat_code=sunat, name=name, category=cat, subcategory=sub,
                    affects_income_tax=bool(it), affects_afp_onp=bool(afp),
                    affects_essalud=bool(es), affects_cts=bool(cts),
                    affects_gratification=bool(gra), is_remunerative=bool(remun),
                    is_variable=bool(var), is_active=code not in _INACTIVE_CODES,
                ),
            )
            n += 1
        return n

    def _seed_regimen(self):
        RegimenConfig.objects.update_or_create(
            regimen_code="728", valid_from=REGIMEN_728["valid_from"],
            defaults={k: v for k, v in REGIMEN_728.items() if k not in ("regimen_code", "valid_from")},
        )
        return 1
