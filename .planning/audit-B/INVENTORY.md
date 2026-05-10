# Vyntia Core — Inventory (B.0 audit)

> Per-app inventory of state-of-the-codebase for Vyntia Core (post-Foundation A + Multi-tenancy C).
> Audit date: 2026-05-09.
> Sources: VYNTIA `apps/api/apps/*` and `apps/web/src/features/*`, INTRANET legacy `D:/INTRANET/`, maestro `docs/00_VYNTIA_MAESTRO.md` § 3.

## Status legend

- ✅ Implemented and working
- ⚠️ Partial / needs polish
- ❌ Missing / not started
- 🐛 Bug or deuda técnica

## App: identity

### Estado actual en VYNTIA (post-A+C)

#### Modelos
- `User` (file: `apps/api/apps/identity/models/user.py:20`) — usuario de autenticación VYNTIA. Subclase de `AbstractBaseUser + PermissionsMixin`. PK UUID. Mantiene compatibilidad legacy via `db_column` (`fecha_creacion`, `fecha_actualizacion`, `creado_por_id`).
  - Campos clave: `username` (unique), `email` (unique), `password`, `nombres_usuario`, `apellidos_usuario`, `tipo_usuario` (choices ES), `nivel_acceso`, `is_active`, `is_staff`, `is_superuser`, `is_vyntia_staff` (C.5, line 76), `estado_usuario`, password lifecycle (`fecha_ultimo_cambio_password`, `fecha_expiracion_password`, `requiere_cambio_password`), bloqueo (`intentos_fallidos`, `fecha_bloqueo`, `token_recuperacion`, `fecha_expiracion_token`), audit (`ip_ultimo_acceso`, `user_agent_ultimo_acceso`), `empleado` OneToOne→`employees.Employee`, `created_by` self-FK.
  - Tenant FK: ❌ (intencional — usuarios cross-tenant; pertenencia vía `tenancy.TenantMembership`).
  - Manager: `UsuarioManager` (managers.py:10) — sobrescribe `get_queryset` con `select_related("empleado")`, `create_user`/`create_superuser`, helpers de búsqueda.
- `Role` (file: `apps/api/apps/identity/models/roles.py:6`) — rol RBAC.
  - Campos clave: `nombre_rol`, `descripcion_rol`, `nivel_jerarquico`, `es_rol_sistema`, `estado_rol`, `tenant` FK→`tenancy.Tenant` (line 25), unique `(tenant, nombre_rol)`.
  - Tenant FK: ✅ (line 25, nullable=true para datos globales/seed legacy).
  - Manager: default (custom comentado).
- `Permission` (file: `apps/api/apps/identity/models/roles.py:107`) — permiso atómico ligado a un módulo string-id.
  - Campos clave: `nombre_permiso`, `descripcion_permiso`, `modulo` (CharField — ID legacy, NO FK al modelo `Module`), `tipo_permiso` (crear/leer/actualizar/eliminar/ejecutar/aprobar), `estado_permiso`, `tenant` FK (line 139).
  - Tenant FK: ✅ (nullable=true).
  - Manager: default.
- `Module` (file: `apps/api/apps/identity/models/rbac.py:9`) — entrada del sidebar/menú jerárquico.
  - Campos clave: `nombre_modulo`, `icono_modulo`, `ruta_modulo`, `orden_visualizacion`, `estado_modulo`, `modulo_padre` self-FK, `permisos_requeridos` (CharField legacy CSV — fallback).
  - Tenant FK: ❌ (intencional — catálogo de módulos es global por ahora; cada permiso/asignación SÍ es tenant-scoped).
  - Manager: default (custom comentado).
- `RolePermission` (file: `apps/api/apps/identity/models/rbac.py:166`) — pivote rol↔permiso.
  - Campos clave: `rol`, `permiso`, `fecha_asignacion`, `asignado_por_usuario`, `tenant` (line 185), unique `(tenant, rol, permiso)`.
  - Tenant FK: ✅.
- `ModulePermission` (file: `apps/api/apps/identity/models/rbac.py:248`) — pivote módulo↔permiso (visibilidad sidebar). Tabla `modulo_permisos`.
  - Tenant FK: ✅, unique `(tenant, modulo, permiso)`.
- `UserRole` (file: `apps/api/apps/identity/models/rbac.py:286`) — pivote usuario↔rol con expiración.
  - Campos clave: `usuario`, `rol`, `fecha_asignacion`, `fecha_expiracion`, `asignado_por_usuario`, `estado_asignacion` (activo/inactivo/suspendido/expirado), `tenant` (line 316), unique `(tenant, usuario, rol)`.
  - Tenant FK: ✅ — implementa la pertenencia a workspace para RBAC. NOTA: convive con `tenancy.TenantMembership` (otro modelo que también gestiona membership con un campo `role` plano); ver Notas.

#### Endpoints REST
- `POST /api/v1/auth/login/` — JWT login con enforcement de TenantMembership en subdominios (file: `api/v1/auth/views.py:82`, `serializers.py:65`).
- `POST /api/v1/auth/activate/` — acepta `TenantInvitation` token y crea User+Membership (file: `api/v1/auth/views.py:720`).
- `POST /api/v1/auth/exchange/` — canjea exchange-token de `app.vyntia.pe` por sesión JWT en subdominio tenant (file: `api/v1/auth/views.py:780`).
- `POST /api/v1/auth/logout/` — blacklist refresh token (views.py:138).
- `POST /api/v1/auth/refresh/` — JWT refresh (SimpleJWT TokenRefreshView).
- `GET/PUT /api/v1/auth/profile/` — perfil del usuario (views.py:181).
- `POST /api/v1/auth/user-profile/change-password/` — cambio de contraseña autenticado (views.py:318).
- `POST /api/v1/auth/forgot-password/` — solicita token de recuperación + email (views.py:389).
- `POST /api/v1/auth/reset-password/` — restablece con token (views.py:455).
- `GET /api/v1/auth/menu/` — menú dinámico filtrado por permisos vía `MenuService` (views.py:496).
- `GET /api/v1/auth/menu-structure/` — admin-only, estructura completa (views.py:528).
- `POST /api/v1/auth/permissions-structure/` — admin-only, dump completo permisos+roles (views.py:636).
- `GET /api/v1/auth/test-permisos/` — debug endpoint (test_views.py).
- `/api/v1/identity/users/` — `UsuarioViewSet` (CRUD admin-gated, file: `api/v1/rrhh/views.py:1510`). Routed via `api/v1/identity/urls.py`.
- `/api/v1/identity/roles/` — `RolViewSet` (CRUD admin-gated, file: `api/v1/rrhh/views.py:1779`).
- `/api/v1/identity/permissions/` — `PermisoViewSet` (CRUD HR-gated, file: `api/v1/rrhh/views.py:1868`).
- `/api/v1/identity/modules/` — `ModulosViewSet` (file: `api/v1/rrhh/views.py:403`).
- `/api/v1/identity/role-permissions/` — `RolPermisosViewSet` (file: `api/v1/rrhh/views.py:509`).
- `/api/v1/identity/user-roles/` — `UsuarioRolesViewSet` (file: `api/v1/rrhh/usuario_roles_views.py`).

