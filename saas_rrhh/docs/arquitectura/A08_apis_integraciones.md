# A08. APIs, Webhooks e Integraciones

> Estrategia de exposición de capacidades hacia clientes, integradores y sistemas gubernamentales peruanos (SUNAT, AFPnet, bancos, SERVIR, MINTRA). Enfoque **API-first** para competir contra Buk/Talana/Ofisis en apertura.

---

## 1. Principios

1. **API-first**: todo lo que hace la UI lo hace la API. La UI consume la misma API pública.
2. **REST como baseline + GraphQL opcional** para consumos complejos (reporting dashboards).
3. **Webhooks salientes** para notificar a sistemas externos sin polling.
4. **Idempotencia** en operaciones de escritura críticas (Idempotency-Key header).
5. **Versionado** por URL (`/v1/...`, `/v2/...`).
6. **Autenticación OAuth 2.0 + API Keys** para servidores.
7. **Rate limits** por tier y por endpoint.

---

## 2. Estructura de la API REST

### 2.1 Convenciones

- Base URL por tenant: `https://api.miapp.pe/v1/` (el tenant se resuelve por token).
- Recursos en plural: `/empleados`, `/planillas`, `/contratos`.
- Filtros en query: `?estado=activo&area_id=UUID&page=2&limit=50`.
- Paginación: cursor-based (`?cursor=abc`) preferido sobre offset para data grande.
- Respuestas en JSON con envolvente:

```json
{
  "data": [ ... ],
  "meta": { "total": 1234, "next_cursor": "xyz", "updated_at": "2026-04-19T12:00:00Z" },
  "links": { "self": "...", "next": "..." }
}
```

### 2.2 Endpoints núcleo

```
# Empleados
GET    /v1/empleados                    # listar con filtros
POST   /v1/empleados                    # crear
GET    /v1/empleados/{id}               # obtener detalle
PATCH  /v1/empleados/{id}               # actualización parcial
DELETE /v1/empleados/{id}               # baja (soft-delete)
POST   /v1/empleados/{id}/activar       # reactivar

# Contratos
GET    /v1/contratos?empleado_id={id}
POST   /v1/contratos
POST   /v1/contratos/{id}/renovar
POST   /v1/contratos/{id}/cesar         # registra cese + calcula liquidación

# Planilla
GET    /v1/planillas?periodo=2026-04
POST   /v1/planillas                    # abre período
POST   /v1/planillas/{id}/calcular
POST   /v1/planillas/{id}/aprobar
POST   /v1/planillas/{id}/cerrar

# Recibos / Boletas
GET    /v1/recibos?empleado_id={id}&periodo=2026-04
GET    /v1/recibos/{id}/pdf             # PDF firmado digitalmente
POST   /v1/recibos/{id}/reenviar-email

# Ausencias
GET    /v1/solicitudes-ausencia
POST   /v1/solicitudes-ausencia
POST   /v1/solicitudes-ausencia/{id}/aprobar

# Tablas paramétricas SUNAT
GET    /v1/parametros/tabla/{numero}    # Tabla Anexo 2 SUNAT
GET    /v1/parametros/vigentes          # UIT, RMV, URP, tasas AFP, EsSalud
```

### 2.3 Endpoints de exportadores peruanos

```
POST   /v1/export/plame?periodo=2026-04        # genera archivos Anexo 3 SUNAT
POST   /v1/export/tregistro?tipo=alta&emp={id}
POST   /v1/export/afpnet?periodo=2026-04&afp=PROFUTURO
POST   /v1/export/bancos?periodo=2026-04&banco=BCP&producto=planilla
GET    /v1/export/historial                     # log de exportaciones
```

### 2.4 Webhooks entrantes

```
POST   /v1/webhooks/biometricos                 # ingesta ZKTeco / Hikvision
POST   /v1/webhooks/candidatos                  # ATS externo
POST   /v1/webhooks/firma-electronica/callback  # Llama.pe, Digiflow
```

---

## 3. Autenticación y autorización

### 3.1 Esquemas soportados

