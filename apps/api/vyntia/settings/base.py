"""Configuración base de Django para VYNTIA."""

import os
from datetime import timedelta
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get(
    "SECRET_KEY", "django-insecure-$w9cc=bh9ef9cyuqczd%o4p&5bo1f4zorl@-^jq0kw#0gx8tak"
)

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    "corsheaders",
    "drf_spectacular",
]

LOCAL_APPS = [
    "apps.core.apps.CoreConfig",
    "apps.identity.apps.IdentityConfig",
    "apps.organization.apps.OrganizationConfig",
    "apps.employees.apps.EmployeesConfig",
    "apps.contracts.apps.ContractsConfig",
    "apps.documents.apps.DocumentsConfig",
    "apps.payroll.apps.PayrollConfig",
    "apps.time_off.apps.TimeOffConfig",
    "apps.onboarding.apps.OnboardingConfig",
    "app_rrhh",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "apps.core.middleware.SecurityHeadersMiddleware",
    "apps.core.middleware.HealthCheckMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "apps.core.middleware.JWTCookieMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.RequestLoggingMiddleware",
    "apps.core.middleware.PerformanceMonitoringMiddleware",
    "apps.core.middleware.AuditMiddleware",
    # "apps.core.middleware.RateLimitingMiddleware",  # Deshabilitado temporalmente (requiere Redis)
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vyntia.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "vyntia.wsgi.application"

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "es-pe"
TIME_ZONE = "America/Lima"
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# Media files
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Frontend URL (used for emails and redirects)
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Database optimization settings
DATABASE_CONNECTION_POOLING = {
    "MAX_CONNS": 20,
    "MIN_CONNS": 5,
    "MAX_LIFETIME": 3600,  # 1 hour
    "CONN_MAX_AGE": 600,  # 10 minutes
}

# Database routing
DATABASE_ROUTERS = ["apps.core.database.DatabaseRouter"]

# Custom User Model
AUTH_USER_MODEL = "identity.User"

# Authentication Backends
AUTHENTICATION_BACKENDS = [
    "apps.identity.auth.CustomAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

# Django REST Framework
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "apps.core.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "apps.core.pagination.StandardResultsSetPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
        "rest_framework.parsers.FormParser",
    ],
    "EXCEPTION_HANDLER": "apps.core.exceptions.custom_exception_handler",
    # Throttling deshabilitado temporalmente (requiere Redis)
    # "DEFAULT_THROTTLE_CLASSES": [
    #     "rest_framework.throttling.AnonRateThrottle",
    #     "rest_framework.throttling.UserRateThrottle",
    # ],
    # "DEFAULT_THROTTLE_RATES": {"anon": "100/hour", "user": "1000/hour"},
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "VERSION_PARAM": "version",
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Simple JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUDIENCE": None,
    "ISSUER": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "JTI_CLAIM": "jti",
}

# CORS settings
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]

CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

# Logging configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "django.log",
            "formatter": "simple",
        },
        "api_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "api.log",
            "formatter": "simple",
        },
        "security_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "security.log",
            "formatter": "simple",
        },
        "performance_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "performance.log",
            "formatter": "simple",
        },
        "audit_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "audit.log",
            "formatter": "simple",
        },
        "business_file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "business.log",
            "formatter": "simple",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "app_rrhh": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": False,
        },
        "api": {
            "handlers": ["api_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "security": {
            "handlers": ["security_file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "performance": {
            "handlers": ["performance_file", "console"],
            "level": "WARNING",
            "propagate": False,
        },
        "audit": {
            "handlers": ["audit_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
        "business": {
            "handlers": ["business_file", "console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

# Cache configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Celery configuration
CELERY_REDIS_URL = os.environ.get(
    "CELERY_REDIS_URL", os.environ.get("REDIS_URL", "redis://127.0.0.1:6379/1")
)
CELERY_BROKER_URL = CELERY_REDIS_URL
CELERY_RESULT_BACKEND = CELERY_REDIS_URL
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60

# Session configuration
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# DRF Spectacular settings
SPECTACULAR_SETTINGS = {
    "TITLE": "VYNTIA API",
    "DESCRIPTION": "API del SaaS modular VYNTIA — gestión de Recursos Humanos para Perú",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SCHEMA_PATH_PREFIX": "/api/v1/",
    "COMPONENT_SPLIT_REQUEST": True,
    "SORT_OPERATIONS": False,
    "ENUM_NAME_OVERRIDES": {
        "ValidationErrorEnum": "drf_spectacular.plumbing.ValidationErrorEnum.choices",
    },
    "POSTPROCESSING_HOOKS": ["drf_spectacular.hooks.postprocess_schema_enums"],
    "TAGS": [
        {
            "name": "Authentication",
            "description": "Endpoints de autenticación y autorización",
        },
        {"name": "Areas", "description": "Gestión de áreas organizacionales"},
        {"name": "Empleados", "description": "Gestión de empleados"},
        {"name": "Usuarios", "description": "Gestión de usuarios del sistema"},
        {"name": "Roles", "description": "Gestión de roles y permisos"},
        {"name": "Boletas", "description": "Gestión de boletas de pago"},
        {
            "name": "Datos Familiares",
            "description": "Información familiar de empleados",
        },
        {
            "name": "Datos Académicos",
            "description": "Información académica de empleados",
        },
        {"name": "Datos Laborales", "description": "Información laboral de empleados"},
        {"name": "Ubicaciones", "description": "Gestión de ubicaciones geográficas"},
    ],
    # Ignorar endpoints problemáticos
    "IGNORE_PATTERNS": [
        r"^/admin/",
        r"^/media/",
        r"^/static/",
        r"^/legacy/",  # Excluir endpoints legacy con serializers obsoletos
    ],
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
