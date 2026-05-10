"""record_event helper — single entry point for B-phase audit hooks (ADR-B.2)."""

from .models import AuditEvent


def record_event(
    *,
    tenant,
    actor_user,
    action: str,
    target_model: str,
    target_id,
    payload: dict | None = None,
) -> AuditEvent:
    """Persist an audit event for a high-stakes domain mutation.

    Call inside the same transaction as the mutation so it commits atomically.

    Args:
        tenant: the active Tenant (required).
        actor_user: the User who performed the action (None for system events).
        action: dotted action name, e.g. "employee.terminated".
        target_model: dotted model label, e.g. "employees.Employee".
        target_id: primary key of the affected row, coerced to str.
        payload: optional JSON-serializable dict with mutation details.

    Returns:
        The persisted AuditEvent.
    """
    return AuditEvent.objects.create(
        tenant=tenant,
        actor_user=actor_user,
        action=action,
        target_model=target_model,
        target_id=str(target_id),
        payload_json=payload or {},
    )
