#!/usr/bin/env python
"""
Script para cargar datos de demostración usando Django ORM.

Uso:
    cd back/
    python scripts/load_demo_data.py

Crea: módulos, roles, permisos, áreas, empleados, usuarios con
contraseñas válidas, asignaciones de roles y datos laborales.

Contraseñas de demo:
    admin     -> Admin123!
    jgarcia   -> Demo123!
    mrodriguez-> Demo123!
    cmendoza  -> Demo123!
    atorres   -> Demo123!
    rflores   -> Demo123!
    lvargas   -> Demo123!
    cjimenez  -> Demo123!
    psalinas  -> Demo123!
"""

import os
import sys
from datetime import date

# Agregar el directorio apps/api/ al path para que Django encuentre vyntia.settings
back_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, back_dir)


# Load .env file with UTF-8 encoding
def load_env_file(env_path=None):
    """Load .env file with explicit UTF-8 encoding."""
    if env_path is None:
        env_path = os.path.join(back_dir, ".env")
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "=" in line:
                        key, value = line.split("=", 1)
                        os.environ.setdefault(key.strip(), value.strip())


load_env_file()

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.development")

import django

django.setup()

from app_rrhh.models import (
    DatosLaborales,
    Empleado,
)
from apps.organization.models import Area
from apps.identity.models import (
    Modulos,
    Permiso,
    Rol,
    RolPermisos,
    Usuario,
    UsuarioRoles,
)
from django.db import transaction


def crear_modulos():
    """Crear módulos del sistema."""
    modulos_data = [
        {
            "nombre_modulo": "Dashboard",
            "descripcion_modulo": "Panel principal con estadísticas y resumen general",
            "icono_modulo": "LayoutDashboard",
            "ruta_modulo": "/dashboard",
            "orden_visualizacion": 1,
        },
        {
            "nombre_modulo": "Empleados",
            "descripcion_modulo": "Gestión completa de información de empleados",
            "icono_modulo": "Users",
            "ruta_modulo": "/empleados",
            "orden_visualizacion": 2,
        },
        {
            "nombre_modulo": "Vacaciones",
            "descripcion_modulo": "Gestión de vacaciones, solicitudes y períodos",
            "icono_modulo": "CalendarDays",
            "ruta_modulo": "/vacaciones",
            "orden_visualizacion": 3,
        },
        {
            "nombre_modulo": "Administración",
            "descripcion_modulo": "Configuración del sistema, usuarios, roles y permisos",
            "icono_modulo": "Settings",
            "ruta_modulo": "/administracion",
            "orden_visualizacion": 4,
        },
        {
            "nombre_modulo": "Reportes",
            "descripcion_modulo": "Generación de reportes y estadísticas",
            "icono_modulo": "BarChart3",
            "ruta_modulo": "/reportes",
            "orden_visualizacion": 5,
        },
    ]
    creados = 0
    for data in modulos_data:
        _, created = Modulos.objects.get_or_create(
            nombre_modulo=data["nombre_modulo"], defaults=data
        )
        if created:
            creados += 1
    print(f"  Módulos: {creados} creados, {len(modulos_data) - creados} ya existían")
    return Modulos.objects.all()


def crear_roles():
    """Crear roles del sistema."""
    roles_data = [
        {
            "nombre_rol": "Super Administrador",
            "descripcion_rol": "Acceso completo a todas las funcionalidades",
            "nivel_jerarquico": 1,
            "es_rol_sistema": True,
        },
        {
            "nombre_rol": "Administrador RRHH",
            "descripcion_rol": "Gestión completa del módulo de recursos humanos",
            "nivel_jerarquico": 2,
            "es_rol_sistema": True,
        },
        {
            "nombre_rol": "Jefe de Área",
            "descripcion_rol": "Gestión de empleados de su área y aprobación de solicitudes",
            "nivel_jerarquico": 3,
            "es_rol_sistema": False,
        },
        {
            "nombre_rol": "Analista RRHH",
            "descripcion_rol": "Operaciones de consulta y gestión básica de RRHH",
            "nivel_jerarquico": 4,
            "es_rol_sistema": False,
        },
        {
            "nombre_rol": "Empleado",
            "descripcion_rol": "Acceso básico para consultar información personal",
            "nivel_jerarquico": 5,
            "es_rol_sistema": False,
        },
    ]
    creados = 0
    for data in roles_data:
        _, created = Rol.objects.get_or_create(
            nombre_rol=data["nombre_rol"], defaults=data
        )
        if created:
            creados += 1
    print(f"  Roles: {creados} creados, {len(roles_data) - creados} ya existían")
    return Rol.objects.all()


