# API Contract Audit — Post-L3.10.4f State

> **Purpose:** Map every backend JSON contract to the corresponding frontend TS interface, identifying which fields need rename for **L3.10.4d** (state fields → `status` / `is_active`) and **L3.10.4e** (PK rename → `id` UUID string).
>
> **Generated:** 2026-04-29 (post-L3.10.4f merge `3ed2e7d3`)
>
> **Source:** Read directly from backend serializers + models. Not from runtime curl (avoids needing auth + fixtures).

---

## Methodology

For each entity audited, we read:

1. The **DRF serializer** (source of truth for JSON keys emitted) — file path + line numbers.
2. The **Django model** to confirm field types (UUID vs int) and Python attribute names — file path + line numbers.
3. The **frontend TypeScript interface** that consumes the contract — file path + line numbers.

Then, for each field, we mark:

- **MATCH** — frontend declaration matches backend JSON key emitted.
- **MISMATCH** — frontend declaration does NOT match what the backend emits (relies on normalizer or is broken).
- **PRESERVED-SPANISH** — domain HR field, kept Spanish per spec § 3.6.1 Option B (no rename planned).
- **PLATFORM-RENAMED** — generic platform field that was renamed by L3.10.2 (`status`, `is_active`, `created_at`, `updated_at`).
- **PRESERVED-SPANISH-STATE** — entity-specific state field (`estado_*`) that the L3.10.2 rename **skipped** but a future L3.10.4d may rename to `status`.

Caveats:

- Models all have `id = UUIDField(primary_key=True)` post-L3.10.2. The serializers expose this UUID as the JSON key `id` (default DRF behavior).
- Many serializers expose computed booleans like `es_activo` — these are derived from the `status` / `estado_*` field.
- Frontend interfaces still use `<entity>_id: number` (old contract). After L3.10.2, the backend emits ONLY `id` (UUID string). The frontend normalizers paper over this by reading both keys, but the interfaces are wrong.

---

## Summary table

| # | Entity | Backend serializer | Primary FE interface | State-field rename status (for L3.10.4d) | PK rename status (for L3.10.4e) |
|---|---|---|---|---|---|
| 1 | Employee | `serializers.py:483-593` `EmpleadoSerializer` | `employeesService.ts:9-42` `Employee` | preserved-Spanish (`estado_empleado`) | UUID — FE has `id: number` (MISMATCH) |
| 2 | Department | `serializers.py:36-108` `AreaSerializer` / `AreaListSerializer` | `departmentsService.ts:4-15` `Area` | preserved-Spanish-state (`estado_area`) | UUID — FE has `area_id: number` (MISMATCH) |
| 3 | User | `serializers.py:786-848` `UsuarioSerializer` | `usersService.ts:10-38` `User`, `lib/api.ts:24-47` `User` | platform-renamed (`is_active`) + preserved (`estado_usuario`) | UUID — FE has `id: number` + `usuario_id: number` (MISMATCH) |
| 4 | Role | `serializers.py:914-952` `RolSerializer` | `usersService.ts:40-50` `Role`, `securityService.ts:27-35` `Role`, `lib/api.ts:9-14` `Role` | preserved-Spanish-state (`estado_rol`) — normalizer also adds `is_active` | UUID — FE has `id: number` + `rol_id: number` (MISMATCH) |
| 5 | Permission | `serializers.py:955-971` `PermisoSerializer` | `usersService.ts:52-59` `Permission`, `securityService.ts:37-46` `Permission`, `lib/api.ts:16-22` `Permission` | preserved-Spanish-state (`estado_permiso`) | UUID — FE has `permiso_id: number` (MISMATCH) |
| 6 | Module | `serializers.py:974-1018` `ModulosSerializer` | `securityService.ts:48-53` `Module` (mostly stub) | preserved-Spanish-state (`estado_modulo`) | UUID — FE has `id: number` (MISMATCH) |
| 7 | RolePermission | `serializers.py:1021-1064` `RolPermisosSerializer` | `securityService.ts:55-65` `RolePermission` | N/A (no state field) | UUID — FE has `rol_permiso_id: number` (MISMATCH); also serializer has duplicate `'id'` bug |
| 8 | UserRole | `usuario_roles_serializers.py:13-86` `UsuarioRolesSerializer` | (no top-level FE interface — used as nested in User normalizer) | preserved-Spanish-state (`estado_asignacion`) | UUID — backend exposes `id` |
| 9 | Contract | `contratos_serializers.py:22-81` `ContratosAdendasSerializer` | `contractsService.ts:4-48` `Contrato` | platform-renamed (`status`) — FE still has `estado: string` | UUID — FE has `contrato_id: number` (MISMATCH) |
| 10 | ContractAmendment | `contratos_serializers.py:256-285` `ContractAmendmentSerializer` | (no dedicated FE interface — folded into `Contrato`) | platform-renamed (`status`) | UUID — same situation |
| 11 | EmploymentData | `serializers.py:250-340` `DatosLaboralesSerializer` | `employeesService.ts:68-82` `DatosLaborales` | preserved-Spanish-state (`estado_datos`) | UUID — FE has `id?: number` (MISMATCH) |
| 12 | FamilyMember | `serializers.py:111-167` `DatosFamiliaresSerializer` | `employeesService.ts:84-95` `DatosFamiliares` | preserved-Spanish-state (`estado_familiar`) | UUID — FE has `id?: number` (MISMATCH) |
| 13 | AcademicRecord | `serializers.py:170-223` `DatosAcademicosSerializer` | `employeesService.ts:97-107` `DatosAcademicos` | preserved-Spanish-state (`estado_estudios` is domain, NOT platform) | UUID — FE has `id?: number` (MISMATCH) |
| 14 | Certification | `serializers.py:226-247` `CursosCertificacionesSerializer` | (no FE interface) | preserved-Spanish-state (`estado_registro`) | UUID — no FE consumer |
| 15 | DigitalDocument | `serializers.py:1112-1182` `DocumentosDigitalesSerializer` | `legajoService.ts:4-33` `Documento` | preserved-Spanish-state (`estado_documento`) | UUID — FE has `documento_id: number` (MISMATCH) |
| 16 | DocumentTemplate | (separate views — see `templatesService.ts` calls) | `templatesService.ts:10-20` `PlantillaDocumento` | platform-renamed (`activa: boolean`) | UUID — FE has `plantilla_id: number` (MISMATCH) |
| 17 | Company | `serializers.py:1322-1352` `ConfiguracionEmpresaSerializer` | `companyService.ts:3-20` `ConfiguracionEmpresa` | N/A (singleton, no state field) | int (singleton, `pk=1`) — FE has `id: number` (MATCH) |
| 18 | MonthlyPayroll | `remuneraciones_serializers.py:171-272` `PlanillaMensualListSerializer` / `PlanillaMensualDetailSerializer` | `payrollService.ts:114-140` `PlanillaMensual` | platform-renamed (`status` via `db_column='estado'`) — JSON emits `estado` (sourced via `get_status_display`) | UUID — FE has `planilla_id: number` (MISMATCH) |
| 19 | PayrollDetail | `remuneraciones_serializers.py:359-465` `DetallePlanillaListSerializer` / `DetallePlanillaDetailSerializer` | `payrollService.ts:150-194` `DetallePlanilla` | preserved-Spanish-state (`estado_laboral`, exposed via `source='estado_laboral'` as JSON key `estado`) | UUID — FE has `detalle_id: number` (MISMATCH) |
| 20 | Compensation (CompensationConfiguration) | `serializers.py:343-406` and `remuneraciones_serializers.py:137-163` `ConfiguracionRemuneracionSerializer` | `payrollService.ts:5-19` `ConceptoRemuneracion` | platform-renamed (`status` via `db_column='estado'`) — JSON emits `estado` | UUID — FE has `configuracion_id: number` (MISMATCH) |
| 21 | AfpConfiguration | `serializers.py:409-477` and `remuneraciones_serializers.py:33-56` `ConfiguracionAfpSerializer` | `payrollService.ts:39-52` `ConfiguracionAfp` | platform-renamed (`status` via `db_column='estado'`) — JSON emits `estado` | UUID — FE has `afp_config_id: number` (MISMATCH) |
| 22 | TaxParameter (UIT) | `remuneraciones_serializers.py:59-134` `ConfiguracionUitSerializer` | `payrollService.ts:65-80` `ConfiguracionUit` | platform-renamed (`status` via `db_column='estado'`) — JSON emits `estado` | UUID — FE has `configuracion_uit_id: number` (MISMATCH) |
| 23 | MassDeduction | `remuneraciones_serializers.py:512-583` `DescuentoMasivoListSerializer` / `DescuentoMasivoDetailSerializer` | `payrollService.ts:205-229` `DescuentoMasivo` | platform-renamed (`status` via `db_column='estado'`) — JSON emits `estado` | UUID — FE has `descuento_masivo_id: number` (MISMATCH) |
| 24 | Payslip (PaySlip) | `remuneraciones_serializers.py:611-697` `BoletaPagoListSerializer` / `BoletaPagoDetailSerializer` | `payrollService.ts:237-261` `BoletaPago` | platform-renamed (`status` via `db_column='estado'`) — JSON emits `estado` | UUID — FE has `boleta_id: number` (MISMATCH) |
| 25 | PaymentSchedule | `remuneraciones_serializers.py:705-771` `CalendarioPagoListSerializer` / `CalendarioPagoDetailSerializer` | `payrollService.ts:263-279` `CalendarioPago` | platform-renamed (`status` via `db_column='estado'`) — JSON emits `estado` | UUID — FE has `calendario_id: number` (MISMATCH) |
| 26 | VacationConfiguration | `vacaciones/serializers.py:29-87` `ConfiguracionVacacionesSerializer` | `timeOffService.ts:3-8` `ConfiguracionVacaciones` | platform-renamed (`is_active` with `db_column='activo'`) — JSON emits `activo` (because Meta.fields uses `'activo'` not `'is_active'`) — see CAVEAT | UUID — FE has `configuracion_id: number` (MISMATCH) |
| 27 | VacationPeriod | `vacaciones/serializers.py:90-149` `PeriodoVacacionalSerializer` | `timeOffService.ts:10-33` `PeriodoVacacional` | preserved-Spanish-state (`estado_periodo`) | UUID — FE has `periodo_id: number` (MISMATCH) |
| 28 | VacationRequest | `vacaciones/serializers.py:152-248` `SolicitudVacacionesSerializer` | `timeOffService.ts:35-67` `SolicitudVacaciones` | preserved-Spanish-state (`estado_solicitud`) | UUID — FE has `solicitud_id: number` (MISMATCH) |
| 29 | VacationGrant | `vacaciones/serializers.py:298-334` `GoceVacacionesSerializer` | `timeOffService.ts:69-78` `GoceVacaciones` | preserved-Spanish-state (`estado_goce`) | UUID — FE has `goce_id: number` (MISMATCH) |
| 30 | OnboardingProcess | `serializers.py:1217-1268` `OnboardingEmpleadoSerializer` | `onboardingService.ts:4-33` `OnboardingStatus` | preserved-Spanish-state (`estado_onboarding`) | UUID — FE has `onboarding_id: number` (MISMATCH) |

**Quick stats:**
- 22 of 30 entities have a UUID primary key — frontend declares them as `number` → all need L3.10.4e PK type change.
- 9 entities already had `status` rename (Contract, ContractAmendment, MonthlyPayroll, PayrollDetail-via-estado_laboral, Compensation, AfpConfiguration, TaxParameter, MassDeduction, PaySlip, PaymentSchedule). JSON still emits `estado` as the key (because of `db_column` and serializer field naming). The backend Python attribute is `status`. **L3.10.4d action: rename serializer field declaration from `'estado'` to `'status'` so JSON key matches.**
- 1 entity (VacationConfiguration) has `is_active` rename but exposes JSON key as `activo` (db_column).
- 11 entities have preserved-Spanish-state fields (`estado_<entity>` or similar) that L3.10.4d should leave alone OR rename to `status`. **Decision needed.**
- Frontend always reads via normalizer for User/Role/Employee — others read raw.

---

## Per-entity contracts

### 1. Employee (`apps.employees.Employee`)

**Backend:**
- Model: `apps/api/apps/employees/models/employee.py:18-303`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 91) — **UUID string PK**
  - `numero_documento = CharField(max_length=20, unique=True)` (92)
  - `tipo_documento = CharField(max_length=10, choices=TIPO_DOCUMENTO_CHOICES, default='DNI')` (93-95)
  - `nombres_empleado = CharField(max_length=100)` (96)
  - `apellido_paterno`, `apellido_materno = CharField(max_length=100)` (97-98)
  - `numero_ruc = CharField(max_length=20, null=True, blank=True)` (99)
  - `genero_empleado = CharField(...choices=GENERO_CHOICES)` (100)
  - `fecha_nacimiento = DateField(null=True, blank=True)` (101)
  - `es_padre_familia = BooleanField(default=False)` (102)
  - `es_militar = BooleanField(default=False)` (103)
  - `sistema_pensiones = CharField(...choices=SISTEMA_PENSIONES_CHOICES, default='ONP')` (104-106)
  - `tipo_comision = CharField(...null=True, blank=True)` (107-109)
  - `codigo_cuspp = CharField(max_length=20, null=True, blank=True)` (110)
  - `tipo_seguro_salud = CharField(...default='ESSALUD')` (111-113)
  - `centro_salud`, `direccion_centro_salud`, `departamento_centro_salud` (114-116)
  - `vigencia_estado_seguro = CharField(...default='activo')` (117-119) — **PRESERVED-SPANISH**
  - `tiene_suspension_renta_cuarta_vigente = BooleanField(default=False)` (122)
  - `fecha_inicio_suspension_renta`, `fecha_fin_suspension_renta = DateField(null=True, blank=True)` (126-131)
  - `documento_suspension_renta = FileField(...)` (132-137)
  - `telefono_fijo`, `telefono_celular`, `correo_personal` (140-142)
  - `estado_civil = CharField(...)` (145)
  - `direccion_domicilio`, `distrito_domicilio`, `provincia_domicilio`, `departamento_domicilio` (146-149)
  - `entidad_bancaria`, `numero_cuenta_bancaria`, `numero_cci` (152-154)
  - `tipo_sangre`, `talla_empleado`, `peso_empleado`, `ruta_fotografia` (157-166)
  - `estado_empleado = CharField(...choices=ESTADO_EMPLEADO_CHOICES, default='activo')` (169-171) — **PRESERVED-SPANISH-STATE**
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_registro')` (172) — **PLATFORM-RENAMED** (was `fecha_registro`)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (173)
- Primary serializers:
  - `EmpleadoSerializer` `apps/api/api/v1/rrhh/serializers.py:483-593` — list of fields at 501-532
  - `EmpleadoListSerializer` `serializers.py:595-663` — fields 605-627
  - `EmpleadoCreateSerializer` `serializers.py:674-750`
  - `EmpleadoSimpleCreateSerializer` `serializers.py:753-780`
  - `EmpleadoUpdateSerializer` `serializers.py:1070-1109`
- JSON keys emitted (`EmpleadoSerializer` read shape):
  - `id` (string UUID)
  - `nombres_empleado` (string) — domain Spanish, preserved
  - `apellido_paterno` (string) — domain Spanish, preserved
  - `apellido_materno` (string)
  - `numero_documento` (string, unique)
  - `fecha_nacimiento` (string ISO date | null)
  - `genero_empleado` (string, choices)
  - `estado_civil` (string)
  - `direccion_domicilio`, `distrito_domicilio`, `provincia_domicilio`, `departamento_domicilio` (strings)
  - `telefono_celular`, `correo_personal` (strings)
  - `es_padre_familia` (boolean)
  - `entidad_bancaria`, `numero_cuenta_bancaria`, `numero_cci` (strings)
  - `numero_ruc` (string | null)
  - `sistema_pensiones`, `tipo_comision`, `codigo_cuspp` (strings)
  - `estado_empleado` (string, choices) — domain Spanish, preserved-state
  - `nombre_completo` (string, ReadOnlyField from model property)
  - `edad` (int | null, ReadOnlyField)
  - `genero_texto` (string, ReadOnlyField)
  - `es_activo` (boolean, ReadOnlyField — derived from estado_empleado)
  - `datos_laborales_actuales` (nested DatosLaboralesSerializer | null) — **NESTED**
  - `familiares` (list of DatosFamiliaresSerializer)
  - `formacion` (list of DatosAcademicosSerializer, source='datos_academicos')
