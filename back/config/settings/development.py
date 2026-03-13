"""Configuración de desarrollo para project_intranet."""

import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Override logging for more detailed error information
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {process:d} {thread:d} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "logs/django.log",
            "formatter": "verbose",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
    "loggers": {
        "django": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
        "django.request": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# Database (PostgreSQL)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "bd_rrhh_intranet"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", "postgres"),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
        "OPTIONS": {
            "sslmode": os.environ.get("DB_SSLMODE", "prefer"),
            "connect_timeout": int(os.environ.get("DB_CONNECT_TIMEOUT", "10")),
            "client_encoding": "UTF8",
        },
        "CONN_MAX_AGE": DATABASE_CONNECTION_POOLING["CONN_MAX_AGE"],
        "CONN_HEALTH_CHECKS": True,
        "ATOMIC_REQUESTS": True,
        "TEST": {
            "NAME": os.environ.get("DB_TEST_NAME", "test_bd_rrhh_intranet"),
        },
    }
}

# CORS settings for development
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
]

# Permitir origen null para archivos HTML locales en desarrollo
CORS_ALLOW_ALL_ORIGINS = True  # Solo para desarrollo

# Development-specific apps
INSTALLED_APPS += [
    "django_extensions",  # Para shell_plus y otras utilidades
]

# Email backend for development
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Cache configuration - Local memory for development (no Redis required)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "default-cache",
        "TIMEOUT": 300,  # 5 minutos por defecto
    },
    "sessions": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "session-cache",
        "TIMEOUT": 86400,  # 24 horas
    },
    "database": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "cache_table",
        "TIMEOUT": 300,
        "OPTIONS": {
            "MAX_ENTRIES": 1000,
        },
    },
}

# Logging más detallado para desarrollo
LOGGING["loggers"]["django.db.backends"] = {
    "handlers": ["console"],
    "level": "DEBUG",
    "propagate": False,
}

# Django Debug Toolbar (opcional)
try:
    import debug_toolbar

    INSTALLED_APPS += ["debug_toolbar"]
    MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
except ImportError:
    pass

# Configuración específica para desarrollo
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_SSL_REDIRECT = False

# JWT más permisivo para desarrollo
SIMPLE_JWT.update(
    {
        "ACCESS_TOKEN_LIFETIME": timedelta(hours=8),  # Más tiempo para desarrollo
        "REFRESH_TOKEN_LIFETIME": timedelta(days=30),
    }
)
