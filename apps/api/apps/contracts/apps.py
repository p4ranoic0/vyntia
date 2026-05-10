"""AppConfig for the `apps.contracts` Django app — VYNTIA employment relationship.

Owns the contractual/employment-relationship entities of an employee:
- Contract (immutable issued employment contract)
- ContractAmendment (amendments linked via parent_contract FK; e.g., sueldo
  updates, plazo extensions, addenda)
- EmploymentData (current employment data: position, work modality, salary base,
  schedule, direct supervisor, regimen laboral peruano)

Bounded context boundary: contracts captures HOW someone is employed —
the legal contract instrument and the operational employment terms. Personal
data of the employee lives in `apps.employees`. Compensation calculations
(payroll runs, deductions, AFP/SUNAT) live in `apps.payroll` (L3.7).

Model split completed in L3.10.3 (2026-04-27); Contract and ContractAmendment
are now separate models (previously unified via numero_adenda nullable field).
See L3.10.3 plan for context.
"""

from django.apps import AppConfig


class ContractsConfig(AppConfig):
    name = "apps.contracts"
    label = "contracts"
    verbose_name = "VYNTIA Contracts"