- Notable: ReadOnlyField for computed properties; nested serializers for related data; NO `tipo_documento`, `vigencia_estado_seguro`, `centro_salud*` exposed in main serializer (those are write-only fields on the `EmpleadoListSerializer`)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/employeesService.ts:9-42` `Employee`
- Field declarations:
  - `id: number` ← **MISMATCH** (backend now UUID string)
  - `nombres: string` ← **MISMATCH** (backend has `nombres_empleado`; normalizer maps it)
  - `ape_paterno: string` ← **MISMATCH** (backend has `apellido_paterno`; normalizer maps it)
  - `ape_materno: string` ← **MISMATCH** (backend has `apellido_materno`)
  - `dni: string` ← **MISMATCH** (backend has `numero_documento`; normalizer maps)
  - `telefono?: string` ← **MISMATCH** (backend has `telefono_celular`; normalizer maps)
  - `email?: string` ← **MISMATCH** (backend has `correo_personal`; normalizer maps)
  - `fecha_nacimiento?: string` ← MATCH
  - `direccion?: string` ← **MISMATCH** (backend has `direccion_domicilio`; normalizer maps)
  - `estado_civil?: string` ← MATCH
  - `genero?: string` ← **MISMATCH** (backend has `genero_empleado`; normalizer maps)
  - `area: { id: number; organo: string; siglas: string }` ← **MISMATCH** (backend nested as `datos_laborales_actuales.area` UUID string + different structure; normalizer reconstructs from `ubicacion_actual`)
  - `cargo?: { id: number; nombre: string; descripcion?: string }` ← **MISMATCH** (backend doesn't expose this structure; normalizer drops it)
  - `fecha_ingreso?: string` ← (sourced via `datos_laborales_actuales.fecha_ingreso` — nested)
  - `estado?: string` ← **MISMATCH** (backend has `estado_empleado`; normalizer maps)
  - `usuario?: { id: number; username: string; email: string }` ← MATCH (related User)
  - `tiene_suspension_renta_cuarta_vigente?: boolean` ← MATCH (if exposed)
- Normalizer (`apiNormalizers.ts:92-128`) papers over much of this by mapping `nombres_empleado → nombres`, `apellido_paterno → ape_paterno`, etc.

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend has `estado_empleado` (preserved Spanish). Frontend has `estado?: string` (with normalizer remap). **No rename needed if Option B is followed strictly.** Could rename interface field `estado → estado_empleado` to align — small change. NOT a `status` rename.
- **L3.10.4e (PK):** rename `id: number → id: string`. Update normalizer `getNumber(empleado_id ?? id) → getString(...)`. Many consumers read `empleado.id` and pass to URL paths — check that backend route accepts UUID (post-L3.10.4a it does).

---

### 2. Department (`apps.organization.Department`)

**Backend:**
- Model: `apps/api/apps/organization/models/department.py:16-143`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 26) — **UUID PK**
  - `nombre_organo = CharField(max_length=150, default='SIN ESPECIFICAR')` (29)
  - `nombre_unidad_organica = CharField(max_length=150, default='SIN ESPECIFICAR')` (30)
  - `siglas_area = CharField(max_length=20, unique=True, default='TEMP')` (31)
  - `descripcion_area = TextField(null=True, blank=True)` (32)
  - `jefe_area = CharField(max_length=150, null=True, blank=True)` (33)
  - `area_padre = ForeignKey('self', ...)` (36) — UUID FK
  - `nivel_jerarquico = IntegerField(default=1)` (37)
  - `codigo_presupuestal`, `total_empleados` (40-41)
  - `estado_area = CharField(max_length=20, choices=ESTADO_AREA_CHOICES, default='activo')` (44) — **PRESERVED-SPANISH-STATE**
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_creacion')` (45) — **PLATFORM-RENAMED**
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (46)
  - `db_table = 'area'` (62)
- Primary serializers:
  - `AreaSerializer` `serializers.py:36-81` — fields at 45-55
  - `AreaListSerializer` `serializers.py:84-108` — fields at 91-98
- JSON keys emitted (`AreaSerializer` read shape):
  - `id` (string UUID)
  - `nombre_organo` (string)
  - `nombre_unidad_organica` (string)
  - `siglas_area` (string, unique)
  - `descripcion_area` (string | null)
  - `estado_area` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `nombre_completo` (string, SerializerMethodField from `obj.nombre_completo` property)
  - `es_activa` (boolean, SerializerMethodField from `obj.es_activa`)
  - `empleados_activos_count` (int, SerializerMethodField from `obj.get_empleados_activos_count()`)
- Notable: `AreaListSerializer` is a slimmer version emitted by list endpoints. NO `created_at`/`updated_at` exposed. NO `area_padre`/`nivel_jerarquico`/`codigo_presupuestal` exposed.

**Frontend (current state):**
- Primary interface: `apps/web/src/services/departmentsService.ts:4-15` `Area`
- Field declarations:
  - `area_id: number` ← **MISMATCH** (backend emits `id` as UUID string, NOT `area_id`)
  - `nombre_organo: string` ← MATCH
  - `nombre_unidad_organica?: string` ← MATCH
  - `siglas_area: string` ← MATCH
  - `descripcion_area?: string` ← MATCH
  - `estado_area: 'activo' | 'inactivo'` ← MATCH
  - `nombre_completo?: string` ← MATCH
  - `es_activa?: boolean` ← MATCH
  - `empleados_activos_count?: number` ← MATCH
  - `empleados_count?: number` ← partial (only emitted by `AreaListSerializer`)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend has `estado_area`. Frontend has `estado_area`. **NO rename if Option B preserved.** If decision is to rename Department's `estado_area → status` (treating it as platform-style state), update `Department.estado_area` model field rename + serializer field name + frontend `Area.estado_area → status`.
- **L3.10.4e (PK):** rename `area_id: number → id: string` (UUID). All consumers reading `area.area_id` need refactor. Check `getNumber(ubicacionActual.area_id)` in normalizer (`apiNormalizers.ts:118`) — currently coerces `area_id` to int → will silently fail with UUID.

---

### 3. User (`apps.identity.User`)

**Backend:**
- Model: `apps/api/apps/identity/models/user.py:20-449` (custom `AbstractBaseUser`)
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 49) — **UUID PK**
  - `empleado = OneToOneField('employees.Employee', on_delete=CASCADE, related_name='usuario', null=True, blank=True)` (50-56) — UUID FK
  - `username = CharField(max_length=150, unique=True)` (59)
  - `email = EmailField(max_length=254, unique=True)` (60)
  - `password = CharField(max_length=128)` (61)
  - `nombres_usuario`, `apellidos_usuario` (64-65)
  - `tipo_usuario = CharField(max_length=20, choices=TIPO_USUARIO_CHOICES)` (66)
  - `nivel_acceso = CharField(max_length=20, choices=NIVEL_ACCESO_CHOICES, default='personal')` (67-69)
  - `is_active = BooleanField(default=True)` (72) — **PLATFORM (kept English from Django)**
  - `is_staff = BooleanField(default=False)` (73)
  - `is_superuser = BooleanField(default=False)` (74)
  - `estado_usuario = CharField(max_length=15, choices=ESTADO_USUARIO_CHOICES, default='activo')` (75-77) — **PRESERVED-SPANISH-STATE** (coexists with `is_active`)
  - `date_joined = DateTimeField(default=timezone.now)` (80)
  - `last_login = DateTimeField(null=True, blank=True)` (81)
  - `fecha_ultimo_cambio_password`, `fecha_expiracion_password` (82-83)
  - `requiere_cambio_password = BooleanField(default=False)` (86)
  - `intentos_fallidos = IntegerField(default=0)` (87)
  - `fecha_ultimo_intento_fallido`, `fecha_bloqueo`, `token_recuperacion`, `fecha_expiracion_token` (88-91)
  - `created_by = ForeignKey('self', ..., db_column='creado_por_id')` (103-110)
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_creacion')` (111)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (112)
- Primary serializer: `UsuarioSerializer` `serializers.py:786-848`
- JSON keys emitted (`UsuarioSerializer` read shape):
  - `id` (string UUID)
  - `username` (string, unique)
  - `nombres_usuario` (string)
  - `apellidos_usuario` (string)
  - `email` (string)
  - `tipo_usuario` (string, choices)
  - `empleado` (string UUID — FK to Employee)
  - `empleado_detalle` (nested EmpleadoSerializer, source='empleado')
  - `last_login` (string ISO datetime | null)
  - `estado_usuario` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `date_joined` (string ISO datetime, read_only)
  - `es_activo` (boolean, ReadOnlyField — derived from `is_active AND estado_usuario=='activo'`)
  - `nombre_completo` (string, ReadOnlyField)
  - `roles_activos` (list of `{id, nombre, descripcion}` via SerializerMethodField — note `id` is UUID string)
  - `ultimo_login_texto` (string, SerializerMethodField)
  - `dias_sin_login` (int | null, SerializerMethodField)
- Notable: `is_active` is **NOT exposed in the JSON output** — UsuarioSerializer fields list does not include it. Only `estado_usuario` and the derived `es_activo` are exposed. **This is a contradiction with what the frontend normalizer expects** (`isActive = userObj.is_active === true`). The normalizer falls back to `estado_usuario === 'activo'`.

**Frontend (current state):**
- Primary interfaces:
  - `apps/web/src/services/usersService.ts:10-38` `User`
  - `apps/web/src/lib/api.ts:24-47` `User` (auth/login response shape)
