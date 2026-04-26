"""Permisos personalizados para las APIs de vacaciones."""

from app_rrhh.constants import Roles
from app_rrhh.models import Empleado
from app_rrhh.models.vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)
from app_rrhh.permission_service import PermissionService
from rest_framework import permissions


def _area_empleado(empleado: Empleado):
    datos = empleado.datos_laborales_actuales()
    return datos.area if datos else None


class VacationPermissions(permissions.BasePermission):
    """Permisos base del módulo de vacaciones."""

    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False
        is_hr_admin = PermissionService.has_any_role(user, Roles.HR_ROLES)
        if (
            is_hr_admin
            or getattr(user, "is_staff", False)
            or getattr(user, "is_superuser", False)
        ):
            return True
        if not getattr(user, "empleado", None):
            return False

        action = getattr(view, "action", None)
        view_name = view.__class__.__name__

        if view_name == "ConfiguracionVacacionesViewSet" and action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return is_hr_admin
        if view_name == "PeriodoVacacionalViewSet" and action in [
            "generar_masivo",
            "ajustar_dias",
        ]:
            return is_hr_admin
        if view_name == "SolicitudVacacionesViewSet" and action in [
            "aprobar_jefe",
            "pendientes_jefe",
        ]:
            return user.es_jefe or is_hr_admin
        if view_name == "SolicitudVacacionesViewSet" and action in [
            "aprobar_rrhh",
            "pendientes_rrhh",
        ]:
            return is_hr_admin
        if view_name == "VacacionesReportesViewSet":
            return user.es_jefe or is_hr_admin
        return True

    def has_object_permission(self, request, view, obj):
        user = request.user
        if PermissionService.has_any_role(user, Roles.HR_ROLES):
            return True

        if isinstance(obj, ConfiguracionVacaciones):
            if obj.tipo_configuracion == "general":
                return True
            if obj.tipo_configuracion == "area":
                return _area_empleado(user.empleado) == obj.area
            if obj.tipo_configuracion == "empleado":
                return obj.empleado == user.empleado
            return False

        if isinstance(obj, PeriodoVacacional):
            if obj.empleado == user.empleado:
                return True
            if user.es_jefe:
                return _area_empleado(obj.empleado) == _area_empleado(user.empleado)
            return False

        if isinstance(obj, SolicitudVacaciones):
            if obj.empleado == user.empleado:
                return True
            if user.es_jefe:
                return _area_empleado(obj.empleado) == _area_empleado(user.empleado)
            return False

        if isinstance(obj, GoceVacaciones):
            if obj.empleado == user.empleado:
                return True
            if user.es_jefe:
                return _area_empleado(obj.empleado) == _area_empleado(user.empleado)
            return False

        if isinstance(obj, HistorialSolicitudVacaciones):
            solicitud = obj.solicitud_vacaciones
            if solicitud.empleado == user.empleado:
                return True
            if user.es_jefe:
                return _area_empleado(solicitud.empleado) == _area_empleado(
                    user.empleado
                )
            return False

        return False


class VacationAdminPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and PermissionService.has_any_role(
            request.user, Roles.HR_ROLES
        )


class VacationManagerPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.es_jefe
            or PermissionService.has_any_role(request.user, Roles.HR_ROLES)
        )


class VacationEmployeePermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, "empleado", None) is not None
        )

    def has_object_permission(self, request, view, obj):
        user = request.user
        if PermissionService.has_any_role(user, Roles.HR_ROLES):
            return True
        if hasattr(obj, "empleado"):
            return obj.empleado == user.empleado
        if hasattr(obj, "solicitud_vacaciones"):
            return obj.solicitud_vacaciones.empleado == user.empleado
        return False


class VacationApprovalPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        action = getattr(view, "action", None)
        is_hr_admin = PermissionService.has_any_role(user, Roles.HR_ROLES)
        if not user.is_authenticated or not getattr(user, "empleado", None):
            return False
        if action in ["aprobar_jefe", "pendientes_jefe"]:
            return user.es_jefe or is_hr_admin
        if action in ["aprobar_rrhh", "pendientes_rrhh"]:
            return is_hr_admin
        return True
