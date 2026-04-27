"""Servicio de menu para construir arbol visible por permisos."""

from typing import Any, Dict, List, Optional, Set

from app_rrhh.permission_service import PermissionService
from apps.identity.models import Module
from django.db.models import Prefetch


class MenuService:
    """Construye menu dinamico desde la BD filtrando por permisos."""

    @staticmethod
    def get_menu_for_user(usuario) -> List[Dict[str, Any]]:
        """Retorna menu visible para un usuario autenticado."""
        is_super_admin = PermissionService.is_super_admin(usuario)
        user_permissions: Optional[Set[str]] = None

        if not is_super_admin:
            user_permissions = PermissionService.get_user_permission_names(usuario)

        # Prefetch optimizado: submódulos activos con sus permisos
        submodulos_prefetch = Prefetch(
            "submodulos",
            queryset=(
                Module.objects.filter(estado_modulo="activo")
                .order_by("orden_visualizacion")
                .prefetch_related("modulo_permisos__permiso")
            ),
        )

        modulos_raiz = (
            Module.objects.filter(estado_modulo="activo", modulo_padre__isnull=True)
            .order_by("orden_visualizacion")
            .prefetch_related(
                "modulo_permisos__permiso",
                submodulos_prefetch,
            )
        )

        return [
            MenuService._build_item(modulo, user_permissions)
            for modulo in modulos_raiz
            if MenuService._is_visible(modulo, user_permissions)
        ]

    @staticmethod
    def _is_visible(modulo: Module, user_permissions: Optional[Set[str]]) -> bool:
        """
        Valida visibilidad del modulo para el conjunto de permisos recibido.

        Usa exclusivamente la tabla pivote modulo_permisos como fuente de verdad.
        Si el modulo no tiene permisos requeridos, es visible para todos.
        Si el usuario es super admin (user_permissions=None), puede ver todo.
        """
        required_permissions = {
            rel.permiso.nombre_permiso
            for rel in modulo.modulo_permisos.all()
            if rel.permiso and rel.permiso.nombre_permiso
        }

        # Modulo sin permisos requeridos: visible para todos
        if not required_permissions:
            return True

        # Super admin: acceso total
        if user_permissions is None:
            return True

        # User regular: validar interseccion de permisos
        return bool(required_permissions & user_permissions)

    @staticmethod
    def _build_item(
        modulo: Module, user_permissions: Optional[Set[str]]
    ) -> Dict[str, Any]:
        """Construye el nodo de menu recursivamente."""
        item = {
            "id": f"modulo-{modulo.modulo_id}",
            "title": modulo.nombre_modulo,
            "icon": modulo.icono_modulo or "circle",
            "path": modulo.ruta_modulo or f"/{modulo.nombre_modulo.lower()}",
            "order": modulo.orden_visualizacion,
        }

        children = [
            MenuService._build_item(child, user_permissions)
            for child in modulo.get_children()
            if MenuService._is_visible(child, user_permissions)
        ]

        if children:
            item["submenu"] = children

        return item