- Field declarations (`usersService.ts:User`):
  - `id: number` ← **MISMATCH** (backend emits UUID string)
  - `usuario_id: number` ← **MISMATCH** (backend doesn't emit this; normalizer reads it as fallback)
  - `username: string` ← MATCH
  - `email: string` ← MATCH
  - `nombres_usuario: string` ← MATCH
  - `apellidos_usuario: string` ← MATCH
  - `tipo_usuario: string` ← MATCH
  - `nivel_acceso: string` ← (NOT in serializer fields list — see CAVEAT)
  - `estado_usuario: string` ← MATCH
  - `is_active: boolean` ← (NOT in serializer fields list — normalizer derives from `estado_usuario`)
  - `date_joined: string` ← MATCH
  - `last_login?: string` ← MATCH
  - `empleado?: { id: number; nombres: string; ... area: {...} }` ← partially MATCH (backend emits `empleado_detalle` as nested EmpleadoSerializer, NOT this stub shape)
  - `roles_activos?: Role[]` ← MATCH (but each Role has `id` UUID, not number)
  - `dias_sin_login?: number` ← MATCH
  - `ultimo_login_texto?: string` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend has both `is_active` (Django builtin, NOT exposed) and `estado_usuario` (Spanish, exposed). Frontend declares both — mostly works because normalizer derives `is_active` from `estado_usuario`. **L3.10.4d should add `is_active` to UsuarioSerializer.Meta.fields explicitly so frontend stops needing the normalizer fallback. Then optionally rename `estado_usuario → status` if going strict platform-only.**
- **L3.10.4e (PK):** rename `id: number → id: string`. Drop `usuario_id: number` from interface (backend doesn't emit it). Normalizer line `apiNormalizers.ts:63` `getNumber(userObj.usuario_id ?? userObj.id)` needs `getString(...)`.
- **NESTED issue:** The `empleado` field in User payload comes through as a UUID string (FK), but `empleado_detalle` is the nested object. Frontend should consume `empleado_detalle`, not redefine `empleado` shape.

---

### 4. Role (`apps.identity.Role`)

**Backend:**
- Model: `apps/api/apps/identity/models/roles.py:6-90`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 15) — **UUID PK**
  - `nombre_rol = CharField(max_length=100, unique=True)` (16)
  - `descripcion_rol = TextField(null=True, blank=True)` (17)
  - `nivel_jerarquico = IntegerField(default=1)` (18)
  - `es_rol_sistema = BooleanField(default=False)` (19)
  - `estado_rol = CharField(max_length=10, choices=ESTADO_ROL_CHOICES, default='activo')` (20-22) — **PRESERVED-SPANISH-STATE**
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_creacion')` (23)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (24)
  - `db_table = 'rol'`
- Primary serializer: `RolSerializer` `serializers.py:914-952`
- JSON keys emitted:
  - `id` (string UUID)
  - `nombre_rol` (string)
  - `descripcion_rol` (string | null)
  - `estado_rol` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `es_activo` (boolean, ReadOnlyField from `obj.es_activo`)
  - `total_usuarios` (int, ReadOnlyField from `obj.usuarios_count` — placeholder returns 0)
  - `total_permisos` (int, SerializerMethodField — counts `obj.permisos_asignados`)
  - `permisos` (list of `{id, nombre, modulo, tipo, descripcion}` via SerializerMethodField — `id` is UUID string)
- Notable: NO `created_at`/`updated_at` exposed. NO `nivel_jerarquico`, `es_rol_sistema` exposed.

**Frontend (current state):**
- Primary interfaces (3 places — duplicates):
  - `apps/web/src/services/usersService.ts:40-50` `Role`
  - `apps/web/src/services/securityService.ts:27-35` `Role`
  - `apps/web/src/lib/api.ts:9-14` `Role`
- Field declarations (`usersService.ts:Role`):
  - `id: number` ← **MISMATCH** (UUID string)
  - `rol_id: number` ← **MISMATCH** (backend doesn't emit; normalizer falls back to `id`)
  - `nombre_rol: string` ← MATCH
  - `descripcion_rol: string` ← MATCH
  - `estado_rol: string` ← MATCH
  - `is_active: boolean` ← **MISMATCH** (backend emits `es_activo`, not `is_active`; normalizer adds it)
  - `total_usuarios?: number` ← MATCH
  - `total_permisos?: number` ← MATCH
  - `permisos?: Permission[]` ← MATCH
- Field declarations (`securityService.ts:Role`):
  - `id: number` ← **MISMATCH** (UUID string)
  - `nombre: string` ← **MISMATCH** (backend emits `nombre_rol`; `normalizeSecurityRole` maps it)
  - `descripcion?: string` ← **MISMATCH** (backend emits `descripcion_rol`; `normalizeSecurityRole` maps it)
  - `is_active: boolean` ← **MISMATCH** (normalizer derives from `estado_rol`)
  - `permissions_count: number` ← **MISMATCH** (backend emits `total_permisos`)
  - `users_count: number` ← **MISMATCH** (backend emits `total_usuarios`)
  - `permisos?: Permission[]` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** `RolSerializer` does NOT emit `is_active`. It emits `estado_rol` and `es_activo`. Frontend (post-normalizer) receives `is_active`. To unify: add `is_active` to RolSerializer.Meta.fields explicitly via a SerializerMethodField OR rename `estado_rol → status` and rebuild as platform-style. **Decision blocking** — ambiguous.
- **L3.10.4e (PK):** rename `id: number → id: string`. Drop `rol_id`. Normalizer at `apiNormalizers.ts:25` (`getNumber(roleObj.rol_id ?? roleObj.id)`) → `getString(...)`. Three duplicate `Role` interfaces should be consolidated.

---

### 5. Permission (`apps.identity.Permission`)

**Backend:**
- Model: `apps/api/apps/identity/models/roles.py:93-208`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 111) — **UUID PK**
  - `nombre_permiso = CharField(max_length=100)` (112)
  - `descripcion_permiso = TextField(null=True, blank=True)` (113)
  - `modulo = CharField(max_length=50, db_column='modulo', help_text=...)` (115-119) — string ID, NOT FK
  - `tipo_permiso = CharField(max_length=15, choices=TIPO_PERMISO_CHOICES)` (120)
  - `estado_permiso = CharField(max_length=10, choices=ESTADO_PERMISO_CHOICES, default='activo')` (121-123) — **PRESERVED-SPANISH-STATE**
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_creacion')` (124)
  - `db_table = 'permiso'`
- Primary serializer: `PermisoSerializer` `serializers.py:955-971`
- JSON keys emitted:
  - `id` (string UUID)
  - `nombre_permiso` (string)
  - `descripcion_permiso` (string | null)
  - `modulo` (string — module ID as string, not FK)
  - `tipo_permiso` (string, choices)
  - `estado_permiso` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `es_activo` (boolean, ReadOnlyField)
- Notable: NO `created_at` exposed.

**Frontend (current state):**
- Interfaces (3 places):
  - `apps/web/src/services/usersService.ts:52-59` `Permission`
  - `apps/web/src/services/securityService.ts:37-46` `Permission`
  - `apps/web/src/lib/api.ts:16-22` `Permission`
- Field declarations (`usersService.ts:Permission`):
  - `id: number` ← **MISMATCH** (UUID string)
  - `permiso_id: number` ← **MISMATCH** (backend doesn't emit; FE service fallback maps it)
  - `nombre_permiso: string` ← MATCH
  - `descripcion_permiso: string` ← MATCH
  - `estado_permiso: string` ← MATCH
  - `modulo?: string` ← MATCH (string ID, NOT a FK to Module)
- Field declarations (`securityService.ts:Permission`):
  - `permiso_id: number` ← **MISMATCH**
  - `nombre_permiso, descripcion_permiso, tipo_permiso, estado_permiso` ← MATCH
  - `modulo_id: number` ← **MISMATCH** (backend emits `modulo` as string)
  - `modulo_nombre: string` ← **MISMATCH** (backend doesn't emit this; needs nested or removed)
  - `es_activo: boolean` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Decision needed (as in Role). Backend emits `estado_permiso` + `es_activo`. Frontend wants `is_active` (in some places) or `estado_permiso` (in others).
- **L3.10.4e (PK):** rename `permiso_id` → `id` (string). Note: `modulo` field is a string ID, NOT a UUID. The interface `securityService.ts:Permission.modulo_id: number` is wrong — it's expecting an FK, but the backend stores `modulo` as a free-form string referencing `MODULES_CONFIG`. **Out-of-scope discovery — needs investigation.**

---

### 6. Module (`apps.identity.Module`)

**Backend:**
- Model: `apps/api/apps/identity/models/rbac.py:9-163`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 19) — **UUID PK**
  - `nombre_modulo = CharField(max_length=100)` (20)
  - `descripcion_modulo = TextField(null=True, blank=True)` (21)
  - `icono_modulo`, `ruta_modulo` (22-23)
  - `orden_visualizacion = IntegerField(default=0)` (24)
  - `estado_modulo = CharField(max_length=15, choices=ESTADO_MODULO_CHOICES, default='activo')` (25-27) — **PRESERVED-SPANISH-STATE**
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_creacion')` (28)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (29)
  - `modulo_padre = ForeignKey('self', ...)` (32-40)
  - `permisos_requeridos = CharField(max_length=500, null=True, blank=True)` (43-49)
  - `db_table = 'modulos'`
- Primary serializer: `ModulosSerializer` `serializers.py:974-1018`
- JSON keys emitted:
  - `id` (string UUID)
  - `nombre_modulo` (string)
  - `descripcion_modulo` (string | null)
  - `icono_modulo` (string | null)
  - `ruta_modulo` (string | null)
  - `orden_visualizacion` (int)
  - `estado_modulo` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `created_at` (string ISO datetime)
  - `updated_at` (string ISO datetime)
  - `es_activo` (boolean, ReadOnlyField)
  - `permisos_count` (int, SerializerMethodField — counts active Permissions for this module string ID)
- Notable: NO `modulo_padre`, `permisos_requeridos` exposed in primary serializer.

**Frontend (current state):**
- Primary interface: `apps/web/src/services/securityService.ts:48-53` `Module`
- Field declarations:
  - `id: number` ← **MISMATCH** (UUID string)
  - `name: string` ← **MISMATCH** (backend emits `nombre_modulo`)
  - `description: string` ← **MISMATCH** (backend emits `descripcion_modulo`)
  - `permissions: Permission[]` ← **MISMATCH** (backend emits `permisos_count` int, not a list)
- This interface is essentially a **stub** — the frontend doesn't really consume the Module shape directly anywhere meaningful. Probably out-of-scope.

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend has `estado_modulo`. Frontend's `Module` stub doesn't even have a state field. Could rename to `status` or leave as `estado_modulo`. Decision needed.
- **L3.10.4e (PK):** rename `id: number → id: string`.
- **Out-of-scope discovery:** The `Module` frontend interface is a stub that doesn't match the backend at all. Needs separate investigation/cleanup or deletion.

---

### 7. RolePermission (`apps.identity.RolePermission`)

**Backend:**
- Model: `apps/api/apps/identity/models/rbac.py:166-237`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 170) — **UUID PK**
  - `rol = ForeignKey('Role', on_delete=CASCADE, related_name='permisos_asignados')` (171-173) — UUID FK
  - `permiso = ForeignKey('Permission', on_delete=CASCADE, related_name='roles_asignados')` (174-176) — UUID FK
  - `fecha_asignacion = DateTimeField(auto_now_add=True)` (177)
  - `asignado_por_usuario = ForeignKey('User', ..., null=True, blank=True, db_column='asignado_por_usuario_id')` (178-184) — UUID FK
  - `db_table = 'rol_permisos'`, `unique_together = ['rol', 'permiso']`
- Primary serializer: `RolPermisosSerializer` `serializers.py:1021-1064`
- JSON keys emitted:
  - `id` (string UUID) — **note: serializer fields list has `'id'` THREE TIMES on lines 1038-1040 — bug, but DRF deduplicates**
  - `fecha_asignacion` (string ISO datetime, read_only)
  - `asignado_por_usuario_id` (string UUID — but this is a backend column, NOT a Python attribute)
  - `rol_nombre` (string, source='rol.nombre_rol')
  - `permiso_nombre` (string, source='permiso.nombre_permiso')
  - `modulo_nombre` (string, source='permiso.modulo.nombre_modulo') — **WARNING: `permiso.modulo` is a string, not a FK. This source will fail at runtime!**
  - `asignado_por_nombre` (string, source='asignado_por_usuario.nombre_completo')
- Notable: The serializer has **multiple bugs**:
  - Lines 1038-1040 list `'id'` three times (likely intended to be `id`, `rol_id`, `permiso_id`).
  - `asignado_por_usuario_id` references a `db_column` not the Python attribute `asignado_por_usuario` — DRF likely emits None.
  - `modulo_nombre` uses `permiso.modulo.nombre_modulo` but `permiso.modulo` is a string column.

**Frontend (current state):**
- Primary interface: `apps/web/src/services/securityService.ts:55-65` `RolePermission`
- Field declarations:
  - `rol_permiso_id: number` ← **MISMATCH** (backend emits `id` UUID string)
  - `rol_id: number` ← **MISMATCH** (backend serializer has bug; should emit `rol_id`)
  - `permiso_id: number` ← **MISMATCH** (backend serializer has bug)
  - `fecha_asignacion: string` ← MATCH
  - `asignado_por_usuario_id: number` ← **MISMATCH** (UUID string if emitted)
  - `rol_nombre, permiso_nombre, modulo_nombre, asignado_por_nombre: string` ← MATCH (where serializer works)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** N/A — RolePermission has no state field.
- **L3.10.4e (PK):** rename `rol_permiso_id → id` (string). Also: `rol_id`, `permiso_id`, `asignado_por_usuario_id` all UUID strings.
- **Out-of-scope:** RolPermisosSerializer has critical bugs that should be fixed before this audit's recommendations are applied. Lines 1038-1040 of `serializers.py`.

---

### 8. UserRole (`apps.identity.UserRole`)

**Backend:**
- Model: `apps/api/apps/identity/models/rbac.py:270-432`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 281) — **UUID PK**
  - `usuario = ForeignKey('User', on_delete=CASCADE, related_name='roles_asignados')` (282-284) — UUID FK
  - `rol = ForeignKey('Role', on_delete=CASCADE, related_name='usuarios_asignados')` (285-287) — UUID FK
  - `fecha_asignacion = DateTimeField(auto_now_add=True)` (288)
  - `fecha_expiracion = DateTimeField(null=True, blank=True)` (289)
  - `asignado_por_usuario = ForeignKey('User', ..., null=True, blank=True)` (290-296) — UUID FK
  - `estado_asignacion = CharField(max_length=15, choices=ESTADO_ASIGNACION_CHOICES, default='activo')` (297-299) — **PRESERVED-SPANISH-STATE**
  - `db_table = 'usuario_roles'`, `unique_together = ['usuario', 'rol']`
- Primary serializer: `UsuarioRolesSerializer` `usuario_roles_serializers.py:13-86`
- JSON keys emitted:
  - `id` (string UUID)
  - `usuario` (string UUID — FK to User)
  - `rol` (string UUID — FK to Role)
  - `fecha_asignacion` (string ISO datetime, read_only)
  - `fecha_expiracion` (string ISO datetime | null)
  - `asignado_por_usuario` (string UUID | null)
  - `estado_asignacion` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `usuario_nombre` (string, source='usuario.nombre_completo')
  - `rol_nombre` (string, source='rol.nombre_rol')
  - `asignado_por_nombre` (string, source='asignado_por_usuario.nombre_completo')
  - `es_activo` (boolean, SerializerMethodField — derived from `estado_asignacion=='activo'` AND not expired)
  - `dias_hasta_expiracion` (int | null, SerializerMethodField)
- Notable: `UsuarioRolesListSerializer` `usuario_roles_serializers.py:145-168` is a slimmer variant.

**Frontend (current state):**
- **No top-level FE interface for UserRole.** It's used only nested inside `User.roles_activos`.
- Form-related interfaces in `usersService.ts:81-87` `UserRoleAssignment` only use IDs.

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend has `estado_asignacion`. No standalone FE interface to rename.
- **L3.10.4e (PK):** Backend already exposes `id` UUID string. The `assignRoles` payloads (`usersService.ts:343`) use `usuario_ids: number[]` and `rol_ids: number[]` — these become UUID strings.

---

### 9. Contract (`apps.contracts.Contract`)

**Backend:**
- Model: `apps/api/apps/contracts/models/contract.py:19-356`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 61) — **UUID PK**
  - `empleado = ForeignKey('employees.Employee', on_delete=CASCADE, related_name='contratos_adendas')` (64-69) — UUID FK
  - `area = ForeignKey('organization.Department', on_delete=PROTECT, related_name='contratos_adendas_area')` (71-76) — UUID FK
  - `numero_contrato = CharField(max_length=50, unique=True)` (79-83)
  - `tipo_documento = CharField(max_length=25, choices=TIPO_DOCUMENTO_CHOICES)` (85-89)
  - `fecha_inicio = DateField()` (92-94)
  - `fecha_fin = DateField(null=True, blank=True)` (96-100)
  - `fecha_firma = DateField(null=True, blank=True)` (102-106)
  - `salario_bruto = DecimalField(max_digits=10, decimal_places=2)` (109-114)
  - `salario_neto = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)` (116-122)
  - `cargo = CharField(max_length=100)` (125-128)
  - `jornada_laboral = CharField(max_length=15, choices=JORNADA_CHOICES, default='COMPLETA')` (130-135)
  - `funciones = TextField(null=True, blank=True)` (138-142)
  - `lugar_trabajo`, `horario_trabajo` (144-156)
  - `status = CharField(max_length=15, choices=ESTADO_CHOICES, default='BORRADOR', db_column='estado')` (159-165) — **PLATFORM-RENAMED** (Python attr `status`, DB column `estado`)
  - `observaciones = TextField(null=True, blank=True)` (167-171)
  - `documento_generado = BooleanField(default=False)` (174-177)
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_creacion')` (180-184)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_modificacion')` (186-190)
  - `created_by = ForeignKey('identity.User', ..., db_column='creado_por_id')` (192-200)
  - `updated_by = ForeignKey('identity.User', ..., db_column='modificado_por_id')` (202-210)
  - `db_table = 'contratos_adendas'`
- Primary serializers:
  - `ContratosAdendasSerializer` `contratos_serializers.py:22-81` — fields at 42-57
  - `ContratosAdendasCreateSerializer` `contratos_serializers.py:84-137`
  - `ContratosAdendasUpdateSerializer` `contratos_serializers.py:140-163`
  - `ContratosAdendasListSerializer` `contratos_serializers.py:166-188`
- JSON keys emitted (`ContratosAdendasSerializer` read shape):
  - `id` (string UUID)
  - `empleado` (string UUID — FK)
  - `empleado_detalle` (nested EmpleadoListSerializer)
  - `area` (string UUID — FK)
  - `area_detalle` (nested AreaSerializer)
  - `numero_contrato` (string, unique)
  - `tipo_documento` (string, choices)
  - `fecha_inicio`, `fecha_fin`, `fecha_firma` (string ISO date)
  - `salario_bruto`, `salario_neto` (decimal as string)
  - `cargo` (string)
  - `jornada_laboral` (string, choices)
  - `funciones` (string | null)
  - `lugar_trabajo`, `horario_trabajo`, `observaciones` (string | null)
  - `status` (string, choices) — **JSON key is `status`** (because Meta.fields has `'status'`, not `'estado'`)
  - `documento_generado` (boolean)
  - `created_at`, `updated_at` (string ISO datetime)
  - `created_by` (string UUID | null)
  - `updated_by` (string UUID | null)
  - `dias_hasta_vencimiento` (int | null, ReadOnlyField)
  - `esta_vigente`, `esta_vencido` (boolean, ReadOnlyField)
  - `duracion_dias`, `duracion_meses` (int | float | null, ReadOnlyField)
  - `tipo_documento_texto` (string, source='get_tipo_documento_display')
  - `estado_texto` (string, source='get_status_display')
  - `jornada_texto` (string, source='get_jornada_laboral_display')
- Notable: JSON key is `status` (NOT `estado`) — this is a **L3.10.2 platform-rename**. Frontend currently expects `estado`.

**Frontend (current state):**
- Primary interface: `apps/web/src/services/contractsService.ts:4-48` `Contrato`
- Field declarations:
  - `contrato_id: number` ← **MISMATCH** (backend emits `id` UUID string)
  - `empleado: number` ← **MISMATCH** (UUID string)
  - `empleado_detalle?: { empleado_id: number; nombres_empleado, apellido_paterno, apellido_materno, nombre_completo }` ← partial MATCH (backend emits full EmpleadoListSerializer)
  - `area: number` ← **MISMATCH** (UUID string)
  - `area_detalle?: { area_id: number; nombre: string }` ← **MISMATCH** (backend emits full AreaSerializer)
  - `numero_contrato, tipo_documento, fecha_inicio, fecha_fin, fecha_firma` ← MATCH
  - `salario_bruto, salario_neto, cargo, jornada_laboral` ← MATCH
  - `funciones, lugar_trabajo, horario_trabajo, observaciones` ← MATCH
  - `estado: string` ← **MISMATCH** (backend emits `status`, NOT `estado`!)
  - `estado_texto?: string` ← MATCH
  - `documento_generado: boolean` ← MATCH
  - `created_at, updated_at` ← MATCH
  - `dias_hasta_vencimiento, esta_vigente, esta_vencido, duracion_dias, duracion_meses` ← MATCH
  - `tipo_documento_texto, jornada_texto` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** RENAME `Contrato.estado: string → status: string`. Also rename in `ContratoListItem` and any consumer code (`Contratos.tsx`, etc.) that reads `contrato.estado`. **HIGH-IMPACT** — many places.
- **L3.10.4e (PK):** rename `contrato_id: number → id: string`. Also `empleado: number → empleado: string`, `area: number → area: string`. Update `empleado_detalle.empleado_id → id` (UUID string).

---

### 10. ContractAmendment (`apps.contracts.ContractAmendment`)

**Backend:**
- Model: `apps/api/apps/contracts/models/contract_amendment.py:17-187`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 49) — **UUID PK**
  - `parent_contract = ForeignKey('contracts.Contract', on_delete=CASCADE, related_name='amendments')` (51-56) — UUID FK
  - `numero_adenda = CharField(max_length=20)` (58-61)
  - `tipo_documento = CharField(max_length=25, choices=TIPO_DOCUMENTO_CHOICES)` (63-67)
  - `fecha_inicio = DateField()` (69-71)
  - `fecha_fin = DateField(null=True, blank=True)` (73-77)
  - `fecha_firma = DateField(null=True, blank=True)` (79-83)
  - `nuevo_salario = DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)` (86-93)
  - `nuevo_cargo`, `nuevo_horario`, `nueva_jornada_laboral`, `nueva_fecha_fin_contrato` (95-121)
  - `motivo`, `observaciones = TextField(null=True, blank=True)` (123-132)
  - `status = CharField(max_length=15, choices=ESTADO_CHOICES, default='BORRADOR', db_column='estado')` (134-140) — **PLATFORM-RENAMED**
  - `documento_generado = FileField(upload_to='adendas/%Y/', null=True, blank=True)` (142-147)
  - `created_by`, `updated_by`, `created_at`, `updated_at` (150-173)
  - `db_table = 'contract_amendments'`
- Primary serializer: `ContractAmendmentSerializer` `contratos_serializers.py:256-285`
- JSON keys emitted:
  - `id` (string UUID)
  - `parent_contract` (string UUID — FK to Contract)
  - `parent_contract_numero` (string, source='parent_contract.numero_contrato')
  - `parent_contract_empleado` (string, source='parent_contract.empleado.nombre_completo')
  - `numero_adenda` (string)
  - `tipo_documento` (string, choices)
  - `tipo_documento_texto` (string, source='get_tipo_documento_display')
  - `fecha_inicio`, `fecha_fin`, `fecha_firma` (string ISO date)
  - `nuevo_salario` (decimal | null)
  - `nuevo_cargo`, `nuevo_horario`, `nueva_jornada_laboral` (string | null)
  - `nueva_fecha_fin_contrato` (string ISO date | null)
  - `motivo`, `observaciones` (string | null)
  - `status` (string, choices) — JSON key is `status`
  - `estado_texto` (string, source='get_status_display')
  - `documento_generado` (file URL | null)
  - `created_at`, `updated_at` (string ISO datetime)
  - `created_by` (string UUID | null)
  - `updated_by` (string UUID | null)

**Frontend (current state):**
- **No dedicated FE interface for ContractAmendment.** Folded into `Contrato` and treated as a contract subtype via `tipo_documento` checks.

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Same as Contract — JSON emits `status`. Frontend doesn't have a dedicated interface.
- **L3.10.4e (PK):** UUID — same as Contract.
- **Out-of-scope discovery:** Frontend conflates Contract and ContractAmendment in a single `Contrato` interface. After L3.10.3 split, may need a separate `ContractAmendment` interface in FE.

---

### 11. EmploymentData (`apps.contracts.EmploymentData`)

**Backend:**
- Model: `apps/api/apps/contracts/models/employment_data.py:19-318`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 70) — **UUID PK**
  - `empleado = ForeignKey('employees.Employee', on_delete=CASCADE, related_name='datos_laborales')` (71-75)
  - `area = ForeignKey('organization.Department', on_delete=PROTECT, related_name='empleados_laborales')` (76-80)
  - `cargo_empleado = CharField(max_length=100)` (83)
  - `codigo_puesto`, `nivel_puesto`, `categoria` (84-86)
  - `tipo_contrato`, `regimen_laboral`, `modalidad_trabajo`, `jornada_laboral` (89-92)
  - `fecha_ingreso = DateField()` (95)
  - `fecha_inicio_contrato`, `fecha_fin_contrato`, `fecha_cese` (96-98)
  - `sueldo_basico`, `asignacion_familiar`, `bonificacion_especial`, `otras_bonificaciones` (101-104)
  - `horario_entrada`, `horario_salida`, `horas_semanales` (107-109)
  - `jefe_directo = ForeignKey('employees.Employee', on_delete=SET_NULL, null=True, blank=True, related_name='subordinados_laborales')` (112-118)
  - `estado_datos = CharField(max_length=15, choices=ESTADO_DATOS_CHOICES, default='activo')` (121) — **PRESERVED-SPANISH-STATE**
  - `observaciones = TextField(null=True, blank=True)` (122)
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_registro')` (123)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (124)
  - `db_table = 'datos_laborales'`
