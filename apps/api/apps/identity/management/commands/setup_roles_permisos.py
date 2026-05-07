"""Management command para crear roles, permisos y asignaciones iniciales."""

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.identity.models import Permission, Role, RolePermission, User, UserRole


ROLES_DATA = [
    {
        "nombre_rol": "Super Administrador",
        "descripcion_rol": "Acceso total al sistema",
        "nivel_jerarquico": 1,
        "es_rol_sistema": True,
    },
    {
        "nombre_rol": "Administrador RRHH",
        "descripcion_rol": "Administrador del modulo de Recursos Humanos",
        "nivel_jerarquico": 2,
        "es_rol_sistema": True,
    },
    {
        "nombre_rol": "Jefe de Department",
        "descripcion_rol": "Jefe o supervisor de area",
        "nivel_jerarquico": 3,
        "es_rol_sistema": False,
    },
    {
        "nombre_rol": "Analista RRHH",
        "descripcion_rol": "Analista del area de Recursos Humanos",
        "nivel_jerarquico": 4,
        "es_rol_sistema": False,
    },
    {
        "nombre_rol": "Employee",
        "descripcion_rol": "Employee con acceso basico al sistema",
        "nivel_jerarquico": 5,
        "es_rol_sistema": False,
    },
]

PERMISOS_DATA = [
    # Dashboard
    {"nombre_permiso": "ver_dashboard", "descripcion_permiso": "Ver el dashboard principal", "modulo": "dashboard", "tipo_permiso": "leer"},
    {"nombre_permiso": "ver_estadisticas_dashboard", "descripcion_permiso": "Ver estadisticas del dashboard", "modulo": "dashboard", "tipo_permiso": "leer"},
    # Empleados
    {"nombre_permiso": "ver_empleados", "descripcion_permiso": "Ver lista de empleados", "modulo": "empleados", "tipo_permiso": "leer"},
    {"nombre_permiso": "crear_empleado", "descripcion_permiso": "Crear nuevo empleado", "modulo": "empleados", "tipo_permiso": "crear"},
    {"nombre_permiso": "editar_empleado", "descripcion_permiso": "Editar datos de empleado", "modulo": "empleados", "tipo_permiso": "actualizar"},
    {"nombre_permiso": "eliminar_empleado", "descripcion_permiso": "Eliminar empleado", "modulo": "empleados", "tipo_permiso": "eliminar"},
    {"nombre_permiso": "exportar_empleados", "descripcion_permiso": "Exportar datos de empleados", "modulo": "empleados", "tipo_permiso": "ejecutar"},
    {"nombre_permiso": "ver_datos_propios", "descripcion_permiso": "Ver datos propios del empleado", "modulo": "empleados", "tipo_permiso": "leer"},
    {"nombre_permiso": "editar_datos_propios", "descripcion_permiso": "Editar datos propios del empleado", "modulo": "empleados", "tipo_permiso": "actualizar"},
    # Vacaciones
    {"nombre_permiso": "ver_solicitudes_vacaciones", "descripcion_permiso": "Ver solicitudes de vacaciones", "modulo": "vacaciones", "tipo_permiso": "leer"},
    {"nombre_permiso": "crear_solicitud_vacaciones", "descripcion_permiso": "Crear solicitud de vacaciones", "modulo": "vacaciones", "tipo_permiso": "crear"},
    {"nombre_permiso": "aprobar_solicitud_vacaciones", "descripcion_permiso": "Aprobar o rechazar solicitudes de vacaciones", "modulo": "vacaciones", "tipo_permiso": "aprobar"},
    {"nombre_permiso": "administrar_periodos_vacaciones", "descripcion_permiso": "Administrar periodos vacacionales", "modulo": "vacaciones", "tipo_permiso": "ejecutar"},
    {"nombre_permiso": "configurar_modulo_vacaciones", "descripcion_permiso": "Configurar parametros del modulo de vacaciones", "modulo": "vacaciones", "tipo_permiso": "ejecutar"},
    # Administracion
    {"nombre_permiso": "gestionar_usuarios", "descripcion_permiso": "Gestionar usuarios del sistema", "modulo": "administracion", "tipo_permiso": "ejecutar"},
    {"nombre_permiso": "gestionar_roles", "descripcion_permiso": "Gestionar roles del sistema", "modulo": "administracion", "tipo_permiso": "ejecutar"},
    {"nombre_permiso": "gestionar_permisos", "descripcion_permiso": "Gestionar permisos del sistema", "modulo": "administracion", "tipo_permiso": "ejecutar"},
    {"nombre_permiso": "gestionar_modulos", "descripcion_permiso": "Gestionar modulos del sistema", "modulo": "administracion", "tipo_permiso": "ejecutar"},
    # Reportes
    {"nombre_permiso": "ver_reportes", "descripcion_permiso": "Ver reportes del sistema", "modulo": "reportes", "tipo_permiso": "leer"},
    {"nombre_permiso": "exportar_reportes", "descripcion_permiso": "Exportar reportes del sistema", "modulo": "reportes", "tipo_permiso": "ejecutar"},
]

