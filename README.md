# Intranet RRHH

Sistema de gestión de recursos humanos para uso interno corporativo. Monorepo con backend Django REST API y frontend React + TypeScript.

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.11%2B-blue?style=flat&logo=python)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-4.2-green?style=flat&logo=django)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react)](https://reactjs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.5-3178C6?style=flat&logo=typescript)](https://www.typescriptlang.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql)](https://www.mysql.com/)

</div>

---

## Funcionalidades

| Módulo | Descripción |
|--------|-------------|
| **Empleados** | Datos personales, familiares, académicos y laborales |
| **Estructura organizacional** | Áreas, cargos, ubicaciones |
| **Control de acceso (RBAC)** | Roles, permisos, autenticación JWT |
| **Vacaciones** | Solicitudes, aprobaciones e historial |
| **Contratos y adendas** | Gestión documental con generación de PDFs |
| **Nómina / Remuneraciones** | Planilla mensual, AFP, ingresos y descuentos |
| **Onboarding** | Seguimiento del proceso de incorporación |
| **Reportes** | Exportación y análisis de datos de RRHH |

---

## Estructura del repositorio

```
INTRANET/
├── back/           # Backend — Django 4.2 + DRF
├── front/          # Frontend — React 18 + Vite + TypeScript
├── bd/             # Scripts SQL (esquema, datos demo, funciones)
├── docs/           # Documentación técnica
├── design-system/  # Tokens de diseño y guía de estilos
└── .venv/          # Entorno virtual Python (raíz del repo)
```

---

## Requisitos previos

| Herramienta | Versión mínima |
|-------------|----------------|
| Python | 3.11+ |
| Node.js | 18+ |
| MySQL | 8.0+ |
| npm | 9+ |

---

## Instalación

### 1. Clonar el repositorio

```bash
git clone https://github.com/p4ranoic0/INTRANET.git
cd INTRANET
```

### 2. Backend (Django)

```powershell
# Crear entorno virtual en la raíz del repo
python -m venv .venv
.\.venv\Scripts\Activate.ps1       # Windows PowerShell
# source .venv/bin/activate         # Linux / macOS

# Instalar dependencias
pip install -r back/requirements.txt

# Configurar variables de entorno
Copy-Item back\.env.example back\.env
# Editar back/.env con tus credenciales MySQL
```

Ajustar en `back/.env`:

```env
DB_ENGINE=django.db.backends.mysql
DB_NAME=bd_rrhh_intranet
DB_USER=tu_usuario_mysql
DB_PASSWORD=tu_password_mysql
DB_HOST=localhost
DB_PORT=3306
SECRET_KEY=genera-una-clave-segura
```

> Para generar `SECRET_KEY`:
> ```bash
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

```powershell
# Crear la base de datos en MySQL
# (Ejecutar el script bd/create bd_rrhh_intranet.sql desde MySQL Workbench o CLI)

# Aplicar migraciones
cd back
..\\.venv\Scripts\python.exe manage.py migrate --settings=config.settings.development

# (Opcional) Cargar datos de demostración
..\\.venv\Scripts\python.exe manage.py shell --settings=config.settings.development
# Ver bd/datos-demo-django.sql para datos de prueba

# Iniciar servidor
..\\.venv\Scripts\python.exe manage.py runserver 8000 --settings=config.settings.development
```

API disponible en: http://localhost:8000/api/v1/  
Documentación Swagger: http://localhost:8000/api/docs/

### 3. Frontend (React)

```powershell
cd front
npm install
npm run dev
```

App disponible en: http://localhost:5173

> El proxy de Vite redirige automáticamente `/api/*` y `/media/*` al backend en `localhost:8000`.

---

## Ejecución rápida (ambos servicios)

Desde VS Code, la tarea **"Iniciar Proyecto Completo"** (`.vscode/tasks.json`) lanza backend y frontend en paralelo al abrir el workspace.

O manualmente en dos terminales:

```powershell
# Terminal 1 — Backend
cd back
..\.venv\Scripts\python.exe manage.py runserver 8000 --settings=config.settings.development

# Terminal 2 — Frontend
cd front
npm run dev
```

---

## Scripts útiles

### Backend

```powershell
# Ejecutar todos los tests
cd back
make test

# Tests con cobertura
make test-coverage

# Crear superusuario
..\.venv\Scripts\python.exe manage.py createsuperuser --settings=config.settings.development

# Generar/aplicar migraciones
..\.venv\Scripts\python.exe manage.py makemigrations app_rrhh --settings=config.settings.development
..\.venv\Scripts\python.exe manage.py migrate --settings=config.settings.development
```

### Frontend

```powershell
npm run build          # Build de producción
npm run lint           # ESLint
npm run test           # Tests unitarios (Vitest)
npm run test:coverage  # Cobertura
npm run playwright     # Tests E2E
```

---

## Variables de entorno

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| `DEBUG` | Modo debug Django | `True` |
| `SECRET_KEY` | Clave secreta Django | — (obligatorio) |
| `DB_NAME` | Nombre de la base de datos | `bd_rrhh_intranet` |
| `DB_USER` | Usuario MySQL | `postgres` |
| `DB_PASSWORD` | Contraseña MySQL | — (obligatorio) |
| `DB_HOST` | Host MySQL | `localhost` |
| `DB_PORT` | Puerto MySQL | `3306` |
| `FRONTEND_URL` | URL del frontend (CORS) | `http://localhost:5173` |
| `JWT_ACCESS_TOKEN_LIFETIME` | Duración token acceso (segundos) | `3600` |

Ver `back/.env.example` para la lista completa.

---

## API — Endpoints principales

```
POST   /api/v1/auth/login/              Iniciar sesión
POST   /api/v1/auth/refresh/            Refrescar token JWT
POST   /api/v1/auth/logout/             Cerrar sesión
GET    /api/v1/auth/profile/            Perfil del usuario

GET    /api/v1/rrhh/empleados/          Lista de empleados
POST   /api/v1/rrhh/empleados/          Crear empleado
GET    /api/v1/rrhh/empleados/{id}/     Detalle de empleado
PUT    /api/v1/rrhh/empleados/{id}/     Actualizar empleado

GET    /api/v1/rrhh/areas/              Áreas organizacionales
GET    /api/v1/rrhh/contratos/          Contratos y adendas
GET    /api/v1/rrhh/remuneraciones/     Planilla de remuneraciones
GET    /api/v1/vacaciones/              Gestión de vacaciones
```

Documentación interactiva completa: http://localhost:8000/api/docs/

---

## Documentación adicional

| Documento | Descripción |
|-----------|-------------|
| [back/SETUP.md](back/SETUP.md) | Configuración detallada del backend |
| [back/DEPLOYMENT.md](back/DEPLOYMENT.md) | Despliegue a producción |
| [front/FRONTEND_ARCHITECTURE.md](front/FRONTEND_ARCHITECTURE.md) | Arquitectura del frontend |
| [docs/](docs/) | Documentación técnica general |
| [bd/](bd/) | Scripts SQL del esquema y datos |

---

## Licencia

Proyecto de uso interno. Ver [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) y [CONTRIBUTING.md](CONTRIBUTING.md).
