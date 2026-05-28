"""D.1b regression — legacy payroll dropped, audit_lite.schema_version added,
payroll audit action namespace defined."""


def test_audit_event_has_schema_version_field_default_1():
    from apps.audit_lite.models import AuditEvent

    field = AuditEvent._meta.get_field("schema_version")
    assert field.get_internal_type() == "IntegerField"
    assert field.default == 1