def crear_permisos():
    """Crear permisos del sistema usando módulos estáticos."""

    permisos_data = [
        # Dashboard
        {
            "nombre_permiso": "ver_dashboard",
            "descripcion_permiso": "Visualizar el panel principal",
            "modulo": "dashboard",
            "tipo_permiso": "leer",
        },
        {
            "nombre_permiso": "ver_estadisticas_generales",
            "descripcion_permiso": "Ver estadísticas generales",
            "modulo": "dashboard",
            "tipo_permiso": "leer",
        },
        # Empleados
        {
            "nombre_permiso": "crear_empleado",
            "descripcion_permiso": "Crear nuevos registros de empleados",
            "modulo": "empleados",
            "tipo_permiso": "crear",
        },
        {
            "nombre_permiso": "ver_empleados",
            "descripcion_permiso": "Visualizar información de todos los empleados",
            "modulo": "empleados",
            "tipo_permiso": "leer",
        },
        {
            "nombre_permiso": "editar_empleado",
            "descripcion_permiso": "Modificar información de empleados",
            "modulo": "empleados",
            "tipo_permiso": "actualizar",
        },
        {
            "nombre_permiso": "eliminar_empleado",
            "descripcion_permiso": "Eliminar registros de empleados",
            "modulo": "empleados",
            "tipo_permiso": "eliminar",
        },
        {
            "nombre_permiso": "ver_empleado_propio",
            "descripcion_permiso": "Ver información personal propia",
            "modulo": "empleados",
            "tipo_permiso": "leer",
        },
        {
            "nombre_permiso": "editar_empleado_propio",
            "descripcion_permiso": "Editar información personal propia",
            "modulo": "empleados",
            "tipo_permiso": "actualizar",
        },
        # Vacaciones
        {
            "nombre_permiso": "crear_solicitud_vacaciones",
            "descripcion_permiso": "Crear solicitudes de vacaciones",
            "modulo": "vacaciones",
            "tipo_permiso": "crear",
        },
        {
            "nombre_permiso": "ver_solicitudes_vacaciones",
            "descripcion_permiso": "Ver todas las solicitudes de vacaciones",
            "modulo": "vacaciones",
            "tipo_permiso": "leer",
        },
        {
            "nombre_permiso": "aprobar_solicitudes_vacaciones",
            "descripcion_permiso": "Aprobar o rechazar solicitudes",
            "modulo": "vacaciones",
            "tipo_permiso": "aprobar",
        },
        {
            "nombre_permiso": "ver_reportes_vacaciones",
            "descripcion_permiso": "Visualizar reportes del módulo",
            "modulo": "vacaciones",
            "tipo_permiso": "leer",
        },
        {
            "nombre_permiso": "administrar_periodos_vacaciones",
            "descripcion_permiso": "Gestionar períodos vacacionales",
            "modulo": "vacaciones",
            "tipo_permiso": "ejecutar",
        },
        {
            "nombre_permiso": "configurar_modulo_vacaciones",
            "descripcion_permiso": "Configurar parámetros del módulo",
            "modulo": "vacaciones",
            "tipo_permiso": "ejecutar",
        },
        {
            "nombre_permiso": "ver_vacaciones_propias",
            "descripcion_permiso": "Ver solicitudes y períodos propios",
            "modulo": "vacaciones",
            "tipo_permiso": "leer",
        },
        # Administración
        {
            "nombre_permiso": "gestionar_usuarios",
            "descripcion_permiso": "Crear, editar y eliminar usuarios",
            "modulo": "administracion",
            "tipo_permiso": "ejecutar",
        },
        {
            "nombre_permiso": "gestionar_roles",
            "descripcion_permiso": "Administrar roles y permisos",
            "modulo": "administracion",
            "tipo_permiso": "ejecutar",
        },
        {
            "nombre_permiso": "ver_auditoria",
            "descripcion_permiso": "Visualizar registros de auditoría",
            "modulo": "administracion",
            "tipo_permiso": "leer",
        },
        {
            "nombre_permiso": "configurar_sistema",
            "descripcion_permiso": "Configurar parámetros generales",
            "modulo": "administracion",
            "tipo_permiso": "ejecutar",
        },
        # Reportes
        {
            "nombre_permiso": "generar_reportes",
            "descripcion_permiso": "Generar reportes del sistema",
            "modulo": "reportes",
            "tipo_permiso": "ejecutar",
        },
        {
            "nombre_permiso": "exportar_datos",
            "descripcion_permiso": "Exportar información del sistema",
            "modulo": "reportes",
            "tipo_permiso": "ejecutar",
        },
    ]
    creados = 0
    for data in permisos_data:
        _, created = Permiso.objects.get_or_create(
            nombre_permiso=data["nombre_permiso"], defaults=data
        )
        if created:
            creados += 1
    print(f"  Permisos: {creados} creados, {len(permisos_data) - creados} ya existían")
    return Permiso.objects.all()


