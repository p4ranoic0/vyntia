"""Constantes de roles y permisos para evitar strings magicos."""


class Roles:
    SUPER_ADMIN = "Super Administrador"
    ADMIN_RRHH = "Administrador RRHH"
    JEFE_AREA = "Jefe de Area"
    ANALISTA_RRHH = "Analista RRHH"
    EMPLEADO = "Empleado"

    # Grupos para verificacion
    ADMIN_ROLES = [SUPER_ADMIN, ADMIN_RRHH]
    HR_ROLES = [SUPER_ADMIN, ADMIN_RRHH, ANALISTA_RRHH, JEFE_AREA]
    MANAGER_ROLES = [SUPER_ADMIN, ADMIN_RRHH, JEFE_AREA]
    EMPLOYEE_ROLES = [EMPLEADO, ANALISTA_RRHH, JEFE_AREA, ADMIN_RRHH, SUPER_ADMIN]


class Permissions:
    # Dashboard
    VIEW_DASHBOARD = "ver_dashboard"
    VIEW_DASHBOARD_STATS = "ver_estadisticas_dashboard"

    # Empleados
    VIEW_EMPLOYEES = "ver_empleados"
    CREATE_EMPLOYEE = "crear_empleado"
    EDIT_EMPLOYEE = "editar_empleado"
    DELETE_EMPLOYEE = "eliminar_empleado"
    EXPORT_EMPLOYEES = "exportar_empleados"
    VIEW_OWN_DATA = "ver_datos_propios"
    EDIT_OWN_DATA = "editar_datos_propios"

    # Vacaciones
    VIEW_VACATIONS = "ver_solicitudes_vacaciones"
    CREATE_VACATION = "crear_solicitud_vacaciones"
    APPROVE_VACATION = "aprobar_solicitud_vacaciones"
    ADMIN_VACATION_PERIODS = "administrar_periodos_vacaciones"
    CONFIG_VACATION_MODULE = "configurar_modulo_vacaciones"

    # Administracion
    MANAGE_USERS = "gestionar_usuarios"
    MANAGE_ROLES = "gestionar_roles"
    MANAGE_PERMISSIONS = "gestionar_permisos"
    MANAGE_MODULES = "gestionar_modulos"

    # Reportes
    VIEW_REPORTS = "ver_reportes"
    EXPORT_REPORTS = "exportar_reportes"
