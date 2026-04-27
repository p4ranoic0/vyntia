from django.db import models


class Role(models.Model):
    """Modelo para gestionar roles del sistema."""

    ESTADO_ROL_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    # Campos principales de la tabla roles
    rol_id = models.AutoField(primary_key=True)
    nombre_rol = models.CharField(max_length=100, unique=True)
    descripcion_rol = models.TextField(null=True, blank=True)
    nivel_jerarquico = models.IntegerField(default=1)
    es_rol_sistema = models.BooleanField(default=False)
    estado_rol = models.CharField(
        max_length=10, choices=ESTADO_ROL_CHOICES, default="activo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    # objects = RolManager()  # Comentado temporalmente para migraciones

    class Meta:
        db_table = "rol"  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=["nombre_rol"]),
            models.Index(fields=["estado_rol"]),
            models.Index(fields=["nivel_jerarquico"]),
            models.Index(fields=["es_rol_sistema"]),
        ]

    def __str__(self):
        return self.nombre_rol

    @property
    def es_activo(self):
        """Verificar si el rol está activo."""
        return self.estado_rol == "activo"

    @property
    def es_sistema(self):
        """Verificar si es un rol del sistema."""
        return self.es_rol_sistema

    @property
    def usuarios_count(self):
        """Obtener cantidad de usuarios con este rol."""
        # Esta relación se definirá cuando creemos la tabla intermedia usuario_roles
        return 0  # Placeholder

    @property
    def permisos_count(self):
        """Obtener cantidad de permisos para este rol."""
        # Esta relación se definirá cuando creemos la tabla intermedia rol_permisos
        return 0  # Placeholder

    def activar(self):
        """Activar el rol."""
        self.estado_rol = "activo"
        self.save(update_fields=["estado_rol", "fecha_actualizacion"])

    def desactivar(self):
        """Desactivar el rol."""
        self.estado_rol = "inactivo"
        self.save(update_fields=["estado_rol", "fecha_actualizacion"])

    def asignar_permisos(self, permisos_ids):
        """Asignar permisos al rol."""
        # Implementar cuando se cree la tabla intermedia rol_permisos
        pass

    def remover_permisos(self, permisos_ids):
        """Remover permisos del rol."""
        # Implementar cuando se cree la tabla intermedia rol_permisos
        pass

    @classmethod
    def roles_activos(cls):
        """Obtener todos los roles activos."""
        return cls.objects.filter(estado_rol="activo")

    @classmethod
    def roles_sistema(cls):
        """Obtener todos los roles del sistema."""
        return cls.objects.filter(es_rol_sistema=True)


class Permission(models.Model):
    """Modelo para gestionar permisos del sistema."""

    TIPO_PERMISO_CHOICES = [
        ("crear", "Crear"),
        ("leer", "Leer"),
        ("actualizar", "Actualizar"),
        ("eliminar", "Eliminar"),
        ("ejecutar", "Ejecutar"),
        ("aprobar", "Aprobar"),
    ]

    ESTADO_PERMISO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    # Campos principales de la tabla permiso
    permiso_id = models.AutoField(primary_key=True)
    nombre_permiso = models.CharField(max_length=100)
    descripcion_permiso = models.TextField(null=True, blank=True)
    # Módulo como string (referencia al ID en config/modules_config.py)
    modulo = models.CharField(
        max_length=50,
        db_column="modulo",
        help_text="ID del módulo según MODULES_CONFIG (ej: empleados, vacaciones, etc)",
    )
    tipo_permiso = models.CharField(max_length=15, choices=TIPO_PERMISO_CHOICES)
    estado_permiso = models.CharField(
        max_length=10, choices=ESTADO_PERMISO_CHOICES, default="activo"
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "permiso"  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=["nombre_permiso"]),
            models.Index(fields=["tipo_permiso"]),
            models.Index(fields=["estado_permiso"]),
            models.Index(fields=["modulo"]),
        ]

    def __str__(self):
        return self.nombre_permiso

    @property
    def es_activo(self):
        """Verificar si el permiso está activo."""
        return self.estado_permiso == "activo"

    @property
    def es_lectura(self):
        """Verificar si es un permiso de lectura."""
        return self.tipo_permiso == "leer"

    @property
    def es_escritura(self):
        """Verificar si es un permiso de escritura (crear/actualizar)."""
        return self.tipo_permiso in ["crear", "actualizar"]

    @property
    def es_eliminacion(self):
        """Verificar si es un permiso de eliminación."""
        return self.tipo_permiso == "eliminar"

    @property
    def es_aprobacion(self):
        """Verificar si es un permiso de aprobación."""
        return self.tipo_permiso == "aprobar"

    def activar(self):
        """Activar el permiso."""
        self.estado_permiso = "activo"
        self.save(update_fields=["estado_permiso"])

    def desactivar(self):
        """Desactivar el permiso."""
        self.estado_permiso = "inactivo"
        self.save(update_fields=["estado_permiso"])

    @classmethod
    def permisos_activos(cls):
        """Obtener todos los permisos activos."""
        return cls.objects.filter(estado_permiso="activo")

    @classmethod
    def permisos_por_tipo(cls, tipo):
        """Obtener permisos por tipo específico."""
        return cls.objects.filter(tipo_permiso=tipo, estado_permiso="activo")

    @classmethod
    def permisos_por_modulo(cls, modulo_str):
        """Obtener permisos por módulo (string ID)."""
        return cls.permisos_activos().filter(modulo=modulo_str)

    @classmethod
    def permisos_lectura(cls):
        """Obtener todos los permisos de lectura."""
        return cls.permisos_por_tipo("leer")

    @classmethod
    def permisos_escritura(cls):
        """Obtener todos los permisos de escritura."""
        return cls.objects.filter(
            tipo_permiso__in=["crear", "actualizar"], estado_permiso="activo"
        )

    @classmethod
    def permisos_eliminacion(cls):
        """Obtener todos los permisos de eliminación."""
        return cls.permisos_por_tipo("eliminar")

    @classmethod
    def permisos_aprobacion(cls):
        """Obtener todos los permisos de aprobación."""
        return cls.permisos_por_tipo("aprobar")
