"""ContextVar utilities for tenant context propagation across the request lifecycle.

The tenant and user_id are stored in ContextVars (PEP 567), which provide
isolation across asyncio tasks and threads. Middleware sets these at the
start of a request; views and managers read them; the values are auto-reset
at request end.

Usage:
    # In middleware:
    with tenant_context(tenant, user_id=user.id):
        return get_response(request)

    # In a manager or service:
    tenant = get_current_tenant()
    if tenant is None:
        ...  # no tenant context (reserved subdomain, admin, etc.)
"""

from contextlib import contextmanager
from contextvars import ContextVar
from typing import Optional
from uuid import UUID

# Module-private ContextVars — never import these directly. Use the helpers below.
_current_tenant: ContextVar[Optional[object]] = ContextVar(
    "vyntia_current_tenant", default=None
)
_current_user_id: ContextVar[Optional[UUID]] = ContextVar(
    "vyntia_current_user_id", default=None
)


def get_current_tenant():
    """Return the active Tenant for the current execution context, or None."""
    return _current_tenant.get()


def get_current_tenant_id():
    """Return the active Tenant.id (UUID), or None."""
    tenant = _current_tenant.get()
    return tenant.id if tenant is not None else None


def get_current_user_id():
    """Return the active user.id (UUID), or None."""
    return _current_user_id.get()


def set_current_tenant(tenant):
    """Set the active tenant. Returns a token that can be passed to reset."""
    return _current_tenant.set(tenant)


def set_current_user_id(user_id):
    """Set the active user_id. Returns a token that can be passed to reset."""
    return _current_user_id.set(user_id)


@contextmanager
def tenant_context(tenant, *, user_id=None):
    """Context manager for setting tenant (and optionally user_id) for a block.

    Both vars are reset on exit, including on exceptions.
    """
    tenant_token = _current_tenant.set(tenant)
    user_token = _current_user_id.set(user_id) if user_id is not None else None
    try:
        yield
    finally:
        _current_tenant.reset(tenant_token)
        if user_token is not None:
            _current_user_id.reset(user_token)
