"""Cross-cutting ViewSet mixins.

`TenantAwareViewSetMixin` is the canonical hook for ViewSets serving
tenant-scoped models. It injects `tenant=request.tenant` into serializer.save()
on create, and filters the default queryset by `tenant=request.tenant`.

The mixin is permissive when `request.tenant` is None (admin subdomain,
reserved subdomain, or non-tenant routes) — it does not raise; it falls
through to default behavior. Tenant resolution happens upstream in
`apps.tenancy.middleware.TenantMiddleware`.

Defense-in-depth: even with this mixin in place, RLS (set in
`apps.tenancy.middleware.RLSMiddleware`) is the authoritative database-level
isolation. The mixin is a belt-and-suspenders measure that catches bugs
before they ever reach RLS.

Usage:
    from apps.core.viewsets import TenantAwareViewSetMixin
    from rest_framework import viewsets

    class MyViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
        queryset = MyModel.objects.all()
        serializer_class = MySerializer

When a subclass overrides `get_queryset()` (e.g., to add annotations), it
should END its custom logic with `return self._filter_by_tenant(queryset)`
instead of `return queryset`.
"""


class TenantAwareViewSetMixin:
    """Inject request.tenant on create + filter queryset on read."""

    def perform_create(self, serializer):
        """Save the new instance with tenant=request.tenant if available."""
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            serializer.save(tenant=tenant)
        else:
            serializer.save()

    def get_queryset(self):
        queryset = super().get_queryset()
        return self._filter_by_tenant(queryset)

    def _filter_by_tenant(self, queryset):
        """Filter a queryset by request.tenant if present.

        Use this from a subclass-overridden get_queryset() that needs to
        keep custom annotations or pre-filters but still wants tenant
        filtering applied at the end.
        """
        tenant = getattr(self.request, "tenant", None)
        if tenant is not None:
            return queryset.filter(tenant=tenant)
        return queryset
