"""Canonical audit action names for Vyntia Pay events (ADR-D.3).

Every payroll/CTS/gratification/severance audit event written to
`apps.audit_lite.AuditEvent.action` MUST use one of these constants so all D
phases (D.5 runs, D.7 CTS, D.8 gratificaciones, D.12 liquidación) stay
consistent and the future event store can route by a stable namespace.
"""

# PayrollRun lifecycle (D.5)
PAYROLL_RUN_CREATED = "payroll.run.created"
PAYROLL_RUN_CALCULATED = "payroll.run.calculated"
PAYROLL_RUN_APPROVED = "payroll.run.approved"
PAYROLL_RUN_CLOSED = "payroll.run.closed"
PAYROLL_RUN_REOPENED = "payroll.run.reopened"
PAYROLL_SLIP_CALCULATED = "payroll.slip.calculated"
PAYROLL_ADJUSTMENT_APPLIED = "payroll.adjustment.applied"

# CTS (D.7)
CTS_DEPOSIT_COMPUTED = "cts.deposit.computed"
CTS_DEPOSIT_PAID = "cts.deposit.paid"

# Gratificaciones (D.8)
GRATIFICATION_COMPUTED = "gratification.computed"
GRATIFICATION_PAID = "gratification.paid"

# Severance / liquidación (D.12)
SEVERANCE_SETTLEMENT_COMPUTED = "severance.settlement.computed"
SEVERANCE_SETTLEMENT_PAID = "severance.settlement.paid"

PAYROLL_AUDIT_ACTIONS = frozenset(
    {
        PAYROLL_RUN_CREATED,
        PAYROLL_RUN_CALCULATED,
        PAYROLL_RUN_APPROVED,
        PAYROLL_RUN_CLOSED,
        PAYROLL_RUN_REOPENED,
        PAYROLL_SLIP_CALCULATED,
        PAYROLL_ADJUSTMENT_APPLIED,
        CTS_DEPOSIT_COMPUTED,
        CTS_DEPOSIT_PAID,
        GRATIFICATION_COMPUTED,
        GRATIFICATION_PAID,
        SEVERANCE_SETTLEMENT_COMPUTED,
        SEVERANCE_SETTLEMENT_PAID,
    }
)
