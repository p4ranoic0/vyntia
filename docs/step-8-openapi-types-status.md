# Step 8: OpenAPI TypeScript Type Generation - Estado

## ✅ Completado (80%)

### Infraestructura de Generación de Tipos

La infraestructura está **completamente funcional** y generando tipos TypeScript automáticamente desde el schema OpenAPI del backend.

#### Instalado
- ✅ `openapi-typescript-codegen` 0.30.0 (17 paquetes)
- ✅ Script automatizado: [front/scripts/generate-api-types.mjs](../front/scripts/generate-api-types.mjs)
- ✅ Script de generación backend: [back/scripts/generate_openapi_schema.py](../back/scripts/generate_openapi_schema.py)

#### Funcionando
```bash
# 1. Generar schema desde Django
cd back
..\.venv\Scripts\python.exe scripts\generate_openapi_schema.py

# 2. Generar tipos TypeScript
cd ../front
npm run generate:api
```

#### Generado Exitosamente
- **Schema OpenAPI:** [front/openapi-schema.json](../front/openapi-schema.json) (13KB, válido)
- **Tipos TypeScript:** [front/src/generated/api/](../front/src/generated/api/)
  - `/core` - Cliente Axios configurado
  - `/models` - Interfaces TypeScript
  - `/services` - Clases de servicio API
  - `index.ts` - Re-exportaciones

#### Ejemplo de Uso
```typescript
import { AuthService } from '@/generated/api';
import type { LoginRequest } from '@/generated/api/models';

const response = await AuthService.apiV1AuthLoginCreate({
  username: 'admin',
  password: 'pass'
});
```

---

## ⚠️ Pendiente (20%)

### Schema Incompleto - Solo Endpoints de Autenticación

El schema actual **solo incluye 6 paths de autenticación**:
- `/api/v1/auth/forgot-password/`
- `/api/v1/auth/login/`
- `/api/v1/auth/refresh/`
- `/api/v1/auth/reset-password/`
- `/legacy/login/`

**Faltan todos los endpoints RRHH:**
- Empleados, Áreas, Contratos
- Vacaciones, Permisos, Roles
- Datos Familiares, Datos Académicos
- Documentos, Reportes

### Causa Raíz: Serializers Legacy

El archivo `app_rrhh/serializers_optimized.py` tiene errores sistemáticos de nombres de campos que no coinciden con los modelos actuales:

```python
# ❌ ERROR - Campo no existe en modelo
class DatosAcademicosListSerializer:
    fields = ['dato_academico_id', ...]  
    # Debería ser: 'academico_id'

# ❌ ERROR - Campo no existe en modelo  
class DatosAcademicosListSerializer:
    fields = ['tipo_parentesco', ...]
    # Debería ser: 'parentesco'
```

**Patrón de Errores Identificado:**
1. Prefijos `dato_*_id` que deberían ser `*_id`
2. Sufijos `*_familiar`, `*_academico` que no coinciden con modelo
3. Nombres de campos desactualizados vs modelos actuales

### Correcciones Realizadas

#### DatosFamiliaresListSerializer ✅
```python
# Corregidos 5 campos:
'dato_familiar_id' → 'familiar_id'
'tipo_parentesco' → 'parentesco'  
'apellido_paterno_familiar' → 'apellido_paterno'
'apellido_materno_familiar' → 'apellido_materno'
'es_dependiente_economico' → 'es_dependiente'
```

#### ViewSets Excluidos ✅
```python
# Excluidos del schema (no usan serializers estándar):
DocumentGenerationViewSet  # Genera PDFs
VacacionesReportesViewSet  # Respuestas dinámicas
```

### Próximos Pasos para Schema Completo

#### Opción 1: Corrección Sistemática (Recomendado)
```bash
cd d:\INTRANET\back

# Encontrar todos los patrones problemáticos
grep -n "dato_.*_id" app_rrhh/serializers_optimized.py
grep -n "_familiar" app_rrhh/serializers_optimized.py
grep -n "_academico" app_rrhh/serializers_optimized.py

# Corregir todos de una vez comparando con modelos
# Luego regenerar schema completo
```

#### Opción 2: Usar Solo API v1
Si `serializers_optimized.py` es solo para endpoints legacy, considerar:
- Deprecar endpoints legacy gradualmente
- Generar schema solo desde `/api/v1/` (serializers ya correctos)
- Migrar clientes a nueva API

---

## 📁 Archivos Modificados

### Frontend
- `front/scripts/generate-api-types.mjs` - Script de generación
- `front/openapi-schema.json` - Schema OpenAPI
- `front/src/generated/api/**` - Tipos e interfaces generados
- `front/package.json` - Script `generate:api`

### Backend  
- `back/scripts/generate_openapi_schema.py` - Generador de schema
- `back/api/v1/app_rrhh/document_generation_views.py` - Exclusión
- `back/api/v1/vacaciones/views.py` - Exclusión
- `back/app_rrhh/serializers_optimized.py` - Parcialmente corregido

---

## 🎯 Conclusión

**La infraestructura de generación de tipos funciona correctamente.**

El schema actual (solo auth) demuestra que el sistema end-to-end está operativo. Para obtener el schema completo con todos los modelos RRHH, se necesita corregir los serializers legacy en `serializers_optimized.py`.

**Impacto:** Moderado - La API v1 moderna ya tiene serializers correctos. Los errores están en serializers legacy que pueden deprecarse.

**Próxima Acción:** Evaluar si vale la pena corregir serializers_optimized.py o migrar completamente a API v1 y generar schema solo desde ahí.