def asignar_permisos_a_roles():
    """Asignar permisos a cada rol."""
    todos_permisos = list(Permiso.objects.values_list("permiso_id", flat=True))

    rol_super = Rol.objects.get(nombre_rol="Super Administrador")
    rol_admin_rrhh = Rol.objects.get(nombre_rol="Administrador RRHH")
    rol_jefe = Rol.objects.get(nombre_rol="Jefe de Área")
    rol_analista = Rol.objects.get(nombre_rol="Analista RRHH")
    rol_empleado = Rol.objects.get(nombre_rol="Empleado")

    permisos_por_nombre = {p.nombre_permiso: p for p in Permiso.objects.all()}

    asignaciones = {
        rol_super: todos_permisos,  # Todos los permisos
        rol_admin_rrhh: [
            permisos_por_nombre[n].permiso_id
            for n in [
                "ver_dashboard",
                "ver_estadisticas_generales",
                "crear_empleado",
                "ver_empleados",
                "editar_empleado",
                "ver_empleado_propio",
                "editar_empleado_propio",
                "crear_solicitud_vacaciones",
                "ver_solicitudes_vacaciones",
                "aprobar_solicitudes_vacaciones",
                "ver_reportes_vacaciones",
                "administrar_periodos_vacaciones",
                "configurar_modulo_vacaciones",
                "ver_vacaciones_propias",
                "gestionar_usuarios",
                "gestionar_roles",
                "generar_reportes",
                "exportar_datos",
            ]
        ],
        rol_jefe: [
            permisos_por_nombre[n].permiso_id
            for n in [
                "ver_dashboard",
                "ver_estadisticas_generales",
                "ver_empleados",
                "editar_empleado",
                "ver_empleado_propio",
                "editar_empleado_propio",
                "crear_solicitud_vacaciones",
                "ver_solicitudes_vacaciones",
                "aprobar_solicitudes_vacaciones",
                "ver_reportes_vacaciones",
                "ver_vacaciones_propias",
                "generar_reportes",
            ]
        ],
        rol_analista: [
            permisos_por_nombre[n].permiso_id
            for n in [
                "ver_dashboard",
                "ver_estadisticas_generales",
                "crear_empleado",
                "ver_empleados",
                "editar_empleado",
                "ver_empleado_propio",
                "editar_empleado_propio",
                "crear_solicitud_vacaciones",
                "ver_solicitudes_vacaciones",
                "ver_reportes_vacaciones",
                "administrar_periodos_vacaciones",
                "ver_vacaciones_propias",
                "generar_reportes",
            ]
        ],
        rol_empleado: [
            permisos_por_nombre[n].permiso_id
            for n in [
                "ver_dashboard",
                "ver_empleado_propio",
                "editar_empleado_propio",
                "crear_solicitud_vacaciones",
                "ver_vacaciones_propias",
            ]
        ],
    }

    creados = 0
    for rol, permiso_ids in asignaciones.items():
        for pid in permiso_ids:
            _, created = RolPermisos.objects.get_or_create(rol=rol, permiso_id=pid)
            if created:
                creados += 1
    print(f"  Rol-Permisos: {creados} asignaciones creadas")


