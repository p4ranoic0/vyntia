# -*- coding: utf-8 -*-
"""
Comando de gestión: seed_menu
Crea o actualiza la estructura completa del menú en la base de datos.
Alineada con las rutas de App.tsx del frontend.

Uso:
    python manage.py seed_menu
    python manage.py seed_menu --reset   # Elimina y recrea todo
"""

from app_rrhh.models import ModuloPermiso, Modulos, Permiso
from django.core.management.base import BaseCommand
from django.utils.text import slugify

# ---------------------------------------------------------------------------
# Estructura del menú — alineada con front/src/App.tsx
# Formato: (nombre, icono, ruta, orden, permisos_requeridos, hijos)
# permisos_requeridos vacío = visible para cualquier usuario autenticado
# ---------------------------------------------------------------------------
MENU_STRUCTURE = [
    {
        "nombre": "Dashboard",
        "icono": "layout-dashboard",
        "ruta": "/dashboard",
        "orden": 1,
        "permisos": "ver_dashboard",
        "hijos": [],
    },
    {
        "nombre": "Empleados",
        "icono": "users",
        "ruta": "/empleados",
        "orden": 2,
        "permisos": "ver_empleados,crear_empleado,editar_empleado",
        "hijos": [
            {
                "nombre": "Lista de Empleados",
                "icono": "list",
                "ruta": "/empleados",
                "orden": 1,
                "permisos": "ver_empleados",
            },
            {
                "nombre": "Datos Personales",
                "icono": "user",
                "ruta": "/empleados/datos-personales",
                "orden": 2,
                "permisos": "ver_empleados",
            },
            {
                "nombre": "Datos Laborales",
                "icono": "briefcase",
                "ruta": "/empleados/datos-laborales",
                "orden": 3,
                "permisos": "ver_empleados",
            },
            {
                "nombre": "Formación Académica",
                "icono": "graduation-cap",
                "ruta": "/empleados/datos-academicos",
                "orden": 4,
                "permisos": "ver_empleados",
            },
            {
                "nombre": "Datos Familiares",
                "icono": "heart",
                "ruta": "/empleados/datos-familiares",
                "orden": 5,
                "permisos": "ver_empleados",
            },
            {
                "nombre": "Contratos",
                "icono": "file-signature",
                "ruta": "/contratos",
                "orden": 6,
                "permisos": "gestionar_usuarios",
            },
        ],
    },
    {
        "nombre": "Vacaciones",
        "icono": "calendar",
        "ruta": "/vacaciones",
        "orden": 3,
        "permisos": "ver_vacaciones_propias",
        "hijos": [
            {
                "nombre": "Nueva Solicitud",
                "icono": "plus-circle",
                "ruta": "/vacaciones/nueva-solicitud",
                "orden": 1,
                "permisos": "crear_solicitud_vacaciones",
            },
            {
                "nombre": "Mis Solicitudes",
                "icono": "file-text",
                "ruta": "/vacaciones/solicitudes",
                "orden": 2,
                "permisos": "ver_solicitudes_vacaciones",
            },
            {
                "nombre": "Periodos",
                "icono": "calendar-days",
                "ruta": "/vacaciones/periodos",
                "orden": 3,
                "permisos": "administrar_periodos_vacaciones",
            },
            {
                "nombre": "Reportes",
                "icono": "bar-chart",
                "ruta": "/vacaciones/reportes",
                "orden": 4,
                "permisos": "ver_reportes_vacaciones,administrar_periodos_vacaciones,aprobar_solicitudes_vacaciones",
            },
            {
                "nombre": "Configuración",
                "icono": "settings",
                "ruta": "/vacaciones/configuracion",
                "orden": 5,
                "permisos": "configurar_modulo_vacaciones",
            },
        ],
    },
    {
        "nombre": "Legajo Digital",
        "icono": "folder-open",
        "ruta": "/legajo",
        "orden": 4,
        "permisos": "ver_empleados",
        "hijos": [],
    },

    {
        "nombre": "Remuneraciones",
        "icono": "banknote",
        "ruta": "/remuneraciones",
        "orden": 6,
        "permisos": "gestionar_usuarios",
        "hijos": [
            {
                "nombre": "Planillas Mensuales",
                "icono": "table",
                "ruta": "/remuneraciones/planillas-mensuales",
                "orden": 1,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Proceso de Planillas",
                "icono": "play-circle",
                "ruta": "/remuneraciones/proceso-planillas",
                "orden": 2,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Boletas de Pago",
                "icono": "receipt",
                "ruta": "/remuneraciones/boletas-pago",
                "orden": 3,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Descuentos Masivos",
                "icono": "minus-circle",
                "ruta": "/remuneraciones/descuentos-masivos",
                "orden": 4,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Reportes",
                "icono": "bar-chart",
                "ruta": "/remuneraciones/reportes",
                "orden": 5,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Configuración UIT",
                "icono": "settings",
                "ruta": "/remuneraciones/configuracion-uit",
                "orden": 6,
                "permisos": "gestionar_usuarios",
            },
        ],
    },
    {
        "nombre": "Onboarding",
        "icono": "user-check",
        "ruta": "/onboarding/admin",
        "orden": 7,
        "permisos": "gestionar_usuarios",
        "hijos": [],
    },
    {
        "nombre": "Desplazamiento",
        "icono": "map-pin",
        "ruta": "/desplazamiento",
        "orden": 8,
        "permisos": "ver_empleados",
        "hijos": [],
    },
    {
        "nombre": "Administración",
        "icono": "shield",
        "ruta": "/admin",
        "orden": 10,
        "permisos": "gestionar_usuarios,gestionar_roles,gestionar_permisos",
        "hijos": [
            {
                "nombre": "Usuarios",
                "icono": "users",
                "ruta": "/usuarios/listado",
                "orden": 1,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Áreas",
                "icono": "building",
                "ruta": "/areas/listado",
                "orden": 2,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Roles",
                "icono": "shield-check",
                "ruta": "/seguridad/roles",
                "orden": 3,
                "permisos": "gestionar_roles",
            },
            {
                "nombre": "Permisos",
                "icono": "key",
                "ruta": "/seguridad/permisos",
                "orden": 4,
                "permisos": "gestionar_permisos",
            },
            {
                "nombre": "Roles-Permisos",
                "icono": "link",
                "ruta": "/seguridad/roles-permisos",
                "orden": 5,
                "permisos": "gestionar_roles",
            },
            {
                "nombre": "Plantillas de Documentos",
                "icono": "file-text",
                "ruta": "/plantillas-documentos",
                "orden": 6,
                "permisos": "gestionar_usuarios",
            },
            {
                "nombre": "Configuración Empresa",
                "icono": "building-2",
                "ruta": "/configuracion/empresa",
                "orden": 7,
                "permisos": "gestionar_usuarios",
            },
        ],
    },
]