- Primary serializers:
  - `DatosLaboralesSerializer` `serializers.py:250-340`
  - `DatosLaboralesCreateSerializer` `serializers.py:666-671` (uses `exclude=['id', 'empleado', 'area']`)
- JSON keys emitted (`DatosLaboralesSerializer`):
  - `id` (string UUID)
  - `empleado` (string UUID FK)
  - `area` (string UUID FK)
  - `fecha_ingreso` (string ISO date)
  - `cargo_empleado` (string)
  - `tipo_contrato`, `regimen_laboral`, `modalidad_trabajo`, `jornada_laboral` (strings)
  - `fecha_cese` (string ISO date | null)
  - `categoria` (string)
  - `sueldo_basico` (decimal as string)
  - `es_activo` (boolean, ReadOnlyField — derived from `estado_datos=='activo' and not fecha_cese`)
  - `antiguedad_años` (int, ReadOnlyField)
  - `antiguedad_meses` (int, ReadOnlyField)
  - `tiempo_servicio` (string, ReadOnlyField — but no `tiempo_servicio` property exists on the model!)
  - `empleado_nombre` (string, source='empleado.nombres_empleado')
  - `area_nombre` (string, source='area.nombre_completo')
  - `ultimo_login_texto`, `dias_sin_login` (SerializerMethodField from User)
- Notable: `estado_datos` is **NOT in the serializer fields list**. Read NOT exposed. Frontend has `estado: string` which doesn't match.

**Frontend (current state):**
- Primary interface: `apps/web/src/services/employeesService.ts:68-82` `DatosLaborales`
- Field declarations:
  - `id?: number` ← **MISMATCH** (UUID string)
  - `empleado_id: number` ← **MISMATCH** (backend emits `empleado` as UUID string)
  - `area_id: number` ← **MISMATCH** (backend emits `area` as UUID string)
  - `cargo_id?: number` ← **MISMATCH** (backend has `cargo_empleado: string`, NOT a FK)
  - `fecha_ingreso: string` ← MATCH
  - `tipo_contrato?: string` ← MATCH
  - `modalidad_trabajo?: string` ← MATCH
  - `horario_trabajo?: string` ← **MISMATCH** (backend has `horario_entrada`/`horario_salida`)
  - `salario_base?: number` ← **MISMATCH** (backend has `sueldo_basico`)
  - `estado: string` ← **MISMATCH** (backend doesn't expose `estado_datos`; only `es_activo` boolean is exposed)
  - `fecha_cese?: string` ← MATCH
  - `motivo_cese?: string` ← **MISMATCH** (no such field; observations contain motivo)
  - `supervisor_id?: number` ← **MISMATCH** (backend has `jefe_directo` UUID string; not exposed in serializer)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend has `estado_datos` (preserved Spanish), but the serializer does NOT expose it. Frontend declares `estado: string` which is broken. **L3.10.4d action: rebuild the FE interface to use what the backend actually emits (no state field, only `es_activo`).** Or expose `estado_datos` in the serializer.
- **L3.10.4e (PK):** rename `id?: number → id?: string`. Drop `_id` suffix patterns and use the actual JSON keys (`empleado`, `area`).
- **Out-of-scope:** The frontend interface is largely fictional. Aligning it to backend reality is a larger refactor than just `_id → id` renames. Needs investigation.

---

### 12. FamilyMember (`apps.employees.FamilyMember`)

**Backend:**
- Model: `apps/api/apps/employees/models/family_member.py:17-419`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 79) — **UUID PK**
  - `empleado = ForeignKey('Employee', on_delete=CASCADE, related_name='familiares')` (80-84)
  - `nombres_familiar`, `apellido_paterno`, `apellido_materno` (87-89)
  - `tipo_documento` (90), `numero_documento` (91)
  - `fecha_nacimiento = DateField()` (92)
  - `genero_familiar` (93)
  - `parentesco` (96), `es_dependiente`, `es_beneficiario`, `es_contacto_emergencia` (97-99)
  - `estado_civil`, `nivel_educativo`, `ocupacion`, `centro_trabajo` (102-105)
  - `telefono_familiar`, `correo_familiar`, `direccion_familiar`, `distrito_familiar`, `provincia_familiar`, `departamento_familiar` (108-113)
  - `tiene_seguro_salud`, `tipo_seguro_salud`, `numero_seguro`, `centro_salud_asignado` (116-119)
  - `tiene_discapacidad`, `tipo_discapacidad`, `grado_discapacidad`, `certificado_discapacidad` (122-125)
  - `fecha_inicio_dependencia`, `fecha_fin_dependencia` (128-129)
  - `estado_familiar = CharField(max_length=15, choices=ESTADO_FAMILIAR_CHOICES, default='activo')` (132) — **PRESERVED-SPANISH-STATE**
  - `observaciones`, `created_at`, `updated_at` (133-135)
  - `db_table = 'datos_familiares'`
- Primary serializer: `DatosFamiliaresSerializer` `serializers.py:111-167`
- JSON keys emitted:
  - `id` (string UUID)
  - `empleado` (string UUID FK)
  - `parentesco` (string, choices)
  - `nombres_familiar` (string)
  - `apellido_paterno`, `apellido_materno` (strings)
  - `fecha_nacimiento` (string ISO date | null)
  - `genero_familiar` (string)
  - `edad` (int | null, SerializerMethodField from `obj.edad`)
  - `es_menor_edad` (boolean, SerializerMethodField from `obj.es_menor_edad`)
  - `nombre_completo` (string, SerializerMethodField from `obj.nombre_completo`)
  - `numero_documento`, `tipo_documento` (strings)
  - `es_beneficiario`, `es_dependiente` (booleans)
  - `estado_familiar` (string, choices) — **PRESERVED-SPANISH-STATE**
- Notable: Many model fields NOT exposed (`telefono_familiar`, `correo_familiar`, `tiene_seguro_salud`, etc.).

**Frontend (current state):**
- Primary interface: `apps/web/src/services/employeesService.ts:84-95` `DatosFamiliares`
- Field declarations:
  - `id?: number` ← **MISMATCH** (UUID string)
  - `empleado_id: number` ← **MISMATCH** (backend emits `empleado` UUID string)
  - `nombre_familiar: string` ← **MISMATCH** (backend emits `nombres_familiar` — note the `s`)
  - `apellidos_familiar: string` ← **MISMATCH** (backend emits `apellido_paterno` + `apellido_materno`)
  - `parentesco: string` ← MATCH
  - `dni_familiar?: string` ← **MISMATCH** (backend emits `numero_documento`)
  - `fecha_nacimiento_familiar?: string` ← **MISMATCH** (backend emits `fecha_nacimiento`)
  - `telefono_familiar?: string` ← **NOT EMITTED** (model has it but serializer doesn't)
  - `es_beneficiario: boolean` ← MATCH
  - `es_contacto_emergencia: boolean` ← **NOT EMITTED** (model has it but serializer doesn't expose it)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend has `estado_familiar` (preserved Spanish). FE doesn't have a state field. No rename needed.
- **L3.10.4e (PK):** rename `id?: number → id?: string`, `empleado_id: number → empleado: string`.
- **Out-of-scope:** FE interface is largely incorrect. Need to align field names (`nombre_familiar` should be `nombres_familiar`, etc.) — broader cleanup.

---

### 13. AcademicRecord (`apps.employees.AcademicRecord`)

**Backend:**
- Model: `apps/api/apps/employees/models/academic_record.py:17-428`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 67) — **UUID PK**
  - `empleado = ForeignKey('Employee', on_delete=CASCADE, related_name='formacion_academica')` (68-72)
  - `nivel_educativo`, `nombre_institucion`, `tipo_institucion`, `modalidad_estudio` (75-78)
  - `nombre_carrera`, `codigo_carrera`, `area_conocimiento`, `duracion_anos`, `duracion_semestres` (81-85)
  - `fecha_inicio = DateField()` (88)
  - `fecha_fin`, `fecha_graduacion = DateField(null=True, blank=True)` (89-90)
  - `estado_estudios` (93) — domain Spanish, choices: completo/incompleto/en_curso/trunco/convalidado
  - `promedio_ponderado`, `creditos_aprobados`, `creditos_totales` (94-96)
  - `numero_titulo`, `numero_diploma`, `numero_colegiatura`, `colegio_profesional` (99-102)
  - `pais_institucion`, `departamento_institucion`, `provincia_institucion`, `distrito_institucion` (105-108)
  - `mencion_especialidad`, `tesis_titulo`, `reconocimientos` (111-113)
  - `ruta_certificado`, `ruta_titulo`, `ruta_diploma` (116-118)
  - `documento = ForeignKey('documents.DigitalDocument', on_delete=SET_NULL, null=True, blank=True)` (119-124)
  - `verificado_sunedu`, `fecha_verificacion_sunedu`, `codigo_verificacion_sunedu` (127-129)
  - `estado_registro = CharField(max_length=25, choices=ESTADO_REGISTRO_CHOICES, default='activo')` (132) — **PRESERVED-SPANISH-STATE**
  - `observaciones`, `created_at`, `updated_at` (133-135)
  - `db_table = 'datos_academicos'`
- Primary serializer: `DatosAcademicosSerializer` `serializers.py:170-223`
- JSON keys emitted:
  - `id` (string UUID)
  - `empleado` (string UUID FK)
  - `nivel_educativo`, `nombre_institucion`, `tipo_institucion`, `modalidad_estudio` (strings)
  - `nombre_carrera`, `codigo_carrera`, `area_conocimiento` (strings)
  - `duracion_anos`, `duracion_semestres` (decimal | int | null)
  - `fecha_inicio`, `fecha_fin`, `fecha_graduacion` (string ISO date | null)
  - `estado_estudios` (string, choices) — **DOMAIN-SPANISH** (NOT a platform state, refers to study completion)
  - `promedio_ponderado`, `creditos_aprobados`, `creditos_totales`
  - `numero_titulo`, `numero_diploma`, `numero_colegiatura`, `colegio_profesional`
  - `pais_institucion`, `mencion_especialidad`, `tesis_titulo`
  - `verificado_sunedu` (boolean)
- Notable: NO `estado_registro` exposed in serializer. NO `created_at`/`updated_at` exposed. NO `ruta_*` exposed. NO `fecha_verificacion_sunedu` exposed.

**Frontend (current state):**
- Primary interface: `apps/web/src/services/employeesService.ts:97-107` `DatosAcademicos`
- Field declarations:
  - `id?: number` ← **MISMATCH** (UUID string)
  - `empleado_id: number` ← **MISMATCH** (backend emits `empleado` UUID string)
  - `nivel_educativo: string` ← MATCH
  - `institucion: string` ← **MISMATCH** (backend emits `nombre_institucion`)
  - `titulo_obtenido?: string` ← **MISMATCH** (backend has `numero_titulo`)
  - `fecha_inicio?: string` ← MATCH (but model says `fecha_inicio` is required, not optional)
  - `fecha_fin?: string` ← MATCH
  - `estado_estudio: string` ← **MISMATCH** (backend emits `estado_estudios` — note plural)
  - `documento_sustentatorio?: string` ← **MISMATCH** (backend has FK `documento` to DigitalDocument)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** `estado_estudios` is domain Spanish (a CHOICES field describing whether studies are complete/in-progress, NOT a platform state). **Should NOT be renamed to `status`.** L3.10.4d may simply update the FE field name from `estado_estudio` → `estado_estudios`.
- **L3.10.4e (PK):** rename `id?: number → id?: string`, `empleado_id → empleado: string`.
- **Out-of-scope:** Many field name mismatches between FE and backend. Needs alignment (rename `institucion → nombre_institucion`, etc.).

---

### 14. Certification (`apps.employees.Certification`)

**Backend:**
- Model: `apps/api/apps/employees/models/certification.py:14-42`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 17) — **UUID PK**
  - `empleado = ForeignKey('Employee', on_delete=CASCADE, related_name='cursos_certificaciones')` (18-20)
  - `nombre_curso`, `institucion`, `fecha_inicio`, `fecha_fin`, `horas`, `descripcion` (21-26)
  - `documento = ForeignKey('documents.DigitalDocument', on_delete=SET_NULL, null=True, blank=True)` (27-32)
  - `estado_registro = CharField(max_length=20, default='activo')` (33) — **PRESERVED-SPANISH-STATE**
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_registro')` (34) — **PLATFORM-RENAMED**
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (35)
  - `db_table = 'cursos_certificaciones'`
- Primary serializer: `CursosCertificacionesSerializer` `serializers.py:226-247`
- JSON keys emitted:
  - `id`, `empleado`, `nombre_curso`, `institucion`, `fecha_inicio`, `fecha_fin`, `horas`, `descripcion`, `documento` (UUID FK), `estado_registro`, `created_at`, `updated_at`

