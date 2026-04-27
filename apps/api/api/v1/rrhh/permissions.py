"""Permissions for RRHH API v1."""

from typing import Any

from apps.core.logging import get_logger
from apps.core.permissions import BasePermission
from django.contrib.auth.models import AnonymousUser
from rest_framework import permissions

logger = get_logger(__name__)


class RRHHPermission(BasePermission):
    """Base permission for RRHH module - usando roles_config.py."""

    def is_admin_user(self, user):
        """Check if user is admin (from roles)."""
        try:
            if hasattr(user, "roles_activos"):
                roles_activos = user.roles_activos()
                admin_roles = [
                    "admin", "administrador", "super administrador", "administrador rrhh",
                ]
                return any(
                    rol.nombre_rol.lower() in admin_roles for rol in roles_activos
                )
        except:
            pass
        return False

    def is_super_admin(self, user):
        """Check if user is Super Admin."""
        try:
            if hasattr(user, "roles_activos"):
                roles_activos = user.roles_activos()
                return any(
                    rol.nombre_rol.lower() == "super administrador"
                    for rol in roles_activos
                )
        except:
            pass
        return False

    def get_user_roles_lower(self, user):
        """Get user roles as lowercase list."""
        try:
            if hasattr(user, "roles_activos"):
                roles = user.roles_activos()
                return [r.nombre_rol.lower() for r in roles]
        except:
            pass
        return []

    def has_permission(self, request, view):
        """Check if user has RRHH module access."""
        if not super().has_permission(request, view):
            return False

        # Super Admin full access
        if self.is_super_admin(request.user):
            return True

        # Check RRHH roles (match against known role names, case-insensitive)
        roles = self.get_user_roles_lower(request.user)
        rrhh_role_names = [
            "super administrador",
            "administrador rrhh",
            "analista rrhh",
            "jefe de area",
            "admin",
            "administrador",
            "rrhh",
            "supervisor",
        ]

        if any(r in rrhh_role_names for r in roles):
            return True

        # Allow employees in read operations
        if request.method in permissions.SAFE_METHODS:
            if hasattr(request.user, "empleado") and request.user.empleado:
                return True

        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions."""
        if not self.has_permission(request, view):
            return False

        # Super Administrador tiene acceso completo a todo
        if self.is_super_admin(request.user):
            return True

        # Admins have full access
        if self.is_admin_user(request.user):
            return True

        # Default to True for base RRHH permission
        return True


class AreaPermission(RRHHPermission):
    """Permission for Department management.

    Permite:
    - RRHH/Admin: lectura y escritura completa
    - Empleados normales: solo lectura (necesitan ver áreas para formularios)
    """

    def has_permission(self, request, view):
        """Check area management permissions."""
        # Super Administrador tiene acceso completo
        if self.is_super_admin(request.user):
            return True

        # Read permissions - todos los usuarios autenticados pueden ver áreas
        if request.method in permissions.SAFE_METHODS:
            # No llamar a super() para lectura - permitir a todos
            if request.user.is_authenticated:
                return True

        # Para escritura, verificar roles RRHH
        if not super().has_permission(request, view):
            return False

        # Write permissions - only admin and RRHH
        roles_activos = request.user.roles_activos()
        admin_roles = ["admin", "rrhh"]

        has_write_permission = any(
            rol.nombre_rol.lower() in admin_roles for rol in roles_activos
        )

        if not has_write_permission:
            logger.warning(
                f"Acceso denegado para modificar áreas",
                extra={
                    "user_id": request.user.usuario_id,
                    "username": request.user.nombres_usuario,
                    "method": request.method,
                    "view": view.__class__.__name__,
                    "ip_address": self.get_client_ip(request),
                },
            )

        return has_write_permission

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for areas."""
        if not super().has_object_permission(request, view, obj):
            return False

        # Read permissions
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions - only admin and RRHH
        roles_activos = request.user.roles_activos()
        admin_roles = ["admin", "rrhh"]

        return any(rol.nombre_rol.lower() in admin_roles for rol in roles_activos)


