"""
Configuración estática de módulos del sistema.

Este archivo reemplaza la tabla Modulos en la base de datos,
permitiendo una gestión más sencilla y escalable de la estructura del menú.
"""

MODULES_CONFIG = [
    {
        "id": "dashboard",
        "nombre": "Dashboard",
        "descripcion": "Panel principal con estadísticas y resumen general",
        "icono": "LayoutDashboard",
        "ruta": "/dashboard",
        "orden": 1,
        "permisos_requeridos": ["ver_dashboard"],
        "submodulos": [],
    },
    {
        "id": "empleados",
        "nombre": "Empleados",
        "descripcion": "Gestión completa de información de empleados",
        "icono": "Users",
        "ruta": "/empleados",
        "orden": 2,
        "permisos_requeridos": ["ver_empleados", "ver_empleado_propio"],
        "submodulos": [
            {
                "id": "empleados_lista",
                "nombre": "Lista de Empleados",
                "descripcion": "Ver todos los empleados",
                "icono": "List",
                "ruta": "/empleados",
                "orden": 1,
                "permisos_requeridos": ["ver_empleados"],
            },
            {
                "id": "empleados_nuevo",
                "nombre": "Nuevo Empleado",
                "descripcion": "Crear nuevo empleado",
                "icono": "UserPlus",
                "ruta": "/empleados/nuevo",
                "orden": 2,
                "permisos_requeridos": ["crear_empleado"],
            },
            {
                "id": "empleados_perfil",
                "nombre": "Mi Perfil",
                "descripcion": "Ver y editar datos personales",
                "icono": "User",
                "ruta": "/empleados/perfil",
                "orden": 3,
                "permisos_requeridos": ["ver_empleado_propio"],
            },
            {
                "id": "empleados_contratos",
                "nombre": "Contratos",
                "descripcion": "Gestión de contratos laborales y adendas",
                "icono": "FileSignature",
                "ruta": "/contratos",
                "orden": 4,
                "permisos_requeridos": ["ver_contratos"],
            },
        ],
    },
    {
        "id": "vacaciones",
        "nombre": "Vacaciones",
        "descripcion": "Gestión de vacaciones, solicitudes y períodos",
        "icono": "CalendarDays",
        "ruta": "/vacaciones",
        "orden": 3,
        "permisos_requeridos": ["ver_vacaciones_propias", "ver_solicitudes_vacaciones"],
        "submodulos": [
            {
                "id": "vacaciones_solicitudes",
                "nombre": "Solicitudes",
                "descripcion": "Ver y gestionar solicitudes de vacaciones",
                "icono": "FileText",
                "ruta": "/vacaciones/solicitudes",
                "orden": 1,
                "permisos_requeridos": ["ver_solicitudes_vacaciones"],
            },
            {
                "id": "vacaciones_nueva",
                "nombre": "Nueva Solicitud",
                "descripcion": "Crear nueva solicitud de vacaciones",
                "icono": "FilePlus",
                "ruta": "/vacaciones/nueva-solicitud",
                "orden": 2,
                "permisos_requeridos": ["crear_solicitud_vacaciones"],
            },
            {
                "id": "vacaciones_periodos",
                "nombre": "Períodos",
                "descripcion": "Gestionar períodos vacacionales",
                "icono": "Calendar",
                "ruta": "/vacaciones/periodos",
                "orden": 3,
                "permisos_requeridos": ["administrar_periodos_vacaciones"],
            },
            {
                "id": "vacaciones_configuracion",
                "nombre": "Configuración",
                "descripcion": "Configurar parámetros del módulo de vacaciones",
                "icono": "Settings",
                "ruta": "/vacaciones/configuracion",
                "orden": 4,
                "permisos_requeridos": ["configurar_modulo_vacaciones"],
            },
            {
                "id": "vacaciones_reportes",
                "nombre": "Reportes",
                "descripcion": "Reportes de vacaciones",
                "icono": "BarChart",
                "ruta": "/vacaciones/reportes",
                "orden": 5,
                "permisos_requeridos": ["ver_reportes_vacaciones"],
            },
        ],
    },

    {
        "id": "onboarding",
        "nombre": "Onboarding",
        "descripcion": "Gestión de procesos de incorporación",
        "icono": "UserCheck",
        "ruta": "/onboarding",
        "orden": 5,
        "permisos_requeridos": ["ver_onboarding"],
        "submodulos": [],
    },
    {
        "id": "legajo",
        "nombre": "Legajo Digital",
        "descripcion": "Documentación y legajo de empleados",
        "icono": "FolderOpen",
        "ruta": "/legajo",
        "orden": 6,
        "permisos_requeridos": ["ver_legajo"],
        "submodulos": [],
    },
    {
        "id": "administracion",
        "nombre": "Administración",
        "descripcion": "Configuración del sistema, usuarios, roles y permisos",
        "icono": "Settings",
        "ruta": "/administracion",
        "orden": 7,
        "permisos_requeridos": ["gestionar_usuarios", "gestionar_roles"],
        "submodulos": [
            {
                "id": "admin_usuarios",
                "nombre": "Usuarios",
                "descripcion": "Gestionar usuarios del sistema",
                "icono": "Users",
                "ruta": "/administracion/usuarios",
                "orden": 1,
                "permisos_requeridos": ["gestionar_usuarios"],
            },
            {
                "id": "admin_roles",
                "nombre": "Roles",
                "descripcion": "Gestionar roles y permisos",
                "icono": "Shield",
                "ruta": "/administracion/roles",
                "orden": 2,
                "permisos_requeridos": ["gestionar_roles"],
            },
            {
                "id": "admin_areas",
                "nombre": "Áreas",
                "descripcion": "Gestionar áreas organizacionales",
                "icono": "Building",
                "ruta": "/administracion/areas",
                "orden": 3,
                "permisos_requeridos": ["gestionar_usuarios"],
            },
            {
                "id": "admin_auditoria",
                "nombre": "Auditoría",
                "descripcion": "Ver logs de auditoría del sistema",
                "icono": "History",
                "ruta": "/administracion/auditoria",
                "orden": 4,
                "permisos_requeridos": ["ver_auditoria"],
            },
            {
                "id": "admin_config",
                "nombre": "Configuración",
                "descripcion": "Configuración general del sistema",
                "icono": "Settings",
                "ruta": "/administracion/configuracion",
                "orden": 5,
                "permisos_requeridos": ["configurar_sistema"],
            },
        ],
    },
    {
        "id": "reportes",
        "nombre": "Reportes",
        "descripcion": "Reportes y analíticas del sistema",
        "icono": "BarChart",
        "ruta": "/reportes",
        "orden": 8,
        "permisos_requeridos": ["generar_reportes"],
        "submodulos": [],
    },
]


