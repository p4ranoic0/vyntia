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

(Filled by Task 3.)

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