| Esquema | Uso | Headers |
|---|---|---|
| **OAuth 2.0 Bearer** (access_token) | UI web/móvil | `Authorization: Bearer eyJ...` |
| **API Key + Secret** (server-to-server) | Integraciones backend | `X-API-Key: xxx`, `X-API-Secret-Hash: yyy` |
| **JWT con claims** (B2B SSO) | Integradores que hacen passthrough | `Authorization: Bearer eyJ...` con iss=integrador |

### 3.2 Scopes

Las API keys se emiten con scopes limitados:

```
empleados:read
empleados:write
planilla:read
planilla:calculate
planilla:approve
export:plame
export:afpnet
webhooks:manage
```

### 3.3 Rotación de credenciales

- API Keys expiran cada 90 días por default (configurable).
- Endpoint de rotación sin downtime: viejo y nuevo válidos 24h.
- Audit log de uso por key.

---

## 4. Rate limiting y quotas

| Tier | Requests/min | Requests/día | Export PLAME/mes |
|---|---|---|---|
| Starter | 60 | 10,000 | 3 |
| Pro | 300 | 100,000 | ilimitado |
| Enterprise | 2,000 | 1,000,000 | ilimitado |
| GovTech | Custom | Custom | ilimitado |

Headers de respuesta estándar:

```
X-RateLimit-Limit: 300
X-RateLimit-Remaining: 247
X-RateLimit-Reset: 1713549600
Retry-After: 45    # solo en 429
```

---

## 5. Webhooks salientes (notificaciones hacia el cliente)

### 5.1 Eventos publicables

```
employee.created
employee.updated
employee.terminated
contract.expiring_soon              # 30 días antes del vencimiento
payroll.period_opened
payroll.calculated
payroll.approved
payroll.paid
payslip.generated
absence.requested
absence.approved
pad.opened                          # PAD abierto (sector público)
training.completed
evaluation.closed
```

### 5.2 Formato del payload

```json
{
  "event_id": "evt_01H...",
  "event_type": "payroll.calculated",
  "timestamp": "2026-04-19T12:00:00Z",
  "tenant_id": "...",
  "data": {
    "payroll_id": "...",
    "periodo": "2026-04",
    "total_empleados": 127,
    "total_bruto": 523450.00,
    "total_neto": 412233.50
  },
  "signature": "sha256=..."
}
```

### 5.3 Garantías

- **At-least-once**: reintento con backoff exponencial (1s, 5s, 30s, 2min, 10min, 1h).
- **Firmado HMAC**: `X-Signature: sha256=...` usando secreto compartido.
- **Dead letter queue**: eventos que fallan 10 veces van a DLQ y se notifica al admin.
- **Replay**: endpoint `POST /v1/webhooks/{id}/replay?from={event_id}` para reenvío manual.

---

## 6. Integraciones gubernamentales peruanas

### 6.1 SUNAT T-Registro y PLAME

No hay API real de SUNAT para declaración automatizada; la integración es por **generación de archivos .txt del Anexo 3** + upload manual a través del PDT PLAME. El SaaS genera los archivos y los valida internamente replicando las reglas del PVS.

### 6.2 AFPnet

La carga al portal AFPnet es por archivo Excel con layout específico. Se genera y se entrega al cliente; opcionalmente se automatiza el upload vía RPA (Puppeteer/Playwright headless) en tier Enterprise.

### 6.3 SBS — tasas AFP vigentes

La SBS publica tasas AFP trimestralmente en su portal. Se implementa un **scraper programado mensual** que actualiza la tabla `parametros_vigentes` y emite evento `ParametroActualizado`.

### 6.4 BCR/SBS — tipo de cambio

Fuente oficial para expatriados con salario en USD/EUR: `https://www.bcrp.gob.pe/estadisticas/cuadros-anuales-historicos.html` (parse) o la API JSON de la SBS de Tipo de Cambio.

### 6.5 SERVIR — sector público

SERVIR no expone API pública, pero gestiona el Aplicativo Informático AIRHSP (Registro de Datos de Recursos Humanos del Sector Público). La integración es por carga de archivos periódica. En tier GovTech se incluye el conector.

### 6.6 Bancos (archivos de pago masivo)

Cada banco tiene formato propio (TXT/CSV con layout específico):

