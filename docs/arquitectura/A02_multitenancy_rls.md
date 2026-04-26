# A02. Multi-tenancy y Row-Level Security (RLS)

> Estrategia de aislamiento lógico para SaaS multi-cliente con PostgreSQL como baseline. Diseño alineado al proyecto base `github.com/p4ranoic0/INTRANET` para permitir extensión progresiva.

---

## 1. Principio arquitectónico base

Todo SaaS multi-cliente debe responder con precisión a tres preguntas operativas:

1. ¿Cómo garantizamos que **ningún dato de un cliente (tenant)** aparezca en consultas de otro cliente?
2. ¿Cómo **escalamos** agregando tenants sin degradar rendimiento ni disparar costos?
3. ¿Qué pasa cuando un cliente **grande exige aislamiento físico** o regulatorio (salud, banca, minería, defensa)?

La respuesta recomendada es **multi-tenancy híbrido en tres tiers**, empezando con un modelo pooled + RLS y escalando a esquemas dedicados o bases de datos dedicadas conforme crecen las exigencias del cliente.

---

## 2. Tres modelos de multi-tenancy: comparativa

| Modelo | Aislamiento | Costo infra | Complejidad | Cuándo usar |
|---|---|---|---|---|
| **Pooled** (tablas compartidas con `tenant_id` + RLS) | Lógico | Muy bajo | Media | Tiers Starter/Pro; mayoría Pymes y Mid-Market |
| **Schema-per-tenant** (un schema Postgres por cliente) | Medio (DB compartida) | Medio | Alta (migraciones × N) | Clientes Enterprise medianos; regulados ligeros |
| **Database-per-tenant** (DB dedicada por cliente) | Físico | Alto | Alta (orquestación) | Clientes GovTech/Enterprise con exigencias regulatorias (datos sensibles, residencia, auditoría externa) |

La recomendación es adoptar **Pooled + RLS como baseline** y ofrecer **Database-per-tenant como tier premium** (upsell). El modelo intermedio schema-per-tenant se evita porque suma complejidad operacional sin aislamiento físico.

---

## 3. Modelo Pooled + RLS — diseño detallado

### 3.1 Esquema de datos

Todas las tablas de negocio incluyen la columna `tenant_id UUID NOT NULL`:

```sql
-- Tabla maestra de tenants
CREATE TABLE tenants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  nombre VARCHAR(200) NOT NULL,
  ruc VARCHAR(11) UNIQUE NOT NULL,
  plan VARCHAR(50) NOT NULL,          -- starter | pro | enterprise | govtech
  estado VARCHAR(20) NOT NULL,        -- activo | suspendido | trial | cancelado
  fecha_alta TIMESTAMP DEFAULT NOW(),
  configuracion JSONB DEFAULT '{}'::jsonb,
  CHECK (plan IN ('starter','pro','enterprise','govtech'))
);

-- Ejemplo: tabla de empleados
CREATE TABLE empleados (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  codigo VARCHAR(20) NOT NULL,
  dni VARCHAR(15) NOT NULL,
  nombres VARCHAR(200),
  -- ... otros campos
  UNIQUE (tenant_id, codigo),          -- unicidad por tenant
  UNIQUE (tenant_id, dni)
);

-- Índice compuesto obligatorio (tenant_id siempre primero)
CREATE INDEX idx_empleados_tenant ON empleados(tenant_id);
CREATE INDEX idx_empleados_tenant_dni ON empleados(tenant_id, dni);
```

**Regla dura**: toda query debe filtrar por `tenant_id`. Todo índice debe empezar por `tenant_id`. Toda unicidad lógica se convierte en unicidad compuesta `(tenant_id, campo)`.

### 3.2 Row-Level Security

RLS es la barrera **defensa-en-profundidad** que protege incluso si el código aplicativo olvida filtrar por tenant. Se implementa con policies Postgres:

```sql
-- Activar RLS en tabla
ALTER TABLE empleados ENABLE ROW LEVEL SECURITY;

-- Policy: solo devolver filas del tenant del usuario conectado
CREATE POLICY empleados_tenant_isolation ON empleados
  FOR ALL
  TO app_role
  USING (tenant_id = current_setting('app.tenant_id', true)::uuid)
  WITH CHECK (tenant_id = current_setting('app.tenant_id', true)::uuid);

-- Superusuario bypass (para procesos batch administrativos)
ALTER TABLE empleados FORCE ROW LEVEL SECURITY;  -- ni siquiera owner ve todo sin bypass explícito
```

### 3.3 Inyección del tenant_id en cada request

El backend debe establecer `app.tenant_id` en la conexión al iniciar cada transacción. Patrón típico con pool de conexiones:

```python
# FastAPI middleware
from contextvars import ContextVar
from sqlalchemy import event

tenant_context: ContextVar[str] = ContextVar("tenant_id")

@app.middleware("http")
async def tenant_middleware(request: Request, call_next):
    # Tenant extraído del JWT
    tenant_id = resolve_tenant_from_jwt(request.headers.get("Authorization"))
    token = tenant_context.set(tenant_id)
    try:
        response = await call_next(request)
        return response
    finally:
        tenant_context.reset(token)

# Hook en SQLAlchemy: cada checkout de conexión setea el tenant
@event.listens_for(engine, "checkout")
def set_tenant_on_checkout(dbapi_conn, conn_record, conn_proxy):
    tenant_id = tenant_context.get(None)
    if tenant_id:
        cursor = dbapi_conn.cursor()
        cursor.execute(f"SET app.tenant_id = '{tenant_id}'")
        cursor.close()
```

### 3.4 Resolución de tenant

Tres estrategias combinables, elegir según producto:

| Estrategia | Ejemplo | Pros | Contras |
|---|---|---|---|
| **Subdominio** | `acme.miapp.pe` | UX clara, marca por tenant | Requiere DNS wildcard + cert SSL wildcard |
| **Path** | `miapp.pe/t/acme/...` | Simple, sin DNS extra | URLs más largas, menos branding |
| **JWT claim** | `tenant_id` dentro del token | API-friendly, sin cambio URL | Requiere resolver login previo |

La recomendación es combinar **subdominio para web** + **JWT claim para API**. El login redirige al subdominio correcto tras autenticar.

---

## 4. Caso especial: Tiers y upgrade path

### 4.1 Matriz de tiers

| Tier | Modelo BD | Cifrado | Backups | SLA | Clientes típicos |
|---|---|---|---|---|---|
| **Starter** | Pooled + RLS | At-rest AES-256 | Diario, retención 30d | 99.5% | Pymes 1-50 empleados |
| **Pro** | Pooled + RLS | At-rest + key por tenant | Diario, retención 90d | 99.9% | Mid-market 50-500 |
| **Enterprise** | Schema o DB dedicada | KMS gestionado + HSM opcional | Cada 6h, retención 1 año | 99.95% + DR region | Grandes corporaciones 500+ |
| **GovTech** | DB dedicada + residencia datos | HSM + BYOK | Cada 6h + cold storage 5+ años | 99.95% + residencia Perú | Entidades públicas, salud, banca |

### 4.2 Upgrade path sin downtime

Para migrar un cliente de **Pooled → DB dedicada** sin downtime:

```
1. Crear DB destino vacía con mismo schema
2. Exportar filas WHERE tenant_id = X a dump comprimido
3. Importar en DB destino removiendo tenant_id (ya no es necesario)
4. CDC (Change Data Capture) con Debezium: capturar cambios en pooled desde el timestamp del dump
5. Aplicar cambios capturados a DB destino hasta alcanzar lag < 1 segundo
6. Momento de switch: breve pausa writes (ventana < 5 seg), aplicar último delta
7. Cambiar connection string del tenant en service discovery
8. Borrar datos del tenant en pooled tras verificación (grace period 30 días)
```

Herramientas: **pg_dump**, **Debezium**, **HAProxy/PgBouncer** para el switch de conexión.

---

## 5. Consideraciones de seguridad adicionales

### 5.1 Roles Postgres separados