class EmpleadoPermission(RRHHPermission):
    """Permission for Employee management."""

    def has_permission(self, request, view):
        """Check employee access permissions."""
        if not super().has_permission(request, view):
            return False

        # Super Administrador tiene acceso completo
        if self.is_super_admin(request.user):
            return True

        # Read permissions - allow all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions - only RRHH staff
        roles = self.get_user_roles_lower(request.user)
        write_roles = ["admin", "rrhh", "supervisor", "administrador rrhh", "analista rrhh", "jefe de area"]

        return any(r in write_roles for r in roles)

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions."""
        # Admins have full access
        if self.is_admin_user(request.user):
            return True

        # Super admin full access
        if self.is_super_admin(request.user):
            return True

        # Check ownership for regular employees
        is_own_record = (
            hasattr(request.user, "empleado") and request.user.empleado == obj
        )

        # Read permissions
        if request.method in permissions.SAFE_METHODS:
            # Own record
            if is_own_record:
                return True

            # Supervisors can see employees in their area
            roles = self.get_user_roles_lower(request.user)
            if "supervisor" in roles:
                try:
                    user_area = self.get_user_current_area(request.user)
                    employee_area = self.get_employee_current_area(obj)
                    if user_area and employee_area and user_area == employee_area:
                        return True
                except:
                    pass

        # Write permissions
        if request.method in ["PUT", "PATCH"]:
            # Own record
            if is_own_record:
                return True

            # RRHH and supervisors
            roles = self.get_user_roles_lower(request.user)
            if "rrhh" in roles:
                return True

            if "supervisor" in roles:
                try:
                    user_area = self.get_user_current_area(request.user)
                    employee_area = self.get_employee_current_area(obj)
                    if user_area and employee_area and user_area == employee_area:
                        return True
                except:
                    pass

        return False

    def get_user_current_area(self, user):
        """Get user's current area."""
        try:
            if hasattr(user, "empleado") and user.empleado:
                ubicacion = user.empleado.ubicacion_actual()
                return ubicacion.area if ubicacion else None
        except:
            pass
        return None

    def get_employee_current_area(self, empleado):
        """Get employee's current area."""
        try:
            ubicacion = empleado.ubicacion_actual()
            return ubicacion.area if ubicacion else None
        except:
            pass
        return None


# BoletaPermission removed - replaced by DocumentosDigitalesPermission with tipo_documento='BOLETA_PAGO'


class DocumentosDigitalesPermission(BasePermission):
    """Permission for DigitalDocument.

    Allows any authenticated user to list, retrieve, and create documents
    (the view handles ownership validation for non-HR users).
    Requires RRHH/admin roles for update, delete, and custom actions.
    """

    OPEN_ACTIONS = {"list", "retrieve", "create"}
    RRHH_ROLES = {"admin", "administrador", "rrhh", "supervisor", "super administrador"}

    def has_permission(self, request, view):
        """Check document access permissions."""
        if not super().has_permission(request, view):
            return False

        # Open actions: any authenticated user
        action = getattr(view, "action", None)
        if action in self.OPEN_ACTIONS:
            return True

        # All other actions require RRHH roles
        if hasattr(request.user, "roles_activos"):
            roles_activos = request.user.roles_activos()
            if any(rol.nombre_rol.lower() in self.RRHH_ROLES for rol in roles_activos):
                return True

        return False


