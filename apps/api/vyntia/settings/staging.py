"""Configuración de staging para VYNTIA."""

import os

from .production import *

# Staging puede tener debug activado para pruebas
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Hosts permitidos para staging
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'staging.vyntia.com').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'bd_vyntia_staging'),
        'USER': os.environ.get('DB_USER', 'postgres'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'sslmode': os.environ.get('DB_SSLMODE', 'prefer'),
            'connect_timeout': int(os.environ.get('DB_CONNECT_TIMEOUT', '15')),
            'options': '-c default_transaction_isolation=read committed',
        },
        'CONN_MAX_AGE': DATABASE_CONNECTION_POOLING['CONN_MAX_AGE'],
        'CONN_HEALTH_CHECKS': True,
        'TEST': {
            'NAME': os.environ.get('DB_TEST_NAME', 'test_bd_vyntia_staging'),
        },
    }
}

# CORS más permisivo para staging
CORS_ALLOWED_ORIGINS = [
    'https://staging.vyntia.com',
    'http://localhost:3000',
    'http://localhost:5173',
] + [o.strip() for o in os.environ.get('CORS_ALLOWED_ORIGINS', '').split(',') if o.strip()]

# Email backend para staging (puede usar console para pruebas)
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')

# Logging más detallado para staging
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['file'],
    'level': 'INFO',
    'propagate': False,
}

# JWT más permisivo para staging
SIMPLE_JWT.update({
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=2),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
})

# Security settings menos restrictivos para staging
SECURE_SSL_REDIRECT = os.environ.get('SECURE_SSL_REDIRECT', 'False').lower() == 'true'
SESSION_COOKIE_SECURE = os.environ.get('SESSION_COOKIE_SECURE', 'False').lower() == 'true'
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'