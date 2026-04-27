from rest_framework import serializers

from apps.contracts.models import EmploymentData
from apps.employees.models import (
    AcademicRecord,
    FamilyMember,
    Employee,
)
from apps.organization.models import Department, LocationHistory
from apps.identity.models import (
    Permission,
    Role,
    RolePermission,
    User,
)


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = "__all__"


class DatosFamiliaresSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyMember
        fields = "__all__"


class DatosAcademicosSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicRecord
        fields = "__all__"


class DatosLaboralesSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmploymentData
        fields = "__all__"


class HistorialUbicacionesSerializer(serializers.ModelSerializer):
    class Meta:
        model = LocationHistory
        fields = "__all__"


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
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
        model = Role
        fields = "__all__"


class PermisoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
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
        model = RolePermission
        fields = "__all__"


class EmpleadoSerializer(serializers.ModelSerializer):
    # Campos relacionados
    familiares = DatosFamiliaresSerializer(many=True, read_only=True)
    academicos = DatosAcademicosSerializer(many=True, read_only=True)
    laborales = DatosLaboralesSerializer(many=True, read_only=True)
    # boletas = BoletaSerializer(many=True, read_only=True) - removed, replaced by documentos_digitales
    ubicaciones = HistorialUbicacionesSerializer(many=True, read_only=True)

    class Meta:
        model = Employee
        fields = "__all__"
        depth = 1  # Opcional: muestra relaciones anidadas


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=45)
    password = serializers.CharField(max_length=128, write_only=True)
