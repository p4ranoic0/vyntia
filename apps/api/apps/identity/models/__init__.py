"""Identity models — re-exports for backward-compatible imports."""

from .rbac import Module, ModulePermission, RolePermission, UserRole
from .roles import Permission, Role
from .user import User

__all__ = [
    "Module",
    "ModulePermission",
    "Permission",
    "Role",
    "RolePermission",
    "User",
    "UserRole",
]