def crear_areas():
    """Crear áreas organizacionales."""
    areas_data = [
        {
            "nombre_organo": "Gerencia General",
            "nombre_unidad_organica": "Oficina de Tecnologías de la Información",
            "siglas_area": "OTI",
            "descripcion_area": "Gestión tecnológica",
            "jefe_area": "Ing. Carlos Mendoza",
            "nivel_jerarquico": 2,
            "total_empleados": 5,
        },
        {
            "nombre_organo": "Gerencia General",
            "nombre_unidad_organica": "Oficina de Recursos Humanos",
            "siglas_area": "RRHH",
            "descripcion_area": "Gestión del talento humano",
            "jefe_area": "Lic. Roberto Flores",
            "nivel_jerarquico": 2,
            "total_empleados": 8,
        },
        {
            "nombre_organo": "Gerencia General",
            "nombre_unidad_organica": "Oficina de Administración y Finanzas",
            "siglas_area": "OAF",
            "descripcion_area": "Gestión administrativa y financiera",
            "jefe_area": "CPC. Ana Torres",
            "nivel_jerarquico": 2,
            "total_empleados": 6,
        },
        {
            "nombre_organo": "Gerencia General",
            "nombre_unidad_organica": "Oficina de Planificación y Presupuesto",
            "siglas_area": "OPP",
            "descripcion_area": "Planificación estratégica",
            "jefe_area": "Eco. María Rodríguez",
            "nivel_jerarquico": 2,
            "total_empleados": 4,
        },
    ]
    creados = 0
    for data in areas_data:
        _, created = Area.objects.get_or_create(
            siglas_area=data["siglas_area"], defaults=data
        )
        if created:
            creados += 1
    print(f"  Áreas: {creados} creadas, {len(areas_data) - creados} ya existían")


