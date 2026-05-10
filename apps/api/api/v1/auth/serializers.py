"""Serializers for authentication API v1."""

from datetime import timedelta
from typing import Any, Dict, List, Optional

from apps.employees.models import Employee
from apps.identity.models import User
from django.conf import settings
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.crypto import get_random_string
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with additional user data."""

    # Override the username field to use nombre_usuario
    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Keep the username field as is since the model uses 'username'

    @classmethod
    def get_token(cls, user):
        """Mint an access token, injecting tenant claims when a tenant context is active.

        Called by the parent `validate()` during login. We read the active tenant
        from the ContextVar (set by TenantMiddleware) and the user's membership in
        that tenant; both go into the JWT payload so RLSMiddleware and
        TenantAuthMiddleware can validate downstream requests.

        Defensive: omits claims if context is missing or membership doesn't exist.
        Login enforcement (Task 2) ensures membership exists before this is called
        in production paths.
        """
        token = super().get_token(user)

        from apps.tenancy.context import get_current_tenant

        tenant = get_current_tenant()
        if tenant is not None:
            token["tenant_id"] = str(tenant.id)
            token["tenant_slug"] = tenant.slug

            # Lookup the user's membership in this tenant — emit role claim if present
            from apps.tenancy.models import TenantMembership

            membership = (
                TenantMembership.objects.filter(
                    tenant=tenant, user=user, status="active"
                )
                .only("role")
                .first()
            )
            if membership is not None:
                token["membership_role"] = membership.role

        return token

    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate credentials and return token with user data.

        Args:
            attrs: Authentication credentials

        Returns:
            Dict containing tokens and user information

        Raises:
            ValidationError: If credentials are invalid
            PermissionDenied: If on a tenant subdomain and user has no active
                TenantMembership for that workspace.
        """
        # The parent class will use the username_field we set
        data = super().validate(attrs)

        # Add user information to response
        # self.user is already a User instance due to AUTH_USER_MODEL
        usuario = self.user

        # ---- C.4: enforce TenantMembership when request.tenant is set ----
        # When the request comes in on a tenant subdomain (e.g. acme.vyntia.pe),
        # TenantMiddleware populates request.tenant. In that case the user MUST
        # have an active membership for that tenant — otherwise we refuse with
        # 403 (PermissionDenied). When request.tenant is None (testserver,
        # admin.vyntia.pe, app.vyntia.pe, localhost), legacy behavior is
        # preserved: no membership check is performed.
        request = self.context.get("request")
        tenant = getattr(request, "tenant", None) if request is not None else None
        if tenant is not None:
            from apps.tenancy.models import TenantMembership

            has_membership = TenantMembership.objects.filter(
                tenant=tenant, user=usuario, status="active"
            ).exists()
            if not has_membership:
                from rest_framework.exceptions import PermissionDenied

                raise PermissionDenied(
                    detail=f"No active membership in workspace '{tenant.slug}'."
                )

        
        data.update({
            'user': {
                'id': usuario.pk,
                'username': usuario.username,
                'email': usuario.email,
                'is_active': usuario.is_active,
                'is_vyntia_staff': usuario.is_vyntia_staff,
                'id': usuario.pk,
                'tipo_usuario': usuario.tipo_usuario,
                'nivel_acceso': usuario.nivel_acceso,
                'requiere_cambio_password': usuario.requiere_cambio_password,
                'empleado': {
                    'id': usuario.empleado.pk if usuario.empleado else None,
                    'nombres': usuario.empleado.nombres_empleado if usuario.empleado else None,
                    'apellido_paterno': usuario.empleado.apellido_paterno if usuario.empleado else None,
                    'apellido_materno': usuario.empleado.apellido_materno if usuario.empleado else None,
                    'numero_documento': usuario.empleado.numero_documento if usuario.empleado else None,
                    'ruta_fotografia': usuario.empleado.ruta_fotografia if usuario.empleado else None,
                } if usuario.empleado else None,
                'roles': self._get_user_roles_simple(usuario)
            },
            'roles': self._get_user_roles(usuario),
            'permissions': self._get_user_permissions(usuario),
        })
            
        return data
    
    def _get_user_roles(self, usuario: User) -> List[Dict[str, Any]]:
        """Get active roles for the user.
        
        Args:
            usuario: User instance
            
        Returns:
            List of role dictionaries
        """
        try:
            from apps.identity.models import UserRole

            # Obtener roles activos del usuario
            usuario_roles = UserRole.objects.filter(
                usuario=usuario,
                estado_asignacion='activo'
            ).select_related('rol')
            
            roles = []
            for ur in usuario_roles:
                if ur.rol:
                    roles.append({
                        'id': ur.rol.pk,
                        'nombre': ur.rol.nombre_rol,
                        'descripcion': ur.rol.descripcion_rol,
                        'estado': ur.rol.estado_rol
                    })
            
            return roles
        except Exception:
            return []
    
    def _get_user_roles_simple(self, usuario: User) -> List[Dict[str, Any]]:
        """Get active roles for the user with simplified data (only id and name).
        
        Args:
            usuario: User instance
            
        Returns:
            List of simplified role dictionaries
        """
        try:
            from apps.identity.models import UserRole

            # Obtener roles activos del usuario
            usuario_roles = UserRole.objects.filter(
                usuario=usuario,
                estado_asignacion='activo'
            ).select_related('rol')
            
            roles = []
            for ur in usuario_roles:
                if ur.rol:
                    roles.append({
                        'id': ur.rol.pk,
                        'nombre': ur.rol.nombre_rol
                    })
            
            return roles
        except Exception:
            return []
    
    def _get_user_permissions(self, usuario: User) -> List[Dict[str, Any]]:
        """Get active permissions for the user.
        
        Args:
            usuario: User instance
            
        Returns:
            List of permission dictionaries
        """
        try:
            from apps.identity.models import RolePermission, UserRole

            # Obtener roles activos del usuario
            usuario_roles = UserRole.objects.filter(
                usuario=usuario,
                estado_asignacion='activo'
            ).values_list('id', flat=True)
            
            # Obtener permisos de esos roles
            roles_permisos = RolePermission.objects.filter(
                rol_id__in=usuario_roles
            ).select_related('permiso')
            
            permisos = []
            permisos_vistos = set()  # Para evitar duplicados
            
            for rp in roles_permisos:
                if rp.permiso and rp.permiso.pk not in permisos_vistos:
                    permisos.append({
                        'id': rp.permiso.pk,
                        'nombre': rp.permiso.nombre_permiso,
                        'descripcion': rp.permiso.descripcion_permiso,
                        'id': rp.permiso.modulo,
                        'tipo': rp.permiso.tipo_permiso,
                        'estado': rp.permiso.estado_permiso
                    })
                    permisos_vistos.add(rp.permiso.pk)
            
            return permisos
        except Exception:
            return []
    
    def _get_user_modules(self, usuario: User) -> List[Dict[str, Any]]:
        """Get active modules for the user based on their permissions.
        
        Args:
            usuario: User instance
            
        Returns:
            List of module dictionaries with their permissions
        """
        try:
            from apps.identity.models import Module, RolePermission, UserRole

            # Obtener roles activos del usuario
            usuario_roles = UserRole.objects.filter(
                usuario=usuario,
                estado_asignacion='activo'
            ).values_list('id', flat=True)
            
            # Obtener permisos de esos roles
            roles_permisos = RolePermission.objects.filter(
                rol_id__in=usuario_roles
            ).select_related('permiso', 'permiso__modulo')
            
            # Agrupar permisos por módulo
            modulos_permisos = {}
            for rp in roles_permisos:
                if rp.permiso and rp.permiso.modulo:
                    modulo = rp.permiso.modulo
                    if modulo.pk not in modulos_permisos:
                        modulos_permisos[modulo.pk] = {
                            'id': modulo.pk,
                            'name': modulo.nombre_modulo,
                            'status': modulo.estado_modulo,
                            'permissions': []
                        }
                    
                    # Agregar permiso al módulo
                    modulos_permisos[modulo.pk]['permissions'].append({
                        'id': rp.permiso.pk,
                        'nombre': rp.permiso.nombre_permiso,
                        'descripcion': rp.permiso.descripcion_permiso,
                        'tipo': rp.permiso.tipo_permiso,
                        'estado': rp.permiso.estado_permiso
                    })
            
            return list(modulos_permisos.values())
        except Exception:
            return []


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField(
        max_length=150,
        help_text="Nombre de usuario"
    )
    password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Contraseña del usuario"
    )
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate login credentials.
        
        Args:
            attrs: Login credentials
            
        Returns:
            Validated data
            
        Raises:
            ValidationError: If credentials are invalid
        """
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(
                request=self.context.get('request'),
                username=username,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Credenciales inválidas. Verifique su usuario y contraseña.',
                    code='authorization'
                )
                
            if not user.is_active:
                raise serializers.ValidationError(
                    'La cuenta de usuario está desactivada.',
                    code='authorization'
                )
                
            attrs['user'] = user
        else:
            raise serializers.ValidationError(
                'Debe proporcionar username y contraseña.',
                code='authorization'
            )
            
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for user profile information."""
    
    empleado = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()
    permisos = serializers.SerializerMethodField()
    is_active = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 
            'is_active', 'created_at', 'last_login',
            'empleado', 'roles', 'permisos'
        ]
        read_only_fields = [
            'id', 'username', 'created_at', 'last_login',
            'empleado', 'roles', 'permisos'
        ]
    
    def get_empleado(self, obj: User) -> Optional[Dict[str, Any]]:
        """Get employee information."""
        try:
            if obj.empleado:
                return {
                    'id': obj.empleado.pk,
                    'nombres': obj.empleado.nombres_empleado,
                    'apellido_paterno': obj.empleado.apellido_paterno,
                    'apellido_materno': obj.empleado.apellido_materno,
                    'numero_documento': obj.empleado.numero_documento,
                }
            return None
        except Exception:
            return None
    
    def get_roles(self, obj: User) -> List[Dict[str, Any]]:
        """Get user roles.
        
        Args:
            obj: User instance
            
        Returns:
            List of user roles
        """
        try:
            roles_data = []
            # Obtener roles activos del usuario
            usuario_roles = obj.roles_asignados.filter(
                estado_asignacion='activo'
            ).select_related('rol')
            
            for usuario_rol in usuario_roles:
                rol = usuario_rol.rol
                roles_data.append({
                    'id': rol.pk,
                    'nombre_rol': rol.nombre_rol,
                    'descripcion_rol': rol.descripcion_rol,
                    'nivel_jerarquico': rol.nivel_jerarquico,
                    'es_rol_sistema': rol.es_rol_sistema,
                    'fecha_asignacion': usuario_rol.fecha_asignacion,
                    'fecha_expiracion': usuario_rol.fecha_expiracion
                })
            
            return roles_data
        except Exception:
            return []
    
    def get_permisos(self, obj: User) -> List[Dict[str, Any]]:
        """Get user permissions.
        
        Args:
            obj: User instance
            
        Returns:
            List of user permissions
        """
        try:
            permisos_data = []
            permisos_ids = set()
            
            # Obtener permisos a través de roles activos
            usuario_roles = obj.roles_asignados.filter(
                estado_asignacion='activo'
            ).select_related('rol')
            
            for usuario_rol in usuario_roles:
                rol_permisos = usuario_rol.rol.permisos_asignados.select_related('permiso')
                
                for rol_permiso in rol_permisos:
                    permiso = rol_permiso.permiso
                    # Evitar duplicados
                    if permiso.pk not in permisos_ids and permiso.estado_permiso == 'activo':
                        permisos_ids.add(permiso.pk)
                        permisos_data.append({
                            'id': permiso.pk,
                            'nombre_permiso': permiso.nombre_permiso,
                            'descripcion_permiso': permiso.descripcion_permiso,
                            'id': permiso.modulo,
                            'tipo_permiso': permiso.tipo_permiso,
                            'rol_origen': usuario_rol.rol.nombre_rol
                        })
            
            return permisos_data
        except Exception:
            return []
    
    def get_is_active(self, obj: User) -> bool:
        """Get user active status.
        
        Args:
            obj: User instance
            
        Returns:
            User active status
        """
        try:
            return obj.is_active
        except Exception as e:
            print(f"Error in get_is_active: {e}")
            return False


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    
    old_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Contraseña actual"
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Nueva contraseña"
    )
    confirm_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Confirmar nueva contraseña"
    )
    
    def validate_old_password(self, value: str) -> str:
        """Validate current password.
        
        Args:
            value: Current password
            
        Returns:
            Validated password
            
        Raises:
            ValidationError: If current password is incorrect
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError(
                'La contraseña actual es incorrecta.'
            )
        return value
    
    def validate_new_password(self, value: str) -> str:
        """Validate new password.
        
        Args:
            value: New password
            
        Returns:
            Validated password
            
        Raises:
            ValidationError: If password doesn't meet requirements
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                'La contraseña debe tener al menos 8 caracteres.'
            )
        
        # Verificar que contenga al menos una letra y un número
        if not any(c.isalpha() for c in value):
            raise serializers.ValidationError(
                'La contraseña debe contener al menos una letra.'
            )
        
        if not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                'La contraseña debe contener al menos un número.'
            )
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that new password and confirm password match.
        
        Args:
            attrs: Validated attributes
            
        Returns:
            Validated attributes
            
        Raises:
            ValidationError: If passwords don't match
        """
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')
        
        if new_password != confirm_password:
            raise serializers.ValidationError({
                'confirm_password': 'Las contraseñas no coinciden.'
            })
        
        # Verificar que la nueva contraseña sea diferente a la actual
        old_password = attrs.get('old_password')
        if new_password == old_password:
            raise serializers.ValidationError({
                'new_password': 'La nueva contraseña debe ser diferente a la actual.'
            })
        
        return attrs
    
    def save(self) -> Dict[str, Any]:
        """Change user password.

        Returns:
            Success information
        """
        user = self.context['request'].user
        new_password = self.validated_data['new_password']

        # Cambiar la contraseña
        user.set_password(new_password)
        # Desactivar flag de cambio obligatorio si estaba activo
        if user.requiere_cambio_password:
            user.requiere_cambio_password = False
        user.save()

        return {
            'message': 'Contraseña cambiada exitosamente',
            'user_id': user.pk
        }


class ForgotPasswordSerializer(serializers.Serializer):
    """Serializer para solicitud de recuperación de contraseña."""
    
    email = serializers.EmailField(
        help_text="Email del usuario para recuperación de contraseña"
    )
    
    def validate_email(self, value: str) -> str:
        """Validar que el email existe en el sistema.
        
        Args:
            value: Email address
            
        Returns:
            Validated email
            
        Raises:
            ValidationError: Si el email no existe
        """
        try:
            user = User.objects.get(email=value, is_active=True)
            self.context['user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'No se encontró un usuario activo con este email.'
            )
        return value
    
    def save(self) -> Dict[str, Any]:
        """Enviar email de recuperación de contraseña.
        
        Returns:
            Información sobre el envío del email
        """
        user = self.context['user']
        
        # Usar el método del modelo para generar token
        reset_token = user.generar_token_recuperacion()
        
        # Construir URL de recuperación
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        
        # Enviar email
        subject = 'VYNTIA — Recuperación de Contraseña'
        message = f"""
        Hola {user.empleado.nombres_empleado if user.empleado else user.username},
        
        Has solicitado recuperar tu contraseña. Haz clic en el siguiente enlace para crear una nueva contraseña:
        
        {reset_url}
        
        Este enlace expirará en 1 hora.
        
        Si no solicitaste este cambio, puedes ignorar este email.
        
        Saludos,
        Equipo VYNTIA
        """
        
        try:
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )
            return {
                'message': 'Se ha enviado un email con las instrucciones para recuperar tu contraseña.',
                'email_sent': True
            }
        except Exception as e:
            return {
                'message': 'Error al enviar el email. Intenta nuevamente más tarde.',
                'email_sent': False,
                'error': str(e)
            }


class ResetPasswordSerializer(serializers.Serializer):
    """Serializer para restablecer contraseña con token."""
    
    token = serializers.CharField(
        max_length=32,
        help_text="Token de recuperación de contraseña"
    )
    new_password = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'},
        help_text="Nueva contraseña"
    )
    
    def validate_token(self, value: str) -> str:
        """Validar token de recuperación.
        
        Args:
            value: Reset token
            
        Returns:
            Validated token
            
        Raises:
            ValidationError: Si el token es inválido o expirado
        """
        try:
            user = User.objects.get(
                token_recuperacion=value,
                fecha_expiracion_token__gt=timezone.now(),
                is_active=True
            )
            # Validar token usando el método del modelo
            if not user.validar_token_recuperacion(value):
                raise User.DoesNotExist
            
            self.context['reset_user'] = user
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'Token inválido o expirado.'
            )
        return value
    
    def validate_new_password(self, value: str) -> str:
        """Validar nueva contraseña.
        
        Args:
            value: New password
            
        Returns:
            Validated password
            
        Raises:
            ValidationError: Si la contraseña no cumple los requisitos
        """
        if len(value) < 8:
            raise serializers.ValidationError(
                'La contraseña debe tener al menos 8 caracteres.'
            )
        
        if value.isdigit():
            raise serializers.ValidationError(
                'La contraseña no puede ser completamente numérica.'
            )
        
        # Validar que contenga al menos una letra y un número
        if not any(c.isalpha() for c in value) or not any(c.isdigit() for c in value):
            raise serializers.ValidationError(
                'La contraseña debe contener al menos una letra y un número.'
            )
        
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validar datos del formulario.
        
        Args:
            attrs: Password data
            
        Returns:
            Validated data
        """
        return attrs
    
    def save(self) -> User:
        """Guardar nueva contraseña y limpiar token.
        
        Returns:
            User actualizado
        """
        user = self.context['reset_user']
        # Usar el método del modelo para cambiar contraseña
        user.cambiar_password(self.validated_data['new_password'])
        return user
    
class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = ['email', 'nombres_usuario', 'apellidos_usuario']

    def validate_email(self, value: str) -> str:
        """Validate email uniqueness."""
        user = self.instance
        if User.objects.exclude(pk=user.pk).filter(email=value).exists():
            raise serializers.ValidationError(
                'Este email ya está en uso por otro usuario.'
            )
        return value


class ActivateSerializer(serializers.Serializer):
    """Validates the activation request payload."""

    token = serializers.CharField(required=True)
    name = serializers.CharField(required=True, max_length=200)
    password = serializers.CharField(required=True, min_length=8, write_only=True)


class AuthExchangeSerializer(serializers.Serializer):
    """Validates the auth/exchange request payload."""

    exchange_token = serializers.CharField(required=True)