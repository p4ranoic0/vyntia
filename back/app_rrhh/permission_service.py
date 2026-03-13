"""Servicio centralizado para validaciones de roles y permisos."""

from typing import Iterable, Set

from app_rrhh.constants import Roles


class PermissionService:
    """Single source of truth para checks de autorizacion."""

    @staticmethod
    def get_user_role_names(usuario) -> Set[str]:
        if not usuario or not getattr(usuario, "is_authenticated", False):
            return set()
        return {rol.nombre_rol for rol in usuario.roles_activos()}

    @staticmethod
    def get_user_permission_names(usuario) -> Set[str]:
        if not usuario or not getattr(usuario, "is_authenticated", False):
            return set()
        permisos = usuario.permisos_activos()
        if permisos == "*":
            return {"*"}
        if hasattr(permisos, 'values_list'):
            return set(permisos.values_list('nombre_permiso', flat=True))
        return set()

    @staticmethod
    def is_super_admin(usuario) -> bool:
        if not usuario:
            return False
        if getattr(usuario, "is_superuser", False):
            return True
        return Roles.SUPER_ADMIN in PermissionService.get_user_role_names(usuario)

    @staticmethod
    def has_any_role(usuario, required_roles: Iterable[str]) -> bool:
        if PermissionService.is_super_admin(usuario):
            return True
        user_roles = PermissionService.get_user_role_names(usuario)
        return any(role in user_roles for role in required_roles)

    @staticmethod
    def has_any_permission(usuario, required_permissions: Iterable[str]) -> bool:
        if PermissionService.is_super_admin(usuario):
            return True
        user_permissions = PermissionService.get_user_permission_names(usuario)
        return any(perm in user_permissions for perm in required_permissions)