#### UI (frontend)
- `LoginForm` at `apps/web/src/features/auth/components/LoginForm.tsx` — formulario de login.
- `ChangePasswordForm` / `ResetPasswordForm` at `apps/web/src/features/auth/components/` — flujos de cambio/reset password.
- `ChangePasswordPage` / `ResetPasswordPage` at `apps/web/src/features/auth/pages/` — páginas wrapper.
- `AuthContext` at `apps/web/src/features/auth/context/AuthContext.tsx` — estado de sesión, persistencia JWT.
- `useAuth` hook at `apps/web/src/features/auth/hooks/useAuth.ts`.
- `authService` at `apps/web/src/features/auth/services/authService.ts` — llamadas a `/api/v1/auth/*`.
- `UsersList` / `UsersForm` / `UsersManagement` / `UserDetailsModal` / `UserFormModal` at `apps/web/src/features/identity/{pages,components/modals}/` — gestión de usuarios.
- `RolesPage` / `RoleManagement` / `RolePermissionsPage` / `RoleManagementModal` — gestión de roles y permisos por rol.
- `PermissionsPage` — listado de permisos.
- `AdminDashboard` at `apps/web/src/features/identity/pages/AdminDashboard.tsx` — dashboard administrativo.
- `ChangePasswordModal` — modal de cambio de password.
- `usersService` / `securityService` at `apps/web/src/features/identity/services/` — API clients (con tipos inconsistentes — ver bugs).

#### Tests
- `apps/api/tests/test_auth_api.py` — 28 tests (login API, logout, profile, change password, security, performance, integration). 5 fallan (ver bugs).
- `apps/api/tests/test_login_authentication.py` — 17 tests (model-level: bloqueo, intentos, tokens, password lifecycle). Todos PASAN.
- `apps/api/tests/test_auth_system_integration.py` — 7 tests (creación usuario completo, escalación permisos, expiración roles). Todos PASAN.
- ❌ NO existe `apps/api/apps/identity/tests/` — no hay tests in-app del bounded context. Todos los tests viven en el directorio root `apps/api/tests/`.

### Gaps vs INTRANET legacy

VYNTIA identity es básicamente un superset del legacy INTRANET (mismas entidades + tenant FKs + `is_vyntia_staff` + UUID PKs + audit fields EN). No hay funcionalidad legacy "perdida" — la migración L3.10.1/L3.10.2 fue paritaria para identity. Sin embargo, hay deuda técnica heredada y código muerto que arrastra desde el legacy.

| Feature legacy | Ubicación legacy | Estado en VYNTIA | Tipo | Prioridad propuesta | Nota |
|---|---|---|:---:|:---:|---|
| Modelo `Usuario` con AutoField PK + nombres ES | `D:/INTRANET/back/app_rrhh/models/usuario.py:48` | Migrado a `User` con UUID + class-name EN, db_column legacy preservado | done | — | Paridad funcional total. |
| Manager `UsuarioManager` | `D:/INTRANET/back/app_rrhh/managers.py` | Replicado en `apps/api/apps/identity/managers.py` | done | — | Bug heredado: `activos()` filtra por `estado=True` (campo inexistente en User — ver bugs). |
| `Rol` legacy single-tenant | `D:/INTRANET/back/app_rrhh/models/roles.py:4` | `Role` con `tenant` FK | done | — | C añadió tenant scoping. |
| `Permiso` legacy single-tenant | `D:/INTRANET/back/app_rrhh/models/roles.py:91` | `Permission` con `tenant` FK | done | — | C añadió tenant scoping. |
| `Modulos` legacy | `D:/INTRANET/back/app_rrhh/models/sistema.py:7` | `Module` paritario | done | — | Sin tenant FK (decisión: catálogo global). |
| `UsuarioRoles` con expiración | `D:/INTRANET/back/app_rrhh/models/sistema.py:268` | `UserRole` con `tenant` FK | done | — | Paridad + multi-tenant. |
| `permisos_especiales()` placeholder | `D:/INTRANET/back/app_rrhh/models/usuario.py:363` | Mismo placeholder copiado en `User.permisos_especiales` (line 371) — devuelve `[]` | partial | P2 | Nunca se implementó en legacy ni en VYNTIA; abandonable. |
| `nombres ES` en API responses | varias views legacy | Conservado en VYNTIA (`tipo_usuario`, `nivel_acceso`, `nombres_usuario`, `apellidos_usuario`) | done | P1 | Considerar normalización EN en B.2 si se rompe la BC; bajo riesgo de UX. |
| `tiempo_desde_ultimo_login` con bug de fall-through | `D:/INTRANET/back/app_rrhh/models/usuario.py:224` | Bug copiado intacto a VYNTIA `User.tiempo_desde_ultimo_login` (line 232): rama `elif delta.seconds > 60` no retorna nada → `None` implícito | bug | P1 | Fix en B.1 deuda técnica cross-cutting. |
| Backend `CustomAuthBackend` | `D:/INTRANET/back/app_rrhh/auth.py` | Replicado idéntico en `apps/api/apps/identity/auth.py` | done | — | OK. |

### Gaps vs maestro

Identity es transversal — no es un módulo numerado en el maestro. § 5.3 trata del módulo regional Perú, no de identity. Las referencias relevantes son § 5.2 (líneas 415-435) y `arquitectura/A04_rbac_permisos.md`.

