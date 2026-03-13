# ADR 004: Redis como Backend para Cache y Tareas Asíncronas

**Estado:** Aceptado  
**Fecha:** 2026-03-07  
**Decisores:** Equipo de Desarrollo  
**Contexto técnico:** Backend Django con DRF

## Contexto

El sistema RRHH Intranet requiere:
1. **Caché eficiente** para reducir carga en la base de datos y mejorar tiempos de respuesta
2. **Procesamiento asíncrono** para tareas de larga duración (envío de emails, generación de reportes)
3. **Escalabilidad horizontal** para soportar múltiples workers y servidores web

Las alternativas evaluadas fueron:
- **LocMem Cache:** Rápido pero no compartido entre procesos, se pierde al reiniciar
- **Database Cache:** Compartido pero lento, agrega carga adicional a la DB
- **Memcached:** Maduro y rápido, pero solo key-value simple
- **Redis:** Key-value avanzado con soporte para estructuras de datos complejas

Para tareas asíncronas:
- **Database Backend:** Simple pero ineficiente, introduce latencia
- **RabbitMQ:** Robusto pero requiere infraestructura adicional
- **Redis:** Ligero y reutiliza la misma infraestructura del cache

## Decisión

**Se implementará Redis como backend único tanto para cache como para Celery.**

### Configuración adoptada:

#### Cache (development.py):
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/0'),
        'KEY_PREFIX': 'rrhh_dev',
        'TIMEOUT': 300,  # 5 minutos
    },
    'sessions': {
        # Cache dedicado para sesiones (24h TTL)
        'KEY_PREFIX': 'rrhh_session',
        'TIMEOUT': 86400,
    }
}
```

#### Celery (base.py):
```python
CELERY_BROKER_URL = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')
CELERY_RESULT_BACKEND = os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1')
```

**Base de datos separada:** Se usa DB 0 para cache, DB 1 para Celery para evitar colisiones de claves.

### Decoradores implementados:

Se crearon 4 decoradores reutilizables en `core/decorators.py`:

1. **`@cache_response(timeout, key_prefix, vary_on_user)`**  
   Para cachear respuestas de vistas DRF automáticamente
   
2. **`@cache_queryset(timeout, key_prefix)`**  
   Para cachear resultados de consultas a la base de datos
   
3. **`@invalidate_cache(patterns)`**  
   Para invalidar cache después de operaciones de escritura
   
4. **`@cache_method(timeout, key_prefix)`**  
   Para cachear métodos de servicios con lógica compleja

## Consecuencias

### Positivas ✅

- **Simplicidad operacional:** Una sola tecnología (Redis) para dos necesidades
- **Alto rendimiento:** Redis es in-memory, latencias <1ms para cache hits
- **Persistencia opcional:** Redis puede configurarse para persistir a disco en producción
- **Estructuras avanzadas:** Soporte para listas, sets, hashes (útil para features futuras)
- **Escalabilidad:** Múltiples workers Celery pueden compartir la misma cola
- **Decoradores reutilizables:** Patrón consistente en todo el código para caching
- **Invalidación inteligente:** Control fino sobre qué cache invalidar
- **Monitoreo simple:** Redis CLI permite inspeccionar claves y tareas fácilmente

### Negativas ⚠️

- **Dependencia adicional:** Redis debe estar ejecutándose (dev y prod)
- **Sin persistencia por defecto:** Cache se pierde si Redis se reinicia (aceptable)
- **Gestión de memoria:** Redis consume RAM, necesita límites configurados (`maxmemory`)
- **Potencial single point of failure:** En producción se requiere Redis Sentinel/Cluster

### Riesgos mitigados 🛡️

| Riesgo | Mitigación |
|--------|-----------|
| Cache stale (datos obsoletos) | Timeouts cortos (5min default), decorador `@invalidate_cache` |
| Tareas Celery perdidas | `CELERY_TASK_TRACK_STARTED=True`, logs detallados |
| Redis caído en producción | Fallback a LocMem cache en base.py, alertas de monitoreo |
| Consumo excesivo de memoria | `maxmemory-policy allkeys-lru` en producción |

## Notas de implementación

### Instalación local (desarrollo):
```powershell
# Windows (Chocolatey)
choco install redis-64

# O usar Docker
docker run -d -p 6379:6379 redis:7-alpine
```

### Verificar conexión:
```bash
redis-cli ping  # Debe retornar PONG
```

### Monitorear cache:
```bash
redis-cli
> KEYS rrhh_dev:*  # Ver claves de cache
> TTL rrhh_dev:view_cache:abc123  # Ver tiempo de vida
> FLUSHDB  # Limpiar cache (desarrollo)
```

### Ejemplo de uso en código:

```python
from core.decorators import cache_response, invalidate_cache

class AreaViewSet(viewsets.ModelViewSet):
    @cache_response(timeout=600, key_prefix='areas')
    def list(self, request):
        # Cachea lista de áreas por 10 minutos
        return super().list(request)
    
    @invalidate_cache(['*areas*'])
    def create(self, request):
        # Invalida cache al crear nueva área
        return super().create(request)
```

## Referencias

- [Redis Documentation](https://redis.io/docs/)
- [django-redis](https://github.com/jazzband/django-redis)
- [Celery with Redis](https://docs.celeryproject.org/en/stable/getting-started/backends-and-brokers/redis.html)
- ADR 002: Service Layer Pattern (contexto de servicios cacheables)
