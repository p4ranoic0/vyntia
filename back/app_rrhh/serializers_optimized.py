"""Fallback optimized serializers.

This module keeps the public serializer names used by ``app_rrhh.views``.
If specialized optimized serializers are not available, we reuse the base
serializers so the API remains functional.
"""

from .serializers import (
    AreaSerializer,
    DatosAcademicosSerializer,
    DatosFamiliaresSerializer,
    DatosLaboralesSerializer,
    EmpleadoSerializer,
    PermisoSerializer,
    RolPermisosSerializer,
    RolSerializer,
    UsuarioSerializer,
)


class AreaListSerializer(AreaSerializer):
    pass


class AreaDetailSerializer(AreaSerializer):
    pass


class EmpleadoListSerializer(EmpleadoSerializer):
    pass


class EmpleadoDetailSerializer(EmpleadoSerializer):
    pass


class DatosFamiliaresListSerializer(DatosFamiliaresSerializer):
    pass


class DatosAcademicosListSerializer(DatosAcademicosSerializer):
    pass


class DatosLaboralesListSerializer(DatosLaboralesSerializer):
    pass


class UsuarioListSerializer(UsuarioSerializer):
    pass


class UsuarioDetailSerializer(UsuarioSerializer):
    pass


class RolListSerializer(RolSerializer):
    pass


class RolDetailSerializer(RolSerializer):
    pass


class PermisoListSerializer(PermisoSerializer):
    pass


class PermisoDetailSerializer(PermisoSerializer):
    pass


class RolPermisosDetailSerializer(RolPermisosSerializer):
    pass
