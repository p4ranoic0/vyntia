# Quickstart - VYNTIA

## Requisitos Previos

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+
- Redis 7.0+ (cache y Celery)
- npm 9+

## Inicio Rapido (Windows PowerShell)

### 0. PostgreSQL

```powershell
# Opcion A: Servicio local instalado
# Inicia servicio PostgreSQL desde servicios de Windows

# Opcion B: Docker
docker run -d --name rrhh-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=bd_vyntia -p 5432:5432 postgres:15
```

### 1. Redis

```powershell
# Opcion A: Servicio local
redis-server

# Opcion B: Docker
docker run -d -p 6379:6379 redis:7-alpine

# Verificar
redis-cli ping  # retorna PONG
```

### 2. Backend

```powershell
cd d:\VYNTIA\back
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.template .env
python manage.py migrate
python manage.py runserver 8000
```

### 3. Frontend (nueva terminal)

```powershell
cd d:\VYNTIA\front
npm install
copy .env.template .env
npm run dev
```

## URLs de Verificacion

- Frontend: http://localhost:5173
- Backend API root: http://127.0.0.1:8000/api/v1/
- Swagger: http://127.0.0.1:8000/api/docs/
- Redoc: http://127.0.0.1:8000/api/redoc/

## Pruebas Rapidas

### Backend

```powershell
cd d:\VYNTIA\back
.\.venv\Scripts\Activate.ps1
python -m pytest tests -v --tb=short
```

### Frontend

```powershell
cd d:\VYNTIA\front
npm run test
```

## Celery Worker (opcional, recomendado)

Para procesar tareas asíncronas (emails, etc.):

```powershell
cd d:\VYNTIA\back
.\.venv\Scripts\Activate.ps1
celery -A config worker -l info
```

## Tip

Si ya abriste el workspace en VS Code, puedes usar las tareas:
- `Iniciar Backend (Django)`
- `Iniciar Frontend (Vite)`
