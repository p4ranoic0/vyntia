# Guía de Cache - Decoradores Reutilizables

## Introducción

El sistema utiliza **Redis** como backend de cache para mejorar el rendimiento. Se implementaron 4 decoradores en `core/decorators.py` que permiten cachear respuestas de vistas, querysets, y métodos de servicios de forma declarativa.

## Decoradores Disponibles

### 1. `@cache_response` - Cachear Respuestas de Vistas DRF

Cachea automáticamente las respuestas de viewsets/vistas de Django REST Framework.

**Parámetros:**
- `timeout` (int): Tiempo de expiración en segundos (default: 300 = 5 min)
- `key_prefix` (str): Prefijo personalizado para la clave de cache
- `vary_on_user` (bool): Si True, cada usuario tiene su propia cache (default: False)

**Uso en ViewSets:**

```python
from core.decorators import cache_response

class AreaViewSet(viewsets.ModelViewSet):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    
    @cache_response(timeout=600, key_prefix='areas')
    def list(self, request):
        """Lista de áreas - cacheada por 10 minutos."""
        return super().list(request)
    
    @cache_response(timeout=300, vary_on_user=True)
    def retrieve(self, request, pk=None):
        """Detalle de área - cache por usuario."""
        return super().retrieve(request, pk=pk)
```

**Comportamiento:**
- Genera una clave única basada en: URL path + query params + usuario (si `vary_on_user=True`)
- Solo cachea respuestas exitosas (status 200-299)
- Cache hits retornan inmediatamente sin ejecutar la vista
- Query params diferentes generan claves diferentes:
  - `/api/v1/areas/?estado=True` ≠ `/api/v1/areas/`

**Cuándo usar:**
- ✅ Endpoints de solo lectura (GET)
- ✅ Datos que cambian poco (catálogos, configuraciones)
- ✅ Listados con paginación estable
- ❌ Endpoints de escritura (POST/PUT/PATCH/DELETE)
- ❌ Datos en tiempo real o muy dinámicos

---

### 2. `@cache_queryset` - Cachear Resultados de Consultas

Cachea los resultados de funciones que retornan querysets o listas desde la base de datos.

**Parámetros:**
- `timeout` (int): Tiempo de expiración en segundos (default: 300)
- `key_prefix` (str): Prefijo para identificar el tipo de cache

**Uso en Servicios:**

```python
from core.decorators import cache_queryset

class AreaService:
    @staticmethod
    @cache_queryset(timeout=600, key_prefix='active_areas')
    def get_active_areas():
        """Obtener áreas activas - cacheado por 10 min."""
        return Area.objects.filter(estado=True).select_related('area_padre')
    
    @staticmethod
    @cache_queryset(timeout=300, key_prefix='area_hierarchy')
    def get_area_hierarchy(parent_id=None):
        """Jerarquía de áreas - cache por argumentos."""
        return Area.objects.filter(area_padre_id=parent_id)
```

**Comportamiento:**
- La clave incluye el nombre de la función + argumentos
- Argumentos diferentes generan claves diferentes:
  - `get_area_hierarchy(parent_id=1)` ≠ `get_area_hierarchy(parent_id=2)`
- Convierte QuerySets a listas para poder serializar en cache
- Retorna la lista cacheada (no un QuerySet activo)

**Cuándo usar:**
- ✅ Consultas complejas con múltiples JOINs
- ✅ Funciones de servicios que preparan datos para vistas
- ✅ Cálculos agregados costosos (`COUNT`, `SUM`, `AVG`)
- ❌ Consultas con `.filter()` dinámico en la vista
- ❌ QuerySets que necesitan evaluación lazy

---

### 3. `@invalidate_cache` - Invalidar Cache Automáticamente

Limpia las claves de cache después de ejecutar operaciones de escritura.

**Parámetros:**
- `patterns` (str | list[str]): Patrón o lista de patrones de claves a eliminar

**Uso en ViewSets:**