def crear_empleados():
    """Crear empleados de ejemplo."""
    empleados_data = [
        {
            "numero_documento": "12345678",
            "tipo_documento": "DNI",
            "nombres_empleado": "Juan Carlos",
            "apellido_paterno": "García",
            "apellido_materno": "López",
            "numero_ruc": "10123456781",
            "genero_empleado": "masculino",
            "fecha_nacimiento": date(1985, 3, 15),
            "es_padre_familia": False,
            "sistema_pensiones": "AFP PRIMA",
            "telefono_celular": "987654321",
            "correo_personal": "juan.garcia@email.com",
            "estado_civil": "soltero",
            "direccion_domicilio": "Av. Principal 123",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Banco de Crédito",
            "numero_cuenta_bancaria": "1234567890123456",
            "numero_cci": "00212345678901234567",
        },
        {
            "numero_documento": "87654321",
            "tipo_documento": "DNI",
            "nombres_empleado": "María Elena",
            "apellido_paterno": "Rodríguez",
            "apellido_materno": "Pérez",
            "numero_ruc": "10876543211",
            "genero_empleado": "femenino",
            "fecha_nacimiento": date(1990, 7, 22),
            "es_padre_familia": True,
            "sistema_pensiones": "ONP",
            "telefono_celular": "987654322",
            "correo_personal": "maria.rodriguez@email.com",
            "estado_civil": "casado",
            "direccion_domicilio": "Jr. Secundario 456",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Banco Continental",
            "numero_cuenta_bancaria": "2345678901234567",
            "numero_cci": "00223456789012345678",
        },
        {
            "numero_documento": "11223344",
            "tipo_documento": "DNI",
            "nombres_empleado": "Carlos Alberto",
            "apellido_paterno": "Mendoza",
            "apellido_materno": "Silva",
            "numero_ruc": "10112233441",
            "genero_empleado": "masculino",
            "fecha_nacimiento": date(1988, 11, 10),
            "es_padre_familia": True,
            "sistema_pensiones": "AFP INTEGRA",
            "telefono_celular": "987654323",
            "correo_personal": "carlos.mendoza@email.com",
            "estado_civil": "casado",
            "direccion_domicilio": "Calle Tercera 789",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Banco de la Nación",
            "numero_cuenta_bancaria": "3456789012345678",
            "numero_cci": "00234567890123456789",
        },
        {
            "numero_documento": "44332211",
            "tipo_documento": "DNI",
            "nombres_empleado": "Ana Sofía",
            "apellido_paterno": "Torres",
            "apellido_materno": "Vega",
            "numero_ruc": "10443322111",
            "genero_empleado": "femenino",
            "fecha_nacimiento": date(1992, 5, 18),
            "es_padre_familia": False,
            "sistema_pensiones": "AFP PROFUTURO",
            "telefono_celular": "987654324",
            "correo_personal": "ana.torres@email.com",
            "estado_civil": "soltero",
            "direccion_domicilio": "Av. Cuarta 321",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Interbank",
            "numero_cuenta_bancaria": "4567890123456789",
            "numero_cci": "00245678901234567890",
        },
        {
            "numero_documento": "55667788",
            "tipo_documento": "DNI",
            "nombres_empleado": "Roberto Miguel",
            "apellido_paterno": "Flores",
            "apellido_materno": "Castillo",
            "numero_ruc": "10556677881",
            "genero_empleado": "masculino",
            "fecha_nacimiento": date(1983, 9, 3),
            "es_padre_familia": True,
            "sistema_pensiones": "ONP",
            "telefono_celular": "987654325",
            "correo_personal": "roberto.flores@email.com",
            "estado_civil": "casado",
            "direccion_domicilio": "Jr. Quinta 654",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Scotiabank",
            "numero_cuenta_bancaria": "5678901234567890",
            "numero_cci": "00256789012345678901",
        },
        {
            "numero_documento": "99887766",
            "tipo_documento": "DNI",
            "nombres_empleado": "Luis Fernando",
            "apellido_paterno": "Vargas",
            "apellido_materno": "Morales",
            "numero_ruc": "10998877661",
            "genero_empleado": "masculino",
            "fecha_nacimiento": date(1987, 12, 8),
            "es_padre_familia": False,
            "sistema_pensiones": "AFP HABITAT",
            "telefono_celular": "987654326",
            "correo_personal": "luis.vargas@email.com",
            "estado_civil": "soltero",
            "direccion_domicilio": "Av. Sexta 987",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Banco de Crédito",
            "numero_cuenta_bancaria": "6789012345678901",
            "numero_cci": "00267890123456789012",
        },
        {
            "numero_documento": "66554433",
            "tipo_documento": "DNI",
            "nombres_empleado": "Carmen Rosa",
            "apellido_paterno": "Jiménez",
            "apellido_materno": "Herrera",
            "numero_ruc": "10665544331",
            "genero_empleado": "femenino",
            "fecha_nacimiento": date(1991, 4, 25),
            "es_padre_familia": True,
            "sistema_pensiones": "ONP",
            "telefono_celular": "987654327",
            "correo_personal": "carmen.jimenez@email.com",
            "estado_civil": "casado",
            "direccion_domicilio": "Jr. Séptima 654",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Interbank",
            "numero_cuenta_bancaria": "7890123456789012",
            "numero_cci": "00278901234567890123",
        },
        {
            "numero_documento": "33221100",
            "tipo_documento": "DNI",
            "nombres_empleado": "Pedro Antonio",
            "apellido_paterno": "Salinas",
            "apellido_materno": "Ramos",
            "numero_ruc": "10332211001",
            "genero_empleado": "masculino",
            "fecha_nacimiento": date(1989, 8, 14),
            "es_padre_familia": True,
            "sistema_pensiones": "AFP PRIMA",
            "telefono_celular": "987654328",
            "correo_personal": "pedro.salinas@email.com",
            "estado_civil": "casado",
            "direccion_domicilio": "Calle Octava 321",
            "distrito_domicilio": "Lima",
            "provincia_domicilio": "Lima",
            "departamento_domicilio": "Lima",
            "entidad_bancaria": "Scotiabank",
            "numero_cuenta_bancaria": "8901234567890123",
            "numero_cci": "00289012345678901234",
            "estado_empleado": "inactivo",
        },
    ]
    creados = 0
    for data in empleados_data:
        _, created = Empleado.objects.get_or_create(
            numero_documento=data["numero_documento"], defaults=data
        )
        if created:
            creados += 1
    print(
        f"  Empleados: {creados} creados, {len(empleados_data) - creados} ya existían"
    )


