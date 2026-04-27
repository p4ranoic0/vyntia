"""AppConfig for the `apps.contracts` Django app — VYNTIA employment relationship.

Owns the contractual/employment-relationship entities of an employee:
- Contract (employment contract — initial contract or amendment/adenda;
  unified table that handles both via numero_adenda nullable)
- EmploymentData (current employment data: position, work modality, salary base,
  schedule, direct supervisor, regimen laboral peruano)

Bounded context boundary: contracts captures HOW someone is employed —
the legal contract instrument and the operational employment terms. Personal
data of the employee lives in `apps.employees`. Compensation calculations
(payroll runs, deductions, AFP/SUNAT) live in `apps.payroll` (L3.7).

Future split (deferred to L3.10/post-rename):
- Contract → Contract + ContractAmendment (model split + data migration)
- EmploymentData → EmploymentData (rename only)
"""

from django.apps import AppConfig


class ContractsConfig(AppConfig):
    name = "apps.contracts"
    label = "contracts"
    verbose_name = "VYNTIA Contracts"