| Capability del maestro | Estado en VYNTIA | Prioridad |
|---|---|:---:|
| RBAC clásico (roles + permisos) | ✅ Implementado vía `Role`/`Permission`/`RolePermission`/`UserRole`. | — |
| RBAC tenant-scoped (cada tenant su propio set de roles/permisos) | ✅ FK `tenant` en `Role`, `Permission`, `RolePermission`, `UserRole`, `ModulePermission`. | — |
| **Permission Levels 0-9 por campo** (A04 § 3) — granularidad por campo | ❌ NO implementado. `Permission` tiene `tipo_permiso` (CRUD-like) pero NO `permission_level`. Campo `level` ausente del modelo. | P1 (B.2 polish) o B+1 (sub-proyecto dedicado RBAC). |
| **ABAC (Attribute-Based)** — condiciones JSONB por permiso (A04 § 4) | ❌ NO implementado. `Permission.condiciones` JSONB ausente. La lógica ABAC actual está hardcoded en `User.puede_ver_empleado`/`User.puede_acceder_a_area` (file user.py:259-286). | P1 (necesario para spec original "jefe ve solo su equipo"). |
| Workflow Engine declarativo por tenant (5.2) | ❌ Fuera de scope identity (otra app). | — |
| Custom Fields híbridos JSONB | ❌ Fuera de scope identity. | — |
| Audit log de permisos (A04) | ⚠️ Parcial. `RolePermission.asignado_por_usuario` y `fecha_asignacion` existen, pero no hay tabla de cambios históricos. | P2 |
| Login lockout / password expiration / token recovery | ✅ Implementado en `User` model (intentos, fecha_bloqueo, fecha_expiracion_password, token_recuperacion). | — |
| MFA / 2FA | ❌ NO implementado. No hay maestro requirement explícito pero esperable para enterprise tier. | P2 (backlog). |
| Cross-tenant staff (Vyntia internal) | ✅ `User.is_vyntia_staff` (C.5). | — |

### Bugs y deuda técnica conocidos

Tests pytest fallidos atribuibles a identity:

| Test | File | Causa probable | Tipo |
|---|---|---|---|
| `test_login_datos_faltantes` | `tests/test_auth_api.py` | Espera 400, recibe 401 — el view envuelve excepciones genéricas en 401. | bug status code |
| `test_login_usuario_bloqueado` | `tests/test_auth_api.py` | Espera 401, recibe 200 — bloqueo por `estado_usuario=bloqueado` no está siendo respetado en `LoginAPIView`/`CustomTokenObtainPairSerializer.validate()`. **Bug de seguridad real.** | 🐛 bug seguridad |
| `test_logout_token_invalido` | `tests/test_auth_api.py` | Espera 401, recibe 200 — logout acepta cualquier refresh token sin validar. | bug |
| `test_actualizar_perfil_exitoso` | `tests/test_auth_api.py` | `'Test' != 'Nuevo Nombre'` — `UserUpdateSerializer` (serializers.py:761) solo permite actualizar `email`, fixture esperaba campos de nombres. | bug serializer |
| `test_multiples_intentos_login_fallidos` | `tests/test_auth_api.py` | `'activo' != 'bloqueado'` — `registrar_intento_fallido` no se está llamando desde el login flow JWT. **Bug de seguridad.** | 🐛 bug seguridad |

Otros bugs/deuda técnica identificados:

- 🐛 `User.tiempo_desde_ultimo_login` (user.py:232) — la rama `elif delta.seconds > 60` no tiene `return`, devuelve `None` implícito en lugar de string formateado. Bug heredado del legacy. Prioridad P1.
- 🐛 `UsuarioManager.activos()` (managers.py:46) — filtra por `estado=True`, pero `User` no tiene campo `estado` (tiene `estado_usuario` y `is_active`). Si se llama, lanza `FieldError`. Probablemente unused pero código muerto. Prioridad P1.
- 🐛 `UsuarioManager.por_rol` (managers.py:67) — usa `rol__nombre__icontains`, relación inexistente (la real es vía `UserRole`). Código muerto/roto. Prioridad P2.
- 🐛 `CustomTokenObtainPairSerializer._get_user_permissions` (serializers.py:230) — dict literal con `'id'` key duplicada (line 227 y 230), Python silencia la primera. Pequeño bug que reduce el id real del permiso. Prioridad P2.
- 🐛 `CustomTokenObtainPairSerializer._get_user_modules` (serializers.py:267-285) — referencia `permiso.modulo.pk` y `permiso.modulo.nombre_modulo` asumiendo `modulo` es un FK, pero en `Permission.modulo` es un `CharField` (legacy schema). Si se llamara, lanza `AttributeError`. El método nunca se usa actualmente. Prioridad P2.
- 🐛 `User` declares `nombre_completo` pero `__str__` (user.py:144) the build doesn't include estado guard for missing apellidos.
- ⚠️ `Permission.modulo` es `CharField` (string id legacy), NO FK al modelo `Module`. Inconsistencia: `Module` existe como entidad pero los permisos no se vinculan vía FK. Decisión heredada del legacy; documentar o arreglar en B.2.
- ⚠️ `views.py:108` — `LoginAPIView` actualiza `user.ultimo_acceso` con `if hasattr(user, "ultimo_acceso")` — el campo es `last_login`, NO `ultimo_acceso`. Código muerto que nunca se ejecuta. Prioridad P2.
- ⚠️ Identity ViewSets viven en `api/v1/rrhh/views.py` (legacy location) — el split físico hacia un `api/v1/identity/views.py` no se completó en L3. La carpeta `api/v1/identity/` solo tiene `urls.py` que importa de `rrhh/views.py`. Refactor pendiente (P2, B.2 o B-cleanup).
- ⚠️ Custom managers de `Role`, `Permission`, `Module`, `RolPermisos`, `UsuarioRoles` están comentados (`# objects = ... # Comentado temporalmente para migraciones`). Hay que decidir: implementarlos o eliminar el comentario. Prioridad P2.
- ⚠️ Sin `apps/identity/tests/` — todos los tests viven en `apps/api/tests/` (root). Mover/co-locate como parte de B.2.
- ⚠️ Frontend: `usersService.User` define `id: string`, `empleado.id: string` pero el backend devuelve UUIDs como strings ya — probablemente OK. Sin embargo, `usersService.Role.id: string` y `securityService.Role.id: string` divergen en shape (`nombre_rol` vs `nombre`); duplicación de tipos.

