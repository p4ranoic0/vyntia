"""Configuración de producción para VYNTIA."""

import os

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'bd_vyntia'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': os.environ.get('DB_SSLMODE', 'require'),
            'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT', '20')),
            'options': '-c default_transaction_isolation=read committed',
        },
        'CONN_MAX_AGE': DATABASE_CONNECTION_POOLING['CONN_MAX_AGE'],
        'CONN_HEALTH_CHECKS': True,
        'TEST': {
            'NAME': os.environ.get('DB_TEST_NAME', 'test_bd_vyntia_prod'),
        },
    },
    # Read replica for read-only operations (optional)
    'read_replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_READ_NAME', os.environ.get('DB_NAME', 'bd_vyntia')),
        'USER': os.environ.get('DB_READ_USER', os.environ.get('DB_USER', 'postgres')),
        'PASSWORD': os.environ.get('DB_READ_PASSWORD', os.environ.get('DB_PASSWORD')),
        'HOST': os.environ.get('DB_READ_HOST', os.environ.get('DB_HOST', 'localhost')),
        'PORT': os.environ.get('DB_READ_PORT', os.environ.get('DB_PORT', '5432')),
        'OPTIONS': {
            'sslmode': os.environ.get('DB_READ_SSLMODE', os.environ.get('DB_SSLMODE', 'require')),
            'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT', '20')),
            'options': '-c default_transaction_isolation=read committed',
        },
        'CONN_MAX_AGE': DATABASE_CONNECTION_POOLING['CONN_MAX_AGE'],
        'CONN_HEALTH_CHECKS': True,
    }
}

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_HSTS_SECONDS = 31536000  # 1 año
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# CORS settings for production
_cors_origins = [o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',')]
CORS_ALLOWED_ORIGINS = [o for o in _cors_origins if o]

# Static files configuration for production
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files configuration for production
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# S3 Storage configuration for production (optional - uses local storage if not configured)
AWS_STORAGE_BUCKET_NAME = os.environ.get('AWS_STORAGE_BUCKET_NAME')
if AWS_STORAGE_BUCKET_NAME:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')
    AWS_S3_FILE_OVERWRITE = False
    AWS_DEFAULT_ACL = 'private'
    AWS_QUERYSTRING_AUTH = True
    AWS_QUERYSTRING_EXPIRE = 3600

# Storage backends (Django 5+ uses STORAGES dict)
if AWS_STORAGE_BUCKET_NAME:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3boto3.S3Boto3Storage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }
else:
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        },
    }

# Email configuration for production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')

# Frontend URL for production
FRONTEND_URL = os.environ.get('FRONTEND_URL')

# Cache configuration for production (Redis recommended)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('CACHE_REDIS_URL', os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0')),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'intranet_rrhh',
        'TIMEOUT': 300,
    }
}

# Session configuration for production
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Logging configuration for production
LOGGING.update({
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(BASE_DIR, 'logs', 'django_error.log'),
            'maxBytes': 1024*1024*15,  # 15MB
            'backupCount': 10,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'app_rrhh': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
})

# Performance optimizations
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB

# JWT configuration for production
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),  # Más restrictivo en producción
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
})

# Admin configuration
ADMIN_URL = os.environ.get('ADMIN_URL', 'admin/')