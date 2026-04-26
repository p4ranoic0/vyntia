# -*- coding: utf-8 -*-
"""
Modelo Usuario - Gestión de usuarios del sistema

Contiene la definición del modelo Usuario que gestiona los usuarios
del sistema de intranet y sus permisos de acceso.
"""

from datetime import date, timedelta

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models import Q
from django.utils import timezone

from ..managers import UsuarioManager


class Usuario(AbstractBaseUser, PermissionsMixin):
    """Modelo personalizado de usuario para el sistema."""

    TIPO_USUARIO_CHOICES = [
        ("administrador", "Administrador"),
        ("rrhh", "Recursos Humanos"),
        ("jefe", "Jefe de Área"),
        ("empleado", "Empleado"),
        ("consulta", "Solo Consulta"),
        ("invitado", "Invitado"),
    ]

    ESTADO_USUARIO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("suspendido", "Suspendido"),
        ("bloqueado", "Bloqueado"),
        ("pendiente", "Pendiente de Activación"),
    ]

    NIVEL_ACCESO_CHOICES = [
        ("total", "Acceso Total"),
        ("departamental", "Acceso Departamental"),
        ("personal", "Acceso Personal"),
        ("limitado", "Acceso Limitado"),
        ("lectura", "Solo Lectura"),
    ]

    # Campos principales
    usuario_id = models.AutoField(primary_key=True)
    empleado = models.OneToOneField(
        "employees.Empleado",
        on_delete=models.CASCADE,
        related_name="usuario",
        null=True,
        blank=True,
    )

    # Campos de autenticación
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=254, unique=True)
    password = models.CharField(max_length=128)

    # Información del usuario
    nombres_usuario = models.CharField(max_length=100)
    apellidos_usuario = models.CharField(max_length=100)
    tipo_usuario = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)
    nivel_acceso = models.CharField(
        max_length=20, choices=NIVEL_ACCESO_CHOICES, default="personal"
    )

    # Configuración de cuenta
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    estado_usuario = models.CharField(
        max_length=15, choices=ESTADO_USUARIO_CHOICES, default="activo"
    )

    # Fechas importantes
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    fecha_ultimo_cambio_password = models.DateTimeField(null=True, blank=True)
    fecha_expiracion_password = models.DateTimeField(null=True, blank=True)

    # Configuración de seguridad
    requiere_cambio_password = models.BooleanField(default=False)
    intentos_fallidos = models.IntegerField(default=0)
    fecha_ultimo_intento_fallido = models.DateTimeField(null=True, blank=True)
    fecha_bloqueo = models.DateTimeField(null=True, blank=True)
    token_recuperacion = models.CharField(max_length=100, null=True, blank=True)
    fecha_expiracion_token = models.DateTimeField(null=True, blank=True)

    # Configuración de sesión
    sesiones_simultaneas_permitidas = models.IntegerField(default=1)
    ip_ultimo_acceso = models.GenericIPAddressField(null=True, blank=True)
    user_agent_ultimo_acceso = models.TextField(null=True, blank=True)

    # Configuración de notificaciones
    recibir_notificaciones_email = models.BooleanField(default=True)
    recibir_notificaciones_sistema = models.BooleanField(default=True)

    # Campos de auditoría
    creado_por = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="usuarios_creados",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Manager personalizado
    objects = UsuarioManager()

    USERNAME_FIELD = "username"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = ["email", "nombres_usuario", "apellidos_usuario"]

    class Meta:
        db_table = "usuarios"  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=["username"]),
            models.Index(fields=["email"]),
            models.Index(fields=["empleado"]),
            models.Index(fields=["tipo_usuario"]),
            models.Index(fields=["estado_usuario"]),
            models.Index(fields=["nivel_acceso"]),
            models.Index(fields=["is_active"]),
            models.Index(fields=["last_login"]),
            models.Index(fields=["date_joined"]),
            models.Index(fields=["intentos_fallidos"]),
            models.Index(fields=["fecha_bloqueo"]),
        ]

    def __str__(self):
        return f"{self.username} - {self.nombre_completo}"

    @property
    def nombre_completo(self):
        """Retorna el nombre completo del usuario."""
        return f"{self.nombres_usuario} {self.apellidos_usuario}"

    @property
    def es_activo(self):
        """Verifica si el usuario está activo."""
        return self.is_active and self.estado_usuario == "activo"

    @property
    def es_administrador(self):
        """Verifica si el usuario es administrador."""
        return self.tipo_usuario == "administrador" or self.is_superuser

    @property
    def es_rrhh(self):
        """Verifica si el usuario es de recursos humanos."""
        return self.tipo_usuario == "rrhh"

    @property
    def es_jefe(self):
        """Verifica si el usuario es jefe de área."""
        return self.tipo_usuario == "jefe"

    @property
    def es_admin_rrhh(self):
        """Verifica si el usuario puede gestionar el módulo de RRHH (administrador o rrhh)."""
        return self.tipo_usuario in ("administrador", "rrhh") or self.is_superuser

    @property
    def password_expirado(self):
        """Verifica si la contraseña ha expirado."""
        if self.fecha_expiracion_password:
            return timezone.now() > self.fecha_expiracion_password
        return False

    @property
    def dias_para_expiracion_password(self):
        """Calcula los días restantes para la expiración de la contraseña."""
        if self.fecha_expiracion_password:
            delta = self.fecha_expiracion_password - timezone.now()
            return delta.days if delta.days >= 0 else 0
        return None

    @property
    def password_por_expirar(self):
        """Verifica si la contraseña está por expirar (7 días)."""
        dias = self.dias_para_expiracion_password
        return dias is not None and 0 <= dias <= 7

    @property
    def esta_bloqueado(self):
        """Verifica si el usuario está bloqueado."""
        if self.estado_usuario == "bloqueado":
            return True

        # Verificar bloqueo por intentos fallidos
        if self.intentos_fallidos >= 5:  # Máximo 5 intentos
            return True

        # Verificar bloqueo temporal
        if self.fecha_bloqueo:
            tiempo_bloqueo = timedelta(minutes=30)  # Bloqueo por 30 minutos
            return timezone.now() < (self.fecha_bloqueo + tiempo_bloqueo)

        return False

    @property
    def tipo_usuario_texto(self):
        """Retorna el tipo de usuario en formato texto."""
        return dict(self.TIPO_USUARIO_CHOICES).get(self.tipo_usuario, self.tipo_usuario)

    @property
    def nivel_acceso_texto(self):
        """Retorna el nivel de acceso en formato texto."""
        return dict(self.NIVEL_ACCESO_CHOICES).get(self.nivel_acceso, self.nivel_acceso)

    @property
    def estado_usuario_texto(self):
        """Retorna el estado del usuario en formato texto."""
        return dict(self.ESTADO_USUARIO_CHOICES).get(
            self.estado_usuario, self.estado_usuario
        )

    @property
    def tiempo_desde_ultimo_login(self):
        """Calcula el tiempo transcurrido desde el último login."""
        if self.last_login:
            delta = timezone.now() - self.last_login
            if delta.days > 0:
                return f"{delta.days} día{'s' if delta.days != 1 else ''}"
            elif delta.seconds > 3600:
                horas = delta.seconds // 3600
                return f"{horas} hora{'s' if horas != 1 else ''}"
            elif delta.seconds > 60:
                minutos = delta.seconds // 60

    @property
    def ultimo_login_texto(self):
        """Retorna el último login en formato texto legible."""
        if self.last_login:
            return self.tiempo_desde_ultimo_login
        return "Nunca"

    @property
    def dias_sin_login(self):
        """Calcula los días sin login."""
        if self.last_login:
            delta = timezone.now() - self.last_login
            return delta.days
        return None

    def puede_acceder_a_area(self, area):
        """Verifica si el usuario puede acceder a un área específica."""
        if self.es_administrador:
            return True

        if self.nivel_acceso == "total":
            return True

        if self.nivel_acceso == "departamental" and self.empleado:
            datos_laborales = self.empleado.datos_laborales_actuales()
            return datos_laborales and datos_laborales.area == area

        return False

    def puede_ver_empleado(self, empleado):
        """Verifica si el usuario puede ver información de un empleado."""
        if self.es_administrador or self.es_rrhh:
            return True

        if self.nivel_acceso == "personal":
            return self.empleado == empleado

        if self.es_jefe and self.empleado:
            # Verificar si es jefe del empleado
            datos_laborales = empleado.datos_laborales_actuales()
            return datos_laborales and datos_laborales.jefe_directo == self.empleado

        return False

    def registrar_intento_fallido(self):
        """Registra un intento de login fallido."""
        self.intentos_fallidos += 1
        self.fecha_ultimo_intento_fallido = timezone.now()

        if self.intentos_fallidos >= 5:
            self.fecha_bloqueo = timezone.now()
            self.estado_usuario = "bloqueado"

        self.save()

    def resetear_intentos_fallidos(self):
        """Resetea los intentos fallidos después de un login exitoso."""
        self.intentos_fallidos = 0
        self.fecha_ultimo_intento_fallido = None
        self.fecha_bloqueo = None
        if self.estado_usuario == "bloqueado":
            self.estado_usuario = "activo"
        self.save()

    def generar_token_recuperacion(self):
        """Genera un token para recuperación de contraseña."""
        import secrets

        self.token_recuperacion = secrets.token_urlsafe(32)
        self.fecha_expiracion_token = timezone.now() + timedelta(hours=24)
        self.save()
        return self.token_recuperacion

    def validar_token_recuperacion(self, token):
        """Valida el token de recuperación de contraseña."""
        if not self.token_recuperacion or not self.fecha_expiracion_token:
            return False

        if timezone.now() > self.fecha_expiracion_token:
            return False

        return self.token_recuperacion == token

    def cambiar_password(self, nueva_password):
        """Cambia la contraseña del usuario."""
        self.set_password(nueva_password)
        self.fecha_ultimo_cambio_password = timezone.now()
        self.fecha_expiracion_password = timezone.now() + timedelta(
            days=90
        )  # Expira en 90 días
        self.requiere_cambio_password = False
        self.token_recuperacion = None
        self.fecha_expiracion_token = None
        self.save()

    def activar_usuario(self):
        """Activa el usuario."""
        self.is_active = True
        self.estado_usuario = "activo"
        self.save()

    def desactivar_usuario(self, motivo=None):
        """Desactiva el usuario."""
        self.is_active = False
        self.estado_usuario = "inactivo"
        self.save()

    def suspender_usuario(self, motivo=None):
        """Suspende temporalmente el usuario."""
        self.estado_usuario = "suspendido"
        self.save()

    def bloquear_usuario(self, motivo=None):
        """Bloquea permanentemente el usuario."""
        self.estado_usuario = "bloqueado"
        self.fecha_bloqueo = timezone.now()
        self.save()

    def registrar_acceso(self, ip_address=None, user_agent=None):
        """Registra información del último acceso."""
        self.last_login = timezone.now()
        if ip_address:
            self.ip_ultimo_acceso = ip_address
        if user_agent:
            self.user_agent_ultimo_acceso = user_agent
        self.save()

    def permisos_especiales(self):
        """Obtiene los permisos especiales del usuario."""
        # Implementar lógica de permisos especiales
        # return PermisoEspecial.objects.filter(usuario=self, activo=True)
        return []

    def areas_accesibles(self):
        """Obtiene las áreas a las que el usuario tiene acceso."""
        from apps.organization.models import Area

        if self.es_administrador or self.nivel_acceso == "total":
            return Area.objects.filter(estado_area="activo")

        if self.nivel_acceso == "departamental" and self.empleado:
            datos_laborales = self.empleado.datos_laborales_actuales()
            if datos_laborales:
                return Area.objects.filter(area_id=datos_laborales.area.area_id)

        return Area.objects.none()

    @classmethod
    def usuarios_activos(cls):
        """Obtiene todos los usuarios activos."""
        return cls.objects.filter(is_active=True, estado_usuario="activo")

    @classmethod
    def usuarios_por_tipo(cls, tipo_usuario):
        """Obtiene usuarios por tipo."""
        return cls.objects.filter(tipo_usuario=tipo_usuario, is_active=True)

    @classmethod
    def usuarios_con_password_por_expirar(cls, dias=7):
        """Obtiene usuarios con contraseña por expirar."""
        fecha_limite = timezone.now() + timedelta(days=dias)
        return cls.objects.filter(
            fecha_expiracion_password__lte=fecha_limite, is_active=True
        )

    def roles_activos(self):
        """Obtiene los roles activos del usuario."""
        from .roles import Rol
        from .sistema import UsuarioRoles

        # Obtener IDs de roles válidos (activos y no expirados)
        roles_usuario = UsuarioRoles.objects.filter(
            usuario=self, estado_asignacion="activo"
        ).select_related("rol")

        roles_ids = []
        for usuario_rol in roles_usuario:
            # Verificar que la asignación no haya expirado y que el rol esté activo
            if (
                usuario_rol.fecha_expiracion is None
                or usuario_rol.fecha_expiracion > timezone.now()
            ) and usuario_rol.rol.estado_rol == "activo":
                roles_ids.append(usuario_rol.rol.rol_id)

        # Devolver QuerySet de roles activos
        return Rol.objects.filter(rol_id__in=roles_ids, estado_rol="activo")

    def permisos_activos(self):
        """Obtiene los permisos activos del usuario a traves de sus roles."""
        from .roles import Permiso
        from .sistema import RolPermisos

        try:
            roles = self.roles_activos()
            if not roles.exists():
                return Permiso.objects.none()

            # Super Admin tiene acceso total
            if roles.filter(nombre_rol="Super Administrador").exists():
                return "*"

            permiso_ids = RolPermisos.objects.filter(
                rol__in=roles
            ).values_list('permiso_id', flat=True).distinct()

            return Permiso.objects.filter(
                permiso_id__in=permiso_ids,
                estado_permiso='activo'
            )
        except Exception:
            return Permiso.objects.none()
