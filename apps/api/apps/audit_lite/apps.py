"""App config for audit_lite — minimal domain audit events (ADR-B.2)."""

from django.apps import AppConfig


class AuditLiteConfig(AppConfig):
    name = "apps.audit_lite"
    label = "audit_lite"
    verbose_name = "Audit Lite (B.1)"
    default_auto_field = "django.db.models.UUIDField"
