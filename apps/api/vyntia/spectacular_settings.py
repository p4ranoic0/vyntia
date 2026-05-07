"""Configuración avanzada para DRF Spectacular."""

# DRF Spectacular - OpenAPI 3.0.0
SPECTACULAR_SETTINGS = {
    # Titles and descriptions
    "TITLE": "VYNTIA API",
    "DESCRIPTION": "API para el sistema integrado de gestión de recursos humanos (RRHH), "
    "nómina, vacaciones y administración corporativa",
    "VERSION": "1.0.0",
    "CONTACT": {
        "name": "Soporte RRHH",
        "email": "soporte@rrhh.interno",
    },
    "LICENSE": {
        "name": "Propietario",
        "url": "https://interno.rrhh",
    },
    # Schema generation
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "COMPONENT_SPLIT_REQUEST": True,
    "COMPONENT_NO_READ_ONLY_REQUIRED": True,
    "SORT_OPERATIONS": False,
    # Request/Response handling
    "ENUM_NAME_OVERRIDES": {
        "ValidationErrorEnum": "drf_spectacular.plumbing.ValidationErrorEnum.choices",
    },
    # Postprocessing
    "POSTPROCESSING_HOOKS": [
        "drf_spectacular.hooks.postprocess_schema_enums",
    ],
    # API Tags
    "TAGS": [
        {
            "name": "Autenticación",
            "description": "Endpoints de login, logout y refresh de tokens JWT",
        },
        {
            "name": "Empleados",
            "description": "CRUD de empleados y datos personales",
        },
        {
            "name": "Áreas",
            "description": "Gestión de áreas organizacionales",
        },
        {
            "name": "Usuarios",
            "description": "Gestión de usuarios del sistema",
        },
        {
            "name": "Roles y Permisos",
            "description": "Control de acceso basado en roles (RBAC)",
        },
        {
            "name": "Vacaciones",
            "description": "Solicitudes y gestión de vacaciones",
        },
        {
            "name": "Contratos",
            "description": "Gestión de contratos laborales",
        },
        {
            "name": "Nómina",
            "description": "Procesamiento de nómina y pagos",
        },
    ],
    # Method overrides
    "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAuthenticated"],
    # Deep linking and examples
    "SERVE_INCLUDE_SCHEMA": False,
    "X_IGNORE_SETTINGS_ERRORS": False,
    # Regex patterns to ignore
    "IGNORE_PATTERNS": [
        r"^/admin/",
        r"^/media/",
        r"^/static/",
    ],
    # Explicit schema generation for better control
    "SCHEMA_COERCE_DECIMAL_STRINGS": True,
    "SCHEMA_COERCE_PATH_PK": True,
}


def postprocess_schema_hook(result, generator, request, public):
    """
    Postprocessing hook para mejorar el esquema generado.

    - Agrega información de autenticación
    - Mejora descripciones de endpoints
    - Configura ejemplos de request/response
    """
    if result.get("info"):
        result["info"]["x-logo"] = {
            "url": "https://interno.rrhh/logo.png",
            "altText": "VYNTIA",
        }

    # Mejorar descripciones de paths
    if result.get("paths"):
        for path, path_item in result["paths"].items():
            for method, operation in path_item.items():
                if method in ["get", "post", "put", "patch", "delete"]:
                    # Agregar ejemplos comunes de parámetros
                    if method == "get" and operation.get("description"):
                        if "{id}" in path:
                            operation[
                                "description"
                            ] += " - Obtiene un registro específico por ID."
                        elif "list" in path:
                            operation[
                                "description"
                            ] += " - Lista con paginación, filtros y búsqueda."

    return result
