"""D.1b regression — legacy payroll dropped, audit_lite.schema_version added,
payroll audit action namespace defined."""


def test_audit_event_has_schema_version_field_default_1():
    from apps.audit_lite.models import AuditEvent

    field = AuditEvent._meta.get_field("schema_version")
    assert field.get_internal_type() == "IntegerField"
    assert field.default == 1


def test_payroll_audit_action_namespace():
    from apps.payroll import audit_actions as aa

    expected = {
        "payroll.run.created",
        "payroll.run.calculated",
        "payroll.run.approved",
        "payroll.run.closed",
        "payroll.run.reopened",
        "payroll.slip.calculated",
        "payroll.adjustment.applied",
        "cts.deposit.computed",
        "cts.deposit.paid",
        "gratification.computed",
        "gratification.paid",
        "severance.settlement.computed",
        "severance.settlement.paid",
    }
    assert aa.PAYROLL_AUDIT_ACTIONS == expected
    for action in aa.PAYROLL_AUDIT_ACTIONS:
        assert action == action.lower()
        assert "." in action
        assert len(action) <= 128


def test_legacy_payroll_models_are_gone():
    import apps.payroll.models as payroll_models

    assert payroll_models.__all__ == []
    for name in (
        "AfpConfiguration",
        "CompensationConfiguration",
        "MonthlyPayroll",
        "PayrollDetail",
        "PayrollConcept",
        "MassDeduction",
        "PaySlip",
        "PaymentSchedule",
        "TaxParameter",
    ):
        assert not hasattr(payroll_models, name), f"{name} still importable"


def test_payroll_app_has_no_models():
    from django.apps import apps as django_apps

    assert list(django_apps.get_app_config("payroll").get_models()) == []
