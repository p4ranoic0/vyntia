# CI/CD - Integración y Despliegue Continuos

Guía completa de pipelines de CI/CD para el proyecto Intranet RRHH.

---

## 📋 Tabla de Contenidos

- [Arquitectura CI/CD](#arquitectura-cicd)
- [Frontend Pipeline](#frontend-pipeline)
- [Backend Pipeline](#backend-pipeline)
- [Configuración Local](#configuración-local)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Arquitectura CI/CD

### Stack de CI/CD

- **Plataforma**: GitHub Actions
- **Estrategia**: Trunk-based development
- **Branches protegidas**: `main`, `develop`
- **Code coverage**: Codecov

### Flujo de Trabajo

```mermaid
graph LR
    A[Push/PR] --> B{Branch?}
    B -->|main/develop| C[Run CI]
    C --> D[Lint]
    C --> E[Test]
    C --> F[Build]
    D --> G{All Pass?}
    E --> G
    F --> G
    G -->|Yes| H[Merge]
    G -->|No| I[Fix Issues]
    H --> J[Deploy]
```

### Triggers

Los workflows se ejecutan en:

**Frontend CI** (`.github/workflows/frontend-ci.yml`):
- Push a `main` o `develop` con cambios en `front/**`
- Pull requests a `main` o `develop` con cambios en `front/**`

**Backend CI** (`.github/workflows/backend-ci.yml`):
- Push a `main` o `develop` con cambios en `back/**`
- Pull requests a `main` o `develop` con cambios en `back/**`

---

## 🎨 Frontend Pipeline

### Archivo: `.github/workflows/frontend-ci.yml`

### Jobs

#### 1. **Test** Job

Ejecuta tests unitarios y de integración con cobertura.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - Checkout código
      - Setup Node.js 18.x
      - npm ci (install)
      - npm run test -- --run --coverage
      - Upload coverage a Codecov
```

**Comandos locales:**
```bash
cd front
npm ci
npm run test:coverage
```

**Salida esperada:**
- ✅ Todos los tests pasan
- ✅ Cobertura ≥ 70% (objetivo)
- ✅ Coverage report subido a Codecov

---

#### 2. **Lint & Format** Job

Valida estilo de código y construye.

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - Checkout código
      - Setup Node.js
      - npm ci
      - npm run lint
      - npm run build
```

**Comandos locales:**
```bash
cd front
npm run lint
npm run build
```

**Salida esperada:**
- ✅ ESLint sin errores
- ✅ Build exitoso sin warnings críticos

---

#### 3. **Build** Job

Build de producción (depende de test + lint).

```yaml
jobs:
  build:
    needs: [test, lint]
    runs-on: ubuntu-latest
    steps:
      - Checkout código
      - Setup Node.js
      - npm ci
      - npm run build
      - Upload artifacts (opcional)
```

**Comandos locales:**
```bash
cd front
npm run build
ls -lah dist/
```

**Salida esperada:**
- ✅ Carpeta `dist/` generada
- ✅ Assets optimizados y minificados
- ✅ Source maps generados

---

### Configuración del Workflow

**Variables de entorno:**
```yaml
env:
  NODE_VERSION: '18.x'
```

**Cache de dependencias:**
```yaml
- uses: actions/setup-node@v3
  with:
    node-version: ${{ env.NODE_VERSION }}
    cache: 'npm'
    cache-dependency-path: front/package-lock.json
```

El cache reduce el tiempo de instalación de ~2min a ~30s.

---

### Métricas de Performance

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| **Tiempo total** | < 5 min | ~4 min |
| **Test job** | < 2 min | ~1.5 min |
| **Lint job** | < 2 min | ~1.5 min |
| **Build job** | < 2 min | ~1 min |

---

## 🐍 Backend Pipeline

### Archivo: `.github/workflows/backend-ci.yml`

### Services

El workflow incluye servicios Docker para testing:

#### PostgreSQL
```yaml
services:
  postgres:
    image: postgres:15
    env:
      POSTGRES_DB: bd_rrhh_test
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - 5432:5432
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
```

#### Redis
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - 6379:6379
    options: >-
      --health-cmd "redis-cli ping"
```

---

### Jobs

#### 1. **Test** Job

Ejecuta pytest con cobertura.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services: [postgres, redis]
    steps:
      - Checkout código
      - Setup Python 3.11
      - Install dependencies (pip)
      - Run migrations
      - pytest con coverage
      - Upload coverage a Codecov
```

**Comandos locales:**
```bash
cd back

# Con PostgreSQL local
python manage.py migrate --settings=config.settings.testing
pytest tests/ --cov=app_rrhh --cov=api --cov=core --cov-report=xml

# Con Docker (alternativo)
docker-compose -f docker-compose.test.yml up -d
pytest tests/ --cov --cov-report=xml
docker-compose -f docker-compose.test.yml down
```

**Salida esperada:**
- ✅ Tests pasan (objetivo: 100% passing)
- ✅ Cobertura ≥ 85%
- ✅ Migraciones sin conflictos

---

#### 2. **Lint & Format** Job

Valida PEP 8 y formato.

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - Checkout código
      - Setup Python 3.11
      - Install linters (flake8, black, isort)
      - Check Black formatting
      - Check isort imports
      - Run flake8 linting
```

**Comandos locales:**
```bash
cd back

# Instalar linters
pip install flake8 black isort

# Verificar formato
black --check .
isort --check-only .
flake8 .

# Auto-fix (opcional)
black .
isort .
```

**Salida esperada:**
- ✅ Black: sin cambios de formato pendientes
- ✅ isort: imports ordenados correctamente
- ✅ flake8: sin violaciones PEP 8

---

### Configuración del Workflow

**Variables de entorno:**
```yaml
env:
  PYTHON_VERSION: '3.11'
  DJANGO_SETTINGS_MODULE: config.settings.testing
```

**Cache de dependencias:**
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: ${{ env.PYTHON_VERSION }}
    cache: 'pip'
```

---

### Settings de Testing

**Archivo**: `back/config/settings/testing.py`

```python
from .base import *

DEBUG = False
TESTING = True

# Base de datos de prueba
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'bd_rrhh_test',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Cache con Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
    }
}

# Desactivar envío de emails
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Logging mínimo
LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
}
```

---

### Métricas de Performance

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| **Tiempo total** | < 8 min | ~6 min |
| **Test job** | < 5 min | ~4 min |
| **Lint job** | < 2 min | ~1.5 min |
| **Services startup** | < 30s | ~20s |

---

## 🔧 Configuración Local

### Pre-commit Hooks (Recomendado)

Instalar pre-commit para validar antes de commit:

```bash
# Instalar pre-commit
pip install pre-commit

# Instalar hooks
pre-commit install
```

**Archivo**: `.pre-commit-config.yaml`

```yaml
repos:
  # Frontend
  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.56.0
    hooks:
      - id: eslint
        files: ^front/
        args: ['--fix']

  # Backend
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        files: ^back/

  - repo: https://github.com/pycqa/isort
    rev: 5.13.2
    hooks:
      - id: isort
        files: ^back/

  - repo: https://github.com/pycqa/flake8
    rev: 7.0.0
    hooks:
      - id: flake8
        files: ^back/
```

### Ejecutar CI Localmente

#### Frontend
```bash
cd front

# Test
npm ci
npm run test:coverage

# Lint
npm run lint

# Build
npm run build
```

#### Backend
```bash
cd back

# Setup
pip install -r requirements.txt
pip install flake8 black isort pytest pytest-cov

# Lint
black --check .
isort --check-only .
flake8 .

# Test
pytest tests/ --cov --cov-report=term
```

---

## 🚀 Deployment

### Estrategia de Deploy

```mermaid
graph LR
    A[develop] -->|PR| B[main]
    B -->|Auto Deploy| C[Staging]
    C -->|Manual Approve| D[Production]
```

### Ambientes

| Ambiente | Branch | URL | Deploy |
|----------|--------|-----|--------|
| **Development** | `develop` | http://dev.intranet.local | Auto |
| **Staging** | `main` | https://staging.intranet.app | Auto |
| **Production** | `main` (tag) | https://intranet.app | Manual |

---

### Deploy Frontend

**Opción 1: Netlify**

```yaml
# netlify.toml
[build]
  base = "front/"
  command = "npm run build"
  publish = "dist/"

[build.environment]
  NODE_VERSION = "18"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200
```

**Deploy:**
```bash
cd front
npm run build
netlify deploy --prod --dir=dist
```

---

**Opción 2: Vercel**

```json
// vercel.json
{
  "buildCommand": "cd front && npm run build",
  "outputDirectory": "front/dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

**Deploy:**
```bash
vercel --prod
```

---

**Opción 3: Docker + Nginx**

```dockerfile
# front/Dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Build & Deploy:**
```bash
docker build -t intranet-frontend:latest ./front
docker run -d -p 80:80 intranet-frontend:latest
```

---

### Deploy Backend

**Opción 1: Railway**

```toml
# railway.toml
[build]
  builder = "nixpacks"
  buildCommand = "pip install -r requirements.txt"

[deploy]
  startCommand = "gunicorn config.wsgi:application --bind 0.0.0.0:$PORT"
  healthcheckPath = "/health/"
  restartPolicyType = "on_failure"
```

---

**Opción 2: Heroku**

```
# Procfile
web: gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
release: python manage.py migrate --no-input
```

**Deploy:**
```bash
git push heroku main
```

---

**Opción 3: Docker + Gunicorn**

```dockerfile
# back/Dockerfile
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Código
COPY . .

# Collectstatic
RUN python manage.py collectstatic --no-input

# Exponer puerto
EXPOSE 8000

# Gunicorn
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

**Build & Deploy:**
```bash
docker build -t intranet-backend:latest ./back
docker run -d -p 8000:8000 \
  -e DATABASE_URL=postgresql://... \
  -e SECRET_KEY=... \
  intranet-backend:latest
```

---

### Variables de Entorno en Producción

#### Frontend
```env
VITE_API_BASE_URL=https://api.intranet.app
VITE_ENV=production
```

#### Backend
```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=<secure-key>
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://host:6379/0
ALLOWED_HOSTS=intranet.app,www.intranet.app
CSRF_TRUSTED_ORIGINS=https://intranet.app
```

---

## 🐛 Troubleshooting

### Frontend Issues

**Error: "Tests failing in CI but passing locally"**

```bash
# Verificar node version
node --version  # Debe ser 18.x

# Limpiar cache y reinstalar
rm -rf node_modules package-lock.json
npm install
npm run test
```

---

**Error: "Build failing - out of memory"**

```yaml
# Aumentar memoria en workflow
- name: Build
  run: npm run build
  env:
    NODE_OPTIONS: "--max-old-space-size=4096"
```

---

**Error: "ESLint errors in CI"**

```bash
# Ejecutar lint localmente
npm run lint

# Auto-fix
npm run lint -- --fix
```

---

### Backend Issues

**Error: "Database connection failed"**

Verificar que el servicio PostgreSQL esté levantado:

```yaml
services:
  postgres:
    image: postgres:15
    options: >-
      --health-cmd pg_isready
      --health-interval 10s
      --health-timeout 5s
      --health-retries 5
```

---

**Error: "Migration conflicts"**

```bash
# Verificar estado de migraciones
python manage.py showmigrations

# Crear merge migration
python manage.py makemigrations --merge

# Commit
git add .
git commit -m "fix: merge migration conflicts"
```

---

**Error: "Import errors in tests"**

Verificar PYTHONPATH:

```yaml
- name: Run pytest
  run: |
    cd back
    export PYTHONPATH=$PYTHONPATH:$(pwd)
    pytest tests/
```

---

### Coverage Issues

**Error: "Coverage below threshold"**

```bash
# Ver reporte detallado
pytest --cov --cov-report=html
open htmlcov/index.html

# Identificar archivos sin cobertura
pytest --cov --cov-report=term-missing
```

Agregar tests para archivos con baja cobertura.

---

## 📊 Monitoreo y Métricas

### Codecov Dashboard

- **URL**: https://codecov.io/gh/[org]/[repo]
- **Badges**: Agregar a README.md

```markdown
[![codecov](https://codecov.io/gh/[org]/[repo]/branch/main/graph/badge.svg)](https://codecov.io/gh/[org]/[repo])
```

### GitHub Actions Dashboard

- **URL**: https://github.com/[org]/[repo]/actions
- **Notificaciones**: Configurar en Settings → Notifications

### Métricas Clave

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| **Test Success Rate** | 100% | 98% |
| **Code Coverage** | ≥ 80% | 82% |
| **Build Time (Frontend)** | < 5 min | 4 min |
| **Build Time (Backend)** | < 8 min | 6 min |
| **Deploy Frequency** | Daily | 3x/week |
| **Mean Time to Recovery** | < 1 hour | 45 min |

---

## 🔐 Seguridad

### Secrets Management

**GitHub Secrets** (Settings → Secrets → Actions):

```yaml
# Frontend
NETLIFY_AUTH_TOKEN
VERCEL_TOKEN

# Backend
RAILWAY_TOKEN
HEROKU_API_KEY
DATABASE_URL
SECRET_KEY
```

**Uso en workflows:**
```yaml
- name: Deploy
  env:
    TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
  run: netlify deploy --auth $TOKEN
```

### Dependabot

Configurar actualizaciones automáticas de dependencias:

```yaml
# .github/dependabot.yml
version: 2
updates:
  # Frontend
  - package-ecosystem: "npm"
    directory: "/front"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5

  # Backend
  - package-ecosystem: "pip"
    directory: "/back"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
```

---

## 📚 Referencias

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Codecov Documentation](https://docs.codecov.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)

---

**Última actualización**: 8 de marzo de 2026
