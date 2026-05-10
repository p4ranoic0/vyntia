"""Tests for TenantAwareViewSetMixin (B.1 #6).

Verifies:
1. perform_create propagates request.tenant to serializer.save(tenant=...)
2. perform_create with no tenant context calls save() with no tenant kwarg
3. get_queryset filters by request.tenant when set
4. get_queryset returns unfiltered queryset when request.tenant is None
"""

from unittest.mock import MagicMock

from apps.core.viewsets import TenantAwareViewSetMixin


class _BaseStub:
    """Stand-in for the DRF ModelViewSet base — provides default get_queryset."""

    def __init__(self, base_qs):
        self._base_qs = base_qs

    def get_queryset(self):
        return self._base_qs


class _FakeViewSet(TenantAwareViewSetMixin, _BaseStub):
    def __init__(self, request, base_qs):
        _BaseStub.__init__(self, base_qs)
        self.request = request


class TestTenantAwareViewSetMixin:
    def test_perform_create_passes_tenant_kwarg_when_tenant_set(self):
        request = MagicMock()
        request.tenant = MagicMock()
        viewset = _FakeViewSet(request=request, base_qs=MagicMock())
        serializer = MagicMock()

        viewset.perform_create(serializer)

        serializer.save.assert_called_once_with(tenant=request.tenant)

    def test_perform_create_no_tenant_kwarg_when_tenant_none(self):
        request = MagicMock()
        request.tenant = None
        viewset = _FakeViewSet(request=request, base_qs=MagicMock())
        serializer = MagicMock()

        viewset.perform_create(serializer)

        serializer.save.assert_called_once_with()

    def test_get_queryset_filters_by_tenant_when_set(self):
        request = MagicMock()
        request.tenant = MagicMock()
        base_qs = MagicMock()
        filtered_qs = MagicMock()
        base_qs.filter.return_value = filtered_qs

        viewset = _FakeViewSet(request=request, base_qs=base_qs)

        result = viewset.get_queryset()

        base_qs.filter.assert_called_once_with(tenant=request.tenant)
        assert result is filtered_qs

    def test_get_queryset_passthrough_when_tenant_none(self):
        request = MagicMock()
        request.tenant = None
        base_qs = MagicMock()
        viewset = _FakeViewSet(request=request, base_qs=base_qs)

        result = viewset.get_queryset()

        base_qs.filter.assert_not_called()
        assert result is base_qs

    def test_filter_by_tenant_helper_filters_when_set(self):
        request = MagicMock()
        request.tenant = MagicMock()
        base_qs = MagicMock()
        filtered_qs = MagicMock()
        base_qs.filter.return_value = filtered_qs

        viewset = _FakeViewSet(request=request, base_qs=MagicMock())

        result = viewset._filter_by_tenant(base_qs)

        base_qs.filter.assert_called_once_with(tenant=request.tenant)
        assert result is filtered_qs