def get_modules_for_user(user_permissions):
    """
    Filtra módulos según los permisos del usuario.

    Args:
        user_permissions: Lista de permisos del usuario (strings)

    Returns:
        Lista de módulos filtrados con sus submódulos
    """
    user_perms_set = set(user_permissions)
    filtered_modules = []

    for module in MODULES_CONFIG:
        # Verificar si el usuario tiene alguno de los permisos requeridos
        required_perms = set(module.get("permisos_requeridos", []))

        # Si no hay permisos requeridos o el usuario tiene al menos uno
        if not required_perms or user_perms_set & required_perms:
            module_copy = module.copy()

            # Filtrar submódulos
            if module.get("submodulos"):
                filtered_submodules = []
                for submodule in module["submodulos"]:
                    sub_required = set(submodule.get("permisos_requeridos", []))
                    if not sub_required or user_perms_set & sub_required:
                        filtered_submodules.append(submodule)

                module_copy["submodulos"] = filtered_submodules

            filtered_modules.append(module_copy)

    return filtered_modules


def get_module_by_id(module_id):
    """
    Obtiene un módulo por su ID.

    Args:
        module_id: ID del módulo

    Returns:
        Dict con datos del módulo o None
    """
    for module in MODULES_CONFIG:
        if module["id"] == module_id:
            return module

        # Buscar en submódulos
        for submodule in module.get("submodulos", []):
            if submodule["id"] == module_id:
                return submodule

    return None


def get_all_module_ids():
    """
    Retorna lista de todos los IDs de módulos y submódulos.
    """
    ids = []
    for module in MODULES_CONFIG:
        ids.append(module["id"])
        for submodule in module.get("submodulos", []):
            ids.append(submodule["id"])
    return ids
