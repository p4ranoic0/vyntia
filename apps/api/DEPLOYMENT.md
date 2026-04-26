# Backend Deployment Guide

Guía de deployment del backend de VYNTIA.

## Opciones de Hosting

### 1. Railway (Recomendado - Gratuito con GitHub)

**Ventajas:**
- Fácil de usar
- GitHub integration automática
- PostgreSQL incluido
- Redis incluido
- Certificado SSL automático

**Pasos:**

1. Sign up en [railway.app](https://railway.app)
2. Connect GitHub repository
3. Create new project
4. Add PostgreSQL plugin
5. Add Redis plugin  
6. Configure environment variables
7. Deploy

**Archivo `railway.toml`:**
```toml
[build]
builder = "dockerfile"
dockerfile = "Dockerfile"

[deploy]
healthchecks.enabled = true
healthchecks.cpu = 100
```

### 2. Heroku (Con costo)

```bash
# 1. Instalar Heroku CLI
# 2. Login
heroku login

# 3. Create app
heroku create nombre-app

# 4. Add postgres
heroku addons:create heroku-postgresql:hobby-dev

# 5. Add redis
heroku addons:create heroku-redis:premium-0

# 6. Set config
heroku config:set DEBUG=False
heroku config:set SECRET_KEY=tu-clave

# 7. Deploy
git push heroku main

# 8. Migrate
heroku run python manage.py migrate

# 9. Create superuser
heroku run python manage.py createsuperuser
```

### 3. AWS EC2 + RDS + Elasticache

Más complejo pero más escalable.

## Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy code
COPY . .

# Collect static files
RUN python manage.py collectstatic --noinput --settings=vyntia.settings.production

# Create user
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run gunicorn
CMD gunicorn vyntia.wsgi:application --bind 0.0.0.0:$PORT --workers 4
```

## Docker Compose (Local con stack completo)

```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: bd_vyntia
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: temporary_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    environment:
      DEBUG: 'True'
      DB_HOST: db
      REDIS_URL: redis://redis:6379/0
    depends_on:
      - db
      - redis
    stdin_open: true
    tty: true

  celery:
    build: .
    command: celery -A config worker -l info
    volumes:
      - .:/app
    environment:
      DEBUG: 'True'
      DB_HOST: db
      CELERY_REDIS_URL: redis://redis:6379/1
    depends_on:
      - db
      - redis

volumes:
  postgres_data:
  redis_data:
```

## Environment Variables (Producción)

```env
# Core
DEBUG=False
SECRET_KEY=tu-clave-unica-segura
ALLOWED_HOSTS=api.tudominio.com
ENVIRONMENT=production

# Database (RDS/CloudSQL)
DB_ENGINE=django.db.backends.postgresql
DB_NAME=bd_vyntia_prod
DB_USER=postgres_prod
DB_PASSWORD=super_secure_password_123
DB_HOST=rds.amazonaws.com
DB_PORT=5432

# Redis (ElastiCache/Cloud Redis)
REDIS_URL=redis://redis.aws.amazonaws.com:6379/0
CELERY_REDIS_URL=redis://redis.aws.amazonaws.com:6379/1

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SECURE_HSTS_SECONDS=31536000

# Frontend
FRONTEND_URL=https://app.tudominio.com

# Emails (SendGrid)
EMAIL_BACKEND=sendgrid_backend.SendgridBackend
SENDGRID_API_KEY=tu_api_key

# Sentry (Error tracking)
SENTRY_DSN=https://...@sentry.io/...

# CDN S3
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_STORAGE_BUCKET_NAME=...
```

##  Pre-deployment Checklist

- [ ] `DEBUG=False` en settings de producción
- [ ] `SECURE_SSL_REDIRECT=True`
- [ ] `SESSION_COOKIE_SECURE=True`
- [ ] `SECRET_KEY` único y seguro
- [ ] Database backups configurados
- [ ] Monitoreo y logging configurado
- [ ] Email transaccional funcionando
- [ ] CDN/S3 configurado para media
- [ ] Tests pasando
- [ ] Load testing realizado

## CI/CD Pipeline

### GitHub Actions (Automático)

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres

    steps:
      - uses: actions/checkout@v3
      
      - uses: actions/setup-python@v4
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          pytest tests/ --cov=app_rrhh
      
      - name: Check coverage
        run: |
          coverage report --fail-under=80

  deploy:
    needs: test
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to Railway
        run: |
          railway up
        env:
          RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
```

## Monitoreo en Producción

```bash
# Health check endpoint
curl https://api.tudominio.com/health

# Ver logs (Railway)
railway logs

# Ver logs (Heroku)
heroku logs --tail

# Database backup (PostgreSQL)
pg_dump -U postgres bd_vyntia > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U postgres bd_vyntia < backup_20260307.sql
```

## Rollback

```bash
# Railway
railway rollback

# Heroku
heroku releases
heroku rollback v5

# Docker
docker pull registry/image:previous-tag
docker-compose up
```

## Más Información

- [Django Production Checklist](https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/)
- [Railway Docs](https://docs.railway.app/)
- [PostgreSQL Backup](https://www.postgresql.org/docs/current/backup.html)
- [Gunicorn Config](https://gunicorn.org/#deployment)
