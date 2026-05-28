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
    """The uniquely-legacy model names are no longer importable.

    Note: `PayrollConcept` and `TaxParameter` names are *reused* by the D.2
    greenfield catalog models (different schema), so they are intentionally
    not in this list — the legacy versions of those classes are gone.
    """
    import apps.payroll.models as payroll_models

    for name in (
        "AfpConfiguration",
        "CompensationConfiguration",
        "MonthlyPayroll",
        "PayrollDetail",
        "MassDeduction",
        "PaySlip",
        "PaymentSchedule",
    ):
        assert not hasattr(payroll_models, name), f"{name} still importable"


def test_payroll_app_registry_has_no_legacy_models():
    """The payroll app registry never contains any of the 7 uniquely-legacy
    model class names (D.1b invariant). Greenfield models are added per phase
    (catalog in D.2, Compensation in D.3, etc.) — those are NOT asserted here
    so the test stays stable across phases; see
    `test_legacy_payroll_models_are_gone` for the module-level check.
    `PayrollConcept` and `TaxParameter` names are intentionally NOT in the
    forbidden set: they are reused by the D.2 greenfield models (different
    schema)."""
    from django.apps import apps as django_apps

    names = {m.__name__ for m in django_apps.get_app_config("payroll").get_models()}
    forbidden = {
        "AfpConfiguration",
        "CompensationConfiguration",
        "MonthlyPayroll",
        "PayrollDetail",
        "MassDeduction",
        "PaySlip",
        "PaymentSchedule",
    }
    leaked = names & forbidden
    assert not leaked, f"Legacy models still in registry: {leaked}"