class Command(BaseCommand):
    help = "Crea o actualiza la estructura del menú en la base de datos."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Elimina todos los módulos existentes y los recrea desde cero.",
        )

    def handle(self, *args, **options):
        if options["reset"]:
            count, _ = Modulos.objects.all().delete()
            self.stdout.write(
                self.style.WARNING(f"  Eliminados {count} módulos existentes.")
            )

        created = 0
        updated = 0

        for item in MENU_STRUCTURE:
            padre, is_new = self._upsert_modulo(item, padre=None)
            if is_new:
                created += 1
            else:
                updated += 1

            for hijo in item.get("hijos", []):
                _, is_new = self._upsert_modulo(hijo, padre=padre)
                if is_new:
                    created += 1
                else:
                    updated += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Menú actualizado: {created} creados, {updated} actualizados."
            )
        )

    def _upsert_modulo(self, data, padre):
        """Crea o actualiza un módulo; retorna (instancia, es_nuevo)."""
        permisos_raw = data.get("permisos", "") or ""
        required_permission_names = {
            item.strip() for item in permisos_raw.split(",") if item.strip()
        }

        defaults = {
            "icono_modulo": data["icono"],
            "ruta_modulo": data["ruta"],
            "orden_visualizacion": data["orden"],
            "estado_modulo": "activo",
            # Mantener campo legacy mientras termina la transición al pivote.
            "permisos_requeridos": permisos_raw or None,
            "modulo_padre": padre,
        }
        obj, created = Modulos.objects.update_or_create(
            nombre_modulo=data["nombre"],
            defaults=defaults,
        )

        # Sincronizar tabla pivote modulo_permisos.
        current_relations = ModuloPermiso.objects.filter(modulo=obj).select_related(
            "permiso"
        )
        current_names = {rel.permiso.nombre_permiso for rel in current_relations}

        to_remove = current_names - required_permission_names
        if to_remove:
            ModuloPermiso.objects.filter(
                modulo=obj,
                permiso__nombre_permiso__in=to_remove,
            ).delete()

        if required_permission_names:
            existing_permisos = {
                permiso.nombre_permiso: permiso
                for permiso in Permiso.objects.filter(
                    nombre_permiso__in=required_permission_names
                )
            }

            missing_permissions = required_permission_names - set(
                existing_permisos.keys()
            )
            if missing_permissions:
                modulo_ref = slugify(
                    padre.nombre_modulo if padre else data["nombre"]
                ).replace("-", "_")
                self.stdout.write(
                    self.style.WARNING(
                        f"    Permisos no encontrados para '{data['nombre']}': {', '.join(sorted(missing_permissions))}"
                    )
                )
                for permission_name in missing_permissions:
                    permiso = Permiso.objects.create(
                        nombre_permiso=permission_name,
                        descripcion_permiso=f"Permiso generado automaticamente para el modulo {data['nombre']}",
                        modulo=modulo_ref,
                        tipo_permiso="ejecutar",
                        estado_permiso="activo",
                    )
                    existing_permisos[permission_name] = permiso
                    self.stdout.write(
                        self.style.WARNING(
                            f"      Creado permiso faltante: {permission_name}"
                        )
                    )

            for permission_name, permiso in existing_permisos.items():
                if permission_name not in current_names:
                    ModuloPermiso.objects.create(modulo=obj, permiso=permiso)

        action = "Creado" if created else "Actualizado"
        indent = "    " if padre else ""
        self.stdout.write(f'{indent}{action}: {data["nombre"]}  ({data["ruta"]})')
        return obj, created