Sin errores TS ni warnings ESLint para `features/identity` ni `features/auth`.

### Tenant-readiness

| Concern | Status | Comment |
|---|:---:|---|
| `User` has tenant FK | ❌ | **Intencional** — Users are cross-tenant (un mismo usuario puede pertenecer a múltiples workspaces). La pertenencia se modela vía `tenancy.TenantMembership` (campo `status="active"` y campo `role` plano). El JWT `validate()` (serializers.py:96-106) enforza membership activo en el subdominio. |
| `Role` has tenant FK | ✅ | `roles.py:25` — nullable=true (permite roles seed/legacy globales). Constraint unique `(tenant, nombre_rol)`. |
| `Permission` has tenant FK | ✅ | `roles.py:139` — nullable=true. Sin constraint unique adicional sobre tenant — `Permission.modulo + nombre_permiso` puede colisionar entre tenants intencionalmente o no (revisar P2). |
| `Module` has tenant FK | ❌ | **Decisión documentada** — catálogo de módulos es global (mismo set de pantallas para todos los tenants). Los permisos sobre módulos sí son tenant-scoped vía `ModulePermission`. |
| `UserRole` has tenant FK | ✅ | `rbac.py:316` — clave para que un usuario pueda tener distintos roles en distintos tenants. Unique `(tenant, usuario, rol)`. |
| `RolePermission` has tenant FK | ✅ | `rbac.py:185` — unique `(tenant, rol, permiso)`. |
| `ModulePermission` has tenant FK | ✅ | `rbac.py:265` — unique `(tenant, modulo, permiso)`. |
| RBAC checks tenant context | ⚠️ | `PermissionService` (`apps/core/permission_service.py`) y `MenuService` resuelven roles/permisos vía `usuario.roles_activos()` / `usuario.permisos_activos()` que filtran por `estado_asignacion="activo"` pero NO filtran por `tenant`. Confían en que el RLS de Postgres + middleware tenancy hayan ya aislado los datos. Si RLS bypass o context unset → fuga cross-tenant. **Verificar en B.1.** |
| JWT incluye tenant claims | ✅ | `CustomTokenObtainPairSerializer.get_token` (serializers.py:29) inyecta `tenant_id`, `tenant_slug`, `membership_role` cuando hay contexto activo. |
| Login enforce membership | ✅ | C.4 (serializers.py:86-106) — en subdominio tenant, exige `TenantMembership` activo o devuelve 403 PermissionDenied. |
| Cross-tenant staff path | ✅ | `is_vyntia_staff` exime de membership requirement para admin panel (C.5). |

### Notas

- **Decisión de C: Users cross-tenant.** Un mismo `User` puede tener `TenantMembership` en múltiples tenants. Esto difiere del legacy single-tenant. Cualquier query que asuma "un usuario = un workspace" debe revisarse contra esta semántica.
- **Convivencia `UserRole` vs `TenantMembership`.** Ambos modelos contienen información de pertenencia y rol. `TenantMembership` (en `apps.tenancy`) usa un `role` plano (string), mientras `UserRole` (en `apps.identity`) referencia `Role` model con permisos granulares. Esta dualidad es deuda técnica de C — clarificar fuente de verdad en B.2 (probablemente `TenantMembership.role` se usa para gating ligero del workspace y `UserRole`+`Role` para RBAC granular dentro del tenant).
- **Riesgos al tocar identity en B.2.** (1) Los `db_column` legacy son la única referencia para datos importados; renombrar columnas fisicamente rompe migración. (2) Cualquier cambio en `User` propaga a `auth.py` backend, JWT serializer, todos los tests de auth. (3) Bug de seguridad en bloqueo por intentos fallidos (test_multiples_intentos) debería corregirse antes de exponer admin panel a producción → mover a B.1 fast-track.
- **Renombrado L3.10.x parcial.** Class names ES→EN está hecho, pero campos siguen en ES (`nombres_usuario`, `apellidos_usuario`, `tipo_usuario`, `estado_usuario`, `nivel_acceso`, `intentos_fallidos`, etc.). El maestro y la marca apuntan a EN/internacional — completar normalización es un sub-proyecto futuro, NO scope B.
- **Permission Levels 0-9 / ABAC** del maestro A04 son brecha real. Sin esto, "jefe ve solo su equipo" se hardcodea en el modelo (user.py:281-285) en vez de declararse en metadata. Decisión: dejar fuera de B y abrir sub-proyecto dedicado post-B.

## App: organization

### Estado actual en VYNTIA (post-A+C)

#### Modelos
- `Department` (file: `apps/api/apps/organization/models/department.py:16`) — área / unidad organizacional. Renombre L3.10.x: legacy `Area` → `Department`. PK UUID. Tabla legacy `area` preservada (db_table line 71).
  - Campos clave: `nombre_organo`, `nombre_unidad_organica`, `siglas_area`, `descripcion_area`, `jefe_area` (CharField, NO FK a User), `area_padre` self-FK (jerarquía recursiva), `nivel_jerarquico`, `codigo_presupuestal`, `total_empleados` (cache contador), `estado_area` (activo/inactivo/reestructuracion), `created_at`/`updated_at` (db_column legacy `fecha_creacion`/`fecha_actualizacion`).
  - Tenant FK: ✅ (line 28, nullable=true). Constraint: `unique_department_siglas_per_tenant` sobre `(tenant, siglas_area)` (line 82).
  - Manager: default. Custom `AreaManager` comentado (line 13, igual que en legacy).
  - Métodos: `desactivar()`, `activar()`, `empleados_activos_count()`, `empleados_activos()` (cruza por `EmploymentData.area`), `subareas_activas()`, `todas_las_subareas()` (recursivo), `empleados_totales_con_subareas()`, `actualizar_total_empleados()`. Properties: `nombre_completo`, `es_activa`, `es_area_raiz`, `tiene_subareas`, `ruta_jerarquica`.
