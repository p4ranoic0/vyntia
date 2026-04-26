"""Base permission classes for API endpoints."""

from typing import Any, Dict, List, Optional

from app_rrhh.constants import Roles
from app_rrhh.models import Permiso, Rol, Usuario
from app_rrhh.permission_service import PermissionService
from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions
from rest_framework.request import Request


class BasePermission(permissions.BasePermission):
    """Base permission class with common functionality."""

    def has_permission(self, request: Request, view: Any) -> bool:
        """Check if user has permission to access the view.

        Args:
            request: DRF request object
            view: API view object

        Returns:
            bool: True if user has permission
        """
        if isinstance(request.user, AnonymousUser):
            return False

        return True

    def get_client_ip(self, request: Request) -> str:
        """Get client IP address from request.

        Args:
            request: DRF request object

        Returns:
            str: Client IP address
        """
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """Check if user has permission to access specific object.

        Args:
            request: DRF request object
            view: API view object
            obj: Object being accessed

        Returns:
            bool: True if user has permission
        """
        return self.has_permission(request, view)


class IsAuthenticated(BasePermission):
    """Permission class that requires user authentication."""

    def has_permission(self, request: Request, view: Any) -> bool:
        """Check if user is authenticated.

        Args:
            request: DRF request object
            view: API view object

        Returns:
            bool: True if user is authenticated
        """
        return bool(request.user and request.user.is_authenticated)


class IsOwnerOrReadOnly(BasePermission):
    """Permission class that allows owners to edit, others to read only."""

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """Check if user can access object.

        Args:
            request: DRF request object
            view: API view object
            obj: Object being accessed

        Returns:
            bool: True if user has permission
        """
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions only for owner
        return obj.usuario == request.user


class HasRolePermission(BasePermission):
    """Permission class based on user roles."""

    required_roles: List[str] = []

    def has_permission(self, request: Request, view: Any) -> bool:
        """Check if user has required role.

        Args:
            request: DRF request object
            view: API view object

        Returns:
            bool: True if user has required role
        """
        if not super().has_permission(request, view):
            return False

        if not self.required_roles:
            return True

        try:
            # request.user IS already the Usuario instance (custom user model)
            usuario = request.user
            return PermissionService.has_any_role(usuario, self.required_roles)
        except Exception:
            return False


class HasSpecificPermission(BasePermission):
    """Permission class based on specific permissions (via roles)."""

    required_permissions: List[str] = []

    def has_permission(self, request: Request, view: Any) -> bool:
        """Check if user has specific permissions via their roles.

        Args:
            request: DRF request object
            view: API view object

        Returns:
            bool: True if user has required permissions
        """
        if not super().has_permission(request, view):
            return False

        if not self.required_permissions:
            return True

        try:
            # request.user IS already the Usuario instance
            usuario = request.user
            # Mantener semántica existente: requiere todos los permisos configurados.
            if PermissionService.is_super_admin(usuario):
                return True
            user_permissions = PermissionService.get_user_permission_names(usuario)
            return all(perm in user_permissions for perm in self.required_permissions)
        except Exception:
            return False


class IsAdminUser(HasRolePermission):
    """Permission class for admin users."""

    required_roles = Roles.ADMIN_ROLES


class IsManagerUser(HasRolePermission):
    """Permission class for manager users."""

    required_roles = Roles.MANAGER_ROLES


class IsHRUser(HasRolePermission):
    """Permission class for HR users."""

    required_roles = Roles.HR_ROLES


class IsEmployeeUser(HasRolePermission):
    """Permission class for employee users."""

    required_roles = Roles.EMPLOYEE_ROLES


class CanViewEmployees(HasSpecificPermission):
    """Permission to view employee data."""

    required_permissions = ["ver_empleados"]


class CanEditEmployees(HasSpecificPermission):
    """Permission to edit employee data."""

    required_permissions = ["editar_empleados"]


class CanDeleteEmployees(HasSpecificPermission):
    """Permission to delete employee data."""

    required_permissions = ["eliminar_empleados"]


class CanViewPayrolls(HasSpecificPermission):
    """Permission to view payroll data."""

    required_permissions = ["ver_boletas"]


class CanEditPayrolls(HasSpecificPermission):
    """Permission to edit payroll data."""

    required_permissions = ["editar_boletas"]


class CanManageUsers(HasSpecificPermission):
    """Permission to manage user accounts."""

    required_permissions = ["gestionar_usuarios"]


