"""AppConfig for the `apps.payroll` Django app — VYNTIA payroll & compensation.

Owns the payroll-processing entities of the HR system:
- ConfiguracionAfp (AFP rates per period for pension contribution calculation)
- ConfiguracionRemuneracion (catalog of payroll concepts: incomes + deductions)
- ConfiguracionUit (annual UIT value for SUNAT/legal calculations — renta 4ta tope, ESSALUD CAS)
- PlanillaMensual (monthly payroll header per period and modality)
- DetallePlanilla (per-employee payroll detail with AFP/ONP/EsSalud/renta calculations)
- ConceptoPlanilla (variable income/deduction concepts applied per detail)
- DescuentoMasivo (bulk Excel-loaded deduction batches)
- BoletaPago (generated payroll receipts as PDF)
- CalendarioPago (scheduled payment calendars)

Owned services (payroll calculation engines):
- planilla_calculo_service.py — full monthly payroll calculation per Peruvian regimens
- descuento_masivo_service.py — bulk Excel deduction processor

Bounded context boundary: payroll owns the compensation calculation, deduction
catalog, and payroll-period entities. Personal data lives in `apps.employees`,
contract/employment data in `apps.contracts`, document storage in `apps.documents`.

NOTE: This app does NOT include the multi-régimen calculation engine (CAS/728/276
detailed routing). That's the scope of sub-project D (Vyntia Pay).

Future rename (deferred to L3.10):
- ConfiguracionUit → TaxParameter
- Remuneracion-prefixed → Compensation-prefixed
- PlanillaMensual → MonthlyPayroll
"""

from django.apps import AppConfig


class PayrollConfig(AppConfig):
    name = "apps.payroll"
    label = "payroll"
    verbose_name = "VYNTIA Payroll"