**Frontend (current state):**
- **No FE interface for Certification.** No FE consumers identified.

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend emits `estado_registro`. No FE consumer.
- **L3.10.4e (PK):** UUID. No FE consumer.
- **Out-of-scope discovery:** FE doesn't consume this entity. Either there's a missing FE feature or it's truly orphan.

---

### 15. DigitalDocument (`apps.documents.DigitalDocument`)

**Backend:**
- Model: `apps/api/apps/documents/models/digital_document.py:25-569`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 109) — **UUID PK**
  - `empleado = ForeignKey('employees.Employee', on_delete=CASCADE, related_name='documentos_digitales')` (110-114)
  - `tipo_documento` (117), `categoria` (118), `nombre_documento`, `descripcion` (119-120)
  - `archivo = FileField(...)` (123-128)
  - `nombre_archivo_original`, `formato_archivo`, `tamano_archivo` (129-131)
  - `numero_documento`, `fecha_emision`, `fecha_vencimiento`, `entidad_emisora` (134-137)
  - `nivel_acceso`, `requiere_autorizacion`, `es_documento_oficial`, `es_copia_certificada` (140-143)
  - `version`, `documento_padre`, `familiar`, `es_version_actual` (146-160)
  - `estado_documento = CharField(max_length=20, choices=ESTADO_DOCUMENTO_CHOICES, default='activo')` (163) — **PRESERVED-SPANISH-STATE**
  - `validado_por = ForeignKey('identity.User', on_delete=SET_NULL, null=True, blank=True, related_name='documentos_validados')` (164-170)
  - `fecha_validacion`, `observaciones_validacion` (171-172)
  - `digitalizado_por = ForeignKey('identity.User', ..., related_name='documentos_digitalizados')` (175-181)
  - `fecha_digitalizacion = DateTimeField(auto_now_add=True)` (182)
  - `calidad_digitalizacion = CharField(...)` (183-187)
  - `fecha_subida = DateTimeField(auto_now_add=True)` (190)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (191)
  - `subido_por = ForeignKey('identity.User', on_delete=SET_NULL, null=True, blank=True, related_name='documentos_subidos')` (192-198)
  - `palabras_clave`, `notas_internas`, `es_confidencial`, `requiere_firma_digital` (201-204)
  - `db_table = 'documentos_digitales'`
- Primary serializer: `DocumentosDigitalesSerializer` `serializers.py:1112-1182`
- JSON keys emitted:
  - `id` (string UUID)
  - `empleado` (string UUID FK)
  - `empleado_detalle` (nested EmpleadoListSerializer)
  - `tipo_documento` (string), `tipo_documento_texto` (string, ReadOnlyField)
  - `categoria` (string), `categoria_texto` (string, ReadOnlyField)
  - `nombre_documento`, `descripcion` (strings)
  - `archivo` (file URL), `archivo_url` (string, SerializerMethodField — absolute URL)
  - `nombre_archivo_original`, `formato_archivo` (strings, read_only)
  - `tamano_archivo` (int)
  - `tamano_mb` (float, SerializerMethodField)
  - `fecha_emision`, `fecha_vencimiento` (string ISO date | null)
  - `fecha_subida` (string ISO datetime, read_only)
  - `subido_por` (string UUID | null)
  - `estado_documento` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `estado_texto` (string, ReadOnlyField from `obj.estado_texto`)
  - `nivel_acceso` (string, choices)
  - `dias_para_vencimiento` (int | null, ReadOnlyField)
  - `validado_por` (string UUID | null)
  - `fecha_validacion` (string ISO datetime | null)
  - `observaciones_validacion` (string | null)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/legajoService.ts:4-33` `Documento`
- Field declarations:
  - `documento_id: number` ← **MISMATCH** (UUID string)
  - `empleado: number` ← **MISMATCH** (UUID string)
  - `empleado_nombre?: string` ← **MISMATCH** (backend emits `empleado_detalle` nested, not a string)
  - `tipo_documento`, `categoria`, `nombre_documento`, `descripcion` ← MATCH
  - `archivo, archivo_url, nombre_archivo_original, formato_archivo, tamano_archivo, tamano_mb` ← MATCH
  - `fecha_emision, fecha_vencimiento` ← MATCH
  - `entidad_emisora?: string` ← **NOT EMITTED** (model has it but serializer omits)
  - `numero_referencia?: string` ← **MISMATCH** (no such field; model has `numero_documento`)
  - `estado_documento: string` ← MATCH
  - `estado_texto?, tipo_documento_texto?, categoria_texto?` ← MATCH
  - `nivel_acceso: string` ← MATCH
  - `dias_para_vencimiento` ← MATCH
  - `fecha_subida: string` ← MATCH
  - `subido_por?: number | null` ← **MISMATCH** (UUID string)
  - `validado_por?: number | null` ← **MISMATCH** (UUID string)
  - `fecha_validacion, observaciones_validacion` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend emits `estado_documento` (preserved Spanish). FE matches. No rename needed unless going strict platform-only.
- **L3.10.4e (PK):** rename `documento_id: number → id: string`. `empleado: number → empleado: string`. `subido_por: number → subido_por: string`. `validado_por: number → validado_por: string`.

---

### 16. DocumentTemplate (`apps.documents.DocumentTemplate`)

**Backend:**
- Model: `apps/api/apps/documents/models/document_template.py:11-86`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 27) — **UUID PK**
  - `tipo` (28-32), `nombre` (33), `descripcion` (34)
  - `archivo = FileField(upload_to='plantillas_word/%Y/')` (35-38)
  - `activa = BooleanField(default=True)` (39) — **PLATFORM-RENAMED-ish** (kept as `activa` Spanish, but is a boolean platform-style)
  - `created_at = DateTimeField(auto_now_add=True, db_column='fecha_creacion')` (40)
  - `created_by = ForeignKey('identity.User', ..., db_column='creada_por_id')` (41-48)
  - `db_table = 'app_rrhh_plantilla_documento'`
- Primary serializer: NOT in main serializers file. Used via `views.py` directly. Likely auto-generated `ModelSerializer` with all fields. JSON keys would mirror the model attribute names.
- JSON keys (inferred):
  - `id` (string UUID)
  - `tipo` (string, choices)
  - `nombre`, `descripcion` (strings)
  - `archivo` (file URL)
  - `activa` (boolean) — **JSON key is `activa`** (Python attribute is `activa`)
  - `created_at` (string ISO datetime)
  - `created_by` (string UUID | null)
  - Plus computed `variables_disponibles` (list of strings, from model property)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/templatesService.ts:10-20` `PlantillaDocumento`
- Field declarations:
  - `plantilla_id: number` ← **MISMATCH** (UUID string)
  - `tipo: TipoPlantilla` ← MATCH
  - `tipo_texto: string` ← MATCH (likely emitted as `get_tipo_display`)
  - `nombre: string` ← MATCH
  - `descripcion: string` ← MATCH
  - `activa: boolean` ← MATCH
  - `created_at: string` ← MATCH
  - `variables_disponibles: string[]` ← MATCH (from model property)
  - `archivo_nombre: string | null` ← **MISMATCH** (backend likely emits `archivo` URL not `archivo_nombre`)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** `activa: boolean` is the platform-renamed-ish equivalent of `is_active`. Could rename `activa → is_active` for full consistency, but since it's still Spanish on backend, no urgent rename.
- **L3.10.4e (PK):** rename `plantilla_id: number → id: string`.

---

### 17. Company (`apps.organization.Company`)

**Backend:**
- Model: `apps/api/apps/organization/models/company.py:5-35`
  - **NO custom `id` field** — Django default auto int PK
  - `nombre = CharField(max_length=300, default='Institución Pública')` (8)
  - `ruc = CharField(max_length=20, default='20000000000')` (9)
  - `direccion`, `distrito`, `provincia`, `departamento`, `telefono`, `email`, `web` (10-16)
  - `logo = ImageField(upload_to='empresa/', null=True, blank=True)` (17)
  - `representante_legal`, `cargo_representante`, `dni_representante`, `resolucion_creacion` (18-21)
  - `db_table = 'configuracion_empresa'`
  - Singleton via `get_config()` classmethod (`pk=1`)
- Primary serializer: `ConfiguracionEmpresaSerializer` `serializers.py:1322-1352`
- JSON keys emitted:
  - `id` (int — auto PK, NOT UUID)
  - `nombre`, `ruc`, `direccion`, `distrito`, `provincia`, `departamento`, `telefono`, `email`, `web` (strings)
  - `logo` (file URL | null)
  - `logo_url` (string | null, SerializerMethodField — absolute URL)
  - `representante_legal`, `cargo_representante`, `dni_representante`, `resolucion_creacion` (strings)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/companyService.ts:3-20` `ConfiguracionEmpresa`
- Field declarations:
  - `id: number` ← MATCH (Company has int auto PK — singleton)
  - All other string fields ← MATCH
  - `logo: string | null`, `logo_url: string | null` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** N/A — Company has no state field.
- **L3.10.4e (PK):** **NO change needed** — Company is the only entity with int PK (singleton, not UUID-migrated).

---

### 18. MonthlyPayroll (`apps.payroll.MonthlyPayroll`)

**Backend:**
- Model: `apps/api/apps/payroll/models/compensation.py:115-214`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 135) — **UUID PK**
  - `periodo` (136), `modalidad` (137), `meta_presupuestal`, `descripcion` (138-139)
  - `status = CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador', db_column='estado')` (142) — **PLATFORM-RENAMED**
  - `total_trabajadores`, `total_remuneracion_bruta`, `total_descuentos`, `total_neto_pagar`, `total_essalud`, `total_aporte_afp`, `total_onp` (143-161)
  - `fecha_generacion`, `fecha_aprobacion`, `fecha_pago` (164-166)
  - `usuario_generacion = ForeignKey('identity.User', ...)` (169-175) — UUID FK
  - `usuario_aprobacion = ForeignKey('identity.User', ...)` (176-182) — UUID FK
  - `created_at`, `updated_at` (183-184)
  - `db_table = 'planilla_mensual'`
- Primary serializers:
  - `PlanillaMensualListSerializer` `remuneraciones_serializers.py:171-219`
  - `PlanillaMensualDetailSerializer` `remuneraciones_serializers.py:222-272`
- JSON keys emitted (`PlanillaMensualListSerializer`):
  - `id` (string UUID)
  - `periodo`, `modalidad` (strings)
  - `modalidad_texto` (string, source='get_modalidad_display')
  - `meta_presupuestal`, `descripcion` (strings | null)
  - `estado` (string, choices) — **JSON key is `estado`** (because Meta.fields has `'estado'` not `'status'`. The Python attribute is `status`, but DRF sees `'estado'` in fields list and looks for `obj.estado` — WHICH DOES NOT EXIST. **This is a serializer bug!** Actually looking again: with `db_column='estado'`, Django still creates a Python attribute `status`. The serializer fields list `'estado'` would fail, BUT looking at the serializer at line 195, it's `"estado"`. Need to verify this works at runtime.)

  *(CAVEAT: the serializer references `'estado'` in Meta.fields but the Python attr is `status`. DRF will try to access `instance.estado` which doesn't exist. **This may be a runtime bug the audit just discovered.** OR there's some shim.)*
  - `estado_texto` (string, source='get_status_display')
  - `total_trabajadores`, `total_remuneracion_bruta`, `total_descuentos`, `total_neto_pagar`, `total_essalud`, `total_aporte_afp`, `total_onp` (decimals/ints)
  - `fecha_generacion`, `fecha_aprobacion`, `fecha_pago` (datetimes/dates | null)
  - `usuario_generacion_nombre`, `usuario_aprobacion_nombre` (strings, source='*.nombre_completo')
  - `esta_cerrada`, `puede_generarse` (booleans, ReadOnlyField)
  - `created_at`, `updated_at` (string ISO datetime)
- Notable: **The serializer is internally inconsistent.** The Meta.fields list uses `'estado'` (the JSON key wanted) but the model only has Python attribute `status`. The `source='get_status_display'` for `estado_texto` confirms the model attribute IS `status`. This means the serializer line `"estado"` in fields list will likely raise an error or be silently ignored. **L3.10.4d should fix this by renaming Meta.fields entry `'estado' → 'status'`.**

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:114-140` `PlanillaMensual`
- Field declarations:
  - `planilla_id: number` ← **MISMATCH** (UUID string)
  - `periodo: string` ← MATCH
  - `modalidad?: string` ← MATCH
  - `meta_presupuestal, descripcion` ← MATCH
  - `total_*` numeric fields ← MATCH
  - `estado?: EstadoPlanilla` ← MATCH (assuming serializer works)
  - `estado_texto` ← MATCH
  - `fecha_generacion, fecha_aprobacion, fecha_pago` ← MATCH
  - `usuario_generacion?, usuario_aprobacion?, created_by?, aprobado_por?` ← partial MATCH (backend emits `usuario_generacion_nombre` not nested)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Rename FE `estado: EstadoPlanilla → status: EstadoPlanilla` AFTER backend serializer is fixed to expose `status`.
- **L3.10.4e (PK):** rename `planilla_id: number → id: string`. Same for `usuario_generacion`, `usuario_aprobacion` (UUID strings).

---

### 19. PayrollDetail (`apps.payroll.PayrollDetail`)

**Backend:**
- Model: `apps/api/apps/payroll/models/compensation.py:217-362`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 220) — **UUID PK**
  - `planilla = ForeignKey(MonthlyPayroll, on_delete=CASCADE, related_name='detalles')` (221-225)
  - `empleado = ForeignKey('employees.Employee', on_delete=PROTECT, related_name='detalles_planilla')` (226-230)
  - `datos_laborales = ForeignKey('contracts.EmploymentData', null=True, blank=True)` (231-237)
  - `area_nombre`, `cargo`, `dni`, `sistema_pensiones`, `tipo_comision_afp`, `cuspp` (240-245)
  - `estado_laboral = CharField(...choices=[('activo'), ('licencia'), ('suspendido'), ('descanso_medico')], default='activo')` (248-258) — **PRESERVED-SPANISH-STATE** (different state — labor status of employee in this period)
  - `dias_laborados, dias_no_laborados, dias_subsidiados` (261-263)
  - `remuneracion_basica, asignacion_familiar, bonificacion_especial, otras_bonificaciones, total_haberes` (266-280)
  - AFP/ONP/renta deductions (283-298, 301-323)
  - `essalud, neto_pagar` (327-334)
  - `banco, numero_cuenta` (337-338)
  - `created_at, updated_at` (341-342)
  - `db_table = 'detalle_planilla'`
- Primary serializers:
  - `DetallePlanillaListSerializer` `remuneraciones_serializers.py:359-414`
  - `DetallePlanillaDetailSerializer` `remuneraciones_serializers.py:417-469`
- JSON keys emitted (`DetallePlanillaListSerializer`):
  - `id` (string UUID)
  - `planilla` (string UUID FK)
  - `empleado` (object — SerializerMethodField — `{id, dni, nombres_completos, area_nombre}`)
  - `area_nombre`, `cargo`, `dni` (strings)
  - `sistema_pensiones`, `tipo_comision_afp`, `dias_laborados`, decimals
  - `total_ingresos` (decimal, source='total_haberes')
  - `total_haberes`, `aporte_afp_obligatorio`, `comision_afp`, `prima_seguro_afp`, `total_afp`, `aporte_onp`, `essalud`, `renta_quinta_categoria`, `total_descuentos`, `neto_pagar` (decimals)
  - `estado` (string, source='estado_laboral') — JSON key `estado`, sourced from `estado_laboral`
  - `estado_texto` (string, SerializerMethodField — calls `get_estado_laboral_display()`)
  - `banco`, `numero_cuenta` (strings | null)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:150-194` `DetallePlanilla`
- Field declarations:
  - `detalle_id: number` ← **MISMATCH** (UUID string)
  - `planilla: { planilla_id: number; periodo; modalidad }` ← **MISMATCH** (backend emits `planilla` as UUID string)
  - `empleado: { empleado_id: number; dni; nombres_completos; area_nombre }` ← **MISMATCH** (backend emits `id` UUID string in nested SerializerMethodField, not `empleado_id`)
  - `area_nombre`, `cargo`, `dni`, `sistema_pensiones`, `tipo_comision_afp` ← MATCH
  - `dias_laborados`, `dias_subsidiados`, decimals ← MATCH
  - `estado: EstadoDetalle` ← MATCH (JSON key is `estado`)
  - Various decimal fields ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend `estado_laboral` exposed as JSON `estado`. Frontend has `estado: EstadoDetalle`. **Match.** No rename needed unless renaming `estado_laboral → status` on the backend. Note: `EstadoDetalle = "activo" | "anulado"` doesn't match the model choices `("activo", "licencia", "suspendido", "descanso_medico")` — FE union is wrong.
- **L3.10.4e (PK):** rename `detalle_id → id` (string UUID). Drop nested `planilla.planilla_id` and `empleado.empleado_id` to UUID strings.

---

### 20. Compensation (`apps.payroll.CompensationConfiguration`)

**Backend:**
- Model: `apps/api/apps/payroll/models/compensation.py:61-112`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 74) — **UUID PK**
  - `tipo = CharField(max_length=20, choices=TIPO_CHOICES)` (75)
  - `codigo, nombre, descripcion` (76-78)
  - `porcentaje, monto_fijo` (79-83)
  - `aplica_base_imponible, orden` (85-86)
  - `status = CharField(max_length=10, choices=ESTADO_CHOICES, default='activo', db_column='estado')` (87) — **PLATFORM-RENAMED**
  - `created_at, updated_at` (88-89)
  - `db_table = 'configuracion_remuneracion'`