- `Company` (file: `apps/api/apps/organization/models/company.py:5`) — configuración institucional (nombre, RUC, dirección, logo, representante legal). Renombre L3.10.x: legacy `ConfiguracionEmpresa` → `Company`. PK auto (NO UUID — heredado de legacy).
  - Campos clave: `nombre`, `ruc`, `direccion`, `distrito`, `provincia`, `departamento`, `telefono`, `email`, `web`, `logo` (ImageField, upload `empresa/`), `representante_legal`, `cargo_representante`, `dni_representante`, `resolucion_creacion`.
  - Tenant FK: ✅ (line 8, nullable=true). Constraint condicional: `unique_company_per_tenant` sobre `(tenant)` con `Q(tenant__isnull=False)` — un Company por tenant cuando hay tenant; permite filas globales legacy con tenant=NULL.
  - Tabla: `configuracion_empresa` (db_table preservado). `verbose_name = 'Configuración de Empresa'`.
  - Classmethod `get_config(tenant=None)` (line 47): si `tenant=None`, fallback singleton legacy `pk=1` via `get_or_create`. Comentario explícito: el fallback se removerá en C.3 cuando middleware garantice contexto tenant en cada request autenticado.
- `LocationHistory` (file: `apps/api/apps/organization/models/location_history.py:17`) — historial de movimientos / desplazamientos de empleados entre áreas. Renombre L3.10.x: legacy `HistorialUbicaciones` → `LocationHistory`. PK UUID. Tabla legacy `historial_ubicaciones` preservada.
  - Campos clave: `empleado` FK→`employees.Employee` (related_name `historial_ubicaciones`), `area_origen`/`area_destino` FK→`Department` (PROTECT), `tipo_movimiento` (ingreso/traslado/rotacion/comision/destacamento/retorno), `fecha_inicio`/`fecha_termino`, `motivo_movimiento`, `documento` FK→`documents.DigitalDocument`, `documento_sustento`, `numero_documento_sustento`, `observaciones`, `estado_ubicacion` (activo/inactivo/temporal), `registrado_por_usuario` FK→`identity.User`, `created_at` (db_column `fecha_registro`).
  - Tenant FK: ✅ (line 42, nullable=true). NO constraint adicional sobre tenant.
  - Métodos: `finalizar_movimiento()`, `extender_movimiento()`, `cambiar_estado()`, `agregar_documentacion()`, `empleados_en_area_destino()`, `historial_empleado_movimientos()`, `movimientos_similares()`, classmethods `movimientos_activos`, `empleados_sin_movimiento_activo`, `movimientos_por_periodo`, `estadisticas_movimientos`. Properties: `movimiento_completo`, `duracion_movimiento`, `es_activa`, `es_movimiento_temporal`, `tipo_movimiento_texto`, `estado_texto`, `tiene_documentacion`, `documentacion_completa`, `codigo_movimiento`.

#### Endpoints REST
- `/api/v1/organization/departments/` — `AreaViewSet` (CRUD, file: `api/v1/rrhh/views.py:124`). Routed via `api/v1/organization/urls.py:14`.
  - List/retrieve: `@require_authenticated()` + `@cache_response(timeout=600)`.
  - Create/update/partial_update: `@require_hr()` + `@invalidate_cache`.
  - Destroy: `@require_admin()` (soft delete via `estado_area="inactiva"` — typo de valor, ver bugs).
  - Custom actions: `empleados` (GET, paginado), `estadisticas` (GET), `resumen` (GET, listado completo), `activas` (GET).
  - FilterSet: `AreaFilter` (filters.py:14) — filtros `siglas`, `unidad_organica`, `organo`, `estado`, `min_empleados`, `max_empleados`.
  - Permission class: `AreaPermission` (permissions.py:103) — RRHH/Admin RW; resto sólo lectura.
- `/api/v1/organization/companies/` — `ConfiguracionEmpresaViewSet` (file: `api/v1/rrhh/views.py:2852`). NO es ModelViewSet — es ViewSet plano:
  - `list` (GET): `@require_authenticated()` — devuelve `Company.get_config(tenant=request.tenant)` serializado.
  - `create` (POST): `@require_admin()` — actua como upsert sobre el mismo `Company` (no crea filas nuevas; partial=True).
  - **NO hay endpoint para `LocationHistory`** — modelo existe pero no expuesto vía API.

#### UI (frontend)
- `AreasManagementPage` at `apps/web/src/features/organization/pages/AreasManagementPage.tsx` — gestión de áreas con stats, búsqueda, filtros (Card-based dashboard).
- `AreasListPage` / `AreaFormPage` at `apps/web/src/features/organization/pages/` — listado y formulario CRUD áreas.
- `ConfiguracionEmpresaPage` at `apps/web/src/features/organization/pages/ConfiguracionEmpresaPage.tsx` — formulario edición datos institucionales (logo upload, RUC, dirección, representante legal).
- `AreaForm` / `DeleteAreaDialog` at `apps/web/src/features/organization/components/` — componentes reutilizables.
- `useDepartments` hook at `apps/web/src/features/organization/hooks/useDepartments.ts` — React Query.
- `departmentsService` at `apps/web/src/features/organization/services/departmentsService.ts` — API client. Endpoints declarados: hierarchy, children, parent, stats, report, export, search, validate, bulk-update, bulk-delete, history, metadata. **La mayoría NO existe en backend** (ver gaps).
- `companyService` at `apps/web/src/features/organization/services/companyService.ts` — get/update con soporte de logo multipart.
- ❌ NO existe UI para `LocationHistory` (movimientos/desplazamientos) en frontend.

#### Tests
- `apps/api/tests/test_area_model.py` — 22 tests (modelo Department: campos, jerarquía, métodos activar/desactivar, constraint unique tenant, índices, valores por defecto). **Todos PASAN**.
- ❌ NO existen tests para `Company` (`ConfiguracionEmpresa`).
- ❌ NO existen tests para `LocationHistory` (`HistorialUbicaciones`).
- ❌ NO existen tests para los ViewSets `AreaViewSet` ni `ConfiguracionEmpresaViewSet` (sólo modelo).
- ❌ NO existe `apps/api/apps/organization/tests/` — los tests viven en `apps/api/tests/` (root).

### Gaps vs INTRANET legacy