| Banco | Formato | Producto |
|---|---|---|
| BCP | Telecrédito (TXT) | Pago Planilla, Pago CTS |
| BBVA | Net Cash (TXT/XLS) | Planilla corriente |
| Scotiabank | Cash Management (TXT) | Planilla, CTS |
| Interbank | Netcash (TXT) | Planilla |

Se genera cada uno según preferencia del tenant.

### 6.7 Firma electrónica

Proveedores certificados por INDECOPI: **Llama.pe**, **Digiflow**, **Doc Sing**, **Adobe Sign (con certif. peruano)**. Integración vía REST API para firmar contratos, recibos, certificados de trabajo.

---

## 7. GraphQL complementario

Para dashboards complejos donde REST genera N+1 queries, se expone un endpoint `/graphql` con esquema parcial:

```graphql
type Query {
  empleado(id: ID!): Empleado
  empleados(filtros: EmpleadoFiltros, paginacion: PaginacionInput): EmpleadoConnection
  planillaPeriodo(periodo: String!): Planilla
  kpisEmpresa(empresaId: ID!, periodo: String!): KPIsEmpresa
}

type Empleado {
  id: ID!
  codigo: String!
  nombres: String!
  area: Area
  cargo: Cargo
  contratos: [Contrato!]!
  ausencias(desde: Date, hasta: Date): [Ausencia!]!
  recibosUltimos(cantidad: Int = 3): [ReciboResumen!]!
}
```

Disponible en tier Enterprise y GovTech.

---

## 8. SDK y documentación

### 8.1 SDKs oficiales

Libraries en 3 lenguajes (minimum):

- **Python** (`pip install miapp-sdk`)
- **Node.js / TypeScript** (`npm install @miapp/sdk`)
- **PHP** (para integradores del mercado peruano)

Cada SDK wraps auth, rate limiting, retries, tipados.

### 8.2 Documentación interactiva

- **OpenAPI 3.1** completo (`/openapi.yaml`).
- Portal de desarrolladores (`developers.miapp.pe`) con:
  - Swagger UI / Redoc
  - Postman collections
  - Guías paso a paso (`quickstarts`)
  - Recipes por integración común
  - Sandbox público con datos demo

---

## 9. Outbox Pattern para consistencia

Para garantizar que un evento webhook se publica **si y solo si** la transacción BD fue exitosa:

```sql
CREATE TABLE outbox (
  id UUID PRIMARY KEY,
  tenant_id UUID NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  payload JSONB NOT NULL,
  created_at TIMESTAMP DEFAULT NOW(),
  dispatched_at TIMESTAMP,
  dispatch_attempts INT DEFAULT 0,
  last_error TEXT
);
```

La lógica de negocio inserta en outbox en la **misma transacción** que los cambios de negocio. Un proceso daemon lee outbox y publica al bus/webhooks. Fallas se reintentan.

---

## 10. Versionado de API

- **URL-based**: `/v1/...`, `/v2/...`.
- **Breaking changes** (renombrar campos, eliminar endpoints): nueva versión mayor.
- **Non-breaking** (agregar campos opcionales): versión actual.
- **Deprecation policy**: 12 meses de aviso antes de sunset. Header `Sunset: Wed, 11 Nov 2026 23:59:59 GMT`.

---

## 11. Monitoreo y observabilidad

- **Traces distribuidos** con OpenTelemetry + Jaeger/Datadog.
- **Métricas** por endpoint: latency p50/p95/p99, error rate, throughput.
- **Logs estructurados** JSON con `trace_id`, `tenant_id`, `user_id` para correlación.
- **SLI/SLO publicados** en status page (`status.miapp.pe`).

---

## 12. Checklist

- [ ] OpenAPI 3.1 auto-generado desde código
- [ ] Versionado URL `/v1/`
- [ ] Autenticación OAuth 2.0 + API Keys
- [ ] Rate limits con headers estándar
- [ ] Webhooks firmados HMAC con reintentos
- [ ] Outbox pattern para consistencia de eventos
- [ ] Exportadores PLAME, T-Registro, AFPnet, 4 bancos principales
- [ ] Conector SBS para tasas AFP
- [ ] SDK Python, Node/TS, PHP
- [ ] Portal `developers.miapp.pe` con sandbox
- [ ] Traces OpenTelemetry
- [ ] Status page pública con SLIs