def crear_usuarios():
    """Crear usuarios con contraseñas válidas hasheadas por Django."""
    DEFAULT_PASSWORD = "Demo123!"
    ADMIN_PASSWORD = "Admin123!"

    empleados = {e.numero_documento: e for e in Empleado.objects.all()}

    usuarios_data = [
        {
            "username": "admin",
            "email": "admin@institucion.gob.pe",
            "password": ADMIN_PASSWORD,
            "nombres_usuario": "Super",
            "apellidos_usuario": "Admin",
            "tipo_usuario": "administrador",
            "nivel_acceso": "total",
            "is_staff": True,
            "is_superuser": True,
            "empleado": None,
        },
        {
            "username": "jgarcia",
            "email": "jgarcia@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "Juan Carlos",
            "apellidos_usuario": "García López",
            "tipo_usuario": "empleado",
            "nivel_acceso": "personal",
            "empleado": empleados.get("12345678"),
        },
        {
            "username": "mrodriguez",
            "email": "mrodriguez@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "María Elena",
            "apellidos_usuario": "Rodríguez Pérez",
            "tipo_usuario": "empleado",
            "nivel_acceso": "personal",
            "empleado": empleados.get("87654321"),
        },
        {
            "username": "cmendoza",
            "email": "cmendoza@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "Carlos Alberto",
            "apellidos_usuario": "Mendoza Silva",
            "tipo_usuario": "jefe",
            "nivel_acceso": "departamental",
            "empleado": empleados.get("11223344"),
        },
        {
            "username": "atorres",
            "email": "atorres@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "Ana Sofía",
            "apellidos_usuario": "Torres Vega",
            "tipo_usuario": "empleado",
            "nivel_acceso": "personal",
            "empleado": empleados.get("44332211"),
        },
        {
            "username": "rflores",
            "email": "rflores@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "Roberto Miguel",
            "apellidos_usuario": "Flores Castillo",
            "tipo_usuario": "rrhh",
            "nivel_acceso": "total",
            "empleado": empleados.get("55667788"),
        },
        {
            "username": "lvargas",
            "email": "lvargas@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "Luis Fernando",
            "apellidos_usuario": "Vargas Morales",
            "tipo_usuario": "empleado",
            "nivel_acceso": "personal",
            "empleado": empleados.get("99887766"),
        },
        {
            "username": "cjimenez",
            "email": "cjimenez@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "Carmen Rosa",
            "apellidos_usuario": "Jiménez Herrera",
            "tipo_usuario": "empleado",
            "nivel_acceso": "personal",
            "empleado": empleados.get("66554433"),
        },
        {
            "username": "psalinas",
            "email": "psalinas@institucion.gob.pe",
            "password": DEFAULT_PASSWORD,
            "nombres_usuario": "Pedro Antonio",
            "apellidos_usuario": "Salinas Ramos",
            "tipo_usuario": "empleado",
            "nivel_acceso": "personal",
            "empleado": empleados.get("33221100"),
            "is_active": False,
            "estado_usuario": "inactivo",
        },
    ]

    creados = 0
    actualizados = 0
    for data in usuarios_data:
        password = data.pop("password")
        existing = Usuario.objects.filter(username=data["username"]).first()
        if existing:
            # Siempre actualizar la contrasena para que sea valida
            existing.set_password(password)
            existing.save(update_fields=["password"])
            actualizados += 1
        else:
            user = Usuario(**data)
            user.set_password(password)  # Hashea la contrasena correctamente
            user.save()
            creados += 1
    print(f"  Usuarios: {creados} creados, {actualizados} actualizados")
    print(f"    > admin / {ADMIN_PASSWORD}")
    print(f"    > demas usuarios / {DEFAULT_PASSWORD}")


