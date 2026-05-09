"""Discover tenant-scoped Django models for RLS policy application.

A model is considered tenant-scoped if it has a `tenant` field that is
a ForeignKey to `tenancy.Tenant`. The C.1 migration added this to 32
business models across 8 apps.
"""

from django.apps import apps
from django.db import models


def get_tenant_scoped_models():
    """Return list of all Django models that have a `tenant` FK to tenancy.Tenant.

    Order is deterministic (sorted by app_label, then model_name) for
    idempotent policy generation.
    """
    result = []
    for app_config in apps.get_app_configs():
        for model in app_config.get_models():
            tenant_field = _get_tenant_field(model)
            if tenant_field is not None:
                result.append(model)
    result.sort(key=lambda m: (m._meta.app_label, m._meta.model_name))
    return result


def _get_tenant_field(model):
    """Return the `tenant` field if it's a FK to tenancy.Tenant, else None."""
    for field in model._meta.local_fields:
        if field.name != "tenant":
            continue
        if not isinstance(field, models.ForeignKey):
            continue
        related = field.related_model
        if related is None:
            continue
        if (related._meta.app_label, related._meta.model_name) == ("tenancy", "tenant"):
            return field
    return None


def get_table_names_for_rls():
    """Return the list of `db_table` names to apply RLS to, sorted."""
    return [m._meta.db_table for m in get_tenant_scoped_models()]