- Primary serializer: `ConfiguracionRemuneracionSerializer` (TWO definitions; the active one is from `remuneraciones_serializers.py:137-163`)
- JSON keys emitted:
  - `id` (string UUID)
  - `tipo` (string), `tipo_texto` (string, source='get_tipo_display')
  - `codigo`, `nombre`, `descripcion` (strings)
  - `porcentaje`, `monto_fijo` (decimals)
  - `aplica_base_imponible` (boolean), `orden` (int)
  - `estado` (string, choices) — **JSON key is `estado`** but Python attribute is `status`. Same caveat as MonthlyPayroll — Meta.fields entry `'estado'` may not work without a `source='status'`. **NEEDS VERIFICATION at runtime.**
  - `estado_texto` (string, source='get_status_display')
  - `es_activo` (boolean, ReadOnlyField)
  - `created_at`, `updated_at` (string ISO datetime)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:5-19` `ConceptoRemuneracion`
- Field declarations:
  - `configuracion_id: number` ← **MISMATCH** (UUID string)
  - `tipo`, `codigo`, `nombre`, `descripcion`, `porcentaje`, `monto_fijo`, `aplica_base_imponible`, `orden` ← MATCH
  - `estado: "activo" | "inactivo"` ← MATCH (assuming the serializer works)
  - `es_activo?: boolean` ← MATCH
  - `created_at, updated_at` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Same as MonthlyPayroll. JSON key `estado` should be renamed to `status` after fixing serializer Meta.fields entry. FE update straightforward.
- **L3.10.4e (PK):** rename `configuracion_id: number → id: string`.

---

### 21. AfpConfiguration (`apps.payroll.AfpConfiguration`)

**Backend:**
- Model: `apps/api/apps/payroll/models/compensation.py:10-58`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 18) — **UUID PK**
  - `afp_nombre`, `vigencia_mes` (19-20), aporte/comision/prima fields (21-32)
  - `remuneracion_max_asegurable` (33)
  - `status = CharField(max_length=10, choices=ESTADO_CHOICES, default='activo', db_column='estado')` (34) — **PLATFORM-RENAMED**
  - `created_at, updated_at` (35-36)
  - `db_table = 'configuracion_afp'`
- Two serializers (slightly different):
  - `ConfiguracionAfpSerializer` `serializers.py:409-477` — uses `'estado'` in fields
  - `ConfiguracionAfpSerializer` `remuneraciones_serializers.py:33-56` — uses `'estado'` in fields and adds `estado_texto`
- JSON keys emitted:
  - `id` (string UUID)
  - `afp_nombre`, `vigencia_mes` (strings)
  - `aporte_obligatorio_pct`, `comision_flujo_pct`, `comision_mixta_pct`, `prima_seguro_pct` (decimals)
  - `remuneracion_max_asegurable` (decimal)
  - `estado` (string, choices) — same caveat as before
  - `estado_texto` (string, source='get_status_display')
  - `es_activo` (boolean, ReadOnlyField)
  - `created_at`, `updated_at`

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:39-52` `ConfiguracionAfp`
- Field declarations:
  - `afp_config_id: number` ← **MISMATCH** (UUID string)
  - All decimal/string fields ← MATCH
  - `estado: "activo" | "inactivo"` ← MATCH
  - `es_activo?: boolean` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Same as Compensation/MonthlyPayroll.
- **L3.10.4e (PK):** rename `afp_config_id: number → id: string`.

---

### 22. TaxParameter (UIT) (`apps.payroll.TaxParameter`)

**Backend:**
- Model: `apps/api/apps/payroll/models/tax_parameter.py:12-77`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 20) — **UUID PK**
  - `anio = PositiveIntegerField()` (21)
  - `valor_uit, tope_renta_cuarta_uit, porcentaje_renta_cuarta` (22-37)
  - `status = CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', db_column='estado')` (39) — **PLATFORM-RENAMED**
  - `created_at, updated_at` (42-43)
  - `created_by = ForeignKey('identity.User', ...)` (44-51)
  - `db_table = 'configuracion_uit'`
- Primary serializer: `ConfiguracionUitSerializer` `remuneraciones_serializers.py:59-134`
- JSON keys emitted:
  - `id` (string UUID)
  - `anio` (int)
  - `valor_uit, tope_renta_cuarta_uit, porcentaje_renta_cuarta` (decimals)
  - `estado` (string, choices) — same caveat
  - `estado_texto` (string, source='get_status_display')
  - `es_activo` (boolean, SerializerMethodField — derived from `obj.estado=='activo'`. **WAIT — this code reads `obj.estado` which doesn't exist. The model attribute is `status`. So `get_es_activo` returns False always.** This is another bug discovered.)
  - `tope_renta_cuarta_soles` (decimal, computed property)
  - `essalud_cas_mensual` (decimal, computed property)
  - `created_by` (string UUID | null)
  - `creado_por_nombre` (string, source='created_by.nombres_usuario')
  - `created_at, updated_at`

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:65-80` `ConfiguracionUit`
- Field declarations:
  - `configuracion_uit_id: number` ← **MISMATCH** (UUID string)
  - `anio: number, valor_uit, tope_renta_cuarta_uit, porcentaje_renta_cuarta` ← MATCH
  - `estado: "activo" | "inactivo"` ← MATCH (if serializer works)
  - `estado_texto?, es_activo?` ← MATCH
  - `tope_renta_cuarta_soles: number, essalud_cas_mensual: number` ← MATCH
  - `created_by?: number, created_by_nombre?: string` ← **MISMATCH** (UUID string for created_by; field name is `creado_por_nombre`)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Same as Compensation. JSON key `estado` → `status`.
- **L3.10.4e (PK):** rename `configuracion_uit_id: number → id: string`. `created_by: number → created_by: string`.
- **Out-of-scope discovery:** `get_es_activo` reads `obj.estado` instead of `obj.status` — it's a runtime bug always returning False. FE field name is `created_by_nombre` but backend emits `creado_por_nombre`.

---

### 23. MassDeduction (`apps.payroll.MassDeduction`)

**Backend:**
- Model: `apps/api/apps/payroll/models/compensation.py:404-457`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 414) — **UUID PK**
  - `periodo = CharField(max_length=7)` (415)
  - `configuracion_concepto = ForeignKey(CompensationConfiguration, ...)` (416-421)
  - `archivo_origen = FileField(...)` (422-425)
  - `total_registros, registros_procesados, registros_error` (426-428)
  - `monto_total = DecimalField(...)` (429-431)
  - `status = CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente', db_column='estado')` (432-434) — **PLATFORM-RENAMED**
  - `errores_log = TextField(null=True, blank=True)` (435)
  - `usuario_carga = ForeignKey('identity.User', on_delete=PROTECT, related_name='descuentos_masivos_cargados')` (438-442)
  - `fecha_carga, fecha_procesado, updated_at` (443-445)
  - `db_table = 'descuento_masivo'`
- Primary serializers:
  - `DescuentoMasivoListSerializer` `remuneraciones_serializers.py:512-545`
  - `DescuentoMasivoDetailSerializer` `remuneraciones_serializers.py:548-583`
- JSON keys emitted (`DescuentoMasivoListSerializer`):
  - `id` (string UUID)
  - `periodo` (string)
  - `configuracion_concepto` (string UUID FK)
  - `concepto_nombre` (string, source='configuracion_concepto.nombre')
  - `archivo_origen` (file URL)
  - `total_registros`, `registros_procesados`, `registros_error` (ints)
  - `monto_total` (decimal)
  - `estado` (string, choices) — same caveat
  - `estado_texto` (string, source='get_status_display')
  - `usuario_nombre` (string, source='usuario_carga.nombre_completo')
  - `fecha_carga`, `fecha_procesado` (datetimes)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:205-229` `DescuentoMasivo`
- Field declarations:
  - `descuento_masivo_id: number` ← **MISMATCH** (UUID string)
  - `periodo: string` ← MATCH
  - `configuracion_concepto?: { configuracion_id; nombre; codigo }` ← **MISMATCH** (backend emits as UUID string ID, NOT a nested object — FE service has `concepto_nombre` separately)
  - `archivo_origen, total_registros, registros_procesados, registros_error, monto_total` ← MATCH
  - `estado: EstadoDescuento` ← MATCH
  - `estado_texto?, errores_log?` ← MATCH
  - `usuario_carga?: { usuario_id; username; nombres_completos }` ← **MISMATCH** (backend emits `usuario_carga` UUID string + `usuario_nombre` separately)
  - `fecha_carga, fecha_procesado, updated_at` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** JSON `estado` → `status`.
- **L3.10.4e (PK):** rename `descuento_masivo_id → id` (string). `configuracion_concepto.configuracion_id → id` (string). `usuario_carga.usuario_id → id` (string).

---

### 24. Payslip (`apps.payroll.PaySlip`)

**Backend:**
- Model: `apps/api/apps/payroll/models/compensation.py:460-499`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 469) — **UUID PK**
  - `detalle_planilla = OneToOneField(PayrollDetail, on_delete=CASCADE, related_name='boleta')` (470-474)
  - `archivo_pdf = FileField(...)` (475-480)
  - `status = CharField(max_length=20, choices=ESTADO_CHOICES, default='generada', db_column='estado')` (481) — **PLATFORM-RENAMED**
  - `fecha_generacion, fecha_envio_email, fecha_descarga` (482-484)
  - `hash_documento = CharField(max_length=64, null=True, blank=True)` (485)
  - `db_table = 'boleta_pago'`
- Primary serializers:
  - `BoletaPagoListSerializer` `remuneraciones_serializers.py:611-666`
  - `BoletaPagoDetailSerializer` `remuneraciones_serializers.py:669-697`
- JSON keys emitted (`BoletaPagoListSerializer`):
  - `id` (string UUID)
  - `detalle_planilla` (string UUID FK)
  - `archivo_pdf` (file URL | null)
  - `estado` (string, choices) — caveat
  - `estado_texto` (string, source='get_status_display')
  - `empleado_nombre` (string, source='detalle_planilla.empleado.nombre_completo')
  - `empleado_dni` (string, source='detalle_planilla.empleado.numero_documento')
  - `periodo` (string, source='detalle_planilla.planilla.periodo')
  - `total_ingresos`, `total_descuentos`, `neto_pagar` (decimals from nested)
  - `fecha_generacion`, `fecha_envio_email`, `fecha_descarga` (datetimes | null)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:237-261` `BoletaPago`
- Field declarations:
  - `boleta_id: number` ← **MISMATCH** (UUID string)
  - `detalle_planilla: { detalle_id; planilla_periodo }` ← **MISMATCH** (backend emits UUID string)
  - `empleado?: {...}` ← **MISMATCH** (backend doesn't emit nested empleado, just flat `empleado_nombre`/`empleado_dni`)
  - `empleado_nombre?, empleado_dni?, periodo, total_ingresos, total_descuentos, neto_pagar` ← MATCH
  - `estado: EstadoBoleta` ← MATCH
  - `estado_texto?` ← MATCH
  - `pdf_url?` ← **MISMATCH** (backend emits `archivo_pdf` URL, not `pdf_url`)
  - `hash_documento?` ← MATCH (only in detail serializer)
  - `fecha_generacion, fecha_envio?, fecha_visualizacion?` ← partial MATCH (backend has `fecha_envio_email`, `fecha_descarga`)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** JSON `estado` → `status`.
- **L3.10.4e (PK):** rename `boleta_id → id` (string). `detalle_planilla.detalle_id → id` (string).

---

### 25. PaymentSchedule (`apps.payroll.PaymentSchedule`)

**Backend:**
- Model: `apps/api/apps/payroll/models/compensation.py:502-550`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 518) — **UUID PK**
  - `planilla = ForeignKey(MonthlyPayroll, on_delete=CASCADE, related_name='calendarios_pago')` (519-523)
  - `tipo_pago = CharField(max_length=20, choices=TIPO_PAGO_CHOICES)` (524)
  - `fecha_pago_programada = DateField()` (525)
  - `fecha_pago_ejecutada = DateField(null=True, blank=True)` (526)
  - `descripcion` (527)
  - `status = CharField(max_length=20, choices=ESTADO_CHOICES, default='activo', db_column='estado')` (528) — **PLATFORM-RENAMED**
  - `usuario_programacion = ForeignKey('identity.User', on_delete=PROTECT, related_name='calendarios_programados')` (531-534) — UUID FK
  - `created_at, updated_at` (536-537)
  - `db_table = 'calendario_pago'`
- Primary serializers:
  - `CalendarioPagoListSerializer` `remuneraciones_serializers.py:705-736`
  - `CalendarioPagoDetailSerializer` `remuneraciones_serializers.py:739-771`
- JSON keys emitted (`CalendarioPagoListSerializer`):
  - `id` (string UUID)
  - `planilla` (string UUID FK)
  - `periodo` (string, source='planilla.periodo')
  - `modalidad_planilla` (string, source='planilla.get_modalidad_display')
  - `tipo_pago` (string, choices)
  - `tipo_pago_texto` (string, source='get_tipo_pago_display')
  - `fecha_pago_programada`, `fecha_pago_ejecutada` (dates | null)
  - `descripcion` (string | null)
  - `estado` (string, choices) — caveat
  - `estado_texto` (string, source='get_status_display')
  - `created_at` (datetime)

**Frontend (current state):**
- Primary interface: `apps/web/src/services/payrollService.ts:263-279` `CalendarioPago`
- Field declarations:
  - `calendario_id: number` ← **MISMATCH** (UUID string)
  - `periodo: string` ← MATCH
  - `descripcion: string` ← MATCH
  - `fecha_pago_programada, fecha_pago_real?` ← partial MATCH (backend has `fecha_pago_ejecutada`)
  - `modalidad: ModalidadContrato` ← **MISMATCH** (backend emits `modalidad_planilla` not `modalidad`)
  - `meta_presupuestal?` ← **NOT EMITTED** (the calendar serializer doesn't expose meta_presupuestal)
  - `estado: EstadoCalendario` ← MATCH
  - `estado_texto?, observaciones?` ← partial MATCH
  - `created_by?: { usuario_id; username }` ← **MISMATCH** (backend emits `usuario_programacion` UUID string, not nested)
  - `created_at: string` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** JSON `estado` → `status`.
- **L3.10.4e (PK):** rename `calendario_id → id` (string). `planilla → planilla` (string UUID). `usuario_programacion → usuario_programacion` (string UUID).

---

### 26. VacationConfiguration (`apps.time_off.VacationConfiguration`)

**Backend:**
- Model: `apps/api/apps/time_off/models/vacation.py:25-159`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 42) — **UUID PK**
  - `tipo_configuracion` (43), `area` UUID FK (46-52), `empleado` UUID FK (53-59)
  - Vacation policy fields (62-118)
  - `is_active = BooleanField(default=True, db_column='activo')` (121) — **PLATFORM-RENAMED** (Python attr `is_active`, DB col `activo`)
  - `fecha_inicio_vigencia, fecha_fin_vigencia, observaciones` (122-124)
  - `created_at, updated_at, created_by` (127-136)
  - `db_table = 'configuracion_vacaciones'`
- Primary serializer: `ConfiguracionVacacionesSerializer` `vacaciones/serializers.py:29-87`
- JSON keys emitted:
  - `id` (string UUID)
  - `tipo_configuracion` (string)
  - `tipo_configuracion_display` (string, source='get_tipo_configuracion_display')
  - `area` (string UUID | null)
  - `area_nombre` (string, SerializerMethodField)
  - `empleado` (string UUID | null)
  - `empleado_nombre` (string, source='empleado.nombre_completo')
  - All policy fields (dias_por_ano, dias_adicionales_antiguedad, etc.)
  - `tipo_calculo`, `tipo_calculo_display`
  - `incluye_feriados`, `incluye_fines_semana`, `requiere_aprobacion_jefe`, `requiere_aprobacion_rrhh` (booleans)
  - `niveles_aprobacion`, `permite_fraccionamiento`, `min_dias_por_fraccion`, `max_fracciones_por_ano`
  - `activo` (boolean) — **JSON key is `activo`** because Meta.fields line 78 is `'activo'`. The Python attribute is `is_active` (with `db_column='activo'`). **Same serializer/model mismatch issue — the serializer fields list says `'activo'`, but the model has Python attr `is_active`. This will likely fail at runtime unless DRF maps somehow.**
  - `fecha_inicio_vigencia, fecha_fin_vigencia, observaciones`
  - `created_by` (string UUID | null), `creado_por_nombre`
  - `created_at, updated_at`

**Frontend (current state):**
- Primary interface: `apps/web/src/services/timeOffService.ts:3-8` `ConfiguracionVacaciones`
- Field declarations:
  - `configuracion_id: number` ← **MISMATCH** (UUID string)
  - `tipo_configuracion: string` ← MATCH
  - `dias_por_ano: number` ← MATCH
  - `activo: boolean` ← MATCH (JSON key is `activo`)

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend emits `activo` JSON key. If renaming to `is_active`, fix serializer Meta.fields entry from `'activo'` to `'is_active'`. Then FE rename `activo → is_active`.
- **L3.10.4e (PK):** rename `configuracion_id → id` (string).

---

### 27. VacationPeriod (`apps.time_off.VacationPeriod`)

**Backend:**
- Model: `apps/api/apps/time_off/models/vacation.py:162-291`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 173) — **UUID PK**
  - `empleado = ForeignKey('employees.Employee', on_delete=CASCADE)` (174-178) — UUID FK
  - `contrato = ForeignKey('contracts.Contract', on_delete=PROTECT, null=True, blank=True)` (179-185) — UUID FK
  - `ano_periodo, fecha_inicio_periodo, fecha_fin_periodo, fecha_vencimiento` (188-191)
  - `dias_correspondientes, dias_adicionales, dias_totales, dias_gozados, dias_pendientes, dias_vencidos` (194-228)
  - `estado_periodo = CharField(max_length=15, choices=ESTADO_PERIODO_CHOICES, default='activo')` (231) — **PRESERVED-SPANISH-STATE**
  - `configuracion = ForeignKey(VacationConfiguration, on_delete=PROTECT)` (232-236) — UUID FK
  - `observaciones, motivo_cancelacion` (239-240)
  - `created_at, updated_at, created_by` (243-252)
  - `db_table = 'periodos_vacacionales'`
