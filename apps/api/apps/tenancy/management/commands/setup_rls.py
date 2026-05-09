"""setup_rls — apply PostgreSQL RLS policies to tenant-scoped tables.

Usage:
    manage.py setup_rls           # apply roles + policies (idempotent)
    manage.py setup_rls --check   # verify policies exist, exit 1 if missing
    manage.py setup_rls --verbose-sql # log every SQL statement

This command requires CREATEROLE + table-owner privileges. Typically run
as the postgres superuser during deploys.

Architecture: see docs/superpowers/specs/2026-05-09-vyntia-multitenancy-rls-design.md § 4
Runbook: see docs/operations/rls-setup.md
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Apply PostgreSQL RLS roles and policies to tenant-scoped tables (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--check",
            action="store_true",
            help="Verify policies exist on every tenant-scoped table; do not apply changes.",
        )
        parser.add_argument(
            "--verbose-sql",
            action="store_true",
            help="Print every SQL statement before executing.",
        )

    def handle(self, *args, **options):
        if options["check"]:
            self._handle_check()
        else:
            self._handle_apply(verbose=options["verbose_sql"])

    def _handle_apply(self, verbose):
        self.stdout.write(self.style.NOTICE("setup_rls: scaffold — Tasks 2-5 fill this in"))

    def _handle_check(self):
        self.stdout.write(self.style.NOTICE("setup_rls --check: scaffold — Task 5 fills this in"))
