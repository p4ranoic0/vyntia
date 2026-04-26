# Backend Setup

Setup automático del backend de Intranet RRHH para desarrollo local.

## Requisitos Previos

- Python 3.11+ 
- PostgreSQL 15+
- Redis (opcional, para cache/Celery)

## Instalación Rápida

### Windows (PowerShell)

```powershell
# 1. Crear entorno virtual
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar base de datos
cp .env.example .env
# Edita .env con tus credenciales PostgreSQL

# 4. Ejecutar migraciones
python manage.py migrate --settings=config.settings.development

# 5. Cargar datos de demostración
python scripts/load_demo_data.py --settings=config.settings.development

# 6. Crear superusuario (opcional)
python manage.py createsuperuser --settings=config.settings.development

# 7. Ejecutar servidor de desarrollo
python manage.py runserver 8000 --settings=config.settings.development
```

### Linux/macOS

```bash
# 1. Crear entorno virtual
python3 -m venv .venv
source .venv/bin/activate

# 2. Instalar dependencias  
pip install -r requirements.txt

# 3. Configurar base de datos
cp .env.example .env
# Edita .env con tus credenciales PostgreSQL

# 4. Ejecutar migraciones
python manage.py migrate --settings=config.settings.development

# 5. Cargar datos de demostración
python scripts/load_demo_data.py --settings=config.settings.development

# 6. Ejecutar servidor de desarrollo
python manage.py runserver 8000 --settings=config.settings.development
```

## Estructura de Directorios

```
back/
├── config/              # Configuración de Django
│   ├── settings/        # Archivos de settings por ambiente
│   │   ├── base.py      # Configuración común
│   │   ├── development.py
│   │   ├── production.py
│   │   └── testing.py
│   ├── urls.py
│   └── wsgi.py
├── app_rrhh/            # Aplicación principal RRHH
│   ├── models/          # Modelos de datos
│   ├── views.py         # ViewSets para API
│   ├── serializers.py   # Serializers
│   ├── services/        # Lógica de negocio
│   └── tests.py
├── api/                 # API REST v1
│   └── v1/
│       ├── auth/        # Endpoints de autenticación
│       ├── rrhh/        # Endpoints de RRHH
│       └── urls.py
├── core/                # Funcionalidades core  
│   ├── permissions.py   # Permisos personalizados
│   ├── exceptions.py    # Excepciones custom
│   ├── pagination.py    # Paginación
│   └── responses.py     # Respuestas estandarizadas
├── scripts/             # Scripts de utilidad
│   ├── setup/           # Setup del proyecto
│   ├── data/            # Carga de datos
│   └── maintenance/     # Mantenimiento
├── templates/           # Templates para emails
├── tests/               # Tests de integración
├── requirements.txt     # Dependencias Python
├── .env.example         # Variables de entorno ejemplo
└── manage.py
```

## Configuración de Ambiente

Copiar `.env.example` a `.env` y configurar:

```env
# Base de Datos PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=bd_rrhh_intranet
DB_USER=postgres
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432

# Seguridad
SECRET_KEY=tu-clave-secreta-aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Autenticación JWT
JWT_SECRET=tu-secret-jwt
TOKEN_LIFETIME=3600  # 1 hora

# Frontend
FRONTEND_URL=http://localhost:5173

# Redis (opcional)
REDIS_URL=redis://127.0.0.1:6379/0
CELERY_REDIS_URL=redis://127.0.0.1:6379/1
```

## Endpoints Principales

### Autenticación
- `POST /api/v1/auth/login/` - Iniciar sesión
- `POST /api/v1/auth/refresh/` - Refrescar token
- `POST /api/v1/auth/logout/` - Cerrar sesión

### RRHH
- `GET/POST /api/v1/rrhh/empleados/` - Gestión de empleados
- `GET/POST /api/v1/rrhh/areas/` - Gestión de áreas
- `GET/POST /api/v1/rrhh/usuarios/` - Gestión de usuarios
- `GET/POST /api/v1/rrhh/roles/` - Gestión de roles

### Documentación API
- `GET /api/schema/` - Esquema OpenAPI (JSON)
- `GET /api/docs/` - Swagger UI (interactivo)
- `GET /api/redoc/` - ReDoc (documentación)

## Testing

```bash
# Ejecutar todos los tests
python manage.py test --settings=config.settings.testing

# Tests específicos
pytest tests/ -v

# Con cobertura
pytest --cov=app_rrhh tests/
```

## Comandos Útiles

```bash
# Database
python manage.py makemigrations
python manage.py migrate
python manage.py dbshell

# Admin
python manage.py createsuperuser
python manage.py changepassword username

# Datos
python scripts/load_demo_data.py
python scripts/check_admin_empleado.py

# Desarrollo
python manage.py shell
python manage.py runserver 0.0.0.0:8000
python manage.py harvest  # tests django-harvest
```

## Troubleshooting

### Error: PostgreSQL no conecta
```bash
# Verifica que PostgreSQL esté corriendo
psql -U postgres -h localhost

# Verifica credenciales en .env
# Crea la BD si no existe:
createdb bd_rrhh_intranet
```

### Error: ModuleNotFoundError
```bash
# Reinstala dependencias
pip install --upgrade -r requirements.txt

# Limpia módulos en caché
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete
```

### Error de migraciones
```bash
# Ver estado de migraciones
python manage.py showmigrations

# Retroceder migraciones
python manage.py migrate app_rrhh 0007

# Crear migraciones
python manage.py makemigrations app_rrhh
```

## Deployment

Para deployar a producción, consulta [DEPLOYMENT.md](./DEPLOYMENT.md)

## Contribución

1. Crear rama: `git checkout -b feature/nombre-feature`
2. Commit: `git commit -am 'Agrega feature'`
3. Push: `git push origin feature/nombre-feature`
4. Pull Request

## Licencia

Propietario - Corporativo 2026