- Primary serializer: `PeriodoVacacionalSerializer` `vacaciones/serializers.py:90-149`
- JSON keys emitted:
  - `id` (string UUID)
  - `empleado` (string UUID FK)
  - `empleado_nombre` (string, source='empleado.nombre_completo')
  - `empleado_rut` (string, source='empleado.numero_documento')
  - `area_nombre` (string, SerializerMethodField from `obj.empleado.datos_laborales_actuales().area`)
  - `contrato` (string UUID | null)
  - `contrato_id` — **WAIT, fields list line 123 has `'id'` AGAIN (likely a cut-paste bug for `contrato_id`)** — but `contrato_id = serializers.IntegerField(source='contrato.contrato_id', read_only=True)` line 94 declares it. The `source='contrato.contrato_id'` will fail because Contract has `id` (UUID), not `contrato_id`. **Bug.**
  - `contrato_numero, contrato_fecha_inicio, contrato_fecha_fin, contrato_estado` (strings/dates from contrato.*)
  - `ano_periodo` (int)
  - `periodo_label` (string, SerializerMethodField — `f"{fecha_inicio.year}-{fecha_fin.year}"`)
  - `fecha_inicio_periodo, fecha_fin_periodo, fecha_vencimiento` (dates)
  - `dias_correspondientes, dias_adicionales, dias_totales, dias_gozados, dias_pendientes, dias_vencidos` (decimals)
  - `estado_periodo` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `configuracion` (string UUID FK)
  - `configuracion_tipo` (string, source='configuracion.get_tipo_configuracion_display')
  - `porcentaje_uso, esta_vencido, dias_para_vencimiento` (ReadOnlyField)
  - `observaciones, created_at, updated_at`

**Frontend (current state):**
- Primary interface: `apps/web/src/services/timeOffService.ts:10-33` `PeriodoVacacional`
- Field declarations:
  - `id: number` ← **MISMATCH** (UUID string)
  - `periodo_id: number` ← **MISMATCH** (backend doesn't emit; normalizer falls back to `id`)
  - `empleado: number` ← **MISMATCH** (UUID string)
  - `empleado_nombre, ano_periodo, periodo_label` ← MATCH
  - `fecha_inicio_periodo, fecha_fin_periodo, fecha_vencimiento` ← MATCH
  - `dias_correspondientes, dias_adicionales?, dias_totales?, dias_gozados, dias_pendientes, dias_vencidos?` ← MATCH
  - `estado_periodo: 'activo' | 'cerrado' | 'vencido' | 'cancelado'` ← MATCH
  - `contrato?: number | null` ← **MISMATCH** (UUID string)
  - `contrato_id?: number | null` ← **MISMATCH** (broken on backend; even if working, would be UUID string)
  - `contrato_numero?, contrato_fecha_inicio?, contrato_fecha_fin?, contrato_estado?` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** Backend `estado_periodo` (preserved Spanish). FE matches. No rename if Option B.
- **L3.10.4e (PK):** rename `id: number → id: string`. Drop `periodo_id`. `contrato`, `contrato_id` UUID strings. The `contrato_id` field in the serializer source='contrato.contrato_id' is broken (Contract has just `id`).

---

### 28. VacationRequest (`apps.time_off.VacationRequest`)

**Backend:**
- Model: `apps/api/apps/time_off/models/vacation.py:294-432`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 318) — **UUID PK**
  - `empleado = ForeignKey('employees.Employee', on_delete=CASCADE)` (319-323) — UUID FK
  - `periodo_vacacional = ForeignKey(VacationPeriod, on_delete=CASCADE)` (324-328) — UUID FK
  - `tipo_solicitud = CharField(max_length=25, choices=TIPO_SOLICITUD_CHOICES, default='vacaciones')` (331)
  - `fecha_inicio, fecha_fin = DateField()` (332-333)
  - `dias_solicitados = DecimalField(...)` (334-338)
  - `medio_dia = BooleanField(default=False)` (339)
  - `motivo_solicitud, observaciones_empleado` (342-343)
  - `estado_solicitud = CharField(max_length=20, choices=ESTADO_SOLICITUD_CHOICES, default='borrador')` (346) — **PRESERVED-SPANISH-STATE**
  - `fecha_envio` (347)
  - `aprobado_por_jefe = BooleanField(default=False)` (350)
  - `jefe_aprobador = ForeignKey('employees.Employee', on_delete=SET_NULL, null=True, blank=True)` (351-357) — UUID FK
  - `fecha_aprobacion_jefe, observaciones_jefe` (358-359)
  - `aprobado_por_rrhh = BooleanField(default=False)` (362)
  - `rrhh_aprobador = ForeignKey('identity.User', on_delete=SET_NULL, null=True, blank=True)` (363-369) — UUID FK
  - `fecha_aprobacion_rrhh, observaciones_rrhh` (370-371)
  - `motivo_rechazo, rechazado_por (UUID FK), fecha_rechazo` (374-382)
  - `motivo_cancelacion, cancelado_por (UUID FK), fecha_cancelacion` (385-393)
  - `created_at, updated_at` (396-397)
  - `db_table = 'solicitudes_vacaciones'`
- Primary serializer: `SolicitudVacacionesSerializer` `vacaciones/serializers.py:152-248`
- JSON keys emitted:
  - `id` (string UUID)
  - `empleado` (string UUID FK)
  - `empleado_nombre`, `empleado_rut` (sources)
  - `area_nombre` (SerializerMethodField)
  - `periodo_vacacional` (string UUID FK)
  - `periodo_label` (SerializerMethodField)
  - **Note: line 198 has `'id'` AGAIN duplicated. Likely intended `contrato_id` or `solicitud_id` — bug.**
  - `contrato_numero` (SerializerMethodField — calls `getattr(periodo.contrato, 'numero_contrato', None)`)
  - `tipo_solicitud, tipo_solicitud_display`
  - `fecha_inicio, fecha_fin` (dates)
  - `dias_solicitados, medio_dia`
  - `dias_calendario, dias_habiles` (SerializerMethodField)
  - `motivo_solicitud, observaciones_empleado`
  - `estado_solicitud, estado_solicitud_display` — **PRESERVED-SPANISH-STATE**
  - `fecha_envio, aprobado_por_jefe, jefe_aprobador (UUID), jefe_aprobador_nombre, fecha_aprobacion_jefe, observaciones_jefe`
  - `aprobado_por_rrhh, rrhh_aprobador (UUID), rrhh_aprobador_nombre, fecha_aprobacion_rrhh, observaciones_rrhh`
  - `motivo_rechazo, rechazado_por (UUID), fecha_rechazo`
  - `motivo_cancelacion, cancelado_por (UUID), fecha_cancelacion`
  - `created_at, updated_at`

**Frontend (current state):**
- Primary interface: `apps/web/src/services/timeOffService.ts:35-67` `SolicitudVacaciones`
- Field declarations:
  - `id: number` ← **MISMATCH** (UUID string)
  - `solicitud_id: number` ← **MISMATCH** (backend doesn't emit; normalizer falls back)
  - `empleado: { id: number; nombres?, apellidos?, numero_identificacion? }` ← **MISMATCH** (backend emits `empleado` as UUID string and `empleado_nombre` separately)
  - `empleado_nombre?, empleado_nombre_completo?` ← MATCH (normalizer reproduces)
  - `area?: { nombre_area? }`, `area_nombre?` ← partial MATCH
  - `periodo_vacacional: { id: number; ano_periodo? }` ← **MISMATCH** (backend emits UUID string)
  - `periodo_ano?` ← MATCH (normalizer)
  - `tipo_solicitud, fecha_inicio, fecha_fin, dias_solicitados, medio_dia?` ← MATCH
  - `estado_solicitud: string` ← MATCH
  - `fecha_envio?, created_at` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** `estado_solicitud` (preserved Spanish). FE matches. No rename if Option B.
- **L3.10.4e (PK):** rename `id: number → id: string`. Drop `solicitud_id`. All FK fields (`empleado`, `periodo_vacacional`, `jefe_aprobador`, `rrhh_aprobador`, `rechazado_por`, `cancelado_por`) UUID strings.

---

### 29. VacationGrant (`apps.time_off.VacationGrant`)

**Backend:**
- Model: `apps/api/apps/time_off/models/vacation.py:435-557`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 455) — **UUID PK**
  - `solicitud_vacaciones = OneToOneField(VacationRequest, on_delete=CASCADE, related_name='goce')` (456-460) — UUID FK
  - `empleado = ForeignKey('employees.Employee', on_delete=CASCADE)` (461-465)
  - `periodo_vacacional = ForeignKey(VacationPeriod, on_delete=CASCADE)` (466-470)
  - `fecha_inicio_real, fecha_fin_real, fecha_reincorporacion` (473-475)
  - `dias_gozados` (478-482)
  - `estado_goce = CharField(max_length=15, choices=ESTADO_GOCE_CHOICES, default='programado')` (483) — **PRESERVED-SPANISH-STATE**
  - `fecha_interrupcion, motivo_interrupcion, descripcion_interrupcion, dias_no_gozados` (486-499)
  - `reincorporado, fecha_reincorporacion_real, observaciones_reincorporacion` (502-504)
  - `observaciones, created_at, updated_at, registrado_por` (507-518)
  - `db_table = 'goces_vacaciones'`
