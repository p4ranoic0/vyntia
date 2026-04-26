"""AppConfig for the `apps.core` Django app — VYNTIA platform utilities.

This app contains transversal utilities used across all bounded contexts:
- APIResponse, pagination, exception handler (DRF integration)
- Decorators for auth/role checks
- Custom middleware (security headers, JWT cookie, audit, performance)
- Database router
- Validators (email, phone, RUT)

`apps.core` has NO models — it's pure utility. Bounded contexts (employees,
contracts, payroll, etc.) depend on `apps.core` but never the reverse.
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "apps.core"
    label = "core_utils"
    verbose_name = "VYNTIA Core Utilities"
