# Intranet RRHH - Backend API

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green?style=flat&logo=django)](https://www.djangoproject.com/)
[![DRF](https://img.shields.io/badge/DRF-3.14-red?style=flat)](https://www.django-rest-framework.org/)

Sistema integrado de gestión de RRHH, nómina, vacaciones y administración corporativa.

[📖 Docs](#documentación) • [🚀 Quick Start](#quick-start) • [📡 API](#endpoints) • [🧪 Tests](#testing) • [🐳 Docker](#docker)

</div>

---

## 📋 Descripción

Backend REST API para la **Intranet Corporativa** - Sistema de gestión integrado de recursos humanos con:

- 👥 **Gestión de Empleados** - Datos personales, familiares, académicos, laborales
- 🏢 **Estructura Organizacional** - Áreas, departamentos, cargos, ubicaciones
- 🔐 **Control de Acceso (RBAC)** - Roles, permisos, autenticación JWT
- 📅 **Vacaciones** - Solicitudes, aprobaciones, historial
- 📜 **Contratos** - Gestión de contratos y adendas
- 💰 **Nómina** - Procesamiento de plazas y pagos
- 📊 **Reportes Avanzados** - Análisis de RRHH

## 🏗️ Tech Stack

| Componente | Tecnología | Versión |
|-----------|-----------|---------|
| **Framework** | Django | 4.2 LTS |
| **API** | Django REST Framework | 3.16+ |
| **DB** | PostgreSQL | 15+ |
| **Cache** | Redis | 7+ |
| **Auth** | JWT (Simple JWT) | 5.3+ |
| **Async** | Celery | 5.3+ |
| **Schema** | drf-spectacular | 0.29+ |

## 🚀 Quick Start

### Requisitos
- Python 3.11+
- PostgreSQL 15+
- Redis (opcional)

### Instalación (5 minutos)

```bash
# 1. Clonar
git clone https://github.com/tu-org/intranet-rrhh-backend.git
cd intranet-rrhh-backend

# 2. Entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate      # Linux

# 3. Dependencias
pip install -r requirements.txt

# 4. Configurar .env
cp .env.example .env
# Editar .env con credenciales PostgreSQL

# 5. Migraciones
python manage.py migrate --settings=config.settings.development

# 6. Datos demo (opcional)
python scripts/load_demo_data.py

# 7. Servidor
python manage.py runserver 8000
```

**API en:** http://localhost:8000/api/v1/

## 📖 Documentación

| Documento | Descripción |
|-----------|------------|
| [SETUP.md](./SETUP.md) | Instalación local y troubleshooting |
| [DEPLOYMENT.md](./DEPLOYMENT.md) | Deployment a Railway/Heroku/AWS |
| [/api/docs/](http://localhost:8000/api/docs/) | Swagger UI (interactivo) |
| [/api/redoc/](http://localhost:8000/api/redoc/) | ReDoc (referencia) |

## 📡 Endpoints

### Autenticación
```
POST   /api/v1/auth/login/         Iniciar sesión
POST   /api/v1/auth/refresh/       Refrescar token
POST   /api/v1/auth/logout/        Cerrar sesión
GET    /api/v1/auth/profile/       Perfil usuario
```

### Empleados
```
GET    /api/v1/rrhh/empleados/     Lista
POST   /api/v1/rrhh/empleados/     Crear
GET    /api/v1/rrhh/empleados/{id}/ Detalle
PUT    /api/v1/rrhh/empleados/{id}/ Actualizar
DELETE /api/v1/rrhh/empleados/{id}/ Eliminar
```

### Otros
```
GET    /api/v1/rrhh/areas/         Áreas
GET    /api/v1/rrhh/usuarios/      Usuarios
GET    /api/v1/rrhh/roles/         Roles
GET    /api/v1/rrhh/permisos/      Permisos
```

→ [Ver todos los endpoints en /api/docs/](http://localhost:8000/api/docs/)

## 🏗️ Estructura del Proyecto

```
back/
├── config/                  # Configuración Django
│   ├── settings/
│   │   ├── base.py
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   └── wsgi.py
├── app_rrhh/                # App principal
│   ├── models/
│   │   ├── empleado.py
│   │   ├── roles.py
│   │   └── ...
│   ├── views.py             # ViewSets (optimizados)
│   ├── serializers.py       # Serializers base
│   ├── serializers_optimized.py  # List/Detail variants
│   ├── services.py          # Lógica negocio
│   └── migrations/
├── api/v1/                  # API REST v1
│   ├── auth/
│   ├── rrhh/
│   └── urls.py
├── core/                    # Funcionalidades core
│   ├── permissions.py       # RBAC
│   ├── exceptions.py
│   ├── responses.py
│   ├── pagination.py
│   └── ...
├── scripts/                 # Scripts utilidad
│   ├── load_demo_data.py
│   └── ...
├── tests/                   # Tests integración
├── templates/               # Templates emails
├── requirements.txt
├── pytest.ini
├── .env.example
└── Dockerfile
```

## 🧪 Testing

```bash
# Todos los tests
pytest

# Específicos
pytest tests/test_auth_api.py -v

# Con cobertura
pytest --cov=app_rrhh --cov-report=html

# Linting
flake8 app_rrhh/
black --check .
```

**Requisito:** 80%+ cobertura antes de PR

## 📊 Performance

✅ **Optimizaciones implementadas:**

- Query optimization: `select_related()` + `prefetch_related()`
  - Empleado: ~90% ↓ queries
  - Usuario: ~70% ↓ queries
  
- Serializer variants (List vs Detail)
  - List: 12 campos (essentials)
  - Detail: 60+ campos (completo)
  
- Pagination estándar (20 items/página)
- Redis caching para sessions
- Índices en BD para queries frecuentes

## 🐳 Docker

```bash
# Build
docker build -t intranet-rrhh-backend .

# Run
docker run -p 8000:8000 \
  -e DB_HOST=host.docker.internal \
  -e DB_NAME=bd_rrhh_intranet \
  intranet-rrhh-backend

# Full stack
docker-compose up
```

## 🔧 Desarrollo

### Nueva Feature

```bash
git checkout -b feature/descripcion
# Make changes
pytest
black . && flake8 .
git push origin feature/descripcion
# Create PR
```

### BD Migrations

```bash
python manage.py makemigrations app_rrhh
python manage.py migrate
python manage.py showmigrations
```

### Shell Interactivo

```bash
python manage.py shell
# >>> from app_rrhh.models import Empleado
# >>> Empleado.objects.all()
```

## 🔐 Seguridad

- ✅ HTTPS/SSL en producción
- ✅ CSRF + XSS protection
- ✅ JWT token expiration
- ✅ Rate limiting
- ✅ SQL injection prevention (ORM)
- ✅ CORS configurado
- ✅ Secrets en .env

⚠️ [Pre-deployment checklist](./DEPLOYMENT.md)

## 📝 Logging

```python
import logging
logger = logging.getLogger(__name__)

logger.info("Info")
logger.warning("Warning")
logger.error("Error")
```

Logs en:
- `logs/django.log` - General
- `logs/api.log` - API requests
- `logs/security.log` - Security events
- `logs/audit.log` - Cambios datos

## 🤝 Contribución

1. Fork
2. Branch: `git checkout -b feature/xyz`
3. Commit: `git commit -m 'feat: ...'`
4. Push: `git push origin feature/xyz`
5. Pull Request

## 📞 Soporte

- 📧 soporte@rrhh.interno
- 🐛 [GitHub Issues](https://github.com/tu-org/intranet-rrhh/issues)

## 📄 Licencia

Propietario © 2026

---

**Última actualización:** 7 Marzo 2026

Hecho con ❤️ por el equipo RRHH