VYNTIA organization es paritario con el legacy INTRANET en términos de modelos (mismas entidades + tenant FKs + UUID PK en Department/LocationHistory). El renombre L3.10.x fue parcial: class names EN (`Department`, `Company`, `LocationHistory`) pero todos los campos y db_columns siguen ES. Sin código legacy "perdido". Sin embargo, hay deuda heredada (bugs intactos del legacy) y nuevas brechas creadas por la migración misma.

| Feature legacy | Ubicación legacy | Estado en VYNTIA | Tipo | Prioridad propuesta | Nota |
|---|---|---|:---:|:---:|---|
| Modelo `Area` con AutoField PK + nombres ES | `D:/INTRANET/back/app_rrhh/models/area.py:14` | Migrado a `Department` con UUID + class-name EN, db_column legacy preservado, tabla `area` preservada | done | — | Paridad funcional total. |
| `siglas_area` globalmente único (legacy unique=True) | `area.py:29` | Cambiado: ahora unique `(tenant, siglas_area)` per-tenant | done | — | C.1 cambió la semántica intencionalmente — distintos tenants pueden reusar siglas. |
| Manager `AreaManager` | `D:/INTRANET/back/app_rrhh/managers.py` | Comentado (line 13) — igual que en legacy | partial | P2 | Nunca se implementó en legacy ni en VYNTIA; abandonable o eliminar el `# Comentado temporalmente`. |
| Modelo `ConfiguracionEmpresa` singleton (pk=1 fijo) | `configuracion_empresa.py:5` | Migrado a `Company` con tenant FK + constraint condicional unique-per-tenant. Singleton legacy `pk=1` aún soportado vía fallback `get_config(tenant=None)` (line 54) | partial | P1 | Documentado: fallback se remueve en C.3. Riesgo: si middleware tenancy NO setea `request.tenant` → todos los tenants comparten la fila pk=1. |
| `ConfiguracionEmpresa.get_config()` singleton helper | `configuracion_empresa.py:30` | Replicado con firma extendida `get_config(tenant=None)` | done | — | OK con caveat del fallback. |
| Modelo `HistorialUbicaciones` con AutoField PK | `D:/INTRANET/back/app_rrhh/models/ubicacion.py:15` | Migrado a `LocationHistory` con UUID + class-name EN, tabla `historial_ubicaciones` preservada | done | — | Paridad funcional total. |
| Bug heredado: `LocationHistory.movimiento_completo` referencia `area_origen.nombre_area` y `area_destino.nombre_area`, pero `Department` (ni el legacy `Area`) tiene campo `nombre_area` | `ubicacion.py:150-151` ↔ `location_history.py:163-164` | Bug copiado intacto a VYNTIA — lanza `AttributeError` si se llama | bug | P1 | Probable nunca se llamó (no hay endpoints LocationHistory). Fix: usar `nombre_unidad_organica` o `nombre_completo`. |
| Bug heredado: `LocationHistory.codigo_movimiento` referencia `area_destino.codigo_area`, campo inexistente en `Department` (legacy `Area` tampoco lo tiene) | `ubicacion.py:211` ↔ `location_history.py:224` | Bug copiado intacto a VYNTIA — lanza `AttributeError` si se llama | bug | P1 | Mismo veredicto: código muerto. Fix o eliminar. |
| Endpoints REST para `HistorialUbicaciones` | INTRANET expuso endpoints `/desplazamientos/` (verificar) | ❌ NO migrado — `LocationHistory` NO está expuesto en `/api/v1/organization/` | missing | P1 (B.5 desplazamientos) | Funcionalidad clave de HR (rotación, comisión) sin API. Backlog item. |
| UI gestión de movimientos | INTRANET tenía pantalla de desplazamientos | ❌ NO existe en VYNTIA frontend | missing | P1 (B.5) | Coincide con maestro 03.6 Desplazamiento. |

### Gaps vs maestro

El maestro § 3 Módulo 02 (líneas 156-171) define **Organización del Trabajo y Distribución** con foco en puestos (`Position`), perfiles (`PositionProfile`), unidades organizativas (`OrgUnit`), bandas salariales (`SalaryBand`), tabla de categorías y funciones (`CategoryFunctionTable`), MPP (Manual de Perfiles) y CPE (Cuadro de Puestos de la Entidad). **Estas entidades son completamente NUEVAS** — no existen hoy en `apps.organization`. Su brecha se documenta exhaustivamente en **Task 10 — Maestro gaps Module 02 (Organization extended)** y NO se duplica aquí.

Esta sección audita SÓLO lo que el bounded context `organization` posee hoy: `Department`, `Company`, `LocationHistory` (entidades estructurales-organizacionales y de configuración).

| Capability del maestro | Estado en VYNTIA | Prioridad |
|---|---|:---:|
| Estructura jerárquica de unidades organizacionales (auto-FK area_padre) | ✅ `Department.area_padre` (self-FK) + `nivel_jerarquico` + métodos `subareas_activas`, `todas_las_subareas` (recursivo). Cumple con la lectura mínima del maestro § 156-167. | — |
| Datos institucionales (nombre, RUC, logo, representante legal) | ✅ `Company` paritario. | — |
| Multi-tenant: cada tenant define su propia estructura organizacional | ✅ FK `tenant` en `Department`, `Company`, `LocationHistory` + constraints. | — |
| Versionado histórico de estructura (maestro § 165) | ❌ No hay versionado de cambios en `Department` (renombres, fusiones, escisiones). `LocationHistory` versiona movimientos de **empleados** entre áreas, no cambios de la estructura misma. | P2 (sub-proyecto futuro). |
| Catálogo de puestos (`Position`, `PositionProfile`) | ❌ Inexistente — ver Task 10. | (Task 10) |
| Organigrama dinámico navegable | ⚠️ Backend tiene jerarquía recursiva; frontend `departmentsService` declara `getAreaHierarchy` pero el endpoint `hierarchy/` **NO existe en backend** (ver bugs). | P2 |
| CCF (Cuadro de Categorías y Funciones — Ley 30709) | ❌ Inexistente — ver Task 10. | (Task 10) |
| Banda salarial por categoría (`SalaryBand`) | ❌ Inexistente — ver Task 10. | (Task 10) |
| MPP / CPE (sector público SERVIR) | ❌ Inexistente — ver Task 10. | (Task 10) |
| Desplazamiento de empleados (rotación, encargatura, destaque, comisión, permuta — maestro § 03.6) | ⚠️ Modelo `LocationHistory` existe con `tipo_movimiento` (ingreso/traslado/rotacion/comision/destacamento/retorno), pero SIN endpoints REST y SIN UI. Funcionalidad backend lista, frontend ausente. | P1 (B.5). |