```python
from core.decorators import cache_response, invalidate_cache

class AreaViewSet(viewsets.ModelViewSet):
    @cache_response(timeout=600, key_prefix='areas')
    def list(self, request):
        return super().list(request)
    
    @invalidate_cache(['view_cache:*areas*', 'queryset_cache:*active_areas*'])
    def create(self, request):
        """Al crear área, invalida todas las caches de áreas."""
        return super().create(request)
    
    @invalidate_cache(['view_cache:*areas*'])
    def update(self, request, pk=None):
        """Al actualizar, limpia cache de listados."""
        return super().update(request, pk=pk)
    
    @invalidate_cache(['view_cache:*areas*'])
    def destroy(self, request, pk=None):
        """Al eliminar, limpia cache."""
        return super().destroy(request, pk=pk)
```

**Patrones soportados:**
- `*` = comodín (cualquier carácter)
- `view_cache:*areas*` = todas las claves de vistas que contengan "areas"
- `queryset_cache:*` = todas las claves de querysets
- Múltiples patrones se evalúan en orden

**Cuándo usar:**
- ✅ Siempre en `create`, `update`, `destroy` de ViewSets cacheados
- ✅ Después de llamadas a servicios que modifican datos
- ✅ En endpoints que cambian configuraciones globales
- ❌ En endpoints de solo lectura

---

### 4. `@cache_method` - Cachear Métodos de Clase/Instancia

Cachea resultados de métodos de servicios o modelos con lógica compleja.

**Parámetros:**
- `timeout` (int): Tiempo de expiración en segundos
- `key_prefix` (str): Prefijo de identificación

**Uso en Servicios:**

```python
from core.decorators import cache_method

class VacacionService:
    @cache_method(timeout=600, key_prefix='employee_vacation_stats')
    def calcular_estadisticas_empleado(self, empleado_id: int) -> dict:
        """Calcula días disponibles, usados, pendientes."""
        # Lógica compleja con múltiples consultas y cálculos
        dias_disponibles = self._calcular_dias_anuales(empleado_id)
        dias_usados = self._calcular_dias_consumidos(empleado_id)
        dias_pendientes = self._calcular_solicitudes_pendientes(empleado_id)
        
        return {
            'disponibles': dias_disponibles,
            'usados': dias_usados,
            'pendientes': dias_pendientes,
            'restantes': dias_disponibles - dias_usados
        }
```

**Comportamiento:**
- Incluye el nombre de la clase en la clave (útil para métodos de instancia)
- Argumentos diferentes = cache diferente
- No requiere que el retorno sea serializable a DB (puede ser dict, list, etc.)

**Cuándo usar:**
- ✅ Cálculos matemáticos/estadísticos costosos
- ✅ Lógica de negocio compleja (reglas de vacaciones, cálculo de bonos)
- ✅ Métodos que agregan datos de múltiples fuentes
- ❌ Métodos que modifican estado (siempre ejecutar)

---

## Estrategias de Cache

### Timeouts Recomendados

| Tipo de Dato | Timeout | Ejemplo |
|--------------|---------|---------|
| Catálogos estáticos | 3600s (1h) | Áreas, tipos de contrato, estados |
| Configuraciones | 1800s (30min) | Días festivos, configuración de vacaciones |
| Listados con filtros | 600s (10min) | Empleados activos, solicitudes pendientes |
| Datos de usuario | 300s (5min) | Perfil, permisos |
| Estadísticas/reportes | 900s (15min) | Dashboard, métricas |

### Flujo Completo: Listado + Invalidación

