"""Identity models — re-exports for backward-compatible imports."""

from .roles import Permiso, Rol
from .sistema import ModuloPermiso, Modulos, RolPermisos, UsuarioRoles
from .usuario import Usuario

__all__ = [
    "Modulos",
    "ModuloPermiso",
    "Permiso",
    "Rol",
    "RolPermisos",
    "Usuario",
    "UsuarioRoles",
]
