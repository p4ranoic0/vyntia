# A01 — Arquitectura General del SaaS

> **Audiencia:** agente de desarrollo, arquitectos, tech leads
> **Base existente:** [github.com/p4ranoic0/INTRANET](https://github.com/p4ranoic0/INTRANET) — se asume stack actual y se propone evolución hacia arquitectura modular SaaS multi-tenant.

---

## 1. Principios arquitectónicos

### 1.1 Los 10 principios guía
1. **Metadata-driven**: configurabilidad sin fork de código (inspirado en Frappe DocType)
2. **Modular desacoplado**: cada módulo se vende, habilita y escala independiente
3. **Multi-tenant desde día 1**: RLS Postgres + tenant_id en toda tabla
4. **Cumplimiento normativo por diseño**: la lógica peruana es ciudadano de primera clase
5. **Auditabilidad total**: event sourcing en contextos críticos (Payroll)
6. **APIs abiertas**: REST + GraphQL + webhooks como ciudadanos de primera clase
7. **Mobile-first para empleados**: app móvil no es add-on, es canal principal
8. **Internacional pero peruano**: i18n + enfoque intercultural (lenguas originarias)
9. **Seguridad por capas**: RBAC + ABAC + RLS + cifrado en reposo y tránsito
10. **Escalabilidad horizontal**: stateless, idempotente, cache-friendly

### 1.2 Decisión fundamental: monolito modular primero, microservicios después
- Se arranca con **monolito modular** bien estructurado (bounded contexts) para velocidad de entrega
- Cuando un módulo justifique el costo (volumen, equipo dedicado, SLA distinto), se extrae como microservicio
- Candidatos iniciales a extracción: Payroll (por su complejidad), ATS (por integraciones externas), Analytics (por cargas distintas)

---

## 2. Stack tecnológico recomendado

### 2.1 Backend
| Componente | Tecnología recomendada | Alternativa |
|------------|-------------------------|-------------|
| Lenguaje | **Python 3.12+** (FastAPI/Django) | TypeScript (NestJS) |
| Framework web | **FastAPI** (async-first) o Django 5 | NestJS |
| ORM | SQLAlchemy 2 + Alembic (si FastAPI) / Django ORM | Prisma/TypeORM |
| Auth | Keycloak (self-hosted) | Auth0 (SaaS) |
| Queue/Tasks | Celery + Redis | RQ, Dramatiq |
| Cache | Redis | Memcached |
| Event Bus | RabbitMQ o Apache Kafka | Redis Streams |

### 2.2 Base de datos
| Componente | Tecnología |
|------------|-----------|
| Principal | **PostgreSQL 15+** con Row-Level Security |
| Documentos | PostgreSQL JSONB (no necesita MongoDB separado) |
| Búsqueda | PostgreSQL FTS o Elasticsearch (si se justifica) |
| Analytics/OLAP | PostgreSQL + materialized views; Clickhouse si vol muy alto |
| Time-series (logs, métricas) | TimescaleDB (extensión PG) o Prometheus |

### 2.3 Frontend
| Componente | Tecnología |
|------------|-----------|
| Framework | **React 18 + Next.js 14** (App Router) o Vue/Nuxt |
| UI components | shadcn/ui + Tailwind CSS |
| Estado | Zustand o Redux Toolkit |
| Forms | React Hook Form + Zod |
| Tablas | TanStack Table |
| Gráficos | Recharts o ECharts |
| i18n | react-i18next |

### 2.4 Mobile
| Componente | Tecnología |
|------------|-----------|
| Framework | **React Native** (compartir código con web) o Flutter |
| Biometría | react-native-biometrics |
| Geolocalización | react-native-geolocation |
| Push | Firebase Cloud Messaging |
| Reconocimiento facial | ML Kit / AWS Rekognition |

### 2.5 Infraestructura
| Componente | Tecnología |
|------------|-----------|
| Contenedores | Docker + Kubernetes |
| IaC | Terraform + Helm |
| Cloud | AWS (preferido por cobertura AWS Perú en LATAM) o Azure |
| CDN | CloudFront o Cloudflare |
| Storage | S3 (o MinIO self-hosted) |
| Secrets | AWS Secrets Manager / HashiCorp Vault |
| CI/CD | GitHub Actions + ArgoCD |
| Observabilidad | Prometheus + Grafana + Loki + Tempo |

### 2.6 Seguridad
| Componente | Tecnología |
|------------|-----------|
| WAF | Cloudflare WAF o AWS WAF |
| SAST | SonarQube + Snyk |
| DAST | OWASP ZAP |
| Secrets scanning | GitGuardian / git-secrets |
| Cifrado en reposo | AWS KMS + PG-crypto para campos sensibles |
| Cifrado en tránsito | TLS 1.3 mínimo |

---

## 3. Arquitectura de capas

```
┌─────────────────────────────────────────────────────────┐
│  Clientes: Web (Next.js) | Mobile (React Native) | APIs │
└─────────────────────────────────────────────────────────┘
                           │
                    [API Gateway]
                  (rate limit, auth)
                           │
┌──────────────────────────────────────────────────────────┐
│                  CAPA DE APLICACIÓN                      │
│                                                          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐        │
│  │ Module  │ │ Module  │ │ Module  │ │ Module  │  ...   │
│  │   01    │ │   02    │ │   03    │ │   04    │        │
│  │Polícias │ │ Puestos │ │ Empleo  │ │Planilla │        │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘        │
│                                                          │
│       [Workflow Engine]  [Permission System]            │
│       [Notification Svc] [Document Svc]                 │
│       [Event Bus (RabbitMQ)]                             │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│                   CAPA DE DATOS                          │
│  PostgreSQL (OLTP + RLS) | Redis (cache) | S3 (files)   │
│  Event Store (Payroll)   | Timescale (metrics)          │
└──────────────────────────────────────────────────────────┘
                           │
┌──────────────────────────────────────────────────────────┐
│              CAPA DE INTEGRACIÓN                         │
│  SUNAT | AFPnet | EsSalud | SBS | Bancos                │
│  Biométricos ZKTeco | Firma Digital | Email | Push      │
└──────────────────────────────────────────────────────────┘
```

---

## 4. Bounded Contexts (DDD)

Cada módulo del SaaS es un bounded context con su propio modelo de dominio, lenguaje ubicuo y equipo (si aplica).

| Bounded Context | Agregado raíz | Eventos principales |
|-----------------|---------------|---------------------|
| **Identity & Access** | `User` | UserRegistered, UserDeactivated, RoleAssigned |
| **Organization** | `Tenant`, `OrgUnit` | TenantCreated, OrgRestructured |
| **Employee Management** | `Employee`, `Contract` | EmployeeHired, ContractSigned, EmployeeTerminated |
| **Time & Attendance** | `AttendanceRecord`, `Schedule` | ShiftScheduled, AttendanceMarked |
| **Leave Management** | `LeaveRequest` | LeaveRequested, LeaveApproved |
| **Payroll** | `PayrollRun`, `Payslip` | PayrollStarted, PayslipCalculated, PayslipPaid |
| **Compensation & Benefits** | `SalaryStructure`, `Benefit` | SalaryReviewed, BenefitGranted |
| **Performance** | `EvaluationCycle` | EvaluationLaunched, FeedbackSubmitted |
| **Learning & Development** | `TrainingProgram` | TrainingCompleted |
| **Recruitment** | `JobPosting`, `Candidate` | PositionOpened, CandidateHired |
| **SST** | `IPERCMatrix`, `Accident` | RiskAssessed, AccidentReported |
| **Engagement** | `ClimateSurvey`, `Campaign` | SurveyLaunched, ResponseCollected |

### 4.1 Comunicación entre contextos
- **Síncrona (query):** API interna con contracts bien definidos
- **Asíncrona (comandos):** mensajes en RabbitMQ/Kafka
- **Eventos de dominio:** publicados al event bus para cualquier interesado
- **Anticorruption Layer**: cada contexto traduce conceptos externos a su modelo

---

## 5. Metadata-driven: el patrón DocType

Inspirado en Frappe HR, cada entidad de dominio se define por un **descriptor JSON** que genera:
- Esquema de tabla SQL
- Contrato API REST
- Formulario UI
- Permisos por campo (permission levels)
- Workflow asociado
- Print template

### 5.1 Ejemplo: descriptor de `Employee`
```json
{
  "doctype": "Employee",
  "module": "employee_management",
  "fields": [
    {
      "fieldname": "employee_code",
      "label": "Código",
      "fieldtype": "Data",
      "required": true,
      "unique": true,
      "permlevel": 0
    },
    {
      "fieldname": "dni",
      "label": "DNI",
      "fieldtype": "Data",
      "required": true,
      "validator": "dni_peru",
      "permlevel": 3
    },
    {
      "fieldname": "cci",
      "label": "CCI Bancario",
      "fieldtype": "Data",
      "permlevel": 9,
      "encrypted": true
    },
    {
      "fieldname": "health_data",
      "label": "Datos Médicos",
      "fieldtype": "JSON",
      "permlevel": 9,
      "encrypted": true,
      "sensitive": true
    }
  ],
  "permissions": [
    { "role": "Employee", "read": 0, "write": 0 },
    { "role": "Manager", "read": 3, "write": 3 },
    { "role": "HR Officer", "read": 6, "write": 6 },
    { "role": "Payroll Officer", "read": 9, "write": 9 }
  ],
  "workflow": "employee_lifecycle"
}
```

### 5.2 Ventajas del enfoque
- **Configurabilidad por tenant** sin cambiar código
- **Custom fields** reales (columnas en la DB, no EAV)
- **APIs auto-generadas** con la forma estable del descriptor
- **Validación centralizada**
- **Auditoría uniforme**

### 5.3 Implementación en Python (esbozo)
```python
class DocTypeEngine:
    def register_doctype(self, descriptor: dict):
        # 1. Genera modelo SQLAlchemy dinámico
        model = self._build_model(descriptor)
        # 2. Genera migración Alembic
        migration = self._generate_migration(descriptor)
        # 3. Registra endpoints FastAPI
        self._register_routes(descriptor, model)
        # 4. Registra en permission system
        self._register_permissions(descriptor)
        # 5. Registra workflow si existe
        if descriptor.get('workflow'):
            self.workflow_engine.register(descriptor['workflow'])
```

---

## 6. Multi-tenancy

Ver detalle completo en `A02_multitenancy_rls.md`. Resumen:

### 6.1 Estrategia pooled + RLS (baseline)
- Todas las tablas tienen columna `tenant_id UUID NOT NULL`
- Policy RLS Postgres filtra automáticamente por `current_setting('app.tenant_id')`
- Middleware de aplicación setea el `tenant_id` en cada request
- Índices compuestos `(tenant_id, ...)` para performance

### 6.2 Tier premium: DB dedicada
- Clientes grandes, regulados o con data residency específica
- Schema idéntico, base aislada
- Mayor costo, mayor aislamiento

### 6.3 Ejemplo de policy RLS
```sql
CREATE POLICY tenant_isolation ON employees
  USING (tenant_id = current_setting('app.tenant_id')::uuid);

ALTER TABLE employees ENABLE ROW LEVEL SECURITY;
```

---

## 7. Sistema de permisos (RBAC + ABAC + permlevel)

Ver detalle completo en `A04_rbac_permisos.md`. Resumen:

### 7.1 Capas de permisos
1. **Role-based (RBAC)**: matriz rol × doctype × acción
2. **Permission Levels 0-9 por campo**: granularidad fina
3. **User Permissions (ABAC)**: restricción a valores específicos (ej. solo mi área)
4. **Document sharing**: compartir documento específico temporalmente

### 7.2 Roles base predefinidos
```
- System Administrator (tenant admin)
- HR Director
- HR Officer
- Payroll Officer
- Recruiter
- Training Coordinator
- SST Coordinator
- Manager (jefe directo)
- Employee (base)
- Government Officer (sector público — accesos específicos)
```

---

## 8. Motor de workflows

Ver detalle completo en `A03_motor_workflows.md`. Resumen:

- Workflows declarativos: State Machine con states + transitions + conditions + actions
- Cada tenant puede personalizar workflows
- Integración con notificaciones, emails y tareas pendientes
- Alternativa avanzada: **Flowable** (Apache 2.0) para BPMN riguroso

---

## 9. Event Sourcing acotado al Payroll

Ver detalle en `A06_event_sourcing_payroll.md`. Solo **Payroll** usa event sourcing (el resto CRUD + audit log clásico):

- Event Store en Postgres (tabla `payroll_events`)
- Proyecciones en tablas read-model
- Snapshots cada N eventos para performance
- Replay para recálculos retroactivos

---

## 10. APIs

Ver detalle en `A08_apis_integraciones.md`. Resumen:

### 10.1 API externa pública
- **REST** (OpenAPI 3.1) para operaciones CRUD
- **GraphQL** (opcional) para queries complejas de frontend
- **Webhooks** para notificación de eventos a sistemas cliente
- **SDKs** oficiales: Python, Node.js, PHP

### 10.2 Autenticación
- OAuth 2.0 + OpenID Connect
- API Keys para server-to-server
- JWT con expiración corta + refresh tokens

### 10.3 Integraciones críticas
- SUNAT (T-Registro, PLAME) - generación de archivos + API cuando esté disponible
- AFPnet (.xlsx)
- SBS (tasas AFP)
- Bancos (telecrédito BCP, BBVA, Interbank, Scotiabank)
- Biométricos (ZKTeco SDK)
- Firma digital (Llama.pe, Digiflow, Sunarp)
- Email (SES/SendGrid)
- SMS/WhatsApp (Twilio, Meta Business)

---

## 11. Observabilidad y operaciones

### 11.1 Logs
- Structured logging (JSON)
- Correlación con `request_id`, `tenant_id`, `user_id`
- Agregación en Loki o CloudWatch
- Retención: 90 días hot + 1 año cold

### 11.2 Métricas
- Prometheus + Grafana
- Métricas por tenant
- SLIs: latencia p95/p99, error rate, throughput
- Alertas: PagerDuty / Opsgenie

### 11.3 Tracing distribuido
- OpenTelemetry
- Tempo / Jaeger
- Tracing de cálculos de planilla largos

### 11.4 Backups
- Postgres: WAL-G continuo + snapshots diarios + retention 30 días
- S3: versioning + replicación cross-region
- Prueba de restore mensual

---

## 12. Evolución desde INTRANET actual

### 12.1 Plan de migración recomendado
1. **Auditoría del repositorio actual** — mapear módulos existentes, stack, convenciones
2. **Refactor a bounded contexts** — separar módulos con boundaries claros
3. **Introducir tenant_id + RLS** — baseline multi-tenant
4. **Extraer motor de planilla a módulo con event sourcing**
5. **Construir DocType engine** — habilitar configurabilidad
6. **Migrar módulos uno por uno** al nuevo paradigma
7. **Lanzar plan Starter** en paralelo a legacy
8. **Sunset progresivo del legacy**

### 12.2 Riesgos técnicos
- Migración de datos legacy a nuevo modelo
- Incompatibilidades de lógica de negocio histórica
- Resistencia al cambio del equipo

### 12.3 Mitigación
- Strangler Fig Pattern: nuevo sistema coexiste con legacy, va absorbiendo módulos
- Testing de regresión exhaustivo de planillas calculadas
- Comparación lado a lado durante 3 meses

---

## 13. Referencias
- [Frappe Framework Docs](https://frappeframework.com/docs)
- [DDD - Eric Evans](https://www.domainlanguage.com/ddd/)
- [Event Sourcing - Martin Fowler](https://martinfowler.com/eaaDev/EventSourcing.html)
- [PostgreSQL RLS](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [The Twelve-Factor App](https://12factor.net/)

---

## 14. MDs relacionados
- `A02_multitenancy_rls.md`
- `A03_motor_workflows.md`
- `A04_rbac_permisos.md`
- `A05_campos_personalizados.md`
- `A06_event_sourcing_payroll.md`
- `A07_strategy_regimenes.md`
- `A08_apis_integraciones.md`
