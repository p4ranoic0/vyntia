"""Tests for tenant ContextVar utilities."""

import threading
import uuid

from apps.tenancy.context import (
    get_current_tenant,
    get_current_tenant_id,
    get_current_user_id,
    set_current_tenant,
    set_current_user_id,
    tenant_context,
)


class FakeTenant:
    def __init__(self, id_=None, slug="acme"):
        self.id = id_ or uuid.uuid4()
        self.slug = slug


class TestContextVarBasics:
    def test_default_is_none(self):
        # No tenant set in this test's context
        assert get_current_tenant() is None
        assert get_current_tenant_id() is None
        assert get_current_user_id() is None

    def test_set_and_get(self):
        tenant = FakeTenant()
        token = set_current_tenant(tenant)
        try:
            assert get_current_tenant() is tenant
            assert get_current_tenant_id() == tenant.id
        finally:
            # Reset to avoid leaking into other tests
            from apps.tenancy.context import _current_tenant
            _current_tenant.reset(token)
        assert get_current_tenant() is None

    def test_user_id_set_and_get(self):
        user_id = uuid.uuid4()
        token = set_current_user_id(user_id)
        try:
            assert get_current_user_id() == user_id
        finally:
            from apps.tenancy.context import _current_user_id
            _current_user_id.reset(token)


class TestTenantContextManager:
    def test_sets_and_resets(self):
        tenant = FakeTenant()
        assert get_current_tenant() is None
        with tenant_context(tenant):
            assert get_current_tenant() is tenant
        assert get_current_tenant() is None

    def test_nested(self):
        outer = FakeTenant(slug="outer")
        inner = FakeTenant(slug="inner")
        with tenant_context(outer):
            assert get_current_tenant().slug == "outer"
            with tenant_context(inner):
                assert get_current_tenant().slug == "inner"
            assert get_current_tenant().slug == "outer"
        assert get_current_tenant() is None

    def test_with_user_id(self):
        tenant = FakeTenant()
        user_id = uuid.uuid4()
        with tenant_context(tenant, user_id=user_id):
            assert get_current_tenant() is tenant
            assert get_current_user_id() == user_id
        assert get_current_tenant() is None
        assert get_current_user_id() is None

    def test_exception_resets_context(self):
        tenant = FakeTenant()
        try:
            with tenant_context(tenant):
                raise ValueError("simulated")
        except ValueError:
            pass
        assert get_current_tenant() is None


class TestThreadIsolation:
    def test_each_thread_has_independent_context(self):
        results = {}

        def worker(name, tenant):
            with tenant_context(tenant):
                # Simulate some work
                import time
                time.sleep(0.01)
                results[name] = get_current_tenant().slug

        t1 = FakeTenant(slug="thread1")
        t2 = FakeTenant(slug="thread2")
        threads = [
            threading.Thread(target=worker, args=("a", t1)),
            threading.Thread(target=worker, args=("b", t2)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        assert results["a"] == "thread1"
        assert results["b"] == "thread2"