# Matriz de permisos por rol (nombre_rol -> lista de nombre_permiso)
ROL_PERMISOS_MAP = {
    "Super Administrador": [p["nombre_permiso"] for p in PERMISOS_DATA],  # Todos
    "Administrador RRHH": [
        "ver_dashboard", "ver_estadisticas_dashboard",
        "ver_empleados", "crear_empleado", "editar_empleado", "eliminar_empleado", "exportar_empleados",
        "ver_datos_propios", "editar_datos_propios",
        "ver_solicitudes_vacaciones", "crear_solicitud_vacaciones", "aprobar_solicitud_vacaciones",
        "administrar_periodos_vacaciones", "configurar_modulo_vacaciones",
        "gestionar_usuarios",
        "ver_reportes", "exportar_reportes",
    ],
    "Jefe de Department": [
        "ver_dashboard", "ver_estadisticas_dashboard",
        "ver_empleados", "ver_datos_propios", "editar_datos_propios",
        "ver_solicitudes_vacaciones", "crear_solicitud_vacaciones", "aprobar_solicitud_vacaciones",
        "administrar_periodos_vacaciones",
        "ver_reportes", "exportar_reportes",
    ],
    "Analista RRHH": [
        "ver_dashboard", "ver_estadisticas_dashboard",
        "ver_empleados", "crear_empleado", "editar_empleado", "exportar_empleados",
        "ver_datos_propios", "editar_datos_propios",
        "ver_solicitudes_vacaciones", "crear_solicitud_vacaciones",
        "administrar_periodos_vacaciones",
        "ver_reportes",
    ],
    "Employee": [
        "ver_dashboard",
        "ver_datos_propios", "editar_datos_propios",
        "ver_solicitudes_vacaciones", "crear_solicitud_vacaciones",
    ],
}


class Command(BaseCommand):
    help = "Crea roles, permisos y asignaciones iniciales del sistema RBAC"

    def add_arguments(self, parser):
        parser.add_argument(
            "--force",
            action="store_true",
            help="Recrear asignaciones rol-permiso incluso si ya existen",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        force = options.get("force", False)

        # 1. Crear roles
        self.stdout.write(self.style.MIGRATE_HEADING("Creando roles..."))
        roles_created = 0
        for data in ROLES_DATA:
            rol, created = Role.objects.get_or_create(
                nombre_rol=data["nombre_rol"],
                defaults=data,
            )
            if created:
                roles_created += 1
                self.stdout.write(f"  + Role: {rol.nombre_rol}")
            else:
                self.stdout.write(f"  = Role ya existe: {rol.nombre_rol}")
        self.stdout.write(self.style.SUCCESS(f"  Roles: {roles_created} creados"))

        # 2. Crear permisos
        self.stdout.write(self.style.MIGRATE_HEADING("Creando permisos..."))
        permisos_created = 0
        for data in PERMISOS_DATA:
            permiso, created = Permission.objects.get_or_create(
                nombre_permiso=data["nombre_permiso"],
                defaults=data,
            )
            if created:
                permisos_created += 1
                self.stdout.write(f"  + Permission: {permiso.nombre_permiso}")
            else:
                self.stdout.write(f"  = Permission ya existe: {permiso.nombre_permiso}")
        self.stdout.write(self.style.SUCCESS(f"  Permisos: {permisos_created} creados"))

        # 3. Asignar permisos a roles
        self.stdout.write(self.style.MIGRATE_HEADING("Asignando permisos a roles..."))
        asignaciones_created = 0
        for nombre_rol, permisos_nombres in ROL_PERMISOS_MAP.items():
            try:
                rol = Role.objects.get(nombre_rol=nombre_rol)
            except Role.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"  ! Role no encontrado: {nombre_rol}"))
                continue

            if force:
                deleted, _ = RolePermission.objects.filter(rol=rol).delete()
                if deleted:
                    self.stdout.write(f"  - Eliminadas {deleted} asignaciones de {nombre_rol}")

            for nombre_permiso in permisos_nombres:
                try:
                    permiso = Permission.objects.get(nombre_permiso=nombre_permiso)
                except Permission.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"  ! Permission no encontrado: {nombre_permiso}"))
                    continue

                _, created = RolePermission.objects.get_or_create(
                    rol=rol, permiso=permiso
                )
                if created:
                    asignaciones_created += 1

            count = RolePermission.objects.filter(rol=rol).count()
            self.stdout.write(f"  {nombre_rol}: {count} permisos")

        self.stdout.write(self.style.SUCCESS(f"  Asignaciones: {asignaciones_created} creadas"))

        # 4. Crear usuario admin si no existe
        self.stdout.write(self.style.MIGRATE_HEADING("Verificando usuario admin..."))
        admin_user, created = User.objects.get_or_create(
            username="admin",
            defaults={
                "email": "admin@vyntia.local",
                "tipo_usuario": "administrador",
                "nivel_acceso": "total",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        if created:
            admin_user.set_password("Admin123!")
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("  + User admin creado (password: Admin123!)"))
        else:
            self.stdout.write("  = User admin ya existe")

        # Asignar rol Super Administrador al admin
        try:
            rol_admin = Role.objects.get(nombre_rol="Super Administrador")
            _, created = UserRole.objects.get_or_create(
                usuario=admin_user,
                rol=rol_admin,
                defaults={"estado_asignacion": "activo"},
            )
            if created:
                self.stdout.write(self.style.SUCCESS("  + Role Super Administrador asignado a admin"))
            else:
                self.stdout.write("  = Role Super Administrador ya asignado a admin")
        except Role.DoesNotExist:
            self.stdout.write(self.style.WARNING("  ! Role Super Administrador no encontrado"))

        self.stdout.write(self.style.SUCCESS("\nSetup completado exitosamente."))
