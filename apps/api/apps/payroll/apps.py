"""AppConfig for the `apps.payroll` Django app — VYNTIA payroll & compensation.

Bounded context for payroll processing. As of D.1b the legacy models/services
were dropped (zero-consumer after D.1a); greenfield Vyntia Pay entities are
added from D.2 (catálogo regulatorio), D.3 (Compensation), D.5 (PayrollRun),
D.6 (PaySlip), etc.

Bounded context boundary: payroll owns compensation calculation, the SUNAT
concept/tax catalog, and payroll-period entities. Personal data lives in
`apps.employees`, contract/employment data in `apps.contracts`, document
storage in `apps.documents`.
"""

from django.apps import AppConfig


class PayrollConfig(AppConfig):
    name = "apps.payroll"
    label = "payroll"
    verbose_name = "VYNTIA Payroll"
