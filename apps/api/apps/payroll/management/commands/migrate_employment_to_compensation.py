"""Snapshot active employees' current state into an initial Compensation row (D.3 / BACKLOG #40).

Reconciliation per INVENTORY § 2 salary-divergence warning:
take max(EmploymentData.sueldo_basico, Contract.salario_bruto,
        latest ContractAmendment.nuevo_salario)
and audit-log when those values diverge by > 0.01 PEN.

Idempotent: employees that already have any Compensation row are skipped.
"""

from datetime import date
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from apps.audit_lite.models import AuditEvent
from apps.contracts.models import Contract, ContractAmendment, EmploymentData
from apps.employees.models import Employee
from apps.payroll.models import Compensation

DIVERGENCE_THRESHOLD = Decimal("0.01")


class Command(BaseCommand):
    help = "Snapshot active employees into an initial Compensation row (D.3)."

    @transaction.atomic
    def handle(self, *args, **options):
        created = skipped_existing = skipped_no_data = divergences = 0
        for emp in Employee.objects.select_related("tenant").iterator():
            if Compensation.objects.filter(employee=emp).exists():
                skipped_existing += 1
                continue
            ed = (
                EmploymentData.objects.filter(empleado=emp, estado_datos="activo")
                .order_by("-fecha_inicio_contrato").first()
            )
            if ed is None:
                skipped_no_data += 1
                continue

            contract = (
                Contract.objects.filter(empleado=emp, status="ACTIVO")
                .order_by("-fecha_inicio").first()
            )
            latest_amendment = None
            if contract is not None:
                latest_amendment = (
                    ContractAmendment.objects.filter(
                        parent_contract=contract,
                        tipo_documento="ADENDA_SALARIAL",
                        nuevo_salario__isnull=False,
                    ).order_by("-fecha_inicio").first()
                )

            values = {"sueldo_basico": Decimal(ed.sueldo_basico or 0)}
            if contract is not None:
                values["salario_bruto"] = Decimal(contract.salario_bruto or 0)
            if latest_amendment is not None:
                values["amendment_nuevo_salario"] = Decimal(latest_amendment.nuevo_salario)

            base_salary = max(values.values())

            non_zero = [v for v in values.values() if v > 0]
            if non_zero and (max(non_zero) - min(non_zero)) > DIVERGENCE_THRESHOLD:
                divergences += 1
                AuditEvent.objects.create(
                    tenant=emp.tenant, actor_user=None,
                    action="payroll.compensation.migrated_with_divergence",
                    target_model="payroll.Compensation", target_id=str(emp.id),
                    payload_json={k: str(v) for k, v in values.items()},
                )

            Compensation.objects.create(
                tenant=emp.tenant, employee=emp,
                valid_from=ed.fecha_ingreso or timezone.now().date(),
                valid_to=None,
                base_salary=base_salary,
                has_family_allowance=bool(getattr(emp, "es_padre_familia", False)),
                regimen_laboral=ed.regimen_laboral,
                pension_regime=self._normalize_pension(emp.sistema_pensiones),
                afp_commission_type=(emp.tipo_comision or "") if emp.tipo_comision else "",
                cuspp=emp.codigo_cuspp or "",
                health_regime=self._normalize_health(emp.tipo_seguro_salud),
                eps_provider="",
                cci=emp.numero_cci or "",
                bank_code="",
                bank_account=emp.numero_cuenta_bancaria or "",
                source="MIGRATION",
                contract_snapshot=contract,
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(
            f"Compensation migration: created={created} "
            f"skipped_existing={skipped_existing} skipped_no_data={skipped_no_data} "
            f"divergences_logged={divergences}"
        ))

    @staticmethod
    def _normalize_pension(value):
        """Map Employee.sistema_pensiones string to Compensation.pension_regime choice."""
        if not value:
            return "ONP"
        v = value.upper().replace(" ", "_")
        if v.startswith("AFP_"):
            return v  # AFP_INTEGRA / AFP_PRIMA / AFP_PROFUTURO / AFP_HABITAT
        if v == "ONP":
            return "ONP"
        return "ONP"  # SIN PENSION / PENSIONISTA-* default to ONP for the snapshot

    @staticmethod
    def _normalize_health(value):
        if value and value.upper() == "EPS":
            return "EPS"
        return "ESSALUD"
