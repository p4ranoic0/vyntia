"""Regression tests for MenuService.

Guards against the L3.10.4e stale-consumer class of bug: model PKs were
renamed `<entity>_id -> id`, but `menu_service.py` still referenced
`modulo.modulo_id` in production code. The endpoint `/api/v1/auth/menu/`
returned 500 in a tight loop on every page load until 2026-05-19.

These tests cover:
  - MenuService.get_menu_for_user returns successfully for a fresh
    superuser (the path that was 500-ing).
  - The built item id contains the actual PK value of the Module row.
"""
import pytest

from apps.identity.models import Module, User
from apps.identity.services.menu_service import MenuService


@pytest.fixture
def superuser(db):
    user = User.objects.create_superuser(
        username="menutest", email="menutest@test.local", password="x"
    )
    user.tipo_usuario = "administrador"
    user.save(update_fields=["tipo_usuario"])
    return user


@pytest.fixture
def root_module(db):
    return Module.objects.create(
        nombre_modulo="dashboard",
        ruta_modulo="/dashboard",
        icono_modulo="layout-dashboard",
        orden_visualizacion=1,
        estado_modulo="activo",
    )


@pytest.mark.django_db
class TestMenuService:
    def test_get_menu_for_user_does_not_raise(self, superuser, root_module):
        """The original bug: AttributeError on .modulo_id surfaced as 500."""
        menu = MenuService.get_menu_for_user(superuser)
        assert isinstance(menu, list)

    def test_item_id_uses_pk(self, superuser, root_module):
        """`id` in the built dict must reference Module.id (the UUID PK)."""
        menu = MenuService.get_menu_for_user(superuser)
        dashboard = next(item for item in menu if item["title"] == "dashboard")
        assert dashboard["id"] == f"modulo-{root_module.id}"

    def test_no_attribute_error_on_legacy_field_names(self, root_module):
        """Module.id is the only PK field — legacy modulo_id must not be referenced."""
        # If anyone re-introduces `.modulo_id` this would AttributeError.
        # Direct hasattr check is the cheapest sentinel.
        assert hasattr(root_module, "id")
        assert not hasattr(root_module, "modulo_id")
