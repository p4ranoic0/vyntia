"""Tests for TenantStorage prefix wrapper (ADR-B.4)."""

from unittest.mock import MagicMock, patch

from apps.core.storage import TenantStorage


class TestTenantStorage:
    def test_save_prefixes_path_with_tenant_id(self):
        inner = MagicMock()
        inner.save.return_value = "tenant-abc/legajos/legajo.pdf"

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value="tenant-abc"):
            storage = TenantStorage()
            content = MagicMock()
            result = storage.save("legajos/legajo.pdf", content)

        inner.save.assert_called_once_with(
            "tenant-abc/legajos/legajo.pdf", content, max_length=None
        )
        assert result == "tenant-abc/legajos/legajo.pdf"

    def test_save_without_tenant_falls_back_to_default(self):
        inner = MagicMock()
        inner.save.return_value = "legajos/legajo.pdf"

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value=None):
            storage = TenantStorage()
            content = MagicMock()
            storage.save("legajos/legajo.pdf", content)

        inner.save.assert_called_once_with(
            "legajos/legajo.pdf", content, max_length=None
        )

    def test_url_prefixes_path(self):
        inner = MagicMock()
        inner.url.return_value = "/media/tenant-abc/legajos/legajo.pdf"

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value="tenant-abc"):
            storage = TenantStorage()
            storage.url("legajos/legajo.pdf")

        inner.url.assert_called_once_with("tenant-abc/legajos/legajo.pdf")

    def test_exists_prefixes_path(self):
        inner = MagicMock()
        inner.exists.return_value = True

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value="tenant-abc"):
            storage = TenantStorage()
            result = storage.exists("legajos/x.pdf")

        inner.exists.assert_called_once_with("tenant-abc/legajos/x.pdf")
        assert result is True

    def test_open_delete_size_listdir_prefix_path(self):
        """Smoke test for the remaining operations — all delegate with prefix."""
        inner = MagicMock()

        with patch("apps.core.storage.default_storage", inner), \
             patch("apps.core.storage.get_current_tenant_id", return_value="tenant-abc"):
            storage = TenantStorage()
            storage.open("legajos/x.pdf")
            storage.delete("legajos/x.pdf")
            storage.size("legajos/x.pdf")
            storage.listdir("legajos/")

        inner.open.assert_called_once_with("tenant-abc/legajos/x.pdf", "rb")
        inner.delete.assert_called_once_with("tenant-abc/legajos/x.pdf")
        inner.size.assert_called_once_with("tenant-abc/legajos/x.pdf")
        inner.listdir.assert_called_once_with("tenant-abc/legajos/")
