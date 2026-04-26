"""Serializers for UsuarioRoles management."""

from rest_framework import serializers
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
from typing import Dict, Any

from apps.identity.models import UsuarioRoles, Usuario, Rol
from apps.core.exceptions import BusinessLogicError


class UsuarioRolesSerializer(serializers.ModelSerializer):
    """Serializer for UsuarioRoles model."""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre_rol', read_only=True)
    asignado_por_nombre = serializers.CharField(source='asignado_por_usuario.nombre_completo', read_only=True)
    es_activo = serializers.SerializerMethodField()
    dias_hasta_expiracion = serializers.SerializerMethodField()
    
    class Meta:
        model = UsuarioRoles
        fields = [
            'usuario_rol_id', 'usuario', 'rol', 'fecha_asignacion', 'fecha_expiracion',
            'asignado_por_usuario', 'estado_asignacion', 'usuario_nombre', 'rol_nombre',
            'asignado_por_nombre', 'es_activo', 'dias_hasta_expiracion'
        ]
        read_only_fields = ['usuario_rol_id', 'fecha_asignacion']
    
    def get_es_activo(self, obj):
        """Verificar si la asignación está activa y no ha expirado."""
        if obj.estado_asignacion != 'activo':
            return False
        
        if obj.fecha_expiracion and obj.fecha_expiracion <= timezone.now():
            return False
            
        return True
    
    def get_dias_hasta_expiracion(self, obj):
        """Calcular días hasta la expiración."""
        if not obj.fecha_expiracion:
            return None
        
        dias = (obj.fecha_expiracion - timezone.now()).days
        return max(0, dias)
    
    def validate(self, data):
        """Validar datos de asignación de rol."""
        usuario = data.get('usuario')
        rol = data.get('rol')
        
        # Verificar que el usuario existe y está activo
        if usuario and usuario.estado_usuario != 'activo':
            raise serializers.ValidationError({
                'usuario': 'No se puede asignar rol a un usuario inactivo.'
            })
        
        # Verificar que el rol existe y está activo
        if rol and rol.estado_rol != 'activo':
            raise serializers.ValidationError({
                'rol': 'No se puede asignar un rol inactivo.'
            })
        
        # Verificar que no existe una asignación activa del mismo rol al usuario
        if usuario and rol:
            existing = UsuarioRoles.objects.filter(
                usuario=usuario,
                rol=rol,
                estado_asignacion='activo'
            ).exclude(pk=self.instance.pk if self.instance else None)
            
            if existing.exists():
                raise serializers.ValidationError({
                    'rol': f'El usuario ya tiene asignado el rol {rol.nombre_rol}.'
                })
        
        # Validar fecha de expiración
        fecha_expiracion = data.get('fecha_expiracion')
        if fecha_expiracion and fecha_expiracion <= timezone.now():
            raise serializers.ValidationError({
                'fecha_expiracion': 'La fecha de expiración debe ser futura.'
            })
        
        return data


class UsuarioRolesCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating user role assignments."""
    
    class Meta:
        model = UsuarioRoles
        fields = [
            'usuario', 'rol', 'fecha_expiracion', 'estado_asignacion'
        ]
    
    def validate(self, data):
        """Validar datos de creación de asignación de rol."""
        usuario = data.get('usuario')
        rol = data.get('rol')
        
        # Verificar que el usuario existe y está activo
        if usuario.estado_usuario != 'activo':
            raise serializers.ValidationError({
                'usuario': 'No se puede asignar rol a un usuario inactivo.'
            })
        
        # Verificar que el rol existe y está activo
        if rol.estado_rol != 'activo':
            raise serializers.ValidationError({
                'rol': 'No se puede asignar un rol inactivo.'
            })
        
        # Verificar que no existe una asignación activa del mismo rol al usuario
        existing = UsuarioRoles.objects.filter(
            usuario=usuario,
            rol=rol,
            estado_asignacion='activo'
        )
        
        if existing.exists():
            raise serializers.ValidationError({
                'rol': f'El usuario ya tiene asignado el rol {rol.nombre_rol}.'
            })
        
        # Validar fecha de expiración
        fecha_expiracion = data.get('fecha_expiracion')
        if fecha_expiracion and fecha_expiracion <= timezone.now():
            raise serializers.ValidationError({
                'fecha_expiracion': 'La fecha de expiración debe ser futura.'
            })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Crear asignación de rol."""
        # Asignar el usuario que realiza la asignación
        validated_data['asignado_por_usuario'] = self.context['request'].user
        
        return super().create(validated_data)


class UsuarioRolesListSerializer(serializers.ModelSerializer):
    """Serializer for listing user role assignments."""
    
    usuario_nombre = serializers.CharField(source='usuario.nombre_completo', read_only=True)
    rol_nombre = serializers.CharField(source='rol.nombre_rol', read_only=True)
    rol_descripcion = serializers.CharField(source='rol.descripcion_rol', read_only=True)
    es_activo = serializers.SerializerMethodField()
    
    class Meta:
        model = UsuarioRoles
        fields = [
            'usuario_rol_id', 'usuario', 'rol', 'fecha_asignacion', 'fecha_expiracion',
            'estado_asignacion', 'usuario_nombre', 'rol_nombre', 'rol_descripcion', 'es_activo'
        ]
    
    def get_es_activo(self, obj):
        """Verificar si la asignación está activa y no ha expirado."""
        if obj.estado_asignacion != 'activo':
            return False
        
        if obj.fecha_expiracion and obj.fecha_expiracion <= timezone.now():
            return False
            
        return True


class AsignarRolSerializer(serializers.Serializer):
    """Serializer for assigning roles to users."""
    
    roles = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
        help_text="Lista de IDs de roles a asignar"
    )
    fecha_expiracion = serializers.DateTimeField(
        required=False,
        allow_null=True,
        help_text="Fecha de expiración de la asignación (opcional)"
    )
    
    def validate_roles(self, value):
        """Validar que los roles existen y están activos."""
        roles = Rol.objects.filter(rol_id__in=value, estado_rol='activo')
        
        if len(roles) != len(value):
            roles_encontrados = set(roles.values_list('rol_id', flat=True))
            roles_solicitados = set(value)
            roles_no_encontrados = roles_solicitados - roles_encontrados
            
            raise serializers.ValidationError(
                f"Los siguientes roles no existen o no están activos: {list(roles_no_encontrados)}"
            )
        
        return value
    
    def validate_fecha_expiracion(self, value):
        """Validar fecha de expiración."""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "La fecha de expiración debe ser futura."
            )
        return value