def asignar_roles_a_usuarios():
    """Asignar roles a usuarios."""
    asignaciones = [
        ("admin", "Super Administrador"),
        ("jgarcia", "Empleado"),
        ("mrodriguez", "Analista RRHH"),
        ("cmendoza", "Jefe de Área"),
        ("atorres", "Analista RRHH"),
        ("rflores", "Administrador RRHH"),
        ("lvargas", "Empleado"),
        ("cjimenez", "Analista RRHH"),
        ("psalinas", "Empleado"),
    ]
    creados = 0
    for username, nombre_rol in asignaciones:
        try:
            usuario = Usuario.objects.get(username=username)
            rol = Rol.objects.get(nombre_rol=nombre_rol)
            _, created = UsuarioRoles.objects.get_or_create(
                usuario=usuario, rol=rol, defaults={"estado_asignacion": "activo"}
            )
            if created:
                creados += 1
        except (Usuario.DoesNotExist, Rol.DoesNotExist) as e:
            print(f"    WARNING: No se pudo asignar {nombre_rol} a {username}: {e}")
    print(f"  Usuario-Roles: {creados} asignaciones creadas")


def crear_datos_laborales():
    """Crear datos laborales de ejemplo."""
    areas = {a.siglas_area: a for a in Area.objects.all()}
    empleados = {e.numero_documento: e for e in Empleado.objects.all()}

    datos = [
        {
            "empleado": empleados.get("12345678"),
            "area": areas.get("OTI"),
            "fecha_ingreso": date(2021, 3, 15),
            "cargo_empleado": "Analista de Sistemas",
            "categoria": "SP-ES",
            "tipo_contrato": "CAS",
            "regimen_laboral": "CAS",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2021, 3, 15),
            "sueldo_basico": 3500.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
        },
        {
            "empleado": empleados.get("87654321"),
            "area": areas.get("OPP"),
            "fecha_ingreso": date(2020, 1, 10),
            "cargo_empleado": "Especialista en Planificación",
            "categoria": "SP-ES",
            "tipo_contrato": "CAS",
            "regimen_laboral": "CAS",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2020, 1, 10),
            "sueldo_basico": 4000.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
        },
        {
            "empleado": empleados.get("11223344"),
            "area": areas.get("OTI"),
            "fecha_ingreso": date(2019, 6, 1),
            "cargo_empleado": "Jefe de OTI",
            "categoria": "SP-DS",
            "tipo_contrato": "CAP",
            "regimen_laboral": "CAP",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2019, 6, 1),
            "sueldo_basico": 4500.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
        },
        {
            "empleado": empleados.get("44332211"),
            "area": areas.get("OAF"),
            "fecha_ingreso": date(2022, 8, 15),
            "cargo_empleado": "Especialista en Finanzas",
            "categoria": "SP-ES",
            "tipo_contrato": "CAS",
            "regimen_laboral": "CAS",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2022, 8, 15),
            "sueldo_basico": 3800.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
        },
        {
            "empleado": empleados.get("55667788"),
            "area": areas.get("RRHH"),
            "fecha_ingreso": date(2018, 2, 20),
            "cargo_empleado": "Jefe de RRHH",
            "categoria": "SP-DS",
            "tipo_contrato": "CAP",
            "regimen_laboral": "CAP",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2018, 2, 20),
            "sueldo_basico": 5500.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
        },
        {
            "empleado": empleados.get("99887766"),
            "area": areas.get("OTI"),
            "fecha_ingreso": date(2023, 5, 10),
            "cargo_empleado": "Desarrollador de Software",
            "categoria": "SP-ES",
            "tipo_contrato": "CAS",
            "regimen_laboral": "CAS",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2023, 5, 10),
            "sueldo_basico": 3200.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
        },
        {
            "empleado": empleados.get("66554433"),
            "area": areas.get("RRHH"),
            "fecha_ingreso": date(2022, 11, 20),
            "cargo_empleado": "Asistente de RRHH",
            "categoria": "SP-AP",
            "tipo_contrato": "CAS",
            "regimen_laboral": "CAS",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2022, 11, 20),
            "sueldo_basico": 2800.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
        },
        {
            "empleado": empleados.get("33221100"),
            "area": areas.get("OAF"),
            "fecha_ingreso": date(2021, 9, 15),
            "cargo_empleado": "Analista Contable",
            "categoria": "SP-ES",
            "tipo_contrato": "CAS",
            "regimen_laboral": "CAS",
            "modalidad_trabajo": "presencial",
            "jornada_laboral": "completa",
            "fecha_inicio_contrato": date(2021, 9, 15),
            "sueldo_basico": 3300.00,
            "asignacion_familiar": 93.00,
            "bonificacion_especial": 0,
            "otras_bonificaciones": 0,
            "horas_semanales": 40,
            "estado_datos": "inactivo",
        },
    ]
    creados = 0
    for data in datos:
        emp = data.get("empleado")
        if emp and not DatosLaborales.objects.filter(empleado=emp).exists():
            DatosLaborales.objects.create(**data)
            creados += 1
    print(f"  Datos laborales: {creados} creados, {len(datos) - creados} ya existían")