```python
from core.decorators import cache_response, invalidate_cache

class EmpleadoViewSet(viewsets.ModelViewSet):
    queryset = Empleado.objects.select_related('area', 'cargo')
    serializer_class = EmpleadoSerializer
    
    # LECTURA - cacheada
    @cache_response(timeout=300, key_prefix='empleados')
    def list(self, request):
        return super().list(request)
    
    @cache_response(timeout=600, key_prefix='empleado_detail')
    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk=pk)
    
    # ESCRITURA - invalida cache
    @invalidate_cache(['view_cache:*empleados*', 'queryset_cache:*empleados*'])
    def create(self, request):
        return super().create(request)
    
    @invalidate_cache(['view_cache:*empleados*', 'view_cache:*empleado_detail*'])
    def update(self, request, pk=None):
        return super().update(request, pk=pk)
    
    @invalidate_cache(['view_cache:*empleados*'])
    def destroy(self, request, pk=None):
        return super().destroy(request, pk=pk)
```

---

## Debugging Cache

### Ver claves activas en Redis

```bash
redis-cli
> KEYS rrhh_dev:*  # Todas las claves del entorno dev
> KEYS rrhh_dev:view_cache:*  # Solo vistas cacheadas
> TTL rrhh_dev:view_cache:abc123  # Ver tiempo de vida restante
```

### Limpiar cache manualmente

**Toda la cache de desarrollo:**
```bash
redis-cli -n 0 FLUSHDB
```

**Solo claves del proyecto:**
```bash
redis-cli KEYS "rrhh_dev:*" | xargs redis-cli DEL
```

**Desde Django shell:**
```python
from django.core.cache import cache
cache.clear()  # Limpia toda la DB de cache
cache.delete_pattern('view_cache:*areas*')  # Solo áreas
```

### Logs de cache hits/misses

Habilitar logging en `development.py`:

```python
LOGGING['loggers']['django.core.cache'] = {
    'handlers': ['console'],
    'level': 'DEBUG',  # Ver cada get/set
    'propagate': False,
}
```

---

## Best Practices

### ✅ DO

- Cachea endpoints GET de solo lectura
- Usa `vary_on_user=True` para datos personalizados
- Invalida cache en operaciones de escritura (POST/PUT/DELETE)
- Prefiere timeouts cortos (5-10min) para evitar datos stale
- Usa `key_prefix` descriptivos para facilitar debug
- Combina decoradores: `@cache_response` + `@invalidate_cache`

### ❌ DON'T

- Cachear endpoints POST/PUT/DELETE directamente
- Olvidar invalidar cache después de modificaciones
- Usar timeouts muy largos (>1h) para datos que cambian frecuentemente
- Cachear datos sensibles sin `vary_on_user=True`
- Generar claves dinámicas manualmente (usa los decoradores)

---

## Monitoreo en Producción

### Métricas recomendadas

1. **Hit Rate (ratio hits/total):** Ideal >70%
2. **Memory Usage:** Mantener <80% de `maxmemory`
3. **Evictions:** Idealmente 0 (configura `maxmemory` adecuadamente)
4. **Latency:** <1ms por operación GET/SET

### Configuración Redis producción

```bash
# /etc/redis/redis.conf
maxmemory 2gb
maxmemory-policy allkeys-lru  # Elimina claves menos usadas
save 900 1  # Persistencia opcional cada 15min si hay 1+ cambio
```

---

## Troubleshooting

### Cache no se actualiza después de cambios

**Causa:** Olvido de usar `@invalidate_cache` en endpoints de escritura.  
**Solución:** Agregar decorador en `create`, `update`, `destroy`.

### Cache consume mucha memoria

**Causa:** Timeouts muy largos o claves no expiradas.  
**Solución:** Reducir timeouts, configurar `maxmemory`, revisar patrones de invalidación.

### Performance no mejora con cache

**Causa:** Low hit rate, timeout muy corto, o bottleneck en otra parte.  
**Solución:** Verificar métricas de Redis, revisar logs, analizar queries con Django Debug Toolbar.

---

## Referencias

- [ADR 004: Redis como Backend](./adrs/004-redis-cache-celery.md)
- [django-redis Documentation](https://github.com/jazzband/django-redis)
- [Redis Best Practices](https://redis.io/docs/management/optimization/)
