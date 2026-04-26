from django.db import models
from django.utils import timezone

# from ..managers import ModulosManager, RolPermisosManager, UsuarioRolesManager  # Comentado temporalmente para migraciones


class Modulos(models.Model):
    """Modelo para gestionar módulos del sistema."""

    ESTADO_MODULO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("mantenimiento", "Mantenimiento"),
    ]

    # Campos principales
    modulo_id = models.AutoField(primary_key=True)
    nombre_modulo = models.CharField(max_length=100)
    descripcion_modulo = models.TextField(null=True, blank=True)
    icono_modulo = models.CharField(max_length=100, null=True, blank=True)
    ruta_modulo = models.CharField(max_length=200, null=True, blank=True)
    orden_visualizacion = models.IntegerField(default=0)
    estado_modulo = models.CharField(
        max_length=15, choices=ESTADO_MODULO_CHOICES, default="activo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # Soporte para menú jerárquico
    modulo_padre = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="submodulos",
        db_column="modulo_padre_id",
        verbose_name="Módulo padre",
    )
    # Permisos necesarios para ver este módulo (separados por coma).
    # Vacío = visible para cualquier usuario autenticado.
    permisos_requeridos = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        verbose_name="Permisos requeridos",
        help_text="Nombres de permisos separados por coma. Vacío = visible para todos los autenticados.",
    )

    # objects = ModulosManager()  # Comentado temporalmente para migraciones

    class Meta:
        db_table = "modulos"
        indexes = [
            models.Index(fields=["nombre_modulo"]),
            models.Index(fields=["estado_modulo"]),
            models.Index(fields=["orden_visualizacion"]),
            models.Index(
                fields=["modulo_padre", "estado_modulo", "orden_visualizacion"],
                name="modulos_padre_estado_orden_idx",
            ),
        ]

    def __str__(self):
        return self.nombre_modulo

    @property
    def es_activo(self):
        """Verificar si el módulo está activo."""
        return self.estado_modulo == "activo"

    @property
    def permisos_count(self):
        """Contar permisos en este módulo."""
        return self.modulo_permisos.count()

    @property
    def ruta_completa(self):
        """Obtener ruta completa del módulo."""
        return (
            f"{self.ruta_modulo}"
            if self.ruta_modulo
            else f"/{self.nombre_modulo.lower()}"
        )

    def activar(self):
        """Activar el módulo."""
        self.estado_modulo = "activo"
        self.save(update_fields=["estado_modulo", "fecha_actualizacion"])

    def desactivar(self):
        """Desactivar el módulo."""
        self.estado_modulo = "inactivo"
        self.save(update_fields=["estado_modulo", "fecha_actualizacion"])

    def poner_en_mantenimiento(self):
        """Poner el módulo en mantenimiento."""
        self.estado_modulo = "mantenimiento"
        self.save(update_fields=["estado_modulo", "fecha_actualizacion"])

    def get_children(self):
        """Obtener submódulos directos activos, ordenados."""
        return self.submodulos.filter(estado_modulo="activo").order_by(
            "orden_visualizacion"
        )

    def tiene_acceso(self, usuario):
        """Verificar si un usuario tiene acceso a este módulo.

        Si ``permisos_requeridos`` está vacío, cualquier usuario autenticado
        puede ver el módulo. Si tiene valores, el usuario necesita al menos
        uno de esos permisos (o ser Super Administrador).
        """
        # Super Administrador siempre tiene acceso
        user_roles = {rol.nombre_rol for rol in usuario.roles_activos()}
        if "Super Administrador" in user_roles:
            return True

        # Nueva fuente oficial: tabla pivote modulo_permisos
        requeridos = {
            relacion.permiso.nombre_permiso
            for relacion in self.modulo_permisos.select_related("permiso").all()
        }

        # Fallback temporal para compatibilidad con datos legacy en CSV
        if not requeridos and self.permisos_requeridos:
            requeridos = {
                item.strip()
                for item in self.permisos_requeridos.split(",")
                if item.strip()
            }

        if not requeridos:
            return True

        user_permisos = usuario.permisos_activos()
        if user_permisos == "*":
            return True
        if hasattr(user_permisos, 'values_list'):
            user_permissions = set(user_permisos.values_list('nombre_permiso', flat=True))
        else:
            user_permissions = set()
        return bool(requeridos & user_permissions)

    @classmethod
    def modulos_activos(cls):
        """Obtener todos los módulos activos."""
        return cls.objects.filter(estado_modulo="activo").order_by(
            "orden_visualizacion"
        )

    @classmethod
    def modulos_raiz_activos(cls):
        """Obtener módulos raíz (sin padre) activos, ordenados."""
        return cls.objects.filter(
            estado_modulo="activo", modulo_padre__isnull=True
        ).order_by("orden_visualizacion")

    @classmethod
    def modulos_ordenados(cls):
        """Obtener todos los módulos ordenados por visualización."""
        return cls.objects.all().order_by("orden_visualizacion")


