"""Decoradores para validación de permisos en el backend."""

from functools import wraps
from typing import Any, Callable, List, Union

from apps.core.constants import Roles
from apps.core.permission_service import PermissionService
from apps.identity.models import User
from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from rest_framework import status
from rest_framework.response import Response


def require_roles(roles: Union[str, List[str]]):
    """Decorador que requiere que el usuario tenga uno de los roles especificados.

    Args:
        roles: Role o lista de roles requeridos

    Returns:
        Decorador que valida los roles

    Example:
        @require_roles(['Administrador', 'RRHH'])
        def my_view(request):
            return Response({'message': 'Acceso autorizado'})
    """
    if isinstance(roles, str):
        roles = [roles]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener el request del primer argumento (para vistas basadas en funciones)
            # o del objeto self (para vistas basadas en clases)
            request = None
            if args:
                if hasattr(args[0], "request"):
                    # Vista basada en clase
                    request = args[0].request
                elif hasattr(args[0], "user"):
                    # Request directo
                    request = args[0]

            if not request:
                return _create_error_response(
                    "Error interno: No se pudo obtener el request", "INTERNAL_ERROR"
                )

            # Verificar autenticación
            if (
                isinstance(request.user, AnonymousUser)
                or not request.user.is_authenticated
            ):
                return _create_error_response(
                    "User no autenticado", "AUTHENTICATION_REQUIRED"
                )

            try:
                # request.user IS already the User instance (custom user model)
                usuario = request.user

                # Superusuarios de Django tienen acceso completo sin necesidad de roles
                if getattr(usuario, "is_superuser", False):
                    pass  # authorized
                else:
                    if not PermissionService.has_any_role(usuario, roles):
                        return _create_error_response(
                            f'No tienes permisos para acceder a este recurso. Roles requeridos: {", ".join(roles)}',
                            "INSUFFICIENT_PERMISSIONS",
                        )

            except Exception:
                return _create_error_response(
                    "Error interno del servidor", "INTERNAL_ERROR"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_permissions(permissions: Union[str, List[str]]):
    """Decorador que requiere que el usuario tenga uno de los permisos especificados.

    Args:
        permissions: Permission o lista de permisos requeridos

    Returns:
        Decorador que valida los permisos

    Example:
        @require_permissions(['ver_usuarios', 'gestionar_usuarios'])
        def get_users(request):
            return Response({'users': []})
    """
    if isinstance(permissions, str):
        permissions = [permissions]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener el request
            request = None
            if args:
                if hasattr(args[0], "request"):
                    request = args[0].request
                elif hasattr(args[0], "user"):
                    request = args[0]

            if not request:
                return _create_error_response(
                    "Error interno: No se pudo obtener el request", "INTERNAL_ERROR"
                )

            # Verificar autenticación
            if (
                isinstance(request.user, AnonymousUser)
                or not request.user.is_authenticated
            ):
                return _create_error_response(
                    "User no autenticado", "AUTHENTICATION_REQUIRED"
                )

            try:
                # request.user IS already the User instance
                usuario = request.user

                # Superusuarios de Django tienen acceso completo
                if getattr(usuario, "is_superuser", False):
                    pass  # authorized
                else:
                    if not PermissionService.has_any_permission(usuario, permissions):
                        return _create_error_response(
                            f'No tienes permisos para realizar esta acción. Permisos requeridos: {", ".join(permissions)}',
                            "INSUFFICIENT_PERMISSIONS",
                        )

            except Exception:
                return _create_error_response(
                    "Error interno del servidor", "INTERNAL_ERROR"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def require_admin():
    """Decorador que requiere que el usuario sea administrador.

    Returns:
        Decorador que valida rol de administrador

    Example:
        @require_admin()
        def delete_user(request, user_id):
            # Solo administradores pueden eliminar usuarios
            pass
    """
    return require_roles(Roles.ADMIN_ROLES)


def require_hr():
    """Decorador que requiere que el usuario sea de RRHH o superior.

    Returns:
        Decorador que valida rol de RRHH

    Example:
        @require_hr()
        def view_employee_data(request):
            # Solo RRHH y superiores pueden ver datos de empleados
            pass
    """
    return require_roles(Roles.HR_ROLES)


def require_manager():
    """Decorador que requiere que el usuario sea gerente o superior.

    Returns:
        Decorador que valida rol de gerente

    Example:
        @require_manager()
        def approve_vacation(request):
            # Solo gerentes y superiores pueden aprobar vacaciones
            pass
    """
    return require_roles(Roles.MANAGER_ROLES)


def require_authenticated():
    """Decorador que requiere que el usuario esté autenticado.

    Returns:
        Decorador que valida autenticación

    Example:
        @require_authenticated()
        def get_profile(request):
            # Solo usuarios autenticados pueden ver su perfil
            pass
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener el request
            request = None
            if args:
                if hasattr(args[0], "request"):
                    request = args[0].request
                elif hasattr(args[0], "user"):
                    request = args[0]

            if not request:
                return _create_error_response(
                    "Error interno: No se pudo obtener el request", "INTERNAL_ERROR"
                )

            # Verificar autenticación
            if (
                isinstance(request.user, AnonymousUser)
                or not request.user.is_authenticated
            ):
                return _create_error_response(
                    "User no autenticado", "AUTHENTICATION_REQUIRED"
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def _create_error_response(message: str, error_code: str) -> Response:
    """Crear respuesta de error estandarizada.

    Args:
        message: Mensaje de error
        error_code: Código de error

    Returns:
        Response: Respuesta de error en formato JSON
    """
    return Response(
        {"success": False, "message": message, "error_code": error_code},
        status=status.HTTP_403_FORBIDDEN,
    )


# Decoradores específicos para permisos comunes


# =============================================================================
# CACHE DECORATORS
# =============================================================================


def cache_response(
    timeout: int = 300, key_prefix: str = "", vary_on_user: bool = False
):
    """Decorador para cachear respuestas de vistas DRF.

    Args:
        timeout: Tiempo de expiración en segundos (default: 300 = 5 minutos)
        key_prefix: Prefijo para la clave de cache
        vary_on_user: Si True, cachea por usuario (default: False)

    Returns:
        Decorador que cachea la respuesta

    Example:
        @cache_response(timeout=600, key_prefix='areas')
        def list(self, request):
            # Esta respuesta se cacheará por 10 minutos
            return Response(data)

        @cache_response(timeout=300, vary_on_user=True)
        def retrieve(self, request, pk=None):
            # Cada usuario tendrá su propia cache
            return Response(data)
    """
    import hashlib

    from django.core.cache import cache
    from django.utils.encoding import force_str

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Obtener request del primer argumento (self en viewsets)
            request = None
            if args and len(args) > 0:
                if hasattr(args[0], "request"):
                    request = args[0].request
                elif hasattr(args[0], "user"):
                    request = args[0]

            if not request:
                # No podemos cachear sin request, ejecutar normalmente
                return func(*args, **kwargs)

            # Construir clave de cache
            cache_key_parts = []

            if key_prefix:
                cache_key_parts.append(key_prefix)

            # Agregar path de la URL
            cache_key_parts.append(request.path)

            # Agregar query params (ordenados para consistencia)
            query_string = "&".join(f"{k}={v}" for k, v in sorted(request.GET.items()))
            if query_string:
                cache_key_parts.append(query_string)

            # Agregar usuario si se requiere
            if vary_on_user and request.user.is_authenticated:
                user_id = getattr(request.user, "id", request.user.pk)
                cache_key_parts.append(f"user_{user_id}")

            # Generar hash de la clave para mantenerla corta
            cache_key_str = "|".join(cache_key_parts)
            cache_key_hash = hashlib.md5(force_str(cache_key_str).encode()).hexdigest()
            key_namespace = key_prefix or "global"
            cache_key = f"view_cache:{key_namespace}:{cache_key_hash}"

            # Intentar obtener de cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                if isinstance(cached_response, dict) and "data" in cached_response:
                    from rest_framework.response import Response as DRFResponse
                    return DRFResponse(cached_response["data"], status=cached_response["status_code"])
                return cached_response

            # Ejecutar función y cachear resultado
            response = func(*args, **kwargs)

            # Solo cachear respuestas exitosas
            if hasattr(response, "status_code") and 200 <= response.status_code < 300:
                # Cachear los datos en vez del Response object (DRF Response no se puede
                # serializar/pickle antes de que el renderer sea asignado por dispatch)
                cache.set(cache_key, {"data": response.data, "status_code": response.status_code}, timeout)

            return response

        return wrapper

    return decorator


def cache_queryset(timeout: int = 300, key_prefix: str = ""):
    """Decorador para cachear resultados de querysets.

    Args:
        timeout: Tiempo de expiración en segundos (default: 300 = 5 minutos)
        key_prefix: Prefijo para la clave de cache

    Returns:
        Decorador que cachea el queryset

    Example:
        @cache_queryset(timeout=600, key_prefix='active_areas')
        def get_active_areas():
            return Department.objects.filter(estado=True)
    """
    import hashlib

    from django.core.cache import cache
    from django.utils.encoding import force_str

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Construir clave basada en nombre de función y argumentos
            cache_key_parts = [key_prefix] if key_prefix else []
            cache_key_parts.append(func.__name__)

            # Agregar args y kwargs a la clave
            if args:
                cache_key_parts.append(str(args))
            if kwargs:
                sorted_kwargs = "&".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key_parts.append(sorted_kwargs)

            cache_key_str = "|".join(str(p) for p in cache_key_parts)
            cache_key_hash = hashlib.md5(force_str(cache_key_str).encode()).hexdigest()
            key_namespace = key_prefix or "global"
            cache_key = f"queryset_cache:{key_namespace}:{cache_key_hash}"

            # Intentar obtener de cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Ejecutar función y cachear
            result = func(*args, **kwargs)

            # Para querysets, convertir a lista para cachear
            from django.db.models.query import QuerySet

            if isinstance(result, QuerySet):
                result = list(result)

            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def invalidate_cache(patterns: Union[str, List[str]]):
    """Decorador para invalidar cache después de ejecutar una función.

    Args:
        patterns: Patrón o lista de patrones de claves a invalidar

    Returns:
        Decorador que invalida cache

    Example:
        @invalidate_cache(['view_cache:*areas*', 'queryset_cache:*active_areas*'])
        def crear_area(data):
            # Después de crear, se invalidarán todas las caches de áreas
            return Department.objects.create(**data)
    """
    from django.core.cache import cache

    if isinstance(patterns, str):
        patterns = [patterns]

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Ejecutar función primero
            result = func(*args, **kwargs)

            # Invalidar cache
            for pattern in patterns:
                # django-redis soporta delete_pattern
                if hasattr(cache, "delete_pattern"):
                    cache.delete_pattern(pattern)
                else:
                    # Fallback: intentar borrar la clave exacta
                    cache.delete(pattern)

            return result

        return wrapper

    return decorator


def cache_method(timeout: int = 300, key_prefix: str = ""):
    """Decorador para cachear métodos de clase/instancia.

    Args:
        timeout: Tiempo de expiración en segundos
        key_prefix: Prefijo para la clave de cache

    Returns:
        Decorador que cachea el método

    Example:
        class EmployeeService:
            @cache_method(timeout=600, key_prefix='employee_stats')
            def get_department_statistics(self, department_id):
                # Cálculos costosos aquí
                return stats
    """
    import hashlib

    from django.core.cache import cache
    from django.utils.encoding import force_str

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Construir clave de cache
            cache_key_parts = [key_prefix] if key_prefix else []

            # Agregar nombre de clase si es método de instancia
            if args and hasattr(args[0], "__class__"):
                cache_key_parts.append(args[0].__class__.__name__)
                # Excluir self/cls del hash de args
                hash_args = args[1:]
            else:
                hash_args = args

            cache_key_parts.append(func.__name__)

            # Agregar args y kwargs
            if hash_args:
                cache_key_parts.append(str(hash_args))
            if kwargs:
                sorted_kwargs = "&".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key_parts.append(sorted_kwargs)

            cache_key_str = "|".join(str(p) for p in cache_key_parts)
            cache_key_hash = hashlib.md5(force_str(cache_key_str).encode()).hexdigest()
            key_namespace = key_prefix or "global"
            cache_key = f"method_cache:{key_namespace}:{cache_key_hash}"

            # Intentar obtener de cache
            cached_result = cache.get(cache_key)
            if cached_result is not None:
                return cached_result

            # Ejecutar y cachear
            result = func(*args, **kwargs)
            cache.set(cache_key, result, timeout)
            return result

        return wrapper

    return decorator


def require_view_users():
    """Decorador para ver usuarios."""
    return require_permissions(["ver_usuarios"])


def require_edit_users():
    """Decorador para editar usuarios."""
    return require_permissions(["editar_usuarios"])


def require_delete_users():
    """Decorador para eliminar usuarios."""
    return require_permissions(["eliminar_usuarios"])


def require_view_employees():
    """Decorador para ver empleados."""
    return require_permissions(["ver_empleados"])


def require_edit_employees():
    """Decorador para editar empleados."""
    return require_permissions(["editar_empleados"])


def require_delete_employees():
    """Decorador para eliminar empleados."""
    return require_permissions(["eliminar_empleados"])


def require_view_payrolls():
    """Decorador para ver boletas de pago."""
    return require_permissions(["ver_boletas"])


def require_edit_payrolls():
    """Decorador para editar boletas de pago."""
    return require_permissions(["editar_boletas"])


def require_edit_payrolls():
    """Decorador para editar boletas de pago."""
    return require_permissions(["editar_boletas"])
