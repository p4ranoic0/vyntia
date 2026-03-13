# Deployment - RRHH Intranet

## Objetivo

Definir un proceso repetible para desplegar backend y frontend en ambientes `staging` y `production`.

## 1. Ambientes

- `development`: `config.settings.development`
- `staging`: `config.settings.staging`
- `production`: `config.settings.production`

## 2. Variables de Entorno Backend

Minimas requeridas en staging/production:

- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`
- `CORS_ALLOWED_ORIGINS`
- `FRONTEND_URL`
- `REDIS_URL`

Recomendadas:

- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`, `DEFAULT_FROM_EMAIL`
- `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_S3_REGION_NAME`
- `DB_READ_*` para replica de lectura
- `ADMIN_URL`

## 3. Build y Release Backend

```powershell
cd d:\INTRANET\back
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py check
python manage.py migrate --settings=config.settings.production
python manage.py collectstatic --noinput --settings=config.settings.production
```

Ejecucion sugerida (Gunicorn):

```powershell
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 120
```

## 4. Build y Release Frontend

```powershell
cd d:\INTRANET\front
npm ci
npm run build
```

Publicar carpeta `dist/` en servidor web (Nginx, Apache o CDN).

## 5. Checklist Pre-Deploy

- Tests backend en verde (`pytest`).
- Build frontend exitoso.
- Migraciones revisadas.
- Variables de entorno cargadas.
- Backup de BD ejecutado.

## 6. Verificacion Post-Deploy

- `GET /api/v1/` responde 200.
- `GET /api/docs/` disponible.
- Login funcional (`/api/v1/auth/login/`).
- Logs sin errores criticos en primera hora.

## 7. Rollback Basico

1. Restaurar version anterior de backend/frontend.
2. Si hubo migracion incompatible, restaurar backup de BD.
3. Verificar endpoints criticos.

## 8. Nota de Riesgo Actual

Revisar `back/config/settings/production.py` antes de primer deploy formal para validar sintaxis del bloque `DATABASES` (posible llave sobrante).