class RolPermisos(models.Model):
    """Modelo para gestionar la relación entre roles y permisos."""

    # Campos principales
    rol_permiso_id = models.AutoField(primary_key=True)
    rol = models.ForeignKey(
        "Rol", on_delete=models.CASCADE, related_name="permisos_asignados"
    )
    permiso = models.ForeignKey(
        "Permiso", on_delete=models.CASCADE, related_name="roles_asignados"
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    asignado_por_usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_column="asignado_por_usuario_id",
    )

    # objects = RolPermisosManager()  # Comentado temporalmente para migraciones

    class Meta:
        db_table = "rol_permisos"
        unique_together = ["rol", "permiso"]
        indexes = [
            models.Index(fields=["rol"]),
            models.Index(fields=["permiso"]),
            models.Index(fields=["fecha_asignacion"]),
            models.Index(
                fields=["rol", "permiso", "fecha_asignacion"],
                name="rol_permisos_rol_perm_fec_idx",
            ),
        ]

    def __str__(self):
        return f"{self.rol.nombre_rol} - {self.permiso.nombre_permiso}"

    @property
    def asignacion_reciente(self):
        """Verificar si la asignación es reciente (dentro de 30 días)."""
        return (timezone.now() - self.fecha_asignacion).days <= 30

    @property
    def dias_desde_asignacion(self):
        """Obtener días desde la asignación."""
        return (timezone.now() - self.fecha_asignacion).days

    @classmethod
    def permisos_por_rol(cls, rol_id):
        """Obtener todos los permisos de un rol específico."""
        return cls.objects.filter(rol_id=rol_id).select_related("permiso")

    @classmethod
    def roles_con_permiso(cls, permiso_id):
        """Obtener todos los roles que tienen un permiso específico."""
        return cls.objects.filter(permiso_id=permiso_id).select_related("rol")

    @classmethod
    def asignar_permiso_a_rol(cls, rol_id, permiso_id, usuario_id=None):
        """Asignar un permiso a un rol."""
        try:
            return cls.objects.create(
                rol_id=rol_id, permiso_id=permiso_id, asignado_por_usuario_id=usuario_id
            )
        except Exception:
            return None

    @classmethod
    def remover_permiso_de_rol(cls, rol_id, permiso_id):
        """Remover un permiso de un rol."""
        return cls.objects.filter(rol_id=rol_id, permiso_id=permiso_id).delete()