class CanManageRoles(HasSpecificPermission):
    """Permission to manage roles and permissions."""

    required_permissions = ["gestionar_roles"]


class DynamicPermission(BasePermission):
    """Dynamic permission class that checks permissions based on view action."""

    permission_mapping: Dict[str, List[str]] = {
        "list": ["ver"],
        "retrieve": ["ver"],
        "create": ["crear"],
        "update": ["editar"],
        "partial_update": ["editar"],
        "destroy": ["eliminar"],
    }

    def __init__(self, resource_name: str):
        """Initialize with resource name.

        Args:
            resource_name: Name of the resource (e.g., 'empleados', 'boletas')
        """
        self.resource_name = resource_name

    def has_permission(self, request: Request, view: Any) -> bool:
        """Check if user has permission for the action.

        Args:
            request: DRF request object
            view: API view object

        Returns:
            bool: True if user has permission
        """
        if not super().has_permission(request, view):
            return False

        action = getattr(view, "action", None)
        if not action:
            return True

        required_actions = self.permission_mapping.get(action, [])
        if not required_actions:
            return True

        try:
            # request.user IS already the Usuario instance
            usuario = request.user
            user_roles = [rol.nombre_rol for rol in usuario.roles_activos()]

            # Super Administrador tiene acceso completo
            if "Super Administrador" in user_roles:
                return True

            # Obtener permisos activos - ahora retorna set de strings o '*'
            user_permissions = usuario.permisos_activos()

            # Si es admin (wildcard), tiene acceso a todo
            if user_permissions == "*":
                return True

            # Si es set, construir lista de permisos requeridos y validar
            if isinstance(user_permissions, set):
                required_permissions = [
                    f"{act}_{self.resource_name}" for act in required_actions
                ]

                # Convertir a lista de nombres simples (sin prefijo de acción)
                # y validar que el usuario tiene permisos para este recurso
                resource_names = {perm.split("_")[0] for perm in required_permissions}
                allowed = any(name in user_permissions for name in resource_names)
                return allowed

            # Si llegamos aquí, el usuario no tiene acceso
            return False
        except Exception:
            return False


class OwnershipPermission(BasePermission):
    """Permission class that checks object ownership."""

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """Check if user owns the object or has admin privileges.

        Args:
            request: DRF request object
            view: API view object
            obj: Object being accessed

        Returns:
            bool: True if user has permission
        """
        # Admin users can access everything
        try:
            # request.user IS already the Usuario instance
            usuario = request.user
            admin_roles = ["Administrador", "Super Administrador"]
            user_roles = [rol.nombre_rol for rol in usuario.roles_activos()]

            if any(role in user_roles for role in admin_roles):
                return True
        except Exception:
            pass

        # Check ownership based on object type
        # request.user IS the Usuario instance (no .user sub-field)
        if hasattr(obj, "usuario"):
            return obj.usuario == request.user
        elif hasattr(obj, "empleado") and hasattr(obj.empleado, "usuario"):
            return obj.empleado.usuario == request.user
        elif hasattr(obj, "user"):
            return obj.user == request.user

        return False


class ReadOnlyPermission(BasePermission):
    """Permission class that allows only read operations."""

    def has_permission(self, request: Request, view: Any) -> bool:
        """Check if request is a safe method.

        Args:
            request: DRF request object
            view: API view object

        Returns:
            bool: True if request method is safe
        """
        if not super().has_permission(request, view):
            return False

        return request.method in permissions.SAFE_METHODS


class ConditionalPermission(BasePermission):
    """Permission class with conditional logic."""

    def __init__(self, condition_func):
        """Initialize with condition function.

        Args:
            condition_func: Function that takes (request, view, obj) and returns bool
        """
        self.condition_func = condition_func

    def has_permission(self, request: Request, view: Any) -> bool:
        """Check permission using condition function.

        Args:
            request: DRF request object
            view: API view object

        Returns:
            bool: True if condition is met
        """
        if not super().has_permission(request, view):
            return False

        return self.condition_func(request, view, None)

    def has_object_permission(self, request: Request, view: Any, obj: Any) -> bool:
        """Check object permission using condition function.

        Args:
            request: DRF request object
            view: API view object
            obj: Object being accessed

        Returns:
            bool: True if condition is met
        """
        return self.condition_func(request, view, obj)
