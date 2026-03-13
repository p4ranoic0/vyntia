# Setup Completo - RRHH Intranet

## 1. Estructura del Repositorio

- `back/`: API Django REST Framework y logica de negocio.
- `front/`: Aplicacion React + Vite.
- `bd/`: Scripts SQL de base de datos.
- `docs/`: Documentacion funcional y tecnica.

## 2. Requisitos del Entorno

- Python 3.11 o superior
- Node.js 18 o superior
- PostgreSQL 15 o superior
- Redis 7.0 o superior (para cache y Celery)
- npm 9 o superior
- PowerShell (Windows)

## 3. Configuracion Backend

### 3.0 Instalar PostgreSQL (Windows)

**Opción A: Instalador oficial**
- Instala PostgreSQL 15+ y crea la base `bd_rrhh_intranet`.

**Opción B: Docker**
```powershell
docker run -d --name rrhh-postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=bd_rrhh_intranet -p 5432:5432 postgres:15
```

### 3.1 Crear entorno virtual e instalar dependencias

```powershell
cd d:\INTRANET\back
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.2 Variables de entorno backend

```powershell
copy .env.template .env
```

Revisa y ajusta en `back/.env`:
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, `DB_SSLMODE`
- `FRONTEND_URL` (normalmente `http://localhost:5173`)
- `CACHE_REDIS_URL` (normalmente `redis://127.0.0.1:6379/0`)
- `CELERY_REDIS_URL` (normalmente `redis://127.0.0.1:6379/1`)

### 3.2.1 Instalar y levantar Redis (Windows)

**Opción A: Chocolatey**
```powershell
choco install redis-64
redis-server
```

**Opción B: Docker**
```powershell
docker run -d -p 6379:6379 --name redis redis:7-alpine
```

**Verificar conexión:**
```powershell
redis-cli ping  # Debe retornar PONG
```

### 3.3 Inicializar esquema de base de datos

Opcion A (Django migrations):

```powershell
python manage.py migrate
```

Opcion B (scripts SQL en `bd/`, si necesitas estructura/datos manuales):

Orden recomendado:
1. `create bd_rrhh_intranet.sql`
2. `datos-demo-django.sql`
3. `funciones.sql`
4. `procedimientos.sql`
5. `triggers.sql`
6. `vistas.sql`

### 3.3.1 Migrar datos MySQL -> PostgreSQL (si aplica)

```powershell
cd d:\INTRANET\back
.\scripts\migrate_mysql_to_postgresql.ps1 -SourceSettings config.settings.development -TargetSettings config.settings.development
```

### 3.4 Levantar backend

```powershell
python manage.py runserver 8000
```

Por defecto, `manage.py` usa `config.settings.development`.

### 3.5 Levantar worker Celery (recomendado)

```powershell
cd d:\INTRANET\back
.\.venv\Scripts\Activate.ps1
celery -A config worker -l info
```

Esto permite ejecutar tareas asíncronas como envío de emails.

## 4. Configuracion Frontend

### 4.1 Instalar dependencias

```powershell
cd d:\INTRANET\front
npm install
```

### 4.2 Variables de entorno frontend

```powershell
copy .env.template .env
```

Valor recomendado:
- `VITE_API_BASE_URL=http://127.0.0.1:8000`

### 4.3 Levantar frontend

```powershell
npm run dev
```

El proxy de Vite redirige `/api` y `/media` al backend en `127.0.0.1:8000`.

## 5. Verificacion Funcional

Con backend y frontend activos:

- Frontend: `http://localhost:5173`
- API: `http://127.0.0.1:8000/api/v1/`
- Swagger: `http://127.0.0.1:8000/api/docs/`
- Redoc: `http://127.0.0.1:8000/api/redoc/`

Prueba de autenticacion:
- Endpoint login: `POST /api/v1/auth/login/`
- Endpoint perfil: `GET /api/v1/auth/profile/`

## 6. Flujo Diario Recomendado (1 mantenedor)

1. Actualizar rama de trabajo.
2. Levantar backend y frontend.
3. Implementar cambios pequenos por modulo.
4. Ejecutar pruebas del modulo afectado.
5. Revisar logs de backend (`back/logs/`).
6. Documentar cambios relevantes en `docs/`.

## 7. Troubleshooting

### 7.1 Puerto 8000 ocupado

```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### 7.5 Redis no conecta

Verifica:
- Servicio Redis activo: `redis-cli ping` debe retornar `PONG`
- Puerto 6379 disponible: `netstat -ano | findstr :6379`
- Variable `REDIS_URL` en `back/.env`

**Limpiar cache Redis (desarrollo):**
```powershell
redis-cli FLUSHDB
```

### 7.6 Celery no procesa tareas

Verifica:
- Worker Celery activo: `celery -A config worker -l info`
- Redis conectado (ver 7.5)
- Logs en consola del worker para errores de tareas

**Ver tareas pendientes:**
```powershell
redis-cli LLEN celery
```

### 7.2 Puerto 5173 ocupado

```powershell
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

### 7.3 Error de conexion a PostgreSQL

Verifica:
- Servicio PostgreSQL activo.
- Credenciales en `back/.env`.
- Base de datos existente (`bd_rrhh_intranet`).

### 7.4 Error CORS en frontend

En desarrollo, `config.settings.development` permite origenes de localhost y `CORS_ALLOW_ALL_ORIGINS=True`.
Si cambias host/puerto, ajusta `CORS_ALLOWED_ORIGINS`.

### 7.5 Error de migraciones

```powershell
cd d:\INTRANET\back
.\.venv\Scripts\Activate.ps1
python manage.py showmigrations
python manage.py migrate
```

### 7.6 Tests backend fallan por entorno

Asegura activar virtualenv antes de correr pytest y usar la configuracion de `pytest.ini`.

## 8. Comandos Utiles

Backend:

```powershell
cd d:\INTRANET\back
.\.venv\Scripts\Activate.ps1
python manage.py check
python manage.py showmigrations
python -m pytest tests -v --tb=short
```

Frontend:

```powershell
cd d:\INTRANET\front
npm run lint
npm run test
npm run build
```