@transaction.atomic
def main():
    print("=" * 60)
    print("  CARGA DE DATOS DE DEMOSTRACIÓN")
    print("=" * 60)
    print()

    print("1. Creando roles...")
    crear_roles()

    print("2. Creando permisos...")
    crear_permisos()

    print("3. Asignando permisos a roles...")
    asignar_permisos_a_roles()

    print("4. Creando áreas...")
    crear_areas()

    print("5. Creando empleados...")
    crear_empleados()

    print("6. Creando usuarios (con contraseñas hasheadas)...")
    crear_usuarios()

    print("7. Asignando roles a usuarios...")
    asignar_roles_a_usuarios()

    print("8. Creando datos laborales...")
    crear_datos_laborales()

    print()
    print("=" * 60)
    print("  DATOS DE DEMOSTRACION CARGADOS EXITOSAMENTE")
    print("=" * 60)
    print()
    print("  Credenciales de acceso:")
    print("  +--------------+------------+-------------------------+")
    print("  | Usuario      | Password   | Rol                     |")
    print("  +--------------+------------+-------------------------+")
    print("  | admin        | Admin123!  | Super Administrador     |")
    print("  | rflores      | Demo123!   | Administrador RRHH      |")
    print("  | cmendoza     | Demo123!   | Jefe de Area            |")
    print("  | mrodriguez   | Demo123!   | Analista RRHH           |")
    print("  | atorres      | Demo123!   | Analista RRHH           |")
    print("  | cjimenez     | Demo123!   | Analista RRHH           |")
    print("  | jgarcia      | Demo123!   | Empleado                |")
    print("  | lvargas      | Demo123!   | Empleado                |")
    print("  | psalinas     | Demo123!   | Empleado (inactivo)     |")
    print("  +--------------+------------+-------------------------+")
    print()


if __name__ == "__main__":
    main()