- Primary serializer: `GoceVacacionesSerializer` `vacaciones/serializers.py:298-334`
- JSON keys emitted:
  - `id` (string UUID)
  - `empleado` (string UUID), `empleado_nombre` (string)
  - `solicitud_vacaciones` (string UUID)
  - `solicitud_id` (line 300 — `IntegerField(source='solicitud_vacaciones.solicitud_id', read_only=True)` **broken** — VacationRequest has no `solicitud_id` field, only `id`. Bug.)
  - **Lines 312, 314 in fields list have `'id'` duplicated** (cut-paste bug)
  - `periodo_vacacional` (string UUID)
  - `contrato_id` (broken — references `periodo_vacacional.contrato.contrato_id` which doesn't exist; Contract has `id`)
  - `contrato_numero` (string, source='periodo_vacacional.contrato.numero_contrato')
  - `fecha_inicio_real, fecha_fin_real, fecha_reincorporacion` (dates)
  - `dias_gozados` (decimal)
  - `estado_goce, estado_goce_display` — **PRESERVED-SPANISH-STATE**
  - `fecha_interrupcion, motivo_interrupcion, descripcion_interrupcion, dias_no_gozados`
  - `reincorporado, fecha_reincorporacion_real, observaciones_reincorporacion`
  - `observaciones, registrado_por (UUID), created_at, updated_at`

**Frontend (current state):**
- Primary interface: `apps/web/src/services/timeOffService.ts:69-78` `GoceVacaciones`
- Field declarations:
  - `goce_id: number` ← **MISMATCH** (UUID string)
  - `empleado: number` ← **MISMATCH** (UUID string)
  - `solicitud_vacaciones: number` ← **MISMATCH** (UUID string)
  - `periodo_vacacional: number` ← **MISMATCH** (UUID string)
  - `fecha_inicio_real, fecha_fin_real, dias_gozados, estado_goce` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** `estado_goce` (preserved Spanish). FE matches. No rename if Option B.
- **L3.10.4e (PK):** rename `goce_id → id` (string). All FK fields UUID strings.

---

### 30. OnboardingProcess (`apps.onboarding.OnboardingProcess`)

**Backend:**
- Model: `apps/api/apps/onboarding/models/onboarding_process.py:9-176`
  - `id = UUIDField(primary_key=True, default=uuid.uuid4, editable=False)` (line 21) — **UUID PK**
  - `empleado = OneToOneField('employees.Employee', on_delete=CASCADE, related_name='onboarding')` (24-28) — UUID FK
  - `usuario = OneToOneField('identity.User', on_delete=CASCADE, related_name='onboarding')` (29-33) — UUID FK
  - `estado_onboarding = CharField(max_length=25, choices=ESTADO_ONBOARDING_CHOICES, default='pendiente_datos')` (36-40) — **PRESERVED-SPANISH-STATE**
  - Checklist booleans (43-49): `datos_personales_completos, datos_laborales_completos, dni_subido, declaraciones_juradas_subidas, certificados_academicos_subidos, certificados_trabajo_subidos, documentos_familiares_subidos`
  - `validado_por = ForeignKey('identity.User', on_delete=SET_NULL, null=True, blank=True)` (52-58) — UUID FK
  - `fecha_validacion, observaciones` (59-60)
  - `email_bienvenida_enviado, fecha_email_bienvenida` (63-64)
  - `fecha_inicio = DateTimeField(auto_now_add=True)` (67)
  - `fecha_completado = DateTimeField(null=True, blank=True)` (68)
  - `updated_at = DateTimeField(auto_now=True, db_column='fecha_actualizacion')` (69)
  - `db_table = 'onboarding_empleado'`
- Primary serializer: `OnboardingEmpleadoSerializer` `serializers.py:1217-1268`
- JSON keys emitted:
  - `id` (string UUID)
  - `empleado` (string UUID FK), `empleado_nombre`, `empleado_documento`
  - `usuario` (string UUID FK), `usuario_username`
  - `estado_onboarding` (string, choices) — **PRESERVED-SPANISH-STATE**
  - `datos_personales_completos, datos_laborales_completos, dni_subido, declaraciones_juradas_subidas, certificados_academicos_subidos, certificados_trabajo_subidos, documentos_familiares_subidos` (booleans)
  - `progreso_porcentaje` (int, ReadOnlyField)
  - `items_pendientes` (list of strings, ReadOnlyField)
  - `documentos_pendientes` (list of objects, SerializerMethodField — calls service)
  - `validado_por` (string UUID | null)
  - `fecha_validacion, observaciones`
  - `email_bienvenida_enviado, fecha_email_bienvenida`
  - `fecha_inicio, fecha_completado`
  - `last_login` (datetime | null, source='usuario.last_login')

**Frontend (current state):**
- Primary interface: `apps/web/src/services/onboardingService.ts:4-33` `OnboardingStatus`
- Field declarations:
  - `onboarding_id: number` ← **MISMATCH** (backend emits `id` UUID string)
  - `empleado: number` ← **MISMATCH** (UUID string)
  - `empleado_nombre, empleado_documento` ← MATCH
  - `usuario: number` ← **MISMATCH** (UUID string)
  - `usuario_username` ← MATCH
  - `estado_onboarding: string` ← MATCH
  - All boolean checklist fields ← MATCH
  - `progreso_porcentaje, items_pendientes, documentos_pendientes` ← MATCH
  - `validado_por: number | null` ← **MISMATCH** (UUID string)
  - `fecha_validacion, observaciones, email_bienvenida_enviado, fecha_email_bienvenida` ← MATCH
  - `fecha_inicio, fecha_completado` ← MATCH

**Diff (L3.10.4d/4e action items):**
- **L3.10.4d (state):** `estado_onboarding` preserved Spanish. FE matches. No rename if Option B.
- **L3.10.4e (PK):** rename `onboarding_id: number → id: string`. `empleado, usuario, validado_por` UUID strings.

---

## L3.10.4d action plan derived from this audit

**Two interpretations of L3.10.4d are possible:**

### Interpretation A (Strict Option B: only platform-renamed fields touched)

Renames only the entities where the backend ALREADY has `status` / `is_active` Python attributes. The serializer JSON-key alignment must be fixed first.

**Files to touch (backend — fix serializer Meta.fields keys first):**
| File | Current key | Target key |
|------|------------|------------|
| `apps/api/api/v1/rrhh/contratos_serializers.py:49` (Contract) | `'status'` | (already correct, FE alignment only) |
| `apps/api/api/v1/rrhh/contratos_serializers.py:280` (ContractAmendment) | `'status'` | (already correct, FE alignment only) |
| `apps/api/api/v1/rrhh/serializers.py:360` (Compensation `ConfiguracionRemuneracionSerializer`) | `'estado'` | `'status'` (or add `source='status'`) |
| `apps/api/api/v1/rrhh/serializers.py:425` (Afp `ConfiguracionAfpSerializer` v1) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:50` (Afp v2) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:82` (TaxParameter) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:157` (Compensation v2) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:196` (MonthlyPayroll List) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:247` (MonthlyPayroll Detail) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:535` (MassDeduction List) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:570` (MassDeduction Detail) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:649` (PaySlip List) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:684` (PaySlip Detail) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:729` (PaymentSchedule List) | `'estado'` | `'status'` |
| `apps/api/api/v1/rrhh/remuneraciones_serializers.py:760` (PaymentSchedule Detail) | `'estado'` | `'status'` |
| `apps/api/api/v1/vacaciones/serializers.py:78` (VacationConfig) | `'activo'` | `'is_active'` |

**Files to touch (frontend):**
| File | Field rename |
|------|--------------|
| `apps/web/src/services/contractsService.ts:35` (Contrato) | `estado: string → status: string` |
| `apps/web/src/services/contractsService.ts:65` (ContratoListItem) | `estado: string → status: string` |
| `apps/web/src/services/payrollService.ts:15` (ConceptoRemuneracion) | `estado → status` |
| `apps/web/src/services/payrollService.ts:48` (ConfiguracionAfp) | `estado → status` |
| `apps/web/src/services/payrollService.ts:71` (ConfiguracionUit) | `estado → status` |
| `apps/web/src/services/payrollService.ts:129` (PlanillaMensual) | `estado → status` |
| `apps/web/src/services/payrollService.ts:218` (DescuentoMasivo) | `estado → status` |
| `apps/web/src/services/payrollService.ts:254` (BoletaPago) | `estado → status` |
| `apps/web/src/services/payrollService.ts:271` (CalendarioPago) | `estado → status` |
| `apps/web/src/services/timeOffService.ts:7` (ConfiguracionVacaciones) | `activo → is_active` |
| All consumer components for the above | rename references (`.estado` → `.status`, `.activo` → `.is_active`) |

**Estimated total ref count:**
- Backend: ~16 serializer Meta.fields entries + ~16 references in Python views/filters that read `obj.estado` / `obj.activo` (must use `obj.status` / `obj.is_active`)
- Frontend: 9 interface field renames + ~80–120 component references (`.estado_*` and `.activo` lookups) — high-impact in payroll/contracts UI

### Interpretation B (Aggressive: also rename preserved-Spanish-state fields)

Adds renames for entities where the model still has `estado_<entity>` (Department, Role, Permission, Module, EmploymentData, FamilyMember, AcademicRecord (likely keep — domain), Certification, DigitalDocument, OnboardingProcess, VacationPeriod, VacationRequest, VacationGrant, Employee, User).

**Risk:** Larger blast radius. AcademicRecord's `estado_estudios` is genuinely domain (not platform). Keeping it but renaming `estado_area`, `estado_rol`, `estado_permiso`, `estado_modulo`, `estado_familiar`, `estado_documento`, `estado_onboarding`, `estado_periodo`, `estado_solicitud`, `estado_goce` to `status` is consistent with platform-only-rename — but contradicts spec § 3.6.1 Option B.

**Recommendation:** Stick with Interpretation A (Option B). Defer Interpretation B to a separate sub-PR if needed.

---

## L3.10.4e action plan derived from this audit

**All 22 entities with UUID PKs have frontend interfaces declaring `<entity>_id: number`.**

**Files to touch (frontend — drop `_id` aliases, change PK type number → string):**
| File | Field rename |
|------|--------------|
| `apps/web/src/services/employeesService.ts:10` (Employee) | `id: number → id: string` (also update normalizer) |
| `apps/web/src/services/employeesService.ts:69-73` (DatosLaborales) | `id?, empleado_id, area_id, supervisor_id` → strings |
| `apps/web/src/services/employeesService.ts:85-88` (DatosFamiliares) | `id?, empleado_id` → strings |
| `apps/web/src/services/employeesService.ts:98-100` (DatosAcademicos) | `id?, empleado_id` → strings |
| `apps/web/src/services/departmentsService.ts:5` (Area) | `area_id: number → id: string` |
| `apps/web/src/services/usersService.ts:11-14` (User) | `id, usuario_id, empleado.id, empleado.area.id` → strings |
| `apps/web/src/services/usersService.ts:41-43` (Role) | `id, rol_id` → strings |
| `apps/web/src/services/usersService.ts:53-54` (Permission) | `id, permiso_id` → strings |
| `apps/web/src/services/contractsService.ts:5-9` (Contrato) | `contrato_id, empleado, area, area_detalle.area_id` → strings |
| `apps/web/src/services/contractsService.ts:51-54` (ContratoListItem) | `contrato_id, empleado` → strings |
| `apps/web/src/services/legajoService.ts:5-7` (Documento) | `documento_id, empleado, subido_por, validado_por` → strings |
| `apps/web/src/services/templatesService.ts:11` (PlantillaDocumento) | `plantilla_id → id: string` |
| `apps/web/src/services/payrollService.ts:6` (ConceptoRemuneracion) | `configuracion_id → id: string` |
| `apps/web/src/services/payrollService.ts:40` (ConfiguracionAfp) | `afp_config_id → id: string` |
| `apps/web/src/services/payrollService.ts:66` (ConfiguracionUit) | `configuracion_uit_id → id: string`, `created_by → string` |
| `apps/web/src/services/payrollService.ts:115` (PlanillaMensual) | `planilla_id → id: string` |
| `apps/web/src/services/payrollService.ts:151-160` (DetallePlanilla) | `detalle_id, planilla.planilla_id, empleado.empleado_id` → strings |
| `apps/web/src/services/payrollService.ts:206-220` (DescuentoMasivo) | `descuento_masivo_id, configuracion_concepto.configuracion_id, usuario_carga.usuario_id` → strings |
| `apps/web/src/services/payrollService.ts:238-246` (BoletaPago) | `boleta_id, detalle_planilla.detalle_id, empleado.empleado_id` → strings |
| `apps/web/src/services/payrollService.ts:264-274` (CalendarioPago) | `calendario_id, created_by.usuario_id` → strings |
| `apps/web/src/services/timeOffService.ts:4` (ConfiguracionVacaciones) | `configuracion_id → id: string` |
| `apps/web/src/services/timeOffService.ts:11-12` (PeriodoVacacional) | `id, periodo_id, empleado, contrato, contrato_id` → strings |
| `apps/web/src/services/timeOffService.ts:36-49` (SolicitudVacaciones) | `id, solicitud_id, empleado.id, periodo_vacacional.id` → strings |
| `apps/web/src/services/timeOffService.ts:70-73` (GoceVacaciones) | `goce_id, empleado, solicitud_vacaciones, periodo_vacacional` → strings |
| `apps/web/src/services/onboardingService.ts:5-9` (OnboardingStatus) | `onboarding_id, empleado, usuario, validado_por` → strings |
| `apps/web/src/lib/api.ts:25-44` (User in api.ts) | `id, usuario_id, empleado.id, empleado.area.id, roles[].id, permisos[].id` → strings |
| `apps/web/src/services/normalizers/apiNormalizers.ts` | `getNumber(...) → getString(...)` for `empleado_id`, `usuario_id`, `rol_id`, etc. |
| `apps/web/src/services/securityService.ts:28-65` (Role, Permission, RolePermission) | All `_id: number → id: string` |

**Estimated total ref count:**
- Frontend: ~30 interface declarations changed + ~150–200 consumer references (URL paths in service methods like `/api/v1/employees/${id}/`, query keys in React Query, FK lookups in forms)
- Particular pain points:
  - All hooks doing `useQuery(['employees', id], ...)` — query keys still work with strings but type signatures change
  - URL params in router (`useParams<{ id: string }>()` already returns strings, so this is less painful)
  - All `.find(e => e.id === someId)` comparisons must use string equality

**Estimated new MISMATCH discovery if PK rename ships first:**
- The normalizers (`apiNormalizers.ts`) do `getNumber(employeeObj.empleado_id ?? employeeObj.id)` which silently coerces UUID strings to `0`. Without fixing the normalizer first, all entity IDs become 0 in the FE → cascade failure.

---

## Out-of-scope discoveries

The following issues were uncovered during the audit and need separate investigation. They are **NOT** part of L3.10.4d or L3.10.4e but should be tracked.

### Backend serializer bugs

1. **`RolPermisosSerializer` (`apps/api/api/v1/rrhh/serializers.py:1037-1040`)** has `'id'` listed three times in `Meta.fields`. Likely intended `id`, `rol_id`, `permiso_id` but copy-pasted. Validation `validate()` reads `data.get("id")` (which is now ambiguous) instead of `rol_id`/`permiso_id`. **Bug — validation likely never works.**

2. **`PeriodoVacacionalSerializer` (`apps/api/api/v1/vacaciones/serializers.py:94, 123`)** declares `contrato_id = serializers.IntegerField(source='contrato.contrato_id', read_only=True)` but `Contract` model has `id` (UUID), not `contrato_id`. The source path is broken. The fields list at line 123 has `'id'` (typo for `'contrato_id'`).

3. **`SolicitudVacacionesSerializer` (`apps/api/api/v1/vacaciones/serializers.py:198`)** has `'id'` duplicated in Meta.fields list.

4. **`GoceVacacionesSerializer` (`apps/api/api/v1/vacaciones/serializers.py:300, 302, 312, 314`)** has multiple bugs — `solicitud_id = IntegerField(source='solicitud_vacaciones.solicitud_id')` references non-existent attribute. `contrato_id = IntegerField(source='periodo_vacacional.contrato.contrato_id')` similarly broken. Fields list has `'id'` duplicated.

5. **All payroll serializers and `vacaciones/serializers.py` `ConfiguracionVacacionesSerializer`** reference `'estado'` or `'activo'` in `Meta.fields`, but the model has `status` / `is_active` Python attributes (with `db_column` for storage). DRF's `ModelSerializer` resolves field names through model attributes — **`'estado'` in fields list will fail at runtime unless DRF is doing some magic.** Possible explanations:
   - DRF inspects `db_column` and accepts the column name. Unlikely — DRF reads `model._meta.fields` Python attribute names.
   - The serializers were NOT actually working at runtime when L3.10.2 landed — runtime tests may have been skipped.
   - Test fixtures use raw model creation, bypassing serializer validation.

   **Action: Run `manage.py check` and a smoke test of the endpoints to verify these serializers work at all.**

6. **`TaxParameterSerializer.get_es_activo` (line 99-101)** reads `obj.estado` instead of `obj.status`. Always returns False. Bug.

7. **`AreaSerializer.validate_siglas_area`** (line 73-81) and **`EmpleadoCreateSerializer.validate_area_inicial`** (line 717-723) reference `area_id` in Department queryset filters. Department PK is now UUID called `id`, not `area_id`. Likely runtime errors waiting to happen.

8. **`AsignarRolSerializer.validate_roles` (`usuario_roles_serializers.py:185-198`)** filters by `rol_id__in=value` but Role PK is `id`. Bug.

### Frontend interface stale/incorrect declarations

1. `Module` in `securityService.ts:48-53` is a stub — doesn't reflect backend. Dead code or incomplete feature.
2. `DatosLaborales` (`employeesService.ts:68-82`) has `salario_base, supervisor_id, motivo_cese, cargo_id, horario_trabajo` — none of these field names match the backend `DatosLaboralesSerializer`. This interface is fictional.
3. `DatosFamiliares` (`employeesService.ts:84-95`) has `nombre_familiar, apellidos_familiar, dni_familiar, fecha_nacimiento_familiar` — backend emits `nombres_familiar, apellido_paterno, apellido_materno, numero_documento, fecha_nacimiento`. Interface is fictional.
4. `DatosAcademicos` (`employeesService.ts:97-107`) has `institucion, titulo_obtenido, estado_estudio, documento_sustentatorio` — backend emits `nombre_institucion, numero_titulo, estado_estudios, documento (FK)`. Interface is fictional.
5. Three duplicate `Role` interfaces (`usersService.ts:40-50`, `securityService.ts:27-35`, `lib/api.ts:9-14`) with subtly different field shapes. Need consolidation.
6. Three duplicate `Permission` interfaces with different field shapes. Need consolidation.
7. `BoletaPago.pdf_url` (`payrollService.ts:256`) — backend emits `archivo_pdf`. Mismatch.
8. `CalendarioPago.modalidad` (`payrollService.ts:269`) — backend emits `modalidad_planilla`. Mismatch.

### Frontend normalizer duplication

`apps/web/src/services/normalizers/apiNormalizers.ts` papers over MANY of the field-name and type mismatches above. Once L3.10.4d/4e land, the normalizer should be **removed** (or reduced to a no-op). Future plans should track its eventual deletion.

### URL contracts

The audit uncovers that all frontend service files use `/api/v1/<english-bounded-context>/...` URLs (post-L3.10.4a/4b). E.g., `/api/v1/employees/`, `/api/v1/contracts/`, `/api/v1/identity/users/`. These match the L3.10.4a backend rename.

### Pagination contract

DRF returns `{ success, message, data: { results, count }, meta: { pagination: {...} } }`. Most FE services unwrap with `extractCollection` or inline `raw?.data?.results ?? raw?.results ?? raw?.data ?? raw`. A single `unwrapPaginated` helper would eliminate ~30 duplicated unwrap fragments.

---

**End of audit.**