class ModuloPermiso(models.Model):
    """Relación explícita entre módulos y permisos requeridos para visibilidad."""

    modulo_permiso_id = models.AutoField(primary_key=True)
    modulo = models.ForeignKey(
        "Modulos",
        on_delete=models.CASCADE,
        related_name="modulo_permisos",
        db_column="modulo_id",
    )
    permiso = models.ForeignKey(
        "Permiso",
        on_delete=models.CASCADE,
        related_name="modulos_relacionados",
        db_column="permiso_id",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "modulo_permisos"
        unique_together = ["modulo", "permiso"]
        indexes = [
            models.Index(fields=["modulo"]),
            models.Index(fields=["permiso"]),
        ]

    def __str__(self):
        return f"{self.modulo.nombre_modulo} - {self.permiso.nombre_permiso}"


class UsuarioRoles(models.Model):
    """Modelo para gestionar la relación entre usuarios y roles."""

    ESTADO_ASIGNACION_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
        ("suspendido", "Suspendido"),
        ("expirado", "Expirado"),
    ]

    # Campos principales
    usuario_rol_id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(
        "Usuario", on_delete=models.CASCADE, related_name="roles_asignados"
    )
    rol = models.ForeignKey(
        "Rol", on_delete=models.CASCADE, related_name="usuarios_asignados"
    )
    fecha_asignacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(null=True, blank=True)
    asignado_por_usuario = models.ForeignKey(
        "Usuario",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="asignaciones_realizadas",
    )
    estado_asignacion = models.CharField(
        max_length=15, choices=ESTADO_ASIGNACION_CHOICES, default="activo"
    )

    # objects = UsuarioRolesManager()  # Comentado temporalmente para migraciones

    class Meta:
        db_table = "usuario_roles"  # Nombre real de la tabla en MySQL
        unique_together = ["usuario", "rol"]
        indexes = [
            models.Index(fields=["usuario"]),
            models.Index(fields=["rol"]),
            models.Index(fields=["estado_asignacion"]),
            models.Index(fields=["fecha_expiracion"]),
            models.Index(
                fields=["usuario", "estado_asignacion"],
                name="usuario_roles_usr_estado_idx",
            ),
        ]

    def __str__(self):
        return f"{self.usuario.nombres_usuario} - {self.rol.nombre_rol}"

    @property
    def es_activo(self):
        """Verificar si la asignación de rol está activa."""
        return self.estado_asignacion == "activo"

    @property
    def esta_vigente(self):
        """Verificar si la asignación de rol está vigente y no ha expirado."""
        if not self.es_activo:
            return False
        if self.fecha_expiracion:
            return timezone.now() <= self.fecha_expiracion
        return True

    @property
    def dias_para_expirar(self):
        """Calcular días hasta la expiración."""
        if self.fecha_expiracion:
            delta = self.fecha_expiracion - timezone.now()
            return delta.days if delta.days > 0 else 0
        return None

    @property
    def necesita_renovacion(self):
        """Verificar si la asignación de rol necesita renovación (30 días antes de expirar)."""
        dias = self.dias_para_expirar
        return dias is not None and dias <= 30

    @property
    def esta_expirado(self):
        """Verificar si la asignación ha expirado."""
        if self.fecha_expiracion:
            return timezone.now() > self.fecha_expiracion
        return False

    def activar(self):
        """Activar la asignación de rol."""
        self.estado_asignacion = "activo"
        self.save(update_fields=["estado_asignacion"])

    def desactivar(self):
        """Desactivar la asignación de rol."""
        self.estado_asignacion = "inactivo"
        self.save(update_fields=["estado_asignacion"])

    def suspender(self):
        """Suspender la asignación de rol."""
        self.estado_asignacion = "suspendido"
        self.save(update_fields=["estado_asignacion"])

    def marcar_como_expirado(self):
        """Marcar la asignación como expirada."""
        self.estado_asignacion = "expirado"
        self.save(update_fields=["estado_asignacion"])

    def extender_expiracion(self, nueva_fecha):
        """Extender la fecha de expiración."""
        self.fecha_expiracion = nueva_fecha
        if self.estado_asignacion == "expirado":
            self.estado_asignacion = "activo"
        self.save(update_fields=["fecha_expiracion", "estado_asignacion"])

    @classmethod
    def roles_por_usuario(cls, usuario_id):
        """Obtener todos los roles de un usuario específico."""
        return cls.objects.filter(
            usuario_id=usuario_id, estado_asignacion="activo"
        ).select_related("rol")

    @classmethod
    def usuarios_con_rol(cls, rol_id):
        """Obtener todos los usuarios que tienen un rol específico."""
        return cls.objects.filter(
            rol_id=rol_id, estado_asignacion="activo"
        ).select_related("usuario")

    @classmethod
    def asignar_rol_a_usuario(
        cls, usuario_id, rol_id, fecha_expiracion=None, asignado_por=None
    ):
        """Asignar un rol a un usuario."""
        try:
            return cls.objects.create(
                usuario_id=usuario_id,
                rol_id=rol_id,
                fecha_expiracion=fecha_expiracion,
                asignado_por_usuario_id=asignado_por,
            )
        except Exception:
            return None

    @classmethod
    def remover_rol_de_usuario(cls, usuario_id, rol_id):
        """Remover un rol de un usuario."""
        return cls.objects.filter(usuario_id=usuario_id, rol_id=rol_id).delete()

    @classmethod
    def asignaciones_por_expirar(cls, dias=30):
        """Obtener asignaciones que expiran en los próximos días especificados."""
        fecha_limite = timezone.now() + timezone.timedelta(days=dias)
        return cls.objects.filter(
            fecha_expiracion__lte=fecha_limite,
            fecha_expiracion__gt=timezone.now(),
            estado_asignacion="activo",
        )

    @classmethod
    def asignaciones_expiradas(cls):
        """Obtener todas las asignaciones expiradas."""
        return cls.objects.filter(
            fecha_expiracion__lt=timezone.now(),
            estado_asignacion__in=["activo", "suspendido"],
        )