class UsuarioPermission(RRHHPermission):
    """Permission for User management."""

    def has_permission(self, request, view):
        """Check user management permissions."""
        if not super().has_permission(request, view):
            return False

        # Super Administrador tiene acceso completo
        if self.is_super_admin(request.user):
            return True

        # Only admins can manage users
        if not self.is_admin_user(request.user):
            logger.warning(
                f"Acceso denegado para gestión de usuarios",
                extra={
                    "user_id": request.user.usuario_id,
                    "username": request.user.nombres_usuario,
                    "method": request.method,
                    "view": view.__class__.__name__,
                    "ip_address": self.get_client_ip(request),
                },
            )
            return False

        return True

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for users."""
        if not super().has_object_permission(request, view, obj):
            return False

        # Only admins can manage users
        return self.is_admin_user(request.user)


class DatosPersonalesPermission(RRHHPermission):
    """Permission for personal data (family, academic, labor)."""

    def has_permission(self, request, view):
        """Check personal data management permissions."""
        if not super().has_permission(request, view):
            return False

        # Super Admin full access
        if self.is_super_admin(request.user):
            return True

        # Read - all authenticated
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write - admin, RRHH, supervisors, or own data
        roles = self.get_user_roles_lower(request.user)
        write_roles = ["admin", "rrhh", "supervisor"]

        # Staff can write
        if any(r in write_roles for r in roles):
            return True

        # Employees can edit their own (checked in has_object_permission)
        if request.method in ["PUT", "PATCH", "POST"]:
            return True

        return False

    def has_object_permission(self, request, view, obj):
        """Check object-level permissions for personal data."""
        # Super Admin full access
        if self.is_super_admin(request.user):
            return True

        # Admin and RRHH full access
        roles = self.get_user_roles_lower(request.user)
        if any(r in ["admin", "rrhh"] for r in roles):
            return True

        # Get employee from object
        empleado = None
        if hasattr(obj, "empleado"):
            empleado = obj.empleado
        elif hasattr(obj, "datos_laborales"):
            empleado = obj.datos_laborales.empleado

        if not empleado:
            return False

        # Check ownership
        is_own_record = (
            hasattr(request.user, "empleado") and request.user.empleado == empleado
        )

        # Own data access
        if is_own_record and request.method in permissions.SAFE_METHODS:
            return True

        # Own data edit
        if is_own_record and request.method in ["PUT", "PATCH"]:
            return True

        # Supervisors can manage employees in their area
        if "supervisor" in roles:
            try:
                user_area = self.get_user_current_area(request.user)
                employee_area = self.get_employee_current_area(empleado)
                if user_area and employee_area and user_area == employee_area:
                    return True
            except:
                pass

        return False

    def get_user_current_area(self, user):
        """Get user's current area."""
        try:
            if hasattr(user, "empleado") and user.empleado:
                ubicacion = user.empleado.ubicacion_actual()
                return ubicacion.area if ubicacion else None
        except:
            pass
        return None

    def get_employee_current_area(self, empleado):
        """Get employee's current area."""
        try:
            ubicacion = empleado.ubicacion_actual()
            return ubicacion.area if ubicacion else None
        except:
            pass
        return None


class ReportesPermission(RRHHPermission):
    """Permission for reports and statistics."""

    def has_permission(self, request, view):
        """Check reports access permissions."""
        if not super().has_permission(request, view):
            return False

        # Super Administrador tiene acceso completo
        if self.is_super_admin(request.user):
            return True

        # Only read operations for reports
        if request.method not in permissions.SAFE_METHODS:
            return False

        # Admin, RRHH, and supervisors can access reports
        roles_activos = request.user.roles_activos()
        report_roles = ["admin", "rrhh", "supervisor"]

        has_report_permission = any(
            rol.nombre_rol.lower() in report_roles for rol in roles_activos
        )

        if not has_report_permission:
            logger.warning(
                f"Acceso denegado a reportes",
                extra={
                    "user_id": request.user.usuario_id,
                    "username": request.user.nombres_usuario,
                    "view": view.__class__.__name__,
                    "action": getattr(view, "action", "unknown"),
                    "ip_address": self.get_client_ip(request),
                },
            )

        return has_report_permission


class AuditoriaPermission(RRHHPermission):
    """Permission for audit logs and sensitive operations."""

    def has_permission(self, request, view):
        """Check audit access permissions."""
        if not super().has_permission(request, view):
            return False

        # Super Administrador tiene acceso completo
        if self.is_super_admin(request.user):
            return True

        # Only admins can access audit information
        if not self.is_admin_user(request.user):
            logger.warning(
                f"Acceso denegado a auditoría",
                extra={
                    "user_id": request.user.usuario_id,
                    "username": request.user.nombres_usuario,
                    "view": view.__class__.__name__,
                    "ip_address": self.get_client_ip(request),
                },
            )
            return False

        return True


# Convenience function to get appropriate permission class
def get_permission_class(model_name: str):
    """Get appropriate permission class for model."""
    permission_mapping = {
        "area": AreaPermission,
        "empleado": EmpleadoPermission,
        "usuario": UsuarioPermission,
        "datosfamiliares": DatosPersonalesPermission,
        "datosacademicos": DatosPersonalesPermission,
        "datoslaborales": DatosPersonalesPermission,
        "regubicacion": DatosPersonalesPermission,
        "regpermisos": DatosPersonalesPermission,
        "rol": UsuarioPermission,
        "permiso": RRHHPermission,
    }

    return permission_mapping.get(model_name.lower(), RRHHPermission)