```sql
-- Rol aplicativo (usado por el backend; sujeto a RLS)
CREATE ROLE app_role NOLOGIN;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_role;

-- Rol admin (ETL, reports internos; bypass RLS con BYPASSRLS)
CREATE ROLE admin_role NOLOGIN BYPASSRLS;

-- Usuarios concretos heredan rol
CREATE USER api_user LOGIN PASSWORD 'xxx' IN ROLE app_role;
CREATE USER etl_user LOGIN PASSWORD 'yyy' IN ROLE admin_role;
```

### 5.2 Columnas sensibles: cifrado a nivel de campo

Datos ultra-sensibles (CCI bancaria, número de cuenta CTS, salud mental) van cifrados antes de insertar. Uso típico: `pgcrypto` con clave por tenant derivada de master key en KMS.

```sql
-- Ejemplo: cifrado columnar con pgcrypto
INSERT INTO empleados_banco (empleado_id, cci_encrypted)
VALUES ($1, pgp_sym_encrypt($2::text, current_setting('app.tenant_key')));

SELECT pgp_sym_decrypt(cci_encrypted, current_setting('app.tenant_key')) AS cci
FROM empleados_banco WHERE empleado_id = $1;
```

### 5.3 Auditoría transversal

Toda tabla transaccional debe tener:

```sql
created_at TIMESTAMP NOT NULL DEFAULT NOW(),
created_by UUID NOT NULL,
updated_at TIMESTAMP,
updated_by UUID,
deleted_at TIMESTAMP,         -- soft delete
deleted_by UUID
```

Adicionalmente, tabla `audit_log` global con trigger `AFTER INSERT/UPDATE/DELETE` que captura cada cambio. Este audit log es obligatorio para cumplir Art. 9 Ley 29733 (trazabilidad del tratamiento de datos personales) y SUNAFIL (trazabilidad de planilla).

---

## 6. Integración con el proyecto INTRANET existente

Al revisar `github.com/p4ranoic0/INTRANET`, la extensión recomendada preserva el trabajo ya hecho:

1. **Fase preparación**: identificar tablas actuales y agregar columna `tenant_id` nullable. Backfill con un tenant default.
2. **Fase doble escritura**: nuevas inserciones llevan `tenant_id`, lecturas filtran por él con flag feature.
3. **Fase validación**: pruebas en staging con 2+ tenants simulados; ejecutar suite completa.
4. **Fase activación**: hacer `tenant_id` NOT NULL, activar RLS, quitar feature flag.
5. **Fase hardening**: migrar índices a incluir `tenant_id` como primer campo, reescribir queries ORM afectadas.

Tiempo estimado para una aplicación mediana: 3-6 semanas con feature flag + canary releases.

---

## 7. Checklist de cumplimiento operacional

- [ ] Toda tabla con datos de negocio tiene `tenant_id NOT NULL`
- [ ] Todos los índices importantes empiezan por `tenant_id`
- [ ] Todas las unicidades lógicas son compuestas con `tenant_id`
- [ ] RLS ENABLED y FORCE en todas las tablas de negocio
- [ ] Policy de tenant isolation creada en todas las tablas
- [ ] Rol `app_role` sin BYPASSRLS
- [ ] Middleware backend inyecta `tenant_id` en cada request
- [ ] Hook en pool de conexiones setea `app.tenant_id`
- [ ] Pruebas automáticas verifican que tenant A no vea datos de tenant B
- [ ] Audit log captura cambios con tenant_id + user_id + timestamp
- [ ] Columnas sensibles cifradas con clave por tenant
- [ ] Plan de upgrade a DB dedicada documentado
- [ ] Backups respetan aislamiento (no mezclan dumps de tenants en archivo único)

---

## 8. Referencias técnicas clave

- PostgreSQL docs: [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- Patrón Multi-Tenant SaaS: [AWS SaaS Lens](https://docs.aws.amazon.com/wellarchitected/latest/saas-lens/)
- Debezium CDC: [debezium.io](https://debezium.io/)
- PgBouncer para pool + failover: [pgbouncer.github.io](https://www.pgbouncer.github.io/)