### Bugs y deuda técnica conocidos

Pytest organization: `tests/test_area_model.py` 22/22 PASAN. Sin fallos atribuibles a organization. Sin embargo, hay bugs latentes en código no cubierto por tests:

| Bug | Ubicación | Causa | Tipo | Prioridad |
|---|---|---|:---:|:---:|
| `AreaSerializer.get_empleados_activos_count` llama `obj.get_empleados_activos_count()` (con prefijo `get_`) — el método real es `empleados_activos_count` | `api/v1/rrhh/serializers.py:71` ↔ `apps/organization/models/department.py:121` | Refactor incompleto: el método del modelo nunca tuvo prefijo `get_`. Si una vista entra por la rama del fallback (sin annotation `empleados_activos_count`), lanza `AttributeError`. | 🐛 bug | P1 |
| `AreaViewSet.empleados()` action llama `area.empleados_actuales()` — método inexistente | `api/v1/rrhh/views.py:266` | El método real es `empleados_activos()` (department.py:129). El endpoint custom `/departments/{id}/empleados/` siempre falla con `AttributeError`. | 🐛 bug | P1 |
| `AreaViewSet.activas()` action filtra por `estado="activa"` — campo inexistente y valor inválido | `api/v1/rrhh/views.py:366` | El campo es `estado_area` y el choice válido es `activo` (no `activa`). Lanza `FieldError`. Frontend service declara `getAreasByOrgano` pero no llama a este action — probablemente código muerto. | 🐛 bug | P2 |
| `AreaViewSet.perform_destroy` setea `estado_area="inactiva"` — valor fuera de choices | `api/v1/rrhh/views.py:244` | Choices válidos: `activo`/`inactivo`/`reestructuracion`. El soft-delete crea estado inválido (no falla en SQLite-test pero en validators sí). | 🐛 bug | P2 |
| `AreaViewSet.queryset` declara `prefetch_related("empleados_laborales__empleado", "ubicaciones_destino__empleado")` — relaciones existen pero el segundo es contradictorio | `api/v1/rrhh/views.py:127-130` | `empleados_laborales` (related_name de `EmploymentData`) ✅ existe; `ubicaciones_destino` ✅ existe (LocationHistory.area_destino). OK. | OK | — |
| `LocationHistory.movimiento_completo` y `codigo_movimiento` referencian `nombre_area` / `codigo_area` en `Department`, campos inexistentes | `apps/organization/models/location_history.py:163-164, 224` | Bug heredado del legacy `HistorialUbicaciones`. Como no hay endpoints LocationHistory, nunca se ejecuta. Código muerto. | 🐛 bug heredado | P1 (al exponer LocationHistory en B.5). |
| `ConfiguracionEmpresaViewSet.create()` actúa como upsert sin distinguir create vs update | `api/v1/rrhh/views.py:2865-2880` | Diseño intencional para singleton pre-tenant; ahora con tenant aún funciona (filtra por tenant). Sin embargo, response 200 cuando sí debería ser 201 al crear nueva fila. Cosmético. | ⚠️ deuda | P3 |
| `Company.get_config(tenant=None)` fallback singleton legacy `pk=1` | `apps/organization/models/company.py:54-56` | Riesgo: si middleware tenancy falla en setear `request.tenant`, todos los requests caen al mismo `Company` pk=1 → fuga cross-tenant de datos institucionales. Comentario indica remoción en C.3. | ⚠️ deuda crítica | P1 |
| `Department.empleados_activos()` hace JOIN doble vía `datos_laborales__area` Y `estado_empleado='activo'` Y `estado_datos='activo'` (line 131-136) — sin `.distinct()` puede duplicar filas si un empleado tiene múltiples `EmploymentData` activos en la misma área | `apps/organization/models/department.py:129-136` | Tiene `.distinct()` (line 136) — OK. Falsa alarma. | OK | — |
| `Department.empleados_activos_count()` (line 121) cuenta `EmploymentData` (no empleados únicos) — si un empleado tiene 2 contratos activos en la misma área, cuenta 2 | `apps/organization/models/department.py:121-127` | El `_count` y la lista vía `empleados_activos()` discrepan numéricamente. Para reportes a stakeholders, ajustar a `.values('empleado').distinct().count()` (que `AreaViewSet.estadisticas` SÍ usa correctamente, line 305-307). | 🐛 deuda | P2 |
| `Area`/`AreaList` Serializer expone `siglas_area` con regla de unicidad case-insensitive **global** (`serializers.py:73-81`) — pero la BD es unique `(tenant, siglas_area)` case-sensitive | `api/v1/rrhh/serializers.py:73-81` | El serializer valida sin filtrar por tenant. Si el caller intenta crear un area con siglas que existen en OTRO tenant, falla la validación pre-save (cuando la BD lo permitiría). Bloquea casos legítimos cross-tenant. | 🐛 bug | P1 |
| `departmentsService` (frontend) declara ~15 endpoints que **no existen** en backend: `getAreasStats`, `getAreaHierarchy`, `getAreaChildren`, `getAreaParent`, `generateReport`, `exportAreas`, `searchAreas` (POST), `validateAreaSiglas`, `validateAreaStructure`, `bulkUpdateAreas`, `bulkDeleteAreas`, `getAreaHistory`, `getAreaMetadata`, `assignEmployeeToArea`, `removeEmployeeFromArea`, `updateEmployeeInArea` | `apps/web/src/features/organization/services/departmentsService.ts:137-311` | Probablemente generado por scaffolding y nunca recortado. `AreasManagementPage` SÍ llama `getAreasStats` (line 43) y por eso `statsData` siempre cae al objeto fallback (line 47). Estimación: la stats card del frontend muestra datos hardcoded a cero. | 🐛 frontend dead code / 404s | P2 |
| Custom manager `AreaManager` comentado | `apps/organization/models/department.py:13, 58` | Decisión pendiente: implementar o eliminar el comentario `# Comentado temporalmente para migraciones`. | ⚠️ deuda | P3 |
| Sin `apps/organization/tests/` | — | Tests viven en `apps/api/tests/` (root). Co-locate como parte de B.2. | ⚠️ deuda | P3 |

