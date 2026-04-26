from rest_framework import serializers

from .models import (
    DatosLaborales,
)
from apps.employees.models import (
    DatosAcademicos,
    DatosFamiliares,
    Empleado,
)
from apps.organization.models import Area, HistorialUbicaciones
from apps.identity.models import (
    Permiso,
    Rol,
    RolPermisos,
    Usuario,
)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = "__all__"


class DatosFamiliaresSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosFamiliares
        fields = "__all__"


class DatosAcademicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosAcademicos
        fields = "__all__"


class DatosLaboralesSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosLaborales
        fields = "__all__"


class HistorialUbicacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = HistorialUbicaciones
        fields = "__all__"


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "usuario_id",
            "nombres_usuario",
            "date_joined",
            "last_login",
            "estado_usuario",
        ]
        extra_kwargs = {"password": {"write_only": True}}


class RolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rol
        fields = "__all__"


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permiso
        fields = "__all__"


class RolPermisosSerializer(serializers.ModelSerializer):
    rol_nombre = serializers.CharField(source="rol.nombre_rol", read_only=True)
    permiso_nombre = serializers.CharField(
        source="permiso.nombre_permiso", read_only=True
    )
    asignado_por_nombre = serializers.CharField(
        source="asignado_por_usuario.username", read_only=True
    )

    class Meta:
        model = RolPermisos
        fields = "__all__"


class EmpleadoSerializer(serializers.ModelSerializer):
    # Campos relacionados
    familiares = DatosFamiliaresSerializer(many=True, read_only=True)
    academicos = DatosAcademicosSerializer(many=True, read_only=True)
    laborales = DatosLaboralesSerializer(many=True, read_only=True)
    # boletas = BoletaSerializer(many=True, read_only=True) - removed, replaced by documentos_digitales
    ubicaciones = HistorialUbicacionesSerializer(many=True, read_only=True)

    class Meta:
        model = Empleado
        fields = "__all__"
        depth = 1  # Opcional: muestra relaciones anidadas


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=45)
    password = serializers.CharField(max_length=128, write_only=True)
