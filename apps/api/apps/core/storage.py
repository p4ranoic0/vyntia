"""TenantStorage — wraps default_storage with a per-tenant path prefix (ADR-B.4).

All document-writing code (PDF generator, contract upload, legajo upload)
should use TenantStorage instead of default_storage directly. Switching to
S3/Azure later becomes a settings change plus a one-time data migration,
not a code rewrite.

Usage:
    from apps.core.storage import TenantStorage

    storage = TenantStorage()
    storage.save("legajos/foo.pdf", content)  # actually saves to <tenant_id>/legajos/foo.pdf

When no tenant context is active (admin commands, reserved subdomains),
TenantStorage falls through to default_storage with no prefix. Caller is
responsible for handling that case (typically: refuse to write).

The wrapper is intentionally NOT a Django Storage subclass — it composes via
delegation. Wiring it as `DEFAULT_FILE_STORAGE` would require subclassing
Storage or implementing the full Storage protocol; that's deferred to the
deployment-hardening sub-project, where switching to S3/Azure happens too.
"""

from django.core.files.storage import default_storage

from apps.tenancy.context import get_current_tenant_id


class TenantStorage:
    """Wrap django.core.files.storage.default_storage with a tenant prefix.

    The prefix is `<tenant_id>/` derived from the active tenant context.
    When no tenant is active, no prefix is added — caller is responsible
    for handling that case (typically: refuse to write).
    """

    def _prefix(self, name: str) -> str:
        tenant_id = get_current_tenant_id()
        if tenant_id is None:
            return name
        return f"{tenant_id}/{name}"

    def save(self, name, content, max_length=None):
        return default_storage.save(
            self._prefix(name), content, max_length=max_length
        )

    def open(self, name, mode="rb"):
        return default_storage.open(self._prefix(name), mode)

    def delete(self, name):
        return default_storage.delete(self._prefix(name))

    def exists(self, name):
        return default_storage.exists(self._prefix(name))

    def url(self, name):
        return default_storage.url(self._prefix(name))

    def size(self, name):
        return default_storage.size(self._prefix(name))

    def listdir(self, path):
        return default_storage.listdir(self._prefix(path))