Sin errores TS ni warnings ESLint para `features/organization` (verificado con `tsc --noEmit -p tsconfig.app.json` y `npm run lint`).

### Tenant-readiness

| Concern | Status | Comment |
|---|:---:|---|
| `Department` has tenant FK | ✅ | `department.py:28` — nullable=true. Constraint: unique `(tenant, siglas_area)` (line 82). |
| `Company` has tenant FK | ✅ | `company.py:8` — nullable=true. Constraint condicional: unique `(tenant)` cuando `tenant IS NOT NULL` (line 35-40). Garantiza un Company por tenant. |
| `LocationHistory` has tenant FK | ✅ | `location_history.py:42` — nullable=true. SIN constraint unique adicional (no se requiere). |
| AreaViewSet filters queryset by tenant | ❌ | `api/v1/rrhh/views.py:127-216` — `get_queryset()` NO filtra por tenant. Confía en RLS de Postgres + middleware tenancy para aislar. **Si RLS bypass o middleware no setea contexto → fuga cross-tenant.** Verificar en B.1. |
| ConfiguracionEmpresaViewSet usa tenant context | ⚠️ | `views.py:2861, 2871` — usa `getattr(request, 'tenant', None)`. Si no hay tenant → fallback al singleton `pk=1` (legacy). Documentado pero crítico: cualquier request anónimo o con tenant ausente expone configuracion legacy. |
| LocationHistory no tiene endpoints | n/a | No se expone vía API hoy; cuando se exponga (B.5), filtrar por `tenant` o RLS. |
| Department.perform_create asigna tenant automáticamente | ❌ | `views.py:218-228` — `perform_create` NO setea `tenant` en `serializer.save()`. Si el frontend no envía `tenant`, se crea con `tenant=NULL` (datos huérfanos cross-tenant). Bug de seguridad. **P1 fix en B.1.** |
| Company.perform_create asigna tenant automáticamente | ⚠️ | `views.py:2865-2880` — usa `Company.get_config(tenant=request.tenant)` ANTES de save → resuelve correctamente la fila per-tenant. OK siempre que `request.tenant` esté seteado. |
| `AreaSerializer.validate_siglas_area` filtra por tenant | ❌ | `serializers.py:73-81` — query `Department.objects.filter(siglas_area__iexact=value)` NO filtra por tenant. Bloquea siglas legítimas si existen en otro tenant. (Bug listado arriba.) |
| Test de aislación tenant | ⚠️ | `tests/test_tenant_isolation.py`: 3 PASS, 2 SKIP (`test_orm_isolation_per_tenant`, `test_rls_blocks_raw_sql` — RLS infraestructura aún no probada). NO hay tests específicos de organization. |
| Multi-tenant en frontend | ✅ | El frontend no necesita selector de tenant: `apiClient` añade subdominio en host, JWT trae `tenant_id` (C.4). Departments/Company son scoped automáticamente vía host. |

### Notas

- **Renombrado L3.10.x parcial.** Class names ES→EN (`Area`→`Department`, `ConfiguracionEmpresa`→`Company`, `HistorialUbicaciones`→`LocationHistory`) hechos. Campos siguen en ES (`nombre_organo`, `nombre_unidad_organica`, `siglas_area`, `estado_area`, `tipo_movimiento`, `fecha_inicio`, etc.). db_columns y db_tables intactos para preservar migración. Normalización full a EN es sub-proyecto post-B, NO scope organization B.
- **Decisión de C: company singleton legacy.** `Company.get_config(tenant=None)` mantiene fallback a `pk=1` para BC con datos legacy. Riesgo si middleware tenancy falla. Documentado como deuda P1: remover en C.3.
- **`LocationHistory` sin API.** Modelo completo (tipos de movimiento, documentación, estados) pero sin endpoints REST ni UI. Funcionalidad backend lista para B.5 Desplazamientos (alineada con maestro 03.6).
- **Múltiples bugs en `AreaViewSet` actions de baja cobertura.** `empleados()`, `activas()`, `perform_destroy` tienen errores que sólo se manifiestan al ejercitarlos. Tests de modelo (22 PASS) NO cubren ViewSet behavior. Riesgo: panel admin que descubre estos bugs en QA. Prioridad P1 fix antes de exponer admin organization.
- **Frontend `departmentsService` con ~15 endpoints fantasma.** Resultados 404/500 silenciados por componentes que dan fallbacks vacíos. Detectable sólo por inspección (no rompe UI). Recortar como parte de B.2 cleanup.
- **Riesgos al tocar organization en B.2/B.5.** (1) `db_table='area'` y `db_table='configuracion_empresa'` son referencia para datos importados — renombrar columnas físicamente rompe migración. (2) `Department.area_padre` PROTECT cascade significa no se puede eliminar área con sub-áreas — tener en cuenta en flujos de "fusión de áreas" para Task 10. (3) `LocationHistory.area_origen/destino` son PROTECT — no se puede eliminar área con historial. Diseño correcto pero relevante para UX.
- **Preparación para Module 02 (Task 10).** Department es el equivalente actual de `OrgUnit`. Será FK desde `Position` cuando se introduzca. El campo `jefe_area` (CharField) NO sirve como FK a User/Position; rediseñar como FK cuando llegue Module 02.

## App: employees

(Filled by Task 4.)

## App: contracts

(Filled by Task 5.)

## App: documents

(Filled by Task 6.)

## App: onboarding

(Filled by Task 7.)

## Cross-cutting deuda técnica

(Filled by Task 8 — pytest failures, tsc errors, lint warnings attributed by app.)

## Maestro gaps — Module 01 (Policies)

(Filled by Task 9.)

## Maestro gaps — Module 02 (Organization extended)

(Filled by Task 10.)

## Maestro gaps — Module 03 (Employment lifecycle)

(Filled by Task 11.)
