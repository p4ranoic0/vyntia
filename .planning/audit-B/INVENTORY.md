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

### Estado actual en VYNTIA (post-A+C)

#### Modelos
- `Employee` (file: `apps/api/apps/employees/models/employee.py:18`) — entidad central de la app: información personal, contacto, banco, pensión, salud y suspensión de renta 4ta. Renombre L3.10.x: legacy `Empleado` → `Employee`. PK UUID. Tabla legacy `empleado` preservada (db_table line 187). 50+ campos.
  - **Identidad**: `numero_documento` (CharField), `tipo_documento` (DNI/CE/PASAPORTE/OTROS), `nombres_empleado`, `apellido_paterno`, `apellido_materno`, `numero_ruc`, `genero_empleado` (4 choices), `fecha_nacimiento`, `es_padre_familia`, `es_militar`.
  - **Pensión / régimen**: `sistema_pensiones` (ONP/AFP×4/PENSIONISTA×3/SIN PENSION), `tipo_comision` (FLUJO/MIXTA), `codigo_cuspp`.
  - **Salud**: `tipo_seguro_salud` (ESSALUD/EPS/PRIVADO/NINGUNO), `centro_salud`, `direccion_centro_salud`, `departamento_centro_salud`, `vigencia_estado_seguro` (activo/inactivo).
  - **Renta 4ta**: `tiene_suspension_renta_cuarta_vigente`, `fecha_inicio_suspension_renta`, `fecha_fin_suspension_renta`, `documento_suspension_renta` (FileField, upload `suspensiones_renta/%Y/`).
  - **Contacto**: `telefono_fijo`, `telefono_celular`, `correo_personal` (EmailField, **unique=True**, ver bug).
  - **Personal**: `estado_civil`, `direccion_domicilio`, `distrito_domicilio`, `provincia_domicilio`, `departamento_domicilio`.
  - **Bancario**: `entidad_bancaria`, `numero_cuenta_bancaria`, `numero_cci`.
  - **Físico/médico**: `tipo_sangre` (8 choices), `talla_empleado` (Decimal 3,2), `peso_empleado` (Decimal 5,2), `ruta_fotografia`.
  - **Control**: `estado_empleado` (activo/inactivo/suspendido/cesado), `created_at` (db_column `fecha_registro`), `updated_at` (db_column `fecha_actualizacion`).
  - Tenant FK: ✅ (line 92, nullable=true). Constraint: `unique_employee_doc_per_tenant` sobre `(tenant, numero_documento)` (line 204-207). Migración 0002 retira el `unique=True` global de `numero_documento` y añade el constraint per-tenant (file `migrations/0002_alter_academicrecord_unique_together_and_more.py:47-67`).
  - **NO se actualizó** el `unique=True` global de `correo_personal` (line 150) — sigue siendo único cross-tenant. **Bug C-multitenancy** (ver Tenant-readiness).
  - Manager: default. `EmpleadoManager` comentado (line 15) — igual que legacy.
  - Métodos: `ubicacion_actual()`, `datos_laborales_actuales()`, `historial_ubicaciones()`, `familiares_activos()`, `formacion_academica()`, `boletas_recientes(meses=6)` (stub que devuelve `[]` — herencia legacy). Properties: `nombre_completo`, `edad`, `genero_texto`, `es_activo`, `documento_completo`, `contacto_principal`, `direccion_completa`, `imc`.
- `FamilyMember` (file: `apps/api/apps/employees/models/family_member.py:17`) — datos familiares. Renombre L3.10.x: legacy `DatosFamiliares` → `FamilyMember`. PK UUID. Tabla legacy `datos_familiares`.
  - Campos clave: `empleado` FK→`Employee` (CASCADE, related_name `familiares`), datos personales del familiar (nombres, apellidos, tipo+nro documento, fecha_nacimiento, género, parentesco — 14 choices: cónyuge/conviviente/hijo/padre/madre/hermano/abuelo/nieto/tio/primo/suegro/cuñado/yerno_nuera/otro), flags (`es_dependiente`, `es_beneficiario`, `es_contacto_emergencia`), `estado_civil`, `nivel_educativo` (9 choices), `ocupacion`, `centro_trabajo`, contacto familiar, salud (`tiene_seguro_salud`, `tipo_seguro_salud`, `numero_seguro`, `centro_salud_asignado`), discapacidad (`tiene_discapacidad`, `tipo_discapacidad`, `grado_discapacidad`, `certificado_discapacidad`), fechas dependencia, `estado_familiar` (activo/inactivo/fallecido), `observaciones`, audit (db_column legacy).
  - Tenant FK: ✅ (line 80, nullable=true). `unique_together = [['tenant', 'empleado', 'numero_documento']]` (line 162).
  - Manager: default. `DatosFamiliaresManager` comentado.
  - Métodos: `activar_dependencia()`, `desactivar_dependencia(motivo)`, `activar_beneficiario()`, `desactivar_beneficiario()`, `activar_contacto_emergencia()`, `desactivar_contacto_emergencia()`, `marcar_fallecido()`, `actualizar_seguro_salud(...)`, `actualizar_discapacidad(...)`. Classmethods: `dependientes_activos`, `contactos_emergencia`, `beneficiarios_activos`, `hijos_menores`, `familiares_con_discapacidad`. Properties: `nombre_completo`, `edad`, `es_menor_edad`, `es_mayor_edad`, `parentesco_texto`, `genero_texto`, `documento_completo`, `direccion_completa`, `contacto_completo`, `es_activo`, `dependencia_vigente`, `edad_para_dependencia`, `requiere_documentos_adicionales`.
- `AcademicRecord` (file: `apps/api/apps/employees/models/academic_record.py:17`) — formación académica. Renombre L3.10.x: legacy `DatosAcademicos` → `AcademicRecord`. PK UUID. Tabla legacy `datos_academicos`.
  - Campos clave: `empleado` FK (CASCADE, related_name `formacion_academica`), `nivel_educativo` (12 choices: primaria→doctorado), `nombre_institucion`, `tipo_institucion` (publica/privada/internacional/virtual/presencial/semipresencial), `modalidad_estudio`, programa (`nombre_carrera`, `codigo_carrera`, `area_conocimiento`, `duracion_anos`, `duracion_semestres`), fechas (`fecha_inicio`, `fecha_fin`, `fecha_graduacion`), `estado_estudios` (completo/incompleto/en_curso/trunco/convalidado), `promedio_ponderado`, créditos, titulación (`numero_titulo`, `numero_diploma`, `numero_colegiatura`, `colegio_profesional`), ubicación institución (Perú default), `mencion_especialidad`, `tesis_titulo`, `reconocimientos`, rutas a documentos (legacy CharField + FK opcional a `documents.DigitalDocument`), verificación SUNEDU, `estado_registro`.
  - Tenant FK: ✅ (line 68, nullable=true). `unique_together = [['tenant', 'empleado', 'nivel_educativo', 'nombre_carrera', 'nombre_institucion']]` (line 163).
  - Manager: default. `DatosAcademicosManager` comentado.
  - Métodos: `marcar_graduado()`, `marcar_en_curso()`, `marcar_incompleto()`, `verificar_sunedu()`, `actualizar_promedio()`, `actualizar_creditos()`, `agregar_colegiatura()`, `agregar_documento()`. Classmethods: `por_nivel_educativo`, `graduados_recientes(anos=5)`, `estudiantes_activos`, `pendientes_verificacion_sunedu`, `por_area_conocimiento`, `profesionales_colegiados`, `estadisticas_por_nivel`. Properties: 14+ (texto helpers, `duracion_completa`, `periodo_estudios`, `es_graduado`, `es_estudiante_activo`, `porcentaje_avance`, `anos_desde_graduacion`, `ubicacion_institucion`, `informacion_colegiatura`, `documentos_disponibles`, `requiere_verificacion`, `es_nivel_superior`, `es_postgrado`).
- `Certification` (file: `apps/api/apps/employees/models/certification.py:14`) — cursos y certificaciones. Renombre L3.10.x: legacy `CursosCertificaciones` → `Certification`. PK UUID. Tabla legacy `cursos_certificaciones`. Modelo simple (12 campos).
  - Campos clave: `empleado` FK (CASCADE, related_name `cursos_certificaciones`), `nombre_curso`, `institucion`, `fecha_inicio`, `fecha_fin`, `horas`, `descripcion`, `documento` FK→`documents.DigitalDocument`, `estado_registro` (default `'activo'` — sin choices), audit.
  - Tenant FK: ✅ (line 18, nullable=true). `unique_together = [['tenant', 'empleado', 'nombre_curso', 'institucion', 'fecha_inicio']]` (line 47).

#### Endpoints REST
- `/api/v1/employees/employees/` — `EmpleadoViewSet` (file: `api/v1/rrhh/views.py:653`). Routed via `api/v1/employees/urls.py:16`.
  - `list` (GET): `@cache_response(timeout=300)` + `@require_authenticated()`.
  - `retrieve` (GET): `@cache_response(timeout=600)` + `@require_authenticated()`.
  - `create` (POST): `@require_hr()` + invalidate cache. Usa `EmpleadoCreateSerializer` (nested: datos_laborales + area_inicial + datos_familiares + datos_academicos en una sola transacción atómica, file `serializers.py:725`).
  - `update`/`partial_update` (PUT/PATCH): self-edit habilitado para empleado autenticado sobre su propio legajo con whitelist de 22 campos editables (`_SELF_EDITABLE_FIELDS` views.py:726). RRHH/Admin pueden editar cualquier campo.
  - `destroy` (DELETE): `@require_admin()` — soft delete via `estado_empleado="inactivo"` (perform_destroy line 861).
  - Custom actions: `transferir` (POST detail), `estadisticas` (GET), `activos` (GET), `reporte_integral` (GET, PDF), `reporte_seccion` (GET, PDF, query=`personal|laboral|academico|familiar`), `datos_completos` (GET — devuelve 501 NOT_IMPLEMENTED, ver bugs).
  - FilterSet: `EmpleadoFilter` (filters.py:68) — 18 filtros (nombres, apellidos, dni, género, estado_civil, estado, distrito, fechas y edad, área, área_siglas, puesto, categoría, régimen laboral, remuneración min/max, tiene_hijos, tiene_conyuge).
  - Permission class: `EmpleadoPermission` (permissions.py:165) — RRHH/Admin RW; SAFE_METHODS para todos los autenticados; jefes_de_area parcialmente permitidos.
  - Pagination: `StandardResultsSetPagination` (20/page).
- `/api/v1/employees/family-members/` — `DatosFamiliaresViewSet` (views.py:1030). Self-service: empleado puede CRUD sus propios familiares (líneas 1062-1128). RRHH/Admin pueden CRUD cualquiera.
- `/api/v1/employees/academic-records/` — `DatosAcademicosViewSet` (views.py:1131). Self-service idéntico.
- `/api/v1/employees/certifications/` — `CursosCertificacionesViewSet` (views.py:1232). Self-service idéntico (sin update/partial_update/destroy customizados — usa los del ModelViewSet).

#### UI (frontend)
- `Empleados` (page) at `apps/web/src/features/employees/pages/Empleados.tsx` — listado principal con filtros y tabla.
- `EmpleadosListPage` at `apps/web/src/features/employees/pages/EmpleadosListPage.tsx` — listado alternativo.
- `HROverviewDashboard` at `apps/web/src/features/employees/pages/HROverviewDashboard.tsx` — dashboard HR de KPIs.
- `EmpleadoReportPage` — descarga reporte integral PDF.
- Páginas-detalle: `DatosPersonalesPage`, `DatosLaboralesPage`, `DatosFamiliaresPage`, `DatosAcademicosPage` (4 tabs/pages).
- Modales: `DatosPersonalesModal`, `DatosLaboralesModal`, `DatosFamiliaresModal`, `DatosAcademicosModal`.
- Componentes: `TabPersonales`, `TabLaborales`, `TabFamiliares`, `TabAcademicos`, `AdminDocUpload`.
- Hooks: `useEmployees`, `useEmployeePermissions`.
- Service: `employeesService` at `apps/web/src/features/employees/services/employeesService.ts` — el API client con sub-objetos para `datosPersonales`, `datosLaborales` (apunta a `/api/v1/employment-data/`), `datosFamiliares` (`/api/v1/family-members/`), `datosAcademicos` (`/api/v1/academic-records/`), `reportes` (PDF blob downloads).
- ❌ NO existe UI para `Certification` (cursos/certificaciones) en frontend — modelo expuesto vía `/api/v1/employees/certifications/` pero sin componentes.

#### Tests
- `apps/api/tests/test_empleado_update_v2.py` — 5 tests (PATCH save fields: pensión, banking, domicilio, sin pensión, read serializer). **5/5 PASAN** (verificado 2026-05-09).
- ❌ NO existe `apps/api/apps/employees/tests/` — sin tests in-app.
- ❌ NO hay tests del modelo `Employee` (creación, validaciones, properties como `edad`/`imc`/`nombre_completo`).
- ❌ NO hay tests para `FamilyMember`, `AcademicRecord`, `Certification` (modelos ni ViewSets).
- ❌ NO hay tests para `EmpleadoViewSet` actions custom (`transferir`, `estadisticas`, `reporte_integral`, `reporte_seccion`).
- ❌ NO hay tests para `EmpleadoFilter` (18 filtros sin cobertura).
- ❌ NO hay tests del `EmpleadoCreateSerializer.create()` transaccional (datos laborales + área + familiares + académicos en 1 POST).

### Gaps vs INTRANET legacy

VYNTIA employees es **paritario campo-por-campo** con el legacy en `Employee`/`Empleado`. Ambos modelos comparten **idénticos**:
- Mismas 8 listas de choices (TIPO_DOCUMENTO, GENERO, SISTEMA_PENSIONES, TIPO_COMISION, TIPO_SEGURO, ESTADO_CIVIL, TIPO_SANGRE, ESTADO_EMPLEADO, VIGENCIA_ESTADO_SEGURO).
- Mismos 50+ campos (incluida la suspensión de renta 4ta y el documento SUNAT).
- Mismos 13 indexes en `Meta`.
- Mismos métodos (`ubicacion_actual`, `datos_laborales_actuales`, `historial_ubicaciones`, `familiares_activos`, `formacion_academica`, `boletas_recientes`).
- Mismas properties (`nombre_completo`, `edad`, `genero_texto`, `es_activo`, `documento_completo`, `contacto_principal`, `direccion_completa`, `imc`).

Diferencias estructurales — todas adiciones C/L3, no pérdidas:
- PK: `empleado_id AutoField` → `id UUIDField`.
- Constraint: `numero_documento unique=True` global → `(tenant, numero_documento)` per-tenant + tenant FK.
- Audit timestamps: `fecha_registro/fecha_actualizacion` (legacy nombre) → `created_at/updated_at` (clase EN) con `db_column` legacy preservado.

Field-by-field comparison `FamilyMember`, `AcademicRecord`, `Certification`: **paritario absoluto**. Mismas choices, campos, indexes, métodos, properties — sólo cambian PK→UUID y unique_together extendido con `tenant`.

| Feature legacy | Ubicación legacy | Estado en VYNTIA | Tipo | Prioridad propuesta | Nota |
|---|---|---|:---:|:---:|---|
| Modelo `Empleado` (50+ campos, AutoField PK) | `D:/INTRANET/back/app_rrhh/models/empleado.py:17` | Migrado a `Employee` con UUID + class-name EN, db_table `empleado` preservado, **paridad campo-por-campo** | done | — | Sin pérdida funcional. |
| Modelo `DatosFamiliares` | `datos_familiares.py:15` | Migrado a `FamilyMember` con UUID + class-name EN, db_table `datos_familiares` preservado | done | — | Paridad funcional. |
| Modelo `DatosAcademicos` | `datos_academicos.py:15` | Migrado a `AcademicRecord` con UUID + class-name EN, db_table `datos_academicos` preservado | done | — | Paridad funcional. |
| Modelo `CursosCertificaciones` | `cursos_certificaciones.py:12` | Migrado a `Certification` con UUID + class-name EN, db_table `cursos_certificaciones` preservado | done | — | Paridad funcional. |
| Manager `EmpleadoManager` | `D:/INTRANET/back/app_rrhh/managers.py` | Comentado en VYNTIA `models/employee.py:15` (igual que legacy) | partial | P3 | Decidir: implementar o eliminar comentario. |
| Manager `DatosFamiliaresManager` / `DatosAcademicosManager` | `D:/INTRANET/back/app_rrhh/managers.py` | Comentados en VYNTIA, igual que legacy | partial | P3 | Mismo veredicto. |
| `Empleado.boletas_recientes()` stub | `empleado.py:291` | Stub copiado intacto a VYNTIA `employee.py:306` — devuelve `[]` con código muerto duplicado (lines 316-317 dos `return []`) | partial | P2 | Implementar cuando exista `Payslip` (B+ payroll) o eliminar. |
| Bug heredado: `EmpleadoReportService.generar_reporte_integral` usa `Employee.objects.get(empleado_id=empleado_id)` — campo `empleado_id` NO existe en VYNTIA (es `id` UUID) | `D:/INTRANET/back/app_rrhh/services/empleado_report_service.py` ↔ `apps/employees/services/employee_report_service.py:39, 57` | Bug heredado del rename L3 incompleto en service layer — los endpoints `/employees/{id}/reporte_integral/` y `/reporte_seccion/` SIEMPRE fallan con `FieldError`. **Bug crítico funcional.** | 🐛 bug crítico | P1 |
| Bug heredado: `EmpleadoCreateSerializer.validate_area_inicial` usa `Department.objects.get(area_id=value, ...)` — `area_id` NO existe en `Department` (es `id` UUID) | legacy: `serializers.py` ↔ `api/v1/rrhh/serializers.py:720` | Bug copiado del rename L3 — POST `/employees/` con `area_inicial` lanza `FieldError`. Si frontend SÍ envía `area_inicial`, **endpoint create falla**. | 🐛 bug crítico | P1 |
| Bug heredado: `EmpleadoCreateSerializer.area_inicial` declarado como `IntegerField` | `api/v1/rrhh/serializers.py:678` | Department PK ahora es UUID, debería ser `UUIDField` o `PrimaryKeyRelatedField(queryset=Department.objects.all())`. Combinado con bug anterior, hace el create endpoint de empleados completo **inutilizable**. | 🐛 bug crítico | P1 |
| `Empleado.numero_documento unique=True` global | `empleado.py:91` | Cambiado: ahora unique `(tenant, numero_documento)` per-tenant (migración 0002:47-67) | done | — | C cambió la semántica intencionalmente — distintos tenants pueden tener mismo DNI. |
| `Empleado.correo_personal unique=True` global | `empleado.py:141` | **NO migrado** — sigue `unique=True` global (employee.py:150). **Inconsistente con la decisión multi-tenant**: dos tenants no pueden tener un empleado con mismo email. | 🐛 bug C-multitenancy | P1 |

### Gaps vs maestro

El maestro § 3 Módulo 03 (líneas 175-191) define el ciclo de vida del empleado en **7 sub-procesos**. **Esta sección audita SOLO la entidad Employee y sus datos de soporte (familiares, académicos, certificaciones)** — sub-procesos como Selección, Vinculación, Inducción, Período de prueba, Desplazamiento y Desvinculación se gap-analizan en **Task 11 (Maestro gaps Module 03)** y NO se duplican aquí.

Foco de esta sección: **03.5 Administración de Legajos** — el repositorio digital permanente del trabajador. El maestro define 15 contenidos obligatorios del legajo (líneas 190-205); aquí trazamos cuáles están ya cubiertos por `Employee + FamilyMember + AcademicRecord + Certification + DigitalDocument`, y cuáles faltan.

| Capability del maestro (§ 03.5 / contenido legajo) | Estado en VYNTIA | Prioridad |
|---|---|:---:|
| 1. Datos personales (DNI, fotografía, dirección, estado civil, derechohabientes) | ✅ Cubierto por `Employee` (todos los campos) + `FamilyMember` (derechohabientes vía `es_dependiente`/`es_beneficiario`). Foto vía `ruta_fotografia` (CharField — no FileField, ver bugs). | — |
| 2. Datos académicos (diplomas, certificados, colegiatura, constancias) | ✅ Cubierto por `AcademicRecord` (incluye colegiatura, SUNEDU, diplomas) + `Certification`. | — |
| 3. Experiencia laboral previa | ❌ Inexistente. NO hay modelo `WorkExperience` o `PreviousJob`. Sólo el contrato actual y addendas (`apps.contracts`). | P1 (B feature gap) |
| 4. Contrato vigente y addendas | ⚠️ Cubierto en `apps.contracts` (Task 5) — fuera de scope employees. | (Task 5) |
| 5. Declaraciones juradas (no parentesco, no incompatibilidad, impedimentos, intereses) | ❌ Inexistente. NO hay modelo `SwornDeclaration` ni `Declaration`. Se almacenan como `DigitalDocument` genérico sin estructura. | P1 |
| 6. Documentos de identidad y CUSPP | ✅ Parcial: `numero_documento`, `tipo_documento`, `codigo_cuspp` en Employee. Documentos físicos vía `DigitalDocument` (Task 6). | — |
| 7. Historial de puestos ocupados en la entidad | ⚠️ Parcial vía `LocationHistory` (movimientos de área) + `EmploymentData` historial (con `estado_datos`). NO hay modelo dedicado `JobHistory` ni timeline consolidado. | P2 |
| 8. Evaluaciones de desempeño | ❌ Inexistente — Module 06 (no scope B, post-B). | (Module 06) |
| 9. Capacitaciones recibidas | ✅ Parcial — `Certification` cubre cursos formales. NO hay tracking de capacitaciones internas, asistencias, evaluaciones (Module 05). | (Module 05 post-B) |
| 10. Reconocimientos y felicitaciones | ❌ Inexistente. Existe `AcademicRecord.reconocimientos` (TextField) sólo para reconocimientos académicos. | P2 |
| 11. Sanciones disciplinarias | ❌ Inexistente — Module 09 procedimiento disciplinario (post-B). | (Module 09) |
| 12. Licencias otorgadas | ⚠️ Parcial via `apps.time_off` (vacaciones) — fuera de scope employees. Otras licencias (maternidad, paternidad, sin goce) no modeladas explícitamente. | (Task ??) |
| 13. Exámenes médicos ocupacionales (acceso restringido permlevel 9) | ❌ Inexistente. NO hay modelo `MedicalExam`. Module 07.2 SST (post-B). | (Module 07.2 post-B) |
| 14. Accidentes laborales (acceso restringido) | ❌ Inexistente. Module 07.2 SST (post-B). | (Module 07.2 post-B) |
| 15. Documentos de cese | ⚠️ Cubierto parcialmente vía `DigitalDocument` (categoría `cese`) en Task 6. Sin entidad estructurada `Termination`. | (Task 11 desvinculación) |
| **Funcionalidades 03.5 § 6.3** | | |
| Upload con OCR | ❌ NO implementado. `DigitalDocument` permite upload pero sin OCR. | P3 |
| Clasificación automática por tipo | ⚠️ `DigitalDocument.tipo_documento` y `categoria` son manuales (sin ML). | P3 |
| Firma electrónica | ❌ NO implementado. | P2 (sub-proyecto) |
| Versionado | ⚠️ `DigitalDocument` tiene `es_version_actual` (Task 6) — no expuesto vía UI. | P2 |
| **Control de acceso granular por documento (permission levels)** | ❌ NO implementado. `DigitalDocument.nivel_acceso` existe pero sin enforcement por permlevel del usuario. Coincide con gap A04 RBAC granular (ver identity chapter). | P1 (cross-cutting RBAC) |
| Búsqueda full-text | ❌ NO implementado. Sólo búsqueda por substring (DRF `SearchFilter`). | P3 |
| Exportación completa del legajo (PDF consolidado) | ✅ `EmpleadoReportService.generar_reporte_integral()` — pero **roto** (bug `empleado_id` arriba). Una vez fix, cubre el requisito básico. | P1 (fix bug) |
| Retención mínima 5 años post-cese | ❌ NO hay política implementada. | P3 |
| **Protección datos Ley 29733 (§ 6.4)** | | |
| Cifrado AES-256 datos sensibles (salud, biometría) | ❌ NO implementado. Datos médicos (`tipo_sangre`, `talla_empleado`, `peso_empleado`, `centro_salud`, etc.) en plaintext. | P1 (compliance) |
| Registro banco de datos ANPD | ❌ NO documentado ni implementado. | (compliance docs) |

### Bugs y deuda técnica conocidos

Pytest employees: `tests/test_empleado_update_v2.py` 5/5 PASAN. Sin fallos atribuibles a employees en la suite. Sin embargo, hay bugs latentes y bugs críticos en código no cubierto por tests:

| Bug | Ubicación | Causa | Tipo | Prioridad |
|---|---|---|:---:|:---:|
| `EmpleadoReportService` usa `Employee.objects.get(empleado_id=...)` — campo no existe (es `id` UUID) | `apps/employees/services/employee_report_service.py:39, 57` | Rename L3 incompleto: el legacy usaba `empleado_id` (AutoField) pero el modelo VYNTIA migró a `id` UUID. El service no se actualizó. **Endpoints `/reporte_integral/` y `/reporte_seccion/` siempre fallan con FieldError**. | 🐛 bug crítico | P1 |
| `EmpleadoCreateSerializer.validate_area_inicial` usa `Department.objects.get(area_id=value, estado_area="activo")` — `area_id` no existe (es `id` UUID), choice `activo` debería ser correcto pero se llama desde código legacy | `api/v1/rrhh/serializers.py:720` | Mismo problema rename L3 incompleto. **POST `/employees/` con `area_inicial` falla con FieldError**. | 🐛 bug crítico | P1 |
| `EmpleadoCreateSerializer.area_inicial = serializers.IntegerField(write_only=True)` | `serializers.py:678` | `Department.id` ahora es UUID. Debe ser `PrimaryKeyRelatedField(queryset=Department.objects.all())` o `UUIDField`. Bloquea el endpoint create completo. | 🐛 bug crítico | P1 |
| `Employee.correo_personal` es `unique=True` **global** (no per-tenant) | `apps/employees/models/employee.py:150` | Migración 0002 corrigió el unique de `numero_documento` pero olvidó `correo_personal`. Dos tenants NO pueden tener empleados con el mismo email — **bug C-multitenancy real**. | 🐛 bug seguridad C | P1 |
| `EmpleadoFilter.filter_area` filtra por `ubicaciones_destino__area_id` | `api/v1/rrhh/filters.py:161-167` | El related_name `ubicaciones_destino` es la reverse FK desde `Department` (no desde `Employee`). El filtro debería ser `historial_ubicaciones__area_destino_id` (related_name correcto desde Employee). Lanza `FieldError` al ejercitarse. | 🐛 bug | P1 |
| `EmpleadoFilter.filter_area_siglas` mismo issue + accede `area_destino__siglas_area` | `filters.py:170-177` | Misma causa. Mismo veredicto. | 🐛 bug | P1 |
| `EmpleadoFilter.filter_remuneracion_min/max` filtra por `datos_laborales__sueldo_basico` | `filters.py:206-222` | El campo en `EmploymentData` es `remuneracion_mensual` (no `sueldo_basico`). Filtros silenciosamente devuelven 0 resultados. | 🐛 bug | P2 |
| `EmpleadoFilter.filter_tiene_conyuge` busca parentesco en `["esposo", "esposa", "conviviente"]` | `filters.py:241` | Choices reales en `FamilyMember.PARENTESCO_CHOICES`: `conyuge` (no `esposo`/`esposa`) + `conviviente`. Filtro NO matchea cónyuges casados. | 🐛 bug | P2 |
| `EmpleadoViewSet.get_queryset` filter_by_area usa `historial_ubicaciones__area_destino__area_id` | `api/v1/rrhh/views.py:818-821` | `area_id` no existe; debe ser `area_destino_id` (UUID). Si `?area=` query param se pasa, lanza `FieldError`. | 🐛 bug | P1 |
| `EmpleadoViewSet.datos_completos` action devuelve hardcoded 501 NOT_IMPLEMENTED | `views.py:874-895` | Action declarada con permiso `ver_empleados` pero el body es un wrapper que siempre retorna 501. Endpoint ruidoso. | ⚠️ deuda | P3 |
| `EmpleadoViewSet.transferir` action usa `EmploymentData.objects.filter(...).update(area_id=...)` | `views.py:913-915` | `area_id` no existe; debe ser `area_id` legacy db_column. Actualmente `EmploymentData.area` es FK a Department UUID — ver Task 5 (contracts). Si los tests no lo ejercitan, está roto. | 🐛 bug | P1 |
| `EmpleadoViewSet.estadisticas` action usa `Employee.objects.count()` (sin filtrar por tenant) | `views.py:957-960` | Cuenta empleados de **todos los tenants**. Bug seguridad multi-tenant — confía 100% en RLS sin defense-in-depth. | 🐛 bug seguridad | P1 |
| `Employee.ruta_fotografia` es CharField legacy (no FileField/ImageField) | `employee.py:174` | Stores ruta string; sin manejo de upload, sin validación de tipo de archivo, sin URL absolute. Inconsistente con `documento_suspension_renta` (FileField line 140). | ⚠️ deuda | P2 |
| `Employee.boletas_recientes()` tiene `return []` duplicado | `employee.py:316-317` | Código muerto heredado del legacy: dos `return []` consecutivos. Cosmético pero evidencia de stub abandonado. | ⚠️ deuda | P3 |
| `Department.objects.get(area_id=...)` en `EmpleadoCreateSerializer.create()` | `serializers.py:737` | Repite el bug anterior. Si llegara aquí (no llega porque validate falla antes), lanza FieldError. | 🐛 bug crítico | P1 |
| `DatosFamiliaresViewSet`/`DatosAcademicosViewSet` self-service: confía en `user.empleado` (OneToOne reverse) | `views.py:1067-1070, 1166-1170` | OK funcionalmente. Pero el campo `user.empleado` debería resolverse vía OneToOne (existe en `User.empleado` line 50). Sin embargo, NO hay validación de que `instance.empleado.tenant == request.tenant` — un empleado de tenant A podría editar familiares de tenant B si su user-membership permite acceso (improbable pero defensible). | ⚠️ deuda seguridad | P2 |
| Custom managers comentados en los 4 modelos | `employee.py:15`, `family_member.py:14`, `academic_record.py:14` | Decisión pendiente. | ⚠️ deuda | P3 |
| Sin `apps/employees/tests/` | — | Tests viven en `apps/api/tests/` (root). Co-locate como B.2 cleanup. | ⚠️ deuda | P3 |
| Frontend `Employee` interface declara `nombres`, `ape_paterno`, `ape_materno`, `dni`, `email`, `area: {organo, siglas}`, `cargo: {...}` | `apps/web/src/features/employees/services/employeesService.ts:9-42` | Backend devuelve `nombres_empleado`, `apellido_paterno`, `apellido_materno`, `numero_documento`, `correo_personal`, sin objeto `area` anidado. Mismatch resuelto vía `normalizeEmployee` (`shared/api/apiNormalizers.ts:90`) — pero el tipo TS está mintiendo respecto al BE. | ⚠️ deuda tipos | P2 |
| ~~Frontend `DatosLaboralesService` apunta a `/api/v1/employment-data/`~~ — **CORRECCIÓN Task 15:** la URL es CORRECTA. `api/v1/urls.py:30` monta `contracts.urls` con `path('', include(...))` (flat, no prefix), por lo que `/api/v1/employment-data/` es la ruta real al `DatosLaboralesViewSet`. No es un bug. | `employeesService.ts:218, 230` | Verificado en Task 5 contracts chapter. No-op item — no se necesita fix. | ✅ verified | — |
| Frontend sin UI para `Certification` (cursos) | — | Modelo expuesto vía API pero sin pantallas. Usuarios no pueden gestionar cursos. | ❌ missing | P2 |

Sin errores TS ni warnings ESLint para `features/employees` (verificado con `tsc --noEmit -p tsconfig.app.json` y `npm run lint`).

### Tenant-readiness

| Concern | Status | Comment |
|---|:---:|---|
| `Employee` has tenant FK | ✅ | `employee.py:92` — nullable=true. Constraint: unique `(tenant, numero_documento)` (line 204-207). |
| `FamilyMember` has tenant FK | ✅ | `family_member.py:80` — nullable=true. `unique_together = (tenant, empleado, numero_documento)`. |
| `AcademicRecord` has tenant FK | ✅ | `academic_record.py:68` — nullable=true. `unique_together` extendido con `tenant`. |
| `Certification` has tenant FK | ✅ | `certification.py:18` — nullable=true. `unique_together` extendido con `tenant`. |
| Composite unique constraint sobre `(tenant, numero_documento)` Employee | ✅ | Migración 0002:64-67 añade `unique_employee_doc_per_tenant`. **Pero** el `unique=True` global de `correo_personal` (line 150) NO fue migrado — bug seguridad C. **P1 fix.** |
| `EmpleadoViewSet.get_queryset` filtra por tenant | ❌ | views.py:798-835 — NO filtra por tenant. Confía 100% en RLS+middleware. **Sin defense-in-depth.** |
| `DatosFamiliaresViewSet/DatosAcademicosViewSet/CursosCertificacionesViewSet.get_queryset` filtran por tenant | ❌ | views.py:1062-1074, 1163-1175, 1259-1274 — ninguno filtra por tenant explícitamente. Self-service filter (`user.empleado`) accidentalmente sirve de proxy de aislación, pero un user con membership en múltiples tenants **podría** ver familiares de empleados de otros tenants si su `user.empleado` apunta cross-tenant. Defense-in-depth ausente. |
| `EmpleadoViewSet.perform_create` asigna tenant automáticamente | ❌ | views.py:837-848 — NO setea `tenant` en `serializer.save()`. Si frontend no envía tenant, se crea con `tenant=NULL` (orphan cross-tenant). **Bug seguridad C P1.** |
| `EmpleadoCreateSerializer.create()` (transactional) propaga tenant a `EmploymentData`, `FamilyMember`, `AcademicRecord` | ❌ | serializers.py:725-750 — crea registros relacionados sin pasar tenant. Todos los nested writes tienen `tenant=NULL`. Si esto se invocara con éxito, generaría datos huérfanos. **Bug crítico** combinado con el bug del `area_inicial`. |
| `DatosFamiliares/Academicos/CursosCertificaciones perform_create` propaga tenant | ❌ | Idem — sin override de `perform_create`. `tenant=NULL` automático. |
| `EmpleadoViewSet.estadisticas` cuenta cross-tenant | ❌ | views.py:957-960 — `Employee.objects.count()` global. **Bug seguridad C P1**: dashboard de un tenant vería conteo de todos los tenants si RLS bypass. |
| `EmpleadoViewSet.transferir` propaga tenant | ❌ | views.py:913-915 — `EmploymentData.objects.filter(...).update(...)` sin filtrar por tenant. |
| `EmpleadoFilter` filters tenant | ❌ | filters.py:68-248 — los filtros `area`, `puesto`, `categoria`, etc., recorren relaciones (`historial_ubicaciones`, `datos_laborales`, `familiares`) sin filtrar por tenant. RLS-dependiente. |
| Test de aislación tenant para employees | ❌ | `tests/test_tenant_isolation.py` no incluye casos de Employee/FamilyMember/AcademicRecord/Certification. |
| Multi-tenant en frontend | ✅ | El frontend confía en host+JWT. Subdominio determina tenant. No hay selector. |

### Notas

- **Renombrado L3.10.x parcial — versión más severa que organization.** Class names ES→EN (`Empleado`→`Employee`, `DatosFamiliares`→`FamilyMember`, `DatosAcademicos`→`AcademicRecord`, `CursosCertificaciones`→`Certification`) hechos. PK fields legacy (`empleado_id`, `area_id`, `familiar_id`, `academico_id`, `curso_id`) **no fueron actualizados** en el código consumidor (services, serializers, views). Esto produce bugs críticos en `EmpleadoReportService` (3 endpoints PDF rotos), `EmpleadoCreateSerializer` (endpoint create roto), `EmpleadoViewSet.transferir` (action rota), `EmpleadoFilter.filter_area*` (filtros rotos), `EmpleadoViewSet.get_queryset` (filtro `?area=` roto). **El módulo employees está parcialmente roto en producción** y ningún test lo ejercita. **P1 priority en B.1 fast-track antes de exponer panel admin.**
- **Bug C-multitenancy: `correo_personal` unique global.** La migración 0002 corrigió el unique global de `numero_documento` pero olvidó `correo_personal`. Inconsistencia clara con el modelo multi-tenant. Riesgo: dos tenants con un empleado de mismo email → IntegrityError. **P1 fix:** retirar `unique=True` y añadir constraint `(tenant, correo_personal)` similar a `numero_documento`.
- **`Employee` es la entidad central HR — paritaria con legacy a nivel campos pero rota a nivel código consumidor.** Ningún campo del legacy se perdió. Sin embargo, los servicios/serializers/views/filters que usan `Employee` referencian PK fields legacy que ya no existen. Esto explica por qué los tests existentes (5 PATCH tests) PASAN — sólo testean update simple, NO los endpoints custom rotos.
- **Auto-tenant en perform_create ausente en los 4 ViewSets.** Patrón emergente cross-app (identity, organization, employees): ningún ViewSet asigna tenant automáticamente desde `request.tenant`. Cualquier POST que no envíe explícitamente `tenant` crea filas huérfanas. **Decision para B.1**: introducir un `TenantAwareViewSetMixin` que sobrescribe `perform_create` setting `tenant=request.tenant`. Aplicar a los 6 apps de Vyntia Core en una sola PR.
- **Self-service de familiares/académicos/certificaciones funciona en intención pero defense-in-depth ausente.** Los ViewSets confían 100% en `user.empleado == instance.empleado` para gating, sin verificar que `user.empleado.tenant == request.tenant`. Si un user con multi-membership accede al endpoint en el tenant equivocado, podría ver/editar registros del otro tenant. Improbable en flujo normal pero defensible.
- **Datos médicos sin cifrado.** `tipo_sangre`, `talla_empleado`, `peso_empleado`, `centro_salud`, `direccion_centro_salud`, `tiene_discapacidad` (FamilyMember) — todos en plaintext. Ley 29733 exige cifrado AES-256 para datos sensibles. **P1 compliance** antes de producción enterprise.
- **Endpoint create roto (alto impacto).** `POST /api/v1/employees/employees/` con `EmpleadoCreateSerializer` está roto por 3 bugs combinados (`area_inicial` IntegerField + `Department.objects.get(area_id=...)` + `validate_area_inicial` similar). El frontend `employeesService.create` (employeesService.ts:144-155) llama a este endpoint sin `area_inicial` (sólo manda Partial<Employee>) → posiblemente cae al `EmpleadoCreateSerializer.required area_inicial` y devuelve 400. Si se completa correctamente, falla con FieldError 500. **Cualquier flujo de "alta de empleado" en frontend está roto.**
- **`Certification` huérfano en frontend.** Modelo y endpoint REST listos, pero sin UI. Decisión: incluir en B.2 polish o backlog.
- **Riesgos al tocar employees en B.1/B.2.** (1) `db_table='empleado'`/`'datos_familiares'`/`'datos_academicos'`/`'cursos_certificaciones'` y `db_column='fecha_registro'`/`'fecha_actualizacion'` son referencia para datos importados — renombrar columnas físicamente rompe migración. (2) `Employee.empleado` OneToOne reverse desde `User` (related_name `usuario`, identity:user.py:50-55) — modificar el FK rompe auth flow. (3) `EmploymentData.empleado` y `LocationHistory.empleado` son FK PROTECT-cascading; eliminar Employee con datos laborales activos lanza `ProtectedError` (correcto). (4) Reportes PDF dependen de templates en `apps/api/templates/reportes/reporte_empleado.html` (ver Task 6 documents).
- **Preparación para Module 03 sub-procesos (Task 11).** `Employee` es la entidad ancla; en Task 11 se inventarían las 7 sub-procesos (Selección, Vinculación, Inducción, Periodo de prueba, Legajos extendido, Desplazamiento, Desvinculación). Esta sección sólo cubre la entidad y sus datos de soporte.

## App: contracts

### Estado actual en VYNTIA (post-A+C+L3.10.3)

> **Contexto split L3.10.3 (commit `e7bcf132` 2026-04-27):** El legacy tenía UN solo modelo `ContratosAdendas` con `tipo_documento` que mezclaba CAS/Ley 728/Ley 276 (contratos) + ADENDA_SALARIAL/CARGO/HORARIO/EXTENSION (adendas), distinguidos por `numero_adenda` nullable. L3.10.3 dividió en **DOS modelos**: `Contract` (sólo contratos, sin `numero_adenda`) y `ContractAmendment` (sólo adendas, FK `parent_contract` + `numero_adenda` siempre presente). Esta split deja consumidores stale (ver bugs).

#### Modelos
- `Contract` (file: `apps/api/apps/contracts/models/contract.py:19`) — contrato laboral inicial (sin adendas). Renombre L3.10.x: legacy `ContratosAdendas` → `Contract` con extracción de campos de adenda. PK UUID. Tabla legacy `contratos_adendas` preservada (line 224).
  - **Identidad**: `numero_contrato` (CharField max=50). Generador automático `generar_numero_contrato()` formato `CON-YYYY-NNNN` (line 342). Choice `tipo_documento` (CharField max=25) con **7 valores** (líneas 29-40): 3 de CAS (INDETERMINADO/DETERMINADO/SUPLENCIA), 3 de Ley 728 (FIJO/FIJO_SUPLENCIA/INDETERMINADO), 1 de Ley 276 (INDETERMINADO). **Nótese: NO incluye los 4 ADENDA_*** del legacy — esos se movieron a `ContractAmendment.TIPO_DOCUMENTO_CHOICES`.
  - **Relaciones**: `empleado` FK→`employees.Employee` (CASCADE, related_name `contratos_adendas`), `area` FK→`organization.Department` (PROTECT, related_name `contratos_adendas_area`).
  - **Fechas**: `fecha_inicio`, `fecha_fin` (nullable — para indeterminados), `fecha_firma` (nullable).
  - **Salario**: `salario_bruto` (DecimalField 10,2, MinValueValidator 0.01), `salario_neto` (nullable — calculado en `save()` como `salario_bruto * 0.87` rounded 2 decimals si no provisto, line 279).
  - **Laboral**: `cargo` (CharField max=100), `jornada_laboral` (4 choices: COMPLETA/PARCIAL/REDUCIDA/FLEXIBLE), `funciones` (TextField nullable), `lugar_trabajo`, `horario_trabajo`.
  - **Estado**: `status` (CharField max=15, **field renamed `estado` → `status` con db_column='estado'** line 167-173) con 6 choices: BORRADOR/PENDIENTE/ACTIVO/VENCIDO/TERMINADO/ANULADO. `documento_generado` (BooleanField).
  - **Audit**: `created_at` (auto_now_add, db_column `fecha_creacion`), `updated_at` (auto_now, db_column `fecha_modificacion`), `created_by`/`updated_by` FK→`identity.User` (PROTECT, db_columns `creado_por_id`/`modificado_por_id`).
  - Tenant FK: ✅ (line 78-85, nullable=true). **Constraint per-tenant**: `unique_contract_number_per_tenant` sobre `(tenant, numero_contrato)` (line 235-240). Migración 0003 (`migrations/0003_contract_tenant_contractamendment_tenant_and_more.py`) añade tenant FK a los 3 modelos + el constraint.
  - Manager: default. `ContratosAdendasManager` comentado (líneas 220-221, 369-370) — igual que legacy.
  - **Validaciones (`clean`)**: rechaza `fecha_fin <= fecha_inicio`; rechaza `fecha_fin` en tipos INDETERMINADO; exige `fecha_fin` en tipos DETERMINADO. `save()` invoca `full_clean()` siempre (line 282).
  - **Properties calculadas**: `dias_hasta_vencimiento`, `esta_vigente`, `esta_vencido`, `esta_por_vencer(dias=30)`, `duracion_dias`, `duracion_meses`. **Eliminadas vs legacy**: `es_contrato_inicial`, `es_adenda` (no aplican post-split).
  - **Métodos**: `generar_numero_contrato()`, `generar_numero_adenda()` (ahora delega a `self.amendments.count()` line 351-354), `puede_generar_adenda()`, `obtener_adendas()` (delega a `self.amendments.order_by('created_at')`).

- `ContractAmendment` (file: `apps/api/apps/contracts/models/contract_amendment.py:17`) — adenda a un contrato existente. **Modelo nuevo de L3.10.3** (no existía en legacy como entidad propia). PK UUID. Tabla nueva `contract_amendments` (line 185).
  - **Relación principal**: `parent_contract` FK→`contracts.Contract` (CASCADE, related_name `amendments`, line 60-65). **Diseño "delta-only"**: la adenda guarda sólo los campos que cambian, no duplica todos los del contrato.
  - **Choices propios**: `TIPO_DOCUMENTO_CHOICES` con 4 valores ADENDA_SALARIAL/CARGO/HORARIO/EXTENSION (los que ya no están en `Contract.TIPO_DOCUMENTO_CHOICES`).
  - **Identidad**: `numero_adenda` (CharField max=20, formato `AD-NNN` generado por `Contract.generar_numero_adenda()`).
  - **Fechas**: `fecha_inicio`, `fecha_fin` (nullable), `fecha_firma` (nullable).
  - **Nuevos valores (sólo el que aplica al tipo)**: `nuevo_salario` (Decimal 10,2 nullable), `nuevo_cargo` (CharField nullable), `nuevo_horario` (CharField nullable), `nueva_jornada_laboral` (choices nullable), `nueva_fecha_fin_contrato` (DateField nullable — para ADENDA_EXTENSION).
  - **Otros**: `motivo` (TextField nullable), `observaciones`, `status` (igual 6 choices que Contract, db_column `estado`), `documento_generado` (**FileField** upload `adendas/%Y/` — distinto al `BooleanField` de Contract).
  - **Audit**: created/updated_by/at idénticos a Contract (db_column legacy preservado).
  - Tenant FK: ✅ (line 51-58, nullable=true). NO hay constraint per-tenant explícito sobre `numero_adenda` — `unique_together = [['parent_contract', 'numero_adenda']]` (line 186), suficiente porque `parent_contract` ya pertenece a un tenant.
  - **Sin `clean()` ni `save()` overridden** — no hay validaciones cruzadas (e.g., que ADENDA_SALARIAL exija `nuevo_salario`, que ADENDA_CARGO exija `nuevo_cargo`, etc.). Ver bugs.

- `EmploymentData` (file: `apps/api/apps/contracts/models/employment_data.py:19`) — datos laborales actuales/históricos del empleado. Renombre L3.10.x: legacy `DatosLaborales` → `EmploymentData`. PK UUID. Tabla legacy `datos_laborales` preservada (line 139).
  - **Choices** (líneas 22-67): `TIPO_CONTRATO_CHOICES` (7 valores: CAS/CAP/indefinido/temporal/practicas/consultoria/locacion), `MODALIDAD_TRABAJO_CHOICES` (presencial/remoto/hibrido), `JORNADA_LABORAL_CHOICES` (completa/parcial/por_horas), `ESTADO_DATOS_CHOICES` (activo/inactivo/suspendido), `REGIMEN_LABORAL_CHOICES` (276/728/1057/locacion/consultoria/practicas), `CATEGORIA_CHOICES` (directivo/funcionario/profesional/tecnico/auxiliar/practicante/consultor).
  - **Relaciones**: `empleado` FK→`employees.Employee` (CASCADE, related_name `datos_laborales`), `area` FK→`organization.Department` (PROTECT, related_name `empleados_laborales`), `jefe_directo` FK→`employees.Employee` (SET_NULL, related_name `subordinados_laborales`).
  - **Puesto**: `cargo_empleado` (CharField max=100), `codigo_puesto`, `nivel_puesto`, `categoria` (choices).
  - **Contractual**: `tipo_contrato`, `regimen_laboral`, `modalidad_trabajo` (default `presencial`), `jornada_laboral` (default `completa`).
  - **Fechas**: `fecha_ingreso`, `fecha_inicio_contrato`, `fecha_fin_contrato` (nullable), `fecha_cese` (nullable).
  - **Salario**: `sueldo_basico` (Decimal 10,2, **sin MinValueValidator** — diferente a `Contract.salario_bruto`), `asignacion_familiar`, `bonificacion_especial`, `otras_bonificaciones` (todos Decimal 8,2 default 0).
  - **Horario**: `horario_entrada` (TimeField nullable), `horario_salida`, `horas_semanales` (Decimal 4,2 default 40).
  - **Control**: `estado_datos` (default `activo`), `observaciones`, `created_at` (db_column `fecha_registro`), `updated_at` (db_column `fecha_actualizacion`).
  - Tenant FK: ✅ (line 82-89, nullable=true). **NO hay composite unique constraint con tenant** — `unique_together = [['empleado', 'fecha_inicio_contrato']]` (line 155) — suficiente porque `empleado` ya está taggeado. **Pero**: si dos tenants tuvieran un Employee con el mismo numero_documento (lo cual NO debería pasar gracias al constraint per-tenant en Employee, pero vía bug C de `correo_personal`), no hay defense-in-depth.
  - Manager: default. `DatosLaboralesManager` comentado.
  - **Properties calculadas**: `sueldo_total`, `antiguedad_anos`, `antiguedad_meses`, `antiguedad_dias`, `antiguedad_texto`, `contrato_vigente`, `dias_para_vencimiento`, `contrato_por_vencer`, `es_activo`, `tipo_contrato_texto`, `regimen_laboral_texto`, `categoria_texto`, `modalidad_trabajo_texto`, `jornada_laboral_texto`, `horario_completo`.
  - **Métodos**: `calcular_vacaciones_pendientes()` (stub: retorna `anos_completos * 30` sin restar tomadas, comentario in-line), `generar_codigo_empleado()` (**ROTO** — usa `self.empleado.empleado_id` line 290 que NO existe en VYNTIA; ver bugs), `es_jefe_de(empleado)`, `subordinados_directos()`, `historial_cargos()`, `renovar_contrato(nueva_fecha_fin, observaciones)`, `cesar_empleado(fecha_cese, motivo)`.

#### Endpoints REST
URLs montadas **flat** sobre `/api/v1/` (NO bajo `/contracts/` prefix — file `api/v1/urls.py:30` usa `path('', include('api.v1.contracts.urls'))`). Routes finales:
- `/api/v1/contracts/` — `ContratosAdendasViewSet` (file: `api/v1/rrhh/contratos_views.py:34`). Routed via `api/v1/contracts/urls.py:15`.
  - `list` (GET): `@require_authenticated()`. Sin caché.
  - `retrieve` (GET): `@require_authenticated()`.
  - `create` (POST): `@require_hr()`. Usa `ContratosAdendasCreateSerializer` con `validate()` que duplica las reglas de `Contract.clean()`.
  - `update`/`partial_update` (PUT/PATCH): `@require_hr()`. Usa `ContratosAdendasUpdateSerializer` que recalcula `salario_neto` si cambia `salario_bruto` (line 157).
  - `destroy` (DELETE): `@require_admin()` — **hard delete** (no soft-delete, distinto a Employee).
  - Custom actions: `alertas_vencimiento` (GET, list — RRHH), `reporte_contratos` (GET, list — RRHH, agregaciones por tipo+área), `estadisticas` (GET, list — RRHH), `renovar_contrato` (POST detail — crea nuevo contrato heredando datos del original y marca el original como TERMINADO).
  - Filtros (en `get_queryset` líneas 86-126): `empleado_id`, `area_id`, `tipo_documento`, `estado`, `fecha_inicio`, `fecha_fin`. **Bug**: líneas 93-94 ambos `empleado_id` y `area_id` toman del query param `'id'` (mismo nombre) — los filtros se sobreescriben. Ver bugs.
  - Permission class: `IsAuthenticated` + decoradores por método. Sin filterset DjangoFilterBackend — filtros manuales.
  - Pagination: `StandardResultsSetPagination` (20/page).
- `/api/v1/contract-amendments/` — `ContractAmendmentViewSet` (`contratos_views.py:437`).
  - CRUD ModelViewSet completo (no decoradores `@require_hr` — sólo `IsAuthenticated`). **Bug seguridad**: cualquier autenticado puede crear/editar/eliminar adendas.
  - `get_queryset` filtra por `parent_contract` o `empleado` (query params).
  - Sin custom actions.
- `/api/v1/employment-data/` — `DatosLaboralesViewSet` (file: `api/v1/rrhh/views.py:1289`).
  - CRUD con decoradores `@require_authenticated` (list/retrieve), `@require_hr` (create/update/partial_update), `@require_admin` (destroy).
  - Custom action: `estadisticas_remuneracion` (GET list — RRHH, **ROTA** por uso de `estado_laboral` y `remuneracion_mensual` que no existen; ver bugs).
  - **Anti-patrón**: queryset declarado dos veces (línea 1292-1296 con `select_related` completo, sobrescrito en línea 1298 con sólo `empleado`). El primero está muerto.
  - FilterSet `DatosLaboralesFilter` (file: `filters.py:251`) declara filtros sobre **campos inexistentes**: `reg_laboral`, `condicion`, `grupo_ocupacional`, `puesto`, `estado`, `remuneracion`. Ningún filtro funciona; cualquier query param dispara `FieldError`. Ver bugs.
  - `search_fields = ["puesto_trabajo", "categoria_laboral", "regimen_laboral"]` — los primeros DOS no existen (real: `cargo_empleado`, `categoria`).
  - `ordering_fields = ["fecha_ingreso", "fecha_cese", "remuneracion_mensual"]` — `remuneracion_mensual` no existe.

#### UI (frontend)
- `ContratosPage` at `apps/web/src/features/contracts/pages/ContratosPage.tsx` (657 líneas) — listado con tabla, filtros (estado, tipo_documento, área, empleado, búsqueda), modal create, modal detail. Implementa `getAlertasVencimiento` para banner de vencimiento, `renovar` y `generarContratoPdf`/`generarAdendaPdf`/`generarCertificado`.
- Service: `contractsService` at `apps/web/src/features/contracts/services/contractsService.ts:152`. Endpoints: GET/POST/PATCH `/api/v1/contracts/`, GET `/api/v1/contracts/estadisticas/`, GET `/api/v1/contracts/alertas_vencimiento/`, POST `/api/v1/contracts/{id}/renovar_contrato/`. Cross-app: POST `/api/v1/documents/documents/generar-certificado/`, `generar-contrato/`, `generar-adenda/`.
- ❌ NO existe UI para `ContractAmendment` (adendas) en frontend post-split. La interface `Contrato` aún declara `numero_adenda?`, `es_contrato_inicial?`, `es_adenda?` (líneas 20, 46-47) — **fields stale del modelo unificado pre-L3.10.3**, ahora viven en el modelo `ContractAmendment` separado. Para crear una adenda hace falta una pantalla nueva.
- ❌ NO existe UI dedicada para `EmploymentData` — el listado/edición se hace desde Empleados (`employeesService.datosLaborales`).
- Hooks: NO hay `useContracts.ts`. La página usa React Query inline.

#### Tests
- `apps/api/tests/test_contratos_integration.py` — 11 tests TestContratosIntegration. **11/11 PASAN** (verificado 2026-05-09).
  - Cubre: `test_calculo_salario_neto`, `test_contrato_vencido`, `test_crear_adenda_contrato` (Contract + ContractAmendment), `test_crear_contrato_inicial`, `test_generacion_numeros_contrato`, `test_integracion_area_contratos`, `test_integracion_empleado_contrato`, `test_integracion_usuario_contratos`, `test_propiedades_calculadas_contrato`, `test_sistema_completo_workflow`, `test_validaciones_contrato`.
  - Sólo testea **modelos** — NO ejercita ningún ViewSet, ningún serializer, ningún endpoint. Por eso los bugs en `DatosLaboralesViewSet`/`DatosLaboralesFilter`/`DatosLaboralesSerializer`/filtros de `ContratosAdendasViewSet` quedan invisibles.
- ❌ NO existe `apps/contracts/tests/` (in-app tests).
- ❌ NO hay tests para tenant isolation de Contract/ContractAmendment/EmploymentData.
- ❌ NO hay tests para `ContractAmendmentViewSet` (CRUD adendas).
- ❌ NO hay tests para validación de "ADENDA_SALARIAL exige `nuevo_salario`", "ADENDA_CARGO exige `nuevo_cargo`", etc.
- ❌ NO hay tests para `EmploymentData.calcular_vacaciones_pendientes` ni `cesar_empleado()`.

### Gaps vs INTRANET legacy

VYNTIA contracts es **paritario campo-por-campo** con el legacy unificado, con la salvedad del split L3.10.3. El legacy `ContratosAdendas` se mapea como **unión** de `Contract` (campos no-adenda) + `ContractAmendment` (campos de adenda). `DatosLaborales` → `EmploymentData` es paritario absoluto.

| Feature legacy | Ubicación legacy | Estado en VYNTIA | Tipo | Prioridad propuesta | Nota |
|---|---|---|:---:|:---:|---|
| Modelo `ContratosAdendas` (unificado, AutoField PK) | `D:/INTRANET/back/app_rrhh/models/contratos_adendas.py:17` | **Split a `Contract` + `ContractAmendment`** (L3.10.3 commit `e7bcf132`). PK UUID + class-name EN. Tabla `contratos_adendas` preservada para Contract; `contract_amendments` nueva. | done | — | Sin pérdida funcional. **Decision arquitectural intencional**: separar permite validaciones específicas y queries distintos. |
| Choice `ADENDA_SALARIAL/CARGO/HORARIO/EXTENSION` en `tipo_documento` legacy | `contratos_adendas.py:39-42` | Movidos a `ContractAmendment.TIPO_DOCUMENTO_CHOICES` (líneas 26-31). Eliminados de `Contract.TIPO_DOCUMENTO_CHOICES`. | done | — | Coherente con split. |
| Campo `numero_adenda` (nullable) en modelo unificado | `contratos_adendas.py:87-92` | Movido a `ContractAmendment.numero_adenda` (CharField max=20, requerido). Eliminado de `Contract`. **Pero**: consumidores stale (template_service, word_template_service, frontend interface) aún acceden `contrato.numero_adenda`. | partial | P1 | Ver bugs §. |
| Property `es_contrato_inicial`, `es_adenda` | `contratos_adendas.py:334-342` | **Eliminadas** (no aplican post-split: `Contract` siempre es contrato inicial). Frontend interface `Contrato` aún declara estos fields opcional → siempre `undefined` post-split. | partial | P3 | Limpiar tipo TS. |
| Método `generar_numero_adenda()` legacy (busca por `numero_contrato`) | `contratos_adendas.py:354-364` | Migrado a `Contract.generar_numero_adenda()` (line 351-354) que ahora delega a `self.amendments.count()`. | done | — | Más eficiente con FK. |
| Método `obtener_contrato_base()` (si es adenda devuelve el contrato unificado padre) | `contratos_adendas.py:384-395` | **Eliminado** del `Contract`. La nueva `ContractAmendment.parent_contract` cumple el mismo rol vía FK directa. | done | — | Diseño superior con FK. |
| Constraint `unique_together = [['numero_contrato', 'numero_adenda']]` | `contratos_adendas.py:221` | **Cambiado** a per-tenant: `Contract` tiene `unique_contract_number_per_tenant` sobre `(tenant, numero_contrato)`; `ContractAmendment` tiene `unique_together = [['parent_contract', 'numero_adenda']]`. | done | — | Decisión multi-tenant. |
| Modelo `DatosLaborales` (AutoField PK) | `D:/INTRANET/back/app_rrhh/models/datos_laborales.py:18` | Migrado a `EmploymentData` con UUID + class-name EN, db_table `datos_laborales` preservado, **paridad campo-por-campo absoluta**. | done | — | Sin pérdida funcional. |
| `DatosLaborales.dato_laboral_id AutoField` | `datos_laborales.py:69` | Cambiado a `id UUIDField`. | done | — | Decisión multi-tenant. |
| `EmploymentData` audit fields legacy `fecha_registro`/`fecha_actualizacion` | `datos_laborales.py:132-133` | Renombrados a `created_at`/`updated_at` con `db_column` legacy preservado (líneas 132-133 VYNTIA). | done | — | Compat con datos importados. |
| Manager `ContratosAdendasManager` / `DatosLaboralesManager` | `D:/INTRANET/back/app_rrhh/managers.py` | Comentados en VYNTIA (igual que legacy). | partial | P3 | Implementar o eliminar. |

### Gaps vs maestro

El maestro § 3 Módulo 03.2 (líneas 74-127 de `docs/modulos/03_gestion_empleo.md`) define **Vinculación**: generación de contrato, firma electrónica, T-Registro, EsSalud/AFP, entrega de documentos obligatorios. **Esta sección audita SOLO la entidad Contract en sí** — los flujos de Vinculación completos (T-Registro, firma, plantillas dinámicas) son scope de **Task 11 (Module 03 gaps)**.

| Capability del maestro (§ 03.2 / Contract entity) | Estado en VYNTIA | Prioridad |
|---|---|:---:|
| 7 tipos de contrato régimen 728 (Indefinido, Inicio/Incremento actividad, Necesidad mercado, Reconversión, Ocasional, Suplencia, Emergencia, Obra/servicio, Intermitente, Temporada, Tiempo parcial — 11 según tabla maestro) | ⚠️ Parcial. `Contract.TIPO_DOCUMENTO_CHOICES` tiene 3 de Ley 728 (FIJO/FIJO_SUPLENCIA/INDETERMINADO). **Faltan**: Por inicio/incremento actividad, Necesidad mercado, Reconversión, Ocasional, Emergencia, Obra/servicio, Intermitente, Temporada, Tiempo parcial. La estructura legal es más rica que los 3 buckets actuales. | P1 (B feature gap) |
| Tope conjunto contratos modalidad 5 años → desnaturaliza a indeterminado (Art. 77 LPCL) | ❌ No implementado. Sin lógica que sume duración acumulada de contratos sucesivos por empleado y dispare desnaturalización. | P1 (compliance) |
| `Contract.regimen_laboral` (CAS/728/276) | ⚠️ Parcial. El campo `tipo_documento` codifica indirectamente el régimen vía prefix (`CAS_*`, `LEY_728_*`, `LEY_276_*`) — pero NO hay un campo `regimen_laboral` separado en `Contract`. `EmploymentData.regimen_laboral` SÍ existe (entidad distinta). Inconsistencia de modelo entre Contract y EmploymentData. | P2 |
| `ContractStatus` (VIGENTE/SUSPENDIDO/TERMINADO) | ✅ Cubierto por `Contract.status` (BORRADOR/PENDIENTE/ACTIVO/VENCIDO/TERMINADO/ANULADO) — alineado. | — |
| `ContractDocument` (PDF firmado del contrato) | ⚠️ Parcial. `Contract.documento_generado` es BooleanField (sólo flag); el PDF real va a `apps.documents.DigitalDocument` (ver Task 6). `ContractAmendment.documento_generado` SÍ es FileField (asimétrico). | P2 |
| Generación automática de contrato según régimen y tipo contractual | ⚠️ Parcial. `template_service.py` y `word_template_service.py` arman variables por contrato — pero usan placeholders stale (`numero_adenda` accedido en Contract). Frontend invoca `documents.generar-contrato` (ver Task 6). | (Task 6) |
| Firma electrónica del contrato | ❌ No implementado. `Contract.fecha_firma` existe (DateField) — sin integración con servicio de firma electrónica. | P1 (sub-proyecto) |
| Registro T-Registro SUNAT (alta) — txt estructurado Anexo 3 + PVS | ❌ No implementado. NO hay `TRegistroDeclaration` ni servicios SUNAT. Modelo en maestro § 3.5 menciona la entidad. | P1 (compliance — Task 11) |
| Registro EsSalud / EPS (alta del trabajador) | ❌ No implementado. | (Task 11) |
| Afiliación AFP / ONP (validación o alta) | ❌ No implementado. `Employee.sistema_pensiones` existe pero sin workflow. | (Task 11) |
| Apertura cuenta haberes | ❌ No implementado. `Employee.entidad_bancaria`/`numero_cuenta_bancaria` existen. | P3 |
| Entrega de documentos obligatorios (RIT, Reglamento SST, Código ética, Política protección datos, Manual funciones) | ❌ No implementado. Documents app tiene generic `DigitalDocument` pero sin gating "vinculación incompleta hasta entrega". | (Task 11 + Task 6) |
| Validación ADENDA_SALARIAL exige `nuevo_salario`, ADENDA_CARGO exige `nuevo_cargo`, etc. | ❌ No implementado. `ContractAmendment` no tiene `clean()` ni validators que verifiquen coherencia tipo↔campo. Una adenda puede crearse vacía. | P2 |
| Estado VENCIDO automático cuando `fecha_fin < hoy` | ❌ No implementado. El status no se actualiza por cron — debe hacerse manualmente. Property `esta_vencido` calcula on-the-fly pero `status` en BD se queda en ACTIVO. | P2 |
| Notificaciones de vencimiento próximo (SLA legal: avisar al trabajador antes del fin) | ⚠️ Parcial. Endpoint `alertas_vencimiento` lista contratos próximos a vencer — pero no hay notificación automática (email/celery task). | P2 |
| Multi-régimen (276 público / 728 privado / 1057 CAS) con strategy pattern | ⚠️ Parcial. `Contract.tipo_documento` discrimina por prefix; sin clase strategy real. EmploymentData.regimen_laboral idem. Module 04 (payroll) requeriría strategy real. | P2 (post-B Module 04) |

### Bugs y deuda técnica conocidos

Pytest contracts: 11/11 PASAN (`test_contratos_integration.py`). PERO: tests sólo cubren modelos, NO ejercitan ViewSets/serializers/filters — todos los bugs que listamos están latentes.

| Bug | Ubicación | Causa | Tipo | Prioridad |
|---|---|---|:---:|:---:|
| `EmploymentData.generar_codigo_empleado()` usa `self.empleado.empleado_id` — campo no existe en `Employee` (es `id` UUID) | `apps/contracts/models/employment_data.py:290` | Rename L3 incompleto. Igual patrón que bugs employees Task 4. **Si se invoca, lanza AttributeError**. | 🐛 bug | P1 |
| `EmploymentData.calcular_vacaciones_pendientes()` retorna `anos_completos * 30` sin restar tomadas | `employment_data.py:283-285` | Stub heredado del legacy, aún incompleto. Comentario in-line "Aquí se restaría los días ya tomados". El cálculo correcto vive en `apps.time_off`. | ⚠️ deuda | P2 |
| `ContratosAdendasViewSet.get_queryset` líneas 93-94 leen ambos `empleado_id` y `area_id` del MISMO query param `'id'` | `api/v1/rrhh/contratos_views.py:93-94` | Copy-paste bug — `empleado_id = request.query_params.get("id")` y dos líneas después `area_id = request.query_params.get("id")`. Resultado: ambos filtros se aplican al mismo valor cuando se pasa `?id=...`. **Probablemente debería ser `empleado` y `area`.** | 🐛 bug | P1 |
| `ContratosAdendasViewSet.estadisticas` action invoca `Contract.objects.count()` (sin tenant filter) | `contratos_views.py:297` | Igual patrón que `EmpleadoViewSet.estadisticas`. Cuenta cross-tenant. **Bug seguridad C P1**. También líneas 298, 302, 318, 325 — `Contract.objects.values(...)` sin tenant filter. | 🐛 bug seguridad | P1 |
| `ContratosAdendasViewSet.alertas_vencimiento` action invoca `area_id = request.query_params.get("id")` | `contratos_views.py:142` | Mismo copy-paste — debería ser `area_id = request.query_params.get("area_id")`. | 🐛 bug | P2 |
| `ContratosAdendasViewSet.reporte_contratos` action filtra por `area_id = request.query_params.get("id")` | `contratos_views.py:198` | Idem. Y línea 273 lo serializa al response como `'id': area_id` (clave engañosa). | 🐛 bug | P2 |
| `ContratosAdendasViewSet.renovar_contrato` action: `obs_anterior` con regex `.strip(" -")` line 412 | `contratos_views.py:412-414` | Cosmético: el `.strip(" -")` puede recortar caracteres legítimos del nombre. No bug crítico pero raro. | ⚠️ deuda | P3 |
| `ContratosAdendasViewSet.renovar_contrato` invoca create con `'empleado': contrato.empleado_id`, `'area': contrato.area_id` | `contratos_views.py:378-379` | Funciona porque Django acepta el `_id` field en `ForeignKey`. Pero NO propaga `tenant`. **Combinado con la falta de `perform_create`**, el nuevo contrato se crea con `tenant=NULL`. | 🐛 bug seguridad C | P1 |
| `ContractAmendmentViewSet` tiene `permission_classes = [IsAuthenticated]` SIN `@require_hr` | `contratos_views.py:444` | Cualquier usuario autenticado puede crear/editar/borrar adendas. No hay role-gating. **Bug seguridad serio**. | 🐛 bug seguridad | P1 |
| `ContractAmendment` sin `clean()` que valide coherencia tipo↔campo | `contract_amendment.py` | Una `ADENDA_SALARIAL` sin `nuevo_salario` se guarda silenciosamente. ADENDA_CARGO sin `nuevo_cargo` idem. Validación lógica ausente. | ⚠️ deuda lógica | P2 |
| `ContractAmendment` sin manager / sin `documento_generado` valor inicial coherente con Contract | `contract_amendment.py:151-156` | Diseño asimétrico: Contract usa BooleanField; ContractAmendment usa FileField. Confunde a consumidores. | ⚠️ deuda | P3 |
| `DatosLaboralesViewSet.queryset` declarado dos veces — el primero (con select_related completo) es código muerto | `views.py:1292-1296 + 1298` | Línea 1298 sobrescribe el queryset de líneas 1292-1296. Performance penalty: queries hace JOINs extra cuando se ejecuta `area`/`jefe_directo`. | 🐛 bug performance | P2 |
| `DatosLaboralesViewSet.search_fields = ["puesto_trabajo", "categoria_laboral", "regimen_laboral"]` — los primeros DOS no existen | `views.py:1308` | Real: `cargo_empleado`, `categoria`. Búsqueda `?search=...` lanza FieldError. | 🐛 bug | P1 |
| `DatosLaboralesViewSet.ordering_fields = [..., "remuneracion_mensual"]` — campo no existe | `views.py:1309` | Real: `sueldo_basico`. `?ordering=remuneracion_mensual` lanza FieldError. | 🐛 bug | P1 |
| `DatosLaboralesViewSet.estadisticas_remuneracion` filtra `estado_laboral="activo"` | `views.py:1355` | Campo real: `estado_datos`. Lanza FieldError. | 🐛 bug crítico | P1 |
| `DatosLaboralesViewSet.estadisticas_remuneracion` agrega `Avg("remuneracion_mensual")` | `views.py:1357` | Campo real: `sueldo_basico`. Lanza FieldError. **Endpoint roto al 100%**. | 🐛 bug crítico | P1 |
| `DatosLaboralesFilter` declara filtros sobre **5 campos inexistentes** (`reg_laboral`, `condicion`, `grupo_ocupacional`, `puesto`, `estado` BooleanField, `remuneracion`) | `filters.py:251-296` | Migración fallida del legacy: el legacy tenía esos nombres, VYNTIA renombró. **Cualquier query param dispara FieldError**. Filterset entero está roto. | 🐛 bug crítico | P1 |
| `DatosLaboralesFilter.Meta.fields` lista los mismos campos rotos | `filters.py:289-296` | El FilterSet ni se instancia correctamente — emite warnings al startup. | 🐛 bug | P1 |
| `DatosLaboralesSerializer` declara `antiguedad_años` (con tilde) ReadOnlyField | `serializers.py:258, 306` | Property real: `antiguedad_anos` (sin tilde). DRF intenta acceder a `obj.antiguedad_años` → AttributeError → field se serializa como `null`. **Silencioso pero roto**. | 🐛 bug | P1 |
| `DatosLaboralesSerializer` declara `tiempo_servicio` ReadOnlyField | `serializers.py:260, 308` | Property no existe. Real: `antiguedad_texto`. Field serializa como `null`. | 🐛 bug | P2 |
| `DatosLaboralesSerializer.validate_remuneracion_mensual` | `serializers.py:316-320` | Field `remuneracion_mensual` no existe en el serializer ni en el modelo. La validación nunca se invoca. | ⚠️ deuda | P3 |
| `DatosLaboralesSerializer.get_ultimo_login_texto` accede `obj.empleado.usuario` | `serializers.py:266-274` | El related_name de User→Employee es `empleado` (forward) y de Employee→User es `usuario` (reverse OneToOne). **Si funciona** depende de cómo se nombró en identity:user.py. Verificar Task 1. | ⚠️ deuda | P3 |
| `template_service.py:216` usa `getattr(contrato, 'numero_adenda', None)` — Contract no tiene ese field post-split | `apps/documents/services/template_service.py:216` | **Bug L3.10.3 — consumer stale.** `getattr` con default evita AttributeError pero siempre retorna `None` para Contract. Templates con `{{ contrato.numero_adenda }}` siempre vacío. | 🐛 bug L3.10.3 | P1 |
| `template_service.py:129-132` accede `adenda.numero_adenda` (correcto) — pero línea 216 mezcla en mismo dict | `apps/documents/services/template_service.py:129, 132, 216` | Diseño confuso post-split: el mismo helper se invoca para Contract y para ContractAmendment según contexto. | ⚠️ deuda | P2 |
| `word_template_service.py:139` acceso directo `contrato.numero_adenda or ''` (sin getattr) | `apps/documents/services/word_template_service.py:139` | **Bug crítico L3.10.3.** `Contract` no tiene `numero_adenda` → `AttributeError`. Cualquier flujo de generación Word de contrato (no adenda) **falla**. | 🐛 bug crítico L3.10.3 | P1 |
| `apps/contracts/apps.py:4-16` docstring describe modelo unificado y "Future split (deferred to L3.10/post-rename)" | `apps/contracts/apps.py` | **Documentación stale L3.10.3.** El split YA se hizo, pero el AppConfig docstring lo lista como pendiente. | ⚠️ deuda docs | P3 |
| Frontend `Contrato` interface declara `numero_adenda?`, `es_contrato_inicial?`, `es_adenda?` | `apps/web/src/features/contracts/services/contractsService.ts:20, 46-47` | **Stale fields del modelo unificado pre-L3.10.3.** Backend ya no los devuelve (Contract no los tiene). El tipo TS está mintiendo. | ⚠️ deuda tipos | P2 |
| Frontend `ContratoFormData` declara `numero_adenda?` | `contractsService.ts:74` | Idem — campo no existe en `ContratosAdendasCreateSerializer`. Si el form lo enviara, DRF lo ignoraría silenciosamente. | ⚠️ deuda tipos | P2 |
| Frontend sin UI para crear/editar `ContractAmendment` post-split | — | Modelo y endpoint REST listos, pero ContratosPage sólo gestiona contratos. La acción "renovar" crea un nuevo Contract, no un ContractAmendment. | ❌ missing | P1 |
| `EmpleadoCreateSerializer.create()` (employees app) crea `EmploymentData` sin tenant | `api/v1/rrhh/serializers.py:725-750` | Ya documentado en Task 4 — recordatorio aquí: el bug afecta a contracts también porque crea EmploymentData con `tenant=NULL`. | 🐛 bug C-multitenancy | P1 |
| `Contract.salario_neto` se calcula como `salario_bruto * 0.87` quantize 0.01 | `contract.py:279` | Cálculo de descuentos hardcoded a 13% (sin AFP/ONP/EsSalud reales). Para Module 04 hace falta strategy real. | ⚠️ deuda lógica | P2 |
| `Contract.save()` siempre invoca `full_clean()` | `contract.py:282` | Ineficiente en updates parciales. Pero acepta porque las validaciones son lightweight. | ⚠️ deuda perf | P3 |
| Custom managers comentados | `contract.py:220-221, 369-370`; `employment_data.py:16, 136` | Decisión pendiente. | ⚠️ deuda | P3 |
| Sin `apps/contracts/tests/` | — | Tests viven en `apps/api/tests/test_contratos_integration.py`. Co-locate como B.2 cleanup. | ⚠️ deuda | P3 |
| Tests no ejercitan ViewSet/Serializer/Filter | `tests/test_contratos_integration.py` | Por eso 21+ bugs declarados aquí pasan invisibles. | ⚠️ deuda tests | P1 |

Sin errores TS ni warnings ESLint para `features/contracts` (verificado con `tsc --noEmit -p tsconfig.app.json` y `npm run lint`).

### Tenant-readiness

| Concern | Status | Comment |
|---|:---:|---|
| `Contract` has tenant FK | ✅ | `contract.py:78-85` — nullable=true. Constraint: `unique_contract_number_per_tenant` sobre `(tenant, numero_contrato)` (line 235-240). |
| `ContractAmendment` has tenant FK | ✅ | `contract_amendment.py:51-58` — nullable=true. `unique_together = (parent_contract, numero_adenda)` (line 186) — suficiente porque parent_contract ya está taggeado. |
| `EmploymentData` has tenant FK | ✅ | `employment_data.py:82-89` — nullable=true. `unique_together = (empleado, fecha_inicio_contrato)` (line 155). |
| Composite unique constraint sobre `(tenant, numero_contrato)` Contract | ✅ | Migración 0003:38-43 añade `unique_contract_number_per_tenant`. |
| `ContratosAdendasViewSet.get_queryset` filtra por tenant | ❌ | `contratos_views.py:86-126` — NO filtra por tenant. Confía 100% en RLS+middleware. Sin defense-in-depth. |
| `ContractAmendmentViewSet.get_queryset` filtra por tenant | ❌ | `contratos_views.py:447-455` — NO filtra por tenant. |
| `DatosLaboralesViewSet.get_queryset` filtra por tenant | ❌ | `views.py:1342-1348` — NO filtra por tenant. |
| `ContratosAdendasViewSet.perform_create` asigna tenant automáticamente | ❌ | NO hay override. Si frontend no envía tenant, se crea con `tenant=NULL` (orphan cross-tenant). **Bug seguridad C P1.** El `ContratosAdendasCreateSerializer.create` (line 124) tampoco lo setea. |
| `ContractAmendmentViewSet.perform_create` asigna tenant | ❌ | NO hay override. ContractAmendment se crea con `tenant=NULL`. Combinación crítica con el bug de `permission_classes = [IsAuthenticated]` (cualquier user puede crear adendas en cualquier tenant). |
| `DatosLaboralesViewSet.perform_create` asigna tenant | ❌ | Idem. |
| `ContratosAdendasViewSet.estadisticas` y `reporte_contratos` cuentan cross-tenant | ❌ | `contratos_views.py:297-306, 309-330` — `Contract.objects.count()`/values() sin filter por tenant. **Bug seguridad C P1**. |
| `ContratosAdendasViewSet.renovar_contrato` propaga tenant al nuevo contrato | ❌ | `contratos_views.py:377-403` — el `nuevo_contrato_data` no incluye `tenant`. **Crea contrato huérfano**. |
| Test de aislación tenant para Contract/ContractAmendment/EmploymentData | ❌ | `tests/test_tenant_isolation.py` no incluye casos de estos modelos. |
| Multi-tenant en frontend | ✅ | El frontend confía en host+JWT. Subdominio determina tenant. |

### Notas

- **Split L3.10.3 dejó 4 consumidores stale.** El split de `ContratosAdendas` → `Contract` + `ContractAmendment` (commit `e7bcf132` 2026-04-27) es arquitecturalmente correcto pero NO actualizó: (1) `apps/documents/services/template_service.py:216` (`getattr(contrato, 'numero_adenda', None)` — silencioso pero stale), (2) `apps/documents/services/word_template_service.py:139` (`contrato.numero_adenda or ''` — **AttributeError crítico** en generación Word de contratos no-adenda), (3) `apps/web/src/features/contracts/services/contractsService.ts:20,46-47` (interface TS aún declara `numero_adenda`/`es_contrato_inicial`/`es_adenda`), (4) `apps/contracts/apps.py:4-16` (docstring del AppConfig describe el modelo unificado y lista el split como "Future"). **P1 cleanup en B.1 fast-track**.
- **`DatosLaboralesViewSet`/`Filter`/`Serializer` están rotos al ~80%.** El renombre L3.10.x no actualizó referencias a campos antiguos del legacy: `puesto_trabajo`, `categoria_laboral`, `remuneracion_mensual`, `estado_laboral`, `reg_laboral`, `condicion`, `grupo_ocupacional`, `antiguedad_años` (con tilde), `tiempo_servicio`. **8 fields fantasma**. Cualquier query con search/ordering/filter sobre `EmploymentData` lanza FieldError. El endpoint `estadisticas_remuneracion` está 100% roto. **P1 prioridad antes de exponer panel admin con métricas.**
- **`ContractAmendmentViewSet` sin role-gating.** El ViewSet sólo declara `permission_classes = [IsAuthenticated]` — cualquier usuario logueado puede CRUD adendas en cualquier tenant (compuesto con el bug de tenant filtering ausente). **Bug seguridad serio P1**: un empleado regular podría crear adendas falsificadas.
- **`ContratosAdendasViewSet` get_queryset bug copy-paste.** Líneas 93-94 leen empleado_id y area_id del mismo query param `'id'` — los filtros se sobreescriben. Probablemente debería ser `'empleado'` y `'area'`. Igual patrón en `alertas_vencimiento` (line 142) y `reporte_contratos` (line 198). El frontend `contractsService.getAll` envía `empleado_id` y `area_id` (líneas 156-157) — el backend nunca los recibe. **Filtros no funcionan en absoluto.**
- **Auto-tenant en perform_create ausente — patrón cross-app confirmado.** Igual que identity, organization, employees: ningún ViewSet de contracts asigna tenant automáticamente. **Decision para B.1 fast-track**: introducir `TenantAwareViewSetMixin` aplicable a los 6 apps de Vyntia Core. Esta es la 4ª chapter que reporta el mismo problema.
- **`ContractAmendment` sin validación de coherencia tipo↔campo.** Una `ADENDA_SALARIAL` puede crearse sin `nuevo_salario`; ADENDA_CARGO sin `nuevo_cargo`; etc. **P2 fix**: añadir `clean()` que verifique coherencia.
- **Asimetría `Contract.documento_generado` BooleanField vs `ContractAmendment.documento_generado` FileField.** Confunde consumidores: el primero es flag, el segundo es upload. La elección histórica viene del legacy, pero post-split se debería unificar (probablemente usando Document FK del Task 6 documents app).
- **Tipo de contrato régimen 728 sub-modelado.** El maestro § 03.2 lista 11 tipos de contrato (Indefinido, Inicio/Incremento actividad, Necesidad mercado, Reconversión, Ocasional, Suplencia, Emergencia, Obra/servicio, Intermitente, Temporada, Tiempo parcial). VYNTIA captura sólo 3 (FIJO/FIJO_SUPLENCIA/INDETERMINADO). Para B+ feature parity se necesita extender choices y añadir lógica de desnaturalización (Art. 77 LPCL: 5 años máx → indeterminado automático).
- **Sin `regimen_laboral` field en Contract.** El régimen está implícito en el prefix de `tipo_documento`. Inconsistente con `EmploymentData.regimen_laboral` (campo explícito). **P2 refactor**: añadir `Contract.regimen_laboral` y derivarlo del tipo, o sólo mantener uno de los dos.
- **Tests cubren modelos al 100% pero ViewSets/Serializers/Filters al 0%.** 11 tests de integración pasan validando lógica de modelo (full_clean, properties, FK, generadores), pero NO ejercitan ningún endpoint REST. Por eso los ~21 bugs declarados arriba NO disparan ningún CI failure. **P1 priority en B.1**: smoke tests sobre los endpoints rotos antes de habilitar dashboard.
- **EmpleadoCreateSerializer (employees app) crea EmploymentData sin tenant.** Recordatorio del Task 4: el flujo nested-write `POST /employees/` con `area_inicial` debería crear un `EmploymentData` con tenant — actualmente lo crea con `tenant=NULL`. Cross-bug entre employees y contracts.
- **Riesgos al tocar contracts en B.1/B.2.** (1) `db_table='contratos_adendas'`, `'datos_laborales'`, `'contract_amendments'` y db_columns legacy son referencia para datos importados. (2) `EmploymentData.empleado` FK CASCADE — eliminar Employee borra cascade su EmploymentData. (3) `Contract.empleado` FK CASCADE idem. (4) `ContractAmendment.parent_contract` FK CASCADE — eliminar Contract borra todas sus adendas. (5) `obj.empleado.usuario` reverse OneToOne de identity.User → identidad clave. (6) Generación PDF/Word depende de templates `apps/api/templates/contratos/` y `apps/api/templates/adendas/` (ver Task 6).
- **Preparación para Module 03 sub-procesos (Task 11).** `Contract` es el ancla de **03.2 Vinculación**; en Task 11 se inventarían los flujos completos (T-Registro, firma electrónica, EsSalud/AFP, entrega de docs obligatorios). Esta sección sólo cubrió la entidad. La extensión de tipos de contrato régimen 728 (los 11 del maestro) y la lógica de desnaturalización son las mayores piezas pendientes.

## App: documents

### Estado actual en VYNTIA (post-A+C)

> **Contexto rename L3.11:** El legacy tenía `DocumentosDigitales` (AutoField PK `documento_id`) + `PlantillaDocumento` (AutoField PK `plantilla_id`). VYNTIA renombró a `DigitalDocument` + `DocumentTemplate` con UUID PK = `id`. Tabla `documentos_digitales` y `app_rrhh_plantilla_documento` preservadas. **El renombre dejó múltiples consumidores stale referenciando `documento_id` / `plantilla_id` / `empleado_id` / `contrato_id` que ya no existen** — se documenta sistemáticamente en bugs.

> **Contexto C.3 (Multi-tenancy):** Migration `0003_digitaldocument_tenant_documenttemplate_tenant.py` (2026-05-09) añadió tenant FK nullable a ambos modelos. Ningún ViewSet asigna ni filtra tenant — confianza 100% en RLS+middleware (patrón cross-app).

#### Modelos
- `DigitalDocument` (file: `apps/api/apps/documents/models/digital_document.py:25`) — documento digital del legajo del empleado. Renombre L3.11: legacy `DocumentosDigitales` → `DigitalDocument`. PK `id` UUID. Tabla legacy `documentos_digitales` preservada (line 218).
  - **Choices** (líneas 28-106): `TIPO_DOCUMENTO_CHOICES` (32 valores: dni, pasaporte, certificados varios, contratos, adendas, boletas, constancias, resoluciones, cartas, evaluaciones, otros), `CATEGORIA_CHOICES` (11: personal, academico, laboral, medico, legal, administrativo, capacitacion, evaluacion, remuneraciones, ubicacion, otros), `ESTADO_DOCUMENTO_CHOICES` (7: activo/inactivo/vencido/pendiente_revision/aprobado/rechazado/archivado), `NIVEL_ACCESO_CHOICES` (4: publico/restringido/confidencial/muy_confidencial), `FORMATO_ARCHIVO_CHOICES` (11: pdf/jpg/jpeg/png/doc/docx/xls/xlsx/txt/zip/rar).
  - **Relaciones**: `empleado` FK→`employees.Employee` (CASCADE, related_name `documentos_digitales`), `validado_por` FK→`identity.User` (SET_NULL), `digitalizado_por` FK→`identity.User` (SET_NULL), `subido_por` FK→`identity.User` (SET_NULL), `documento_padre` FK→self (CASCADE, related_name `versiones`), `familiar` FK→`employees.FamilyMember` (SET_NULL).
  - **Identidad/contenido**: `tipo_documento`, `categoria`, `nombre_documento` (CharField max=200), `descripcion` (TextField nullable).
  - **Archivo**: `archivo` FileField con `upload_to='documentos_empleados/%Y/%m/'` y `FileExtensionValidator` (11 ext.); `nombre_archivo_original`, `formato_archivo`, `tamano_archivo` (BigIntegerField, en bytes). Función legacy `documento_upload_path` preservada (líneas 19-22) por compat con migraciones históricas.
  - **Metadatos**: `numero_documento` (nullable), `fecha_emision`, `fecha_vencimiento`, `entidad_emisora`.
  - **Acceso/seguridad**: `nivel_acceso` (default `restringido`), `requiere_autorizacion`, `es_documento_oficial`, `es_copia_certificada`, `es_confidencial`, `requiere_firma_digital`.
  - **Versioning**: `version` (CharField default `1.0`), `documento_padre` (self FK), `es_version_actual` (default True).
  - **Estado/validación**: `estado_documento` (default `activo`), `validado_por`, `fecha_validacion`, `observaciones_validacion`.
  - **Digitalización**: `digitalizado_por`, `fecha_digitalizacion` (auto_now_add), `calidad_digitalizacion` (alta/media/baja).
  - **Audit**: `fecha_subida` (auto_now_add), `updated_at` (auto_now, db_column `fecha_actualizacion`), `subido_por`.
  - **Búsqueda**: `palabras_clave` (CharField max=500, CSV), `notas_internas`.
  - Tenant FK: ✅ (líneas 110-117, nullable=true). NO hay composite unique constraint con tenant — `unique_together = [['empleado', 'tipo_documento', 'numero_documento', 'version']]` (line 233) — suficiente porque `empleado` ya está taggeado vía employees.
  - Manager: default. `DocumentosDigitalesManager` comentado (línea 16, 215 — igual al legacy).
  - **Properties calculadas (16)**: `tipo_documento_texto`, `categoria_texto`, `estado_texto`, `nivel_acceso_texto`, `tamano_archivo_legible`, `extension_archivo`, `esta_vencido`, `dias_para_vencimiento`, `proximo_a_vencer` (30 días), `es_imagen`, `es_pdf`, `es_documento_office`, `url_descarga`, `informacion_validacion`, `informacion_version`, `requiere_atencion`, `nivel_seguridad` (Alto/Medio/Bajo).
  - **Métodos instancia**: `validar_documento(usuario, observaciones)`, `rechazar_documento(usuario, motivo)`, `crear_nueva_version(archivo, usuario, descripcion_cambios)`, `_generar_nueva_version()` (incrementa float +0.1), `marcar_como_vencido()`, `renovar_documento(nueva_fecha, archivo)`, `archivar_documento(motivo)`, `cambiar_nivel_acceso(nuevo_nivel, usuario, justificacion)`, `agregar_palabras_clave(palabras)`. **Bug L3.11**: `informacion_version` accede `self.documento_padre.id` (línea 337) — antes era `documento_padre.documento_id`; aquí está bien porque ahora es UUID.
  - **Class methods (queries)**: `por_tipo_documento`, `documentos_vencidos`, `proximos_a_vencer(dias=30)`, `pendientes_validacion`, `por_categoria`, `buscar_por_palabras_clave`, `documentos_confidenciales`, `estadisticas_por_tipo` (Count('id') — correcto), `documentos_por_empleado`. **Ninguno filtra tenant** — leak cross-tenant si se invoca desde shell.
  - `save()` override: hidrata `tamano_archivo`, `nombre_archivo_original`, `formato_archivo` desde el FileField si están vacíos (líneas 567-577).

- `DocumentTemplate` (file: `apps/api/apps/documents/models/document_template.py:11`) — plantilla Word (.docx) reutilizable para generación de documentos. Renombre L3.11: legacy `PlantillaDocumento` → `DocumentTemplate`. PK `id` UUID. Tabla legacy `app_rrhh_plantilla_documento` preservada (line 59).
  - **Choices**: `TIPO_CHOICES` (4: certificado_trabajo, constancia_laboral, contrato, adenda).
  - **Campos**: `tipo`, `nombre` (max=200), `descripcion` (TextField default ''), `archivo` (FileField `upload_to='plantillas_word/%Y/'`), `activa` (default True).
  - **Audit**: `created_at` (auto_now_add, db_column `fecha_creacion`), `created_by` FK→`identity.User` (SET_NULL, related_name `plantillas_creadas`, db_column `creada_por_id`).
  - Tenant FK: ✅ (líneas 28-35, nullable=true). **NO hay constraint per-tenant** sobre `(tenant, tipo, nombre)` — dos tenants pueden tener plantillas con nombre idéntico, lo cual es OK; pero **NO hay defense-in-depth** para que un user de tenant_b vea las plantillas de tenant_a si el ViewSet no filtra (cosa que no hace, ver bugs).
  - **Property `variables_disponibles`** (líneas 67-93): retorna lista de marcadores `{{...}}` según el tipo. Base 12 variables comunes (NOMBRE_EMPLEADO, APELLIDOS, DNI, CARGO, etc.) + extras según tipo (NUMERO_CERTIFICADO/PROPOSITO/SALARIO_BRUTO para cert/constancia; NUMERO_CONTRATO/TIPO_CONTRATO/SALARIO_NETO/JORNADA para contrato; idem + NUMERO_ADENDA para adenda).

#### Servicios (3 + management commands)
- `apps/documents/services/template_service.py` — `TemplateService` (HTML rendering desde Django templates).
  - **Mappings declarados** (líneas 31-49): `PLANTILLAS_CONTRATO` (7 entradas mapean `Contract.tipo_documento` → archivo HTML; CAS_* → `contratos/contrato_cas.html`, LEY_728_* → `contratos/contrato_728.html`, LEY_276_INDETERMINADO → `contratos/contrato_276.html`); `PLANTILLAS_ADENDA` (4 → todos a `adendas/adenda_base.html`); `PLANTILLAS_CERTIFICADO` (2: CONSTANCIA → `certificados/constancia_laboral.html`, CERTIFICADO → `certificados/certificado_trabajo.html`).
  - **Métodos**: `generar_contrato(contrato_id, tipo_plantilla)` (renderiza HTML), `generar_adenda(adenda_id, tipo_adenda)`, `generar_certificado(empleado_id, tipo_certificado, datos_adicionales)` (auto-detect: empleado `activo` → CONSTANCIA, cesado → CERTIFICADO line 178-181), `_preparar_contexto_contrato/_empleado/_obtener_datos_institucion`, `validar_plantilla`, `listar_plantillas_disponibles`/`obtener_plantillas_disponibles`, `generar_reporte_html(reporte_data)`, `_generar_reporte_html_fallback`.
  - **`_obtener_datos_institucion`**: invoca `Company.get_config(tenant=None)` con TODO inline (line 324: "TODO(C.3): pass tenant from service caller once middleware ships"). **Bug C-multitenancy P1** — todos los documentos generados rinden los datos de la institución del tenant `None` (default seed) en lugar del tenant del request.
  - **Bug L3.10.3 stale**: línea 216 `'numero_adenda': getattr(contrato, 'numero_adenda', None)` — `Contract` post-split NO tiene `numero_adenda` (vive en `ContractAmendment`). Siempre `None` para contratos. Ya documentado en Task 5 contracts.
  - **Bug**: línea 254 `contrato.created_by.nombre_completo if contrato.creado_por_id else ...` — el field es `created_by` (English), pero la condición chequea `creado_por_id`. Si `creado_por_id` es el db_column legacy, el atributo es `created_by_id` en Django. Atributo NO existe → `AttributeError` → cualquier render de contrato lanza excepción.
  - **Bug**: línea 230 `contrato.get_estado_display()` — el field es `status` con `db_column='estado'`. El método auto-generado por choices es `get_status_display`. **`get_estado_display` no existe** → AttributeError. Igual patrón en `_generar_reporte_html_fallback` línea 439.
  - **Bug**: línea 433 `c.numero_contrato or c.contrato_id` — `Contract` post-rename tiene `id` UUID, no `contrato_id`. AttributeError.

- `apps/documents/services/pdf_generator.py` — `PDFGenerator` (HTML→PDF).
  - **Cadena de motores PDF** (líneas 24-45, 213-239): xhtml2pdf → WeasyPrint → ReportLab. Disponibilidad detectada via try/except import. `_html_to_pdf` itera en ese orden y avisa al log cuando cae a ReportLab ("Usando stub ReportLab — el PDF NO contendrá contenido real" line 234-237). Por CLAUDE.md, **sólo ReportLab funciona reliably en Windows**, lo que significa que en dev local todos los PDFs son stubs ("DOCUMENTO GENERADO. Contenido del documento generado desde plantilla.").
  - **Funciones de limpieza**: `_strip_unsupported_css` elimina `@page { ... counter() ... }` (xhtml2pdf no soporta counters) — fix histórico para Windows.
  - **Métodos**: `generar_pdf_contrato(contrato_id, tipo_plantilla, guardar_automatico)`, `generar_pdf_adenda(contrato_id, tipo_adenda, guardar_automatico)`, `generar_pdf_certificado(empleado_id, tipo_certificado, datos_adicionales, guardar_automatico)`, `generar_reporte_pdf(reporte_data, guardar_en_bd, usuario_creador)`. Todos guardan opcionalmente en `DigitalDocument` (líneas 461-505).
  - **`obtener_configuracion_disponible`** retorna info de capacidades (motor disponible + plantillas).
  - **Bug**: `generar_pdf_adenda` recibe `contrato_id` pero invoca `template_service.generar_adenda(contrato_id, tipo_adenda)`; `template_service.generar_adenda` realmente espera **adenda_id** (UUID de `ContractAmendment`). El renombre L3.10.3 (split Contract/Amendment) rompió la signature, pero `pdf_generator.generar_pdf_adenda` no se actualizó.
  - **Bug L3.11**: `_guardar_documento_digital` crea `DigitalDocument` SIN tenant — invocado desde la cadena de generación cualquier PDF generado quedará con `tenant=NULL` (orphan). Afecta `generar_pdf_contrato/adenda/certificado/reporte` todos.

- `apps/documents/services/word_template_service.py` — `WordTemplateService` (replace `{{VAR}}` en .docx).
  - Usa `python-docx`. Métodos: `generar_desde_plantilla(plantilla, variables)`, `_reemplazar_en_documento`, `_reemplazar_en_parrafo` (combina runs y restaura formato del primer run), `construir_variables_empleado(empleado, datos_adicionales)`, `construir_variables_contrato(contrato)`, `construir_variables_certificado(empleado, tipo, numero_certificado, proposito, incluir_salario)`, `_format_date` (formato "DD de mes de YYYY"), `pdf_desde_docx(docx_bytes)` (usa `docx2pdf` que requiere Word instalado en Windows; retorna None si falla).
  - **Bug crítico L3.10.3** (línea 139): `'NUMERO_ADENDA': contrato.numero_adenda or ''` — Contract post-split no tiene `numero_adenda` → AttributeError. **Cualquier flujo de generación Word de contrato falla**. Ya documentado en Task 5.
  - **Bug L3.10.3** (línea 175): filtra `Contract.objects.filter(empleado=empleado, estado='ACTIVO')` — el field es `status`, no `estado`. FieldError. Afecta a `construir_variables_certificado(incluir_salario=True)`.
  - **Bug**: `EMPRESA_NOMBRE`, `EMPRESA_RUC`, `EMPRESA_DIRECCION`, `CIUDAD` están **hardcoded** (líneas 119-123): `'Lima'`, `'Institución Pública'`, `'20123456789'`, `'Av. Principal 123, Lima, Perú'`. **No leen `Company.get_config(tenant=...)`** como sí lo hace `TemplateService._obtener_datos_institucion` (con su propio bug). Cualquier documento Word generado tendrá data institucional falsa.
  - **`pdf_desde_docx` requiere Word instalado (docx2pdf)** — en producción Linux/Docker fallará silenciosamente devolviendo None y el ViewSet hace fallback a .docx (líneas 712-716 del view).

- Management command: `seed_plantillas_default.py` — genera .docx defaults para los 4 tipos de plantilla y los registra en `DocumentTemplate` si no existen. Acepta `--force` para recrear. **Sin scope de tenant** — siembra plantillas con `tenant=NULL` (globales).

#### Endpoints REST
**Estructura URL inusual:** `apps/api/api/v1/documents/urls.py` registra `DocumentosDigitalesViewSet` en el router con prefix `documents` Y simultáneamente incluye `app_rrhh.document_generation_urls` montadas en `documents/`. El resultado es que **todas** las routes terminan bajo `/api/v1/documents/documents/...`. Conflicto potencial con el detail-route `<uuid>` del ViewSet. Ver Notas.

- `/api/v1/documents/documents/` — `DocumentosDigitalesViewSet` (file: `api/v1/rrhh/views.py:1983`). CRUD ModelViewSet completo.
  - `list` (GET): `@require_authenticated()` — non-HR users ven sólo sus documentos (filter `empleado=user.empleado` línea 2080).
  - `retrieve` (GET): `@require_authenticated()`.
  - `create` (POST): `@require_authenticated()`. Non-HR users solo pueden subir para su propio legajo (linea 2026-2031). `perform_create` (línea 2034): inyecta `subido_por`, `nombre_archivo_original`, `formato_archivo`, `tamano_archivo` desde el FileField; si non-HR, fuerza `estado_documento='pendiente_revision'`.
  - `update`/`partial_update`: `@require_hr()` (sólo RRHH puede editar).
  - `destroy`: `@require_admin()` (sólo admin puede eliminar — hard delete, sin soft-delete).
  - **Custom actions**:
    - `por_tipo` (GET, list, RRHH): filtra por `tipo_documento` query param — devuelve lista paginada.
    - `boletas_pago` (GET, list, `@require_permissions(["ver_boletas_pago"])`): filtra `tipo_documento='boleta_pago'` — replaces old `Boleta` model endpoint.
    - `proximos_vencer` (GET, list, RRHH): filtra `fecha_vencimiento__lte=today+30d` and gte today, `estado='activo'`. Acepta `?dias=N`.
    - `validar` (POST, detail, RRHH): invoca `documento.validar_documento(user, observaciones)` — marca como `aprobado`.
    - `rechazar` (POST, detail, RRHH): invoca `documento.rechazar_documento(user, motivo)` — exige `motivo`.
    - `subir_institucional` (POST, list, RRHH): subida múltiple de archivos institucionales (boletas, constancias, resoluciones, etc.). Acepta `archivos[]` o `archivo` único. Auto-asigna categoría según `TIPO_CATEGORIA_MAP` interno (líneas 2247-2262, duplicado con frontend `legajoService.TIPO_CATEGORIA_MAP`).
  - Filtros (`get_queryset` 2072-2138): `empleado`, `tipo_documento`, `categoria`, `estado`, `activos` (boolean), `origen` (institucional/personal — usa lista hardcoded `TIPOS_INSTITUCIONALES`), `es_version_actual` (true/false). Implementación manual (no `DjangoFilterBackend filterset`).
  - **Permission class**: `DocumentosDigitalesPermission` (custom, no analizada en detalle aquí). Decoradores por método.
  - Pagination: `StandardResultsSetPagination` (20/page).

- `/api/v1/documents/documents/<action>/` — `DocumentGenerationViewSet` (file: `api/v1/app_rrhh/document_generation_views.py:50`). NO es ModelViewSet — `ViewSet` plain con acciones POST/GET.
  - `permission_classes = [IsAuthenticated, IsHRUser]` + decoradores `@require_hr` por acción.
  - **Excluido del schema OpenAPI** (`@extend_schema(exclude=True)` línea 49) — porque genera PDFs sin serializer estándar.
  - Custom actions:
    - `generar_contrato` (POST): genera HTML/PDF de un contrato. Acepta `id` (contrato), `formato` (html/pdf), `guardar_documento`, `plantilla`. **3 BUGS L3.11**: (1) línea 110 `get_object_or_404(Contract, contrato_id=contrato_id)` — Contract no tiene `contrato_id`; debería ser `pk=contrato_id` o `id=contrato_id`. **Endpoint roto al 100%**: lanza FieldError. (2) línea 148 `documento.documento_id` — `DigitalDocument` ya no tiene `documento_id`; es `id`. AttributeError. (3) línea 144 `contrato.documento_generado = True` + save update_fields — funciona (campo BooleanField existe).
    - `generar_adenda` (POST): genera HTML/PDF de una adenda. Acepta `adenda_id`, `formato`, `guardar_documento`. **2 BUGS L3.11**: (1) línea 211 `get_object_or_404(ContractAmendment, pk=adenda_id)` — OK (usa pk). (2) línea 245 `documento.documento_id` — broken. Endpoint **medio-roto** (responde data con None en `id` cuando guarda).
    - `generar_certificado` (POST): genera HTML/PDF de certificado/constancia. Acepta `id` (empleado), `tipo_certificado`, `proposito`, `incluir_salario/prestaciones`, `observaciones`, `formato`, `guardar_documento`. **2 BUGS L3.11**: (1) línea 318 `get_object_or_404(Employee, empleado_id=empleado_id)` — Employee no tiene `empleado_id`; **endpoint roto al 100%**. (2) línea 367 `documento.documento_id` — broken.
    - `generar_reporte` (POST): genera reporte de contratos. Acepta filtros (fecha_inicio/fin, area, tipo_contrato, estado, agrupar_por_area, etc.). Invoca `pdf_generator.generar_reporte_pdf` con transaction.atomic. Bug menor línea 474 `documento.documento_id` — broken.
    - `plantillas_disponibles` (GET): retorna `{contratos:[...], adendas:[...], certificados:[...]}` desde `TemplateService.obtener_plantillas_disponibles`.
    - `listar_plantillas_word` (GET, `?tipo=`): lista DocumentTemplates activos. **Bug L3.11**: línea 543 `"id": p.plantilla_id` — DocumentTemplate ya no tiene `plantilla_id`; AttributeError. **Endpoint roto al 100%**.
    - `subir_plantilla_word` (POST, RRHH): valida `archivo`, `nombre`, `tipo` (debe estar en TIPO_CHOICES), `descripcion`. Crea `DocumentTemplate(creada_por=request.user, ...)`. **Bug L3.11**: línea 595 usa `creada_por=request.user` — el field renombrado es `created_by` (con db_column `creada_por_id`). **TypeError: unexpected keyword argument 'creada_por'**. Endpoint **roto al 100%**. (2) línea 600 `plantilla.plantilla_id` — broken.
    - `eliminar_plantilla_word` (DELETE, RRHH): URL pattern `plantillas-word/(?P<plantilla_id>[0-9]+)/eliminar` — **regex `[0-9]+` ya no matchea UUIDs**. Cualquier intento de eliminar lanza 404. Soft-delete (`activa=False`).
    - `descargar_plantilla_word` (GET): mismo bug regex `[0-9]+`. + `plantilla.plantilla_id` AttributeError línea 639.
    - `generar_desde_plantilla_word` (POST, RRHH): MASTER bug — líneas 666-668 leen los TRES IDs (`plantilla_id`, `empleado_id`, `contrato_id`) del **mismo query param** `request.data.get("id")`. Copy-paste catastrófico. **Endpoint funcionalmente roto**: el cliente debe enviar la misma key 3 veces para los 3 tipos distintos. Adicionalmente: `get_object_or_404(DocumentTemplate, plantilla_id=...)` (línea 675) y `get_object_or_404(Employee, empleado_id=...)` (línea 681) y `get_object_or_404(Contract, contrato_id=...)` (línea 695) — los tres campos NO existen post-rename L3.11.

#### UI (frontend)
- `apps/web/src/features/documents/` (post-L4.7).
  - **Pages (3)**:
    - `LegajoPage.tsx` (~530 líneas, basado en `wc -l`): vista del legajo del empleado. Lista documentos con filtros, modal de subida, validar/rechazar.
    - `GestionDocumentosPage.tsx`: gestor RRHH para subida masiva institucional (boletas, resoluciones, etc.). Usa `legajoService.subirInstitucional`.
    - `PlantillasDocumentosPage.tsx`: gestor de plantillas Word (.docx). Lista, sube, descarga, elimina. **Backend roto** (ver bugs arriba: `plantilla_id` AttributeError + regex `[0-9]+` en URL no matchea UUID).
  - **Services (2)**: `legajoService` (líneas ~310 — CRUD `/api/v1/documents/documents/`, validar, rechazar, subir_institucional), `templatesService` (líneas ~143 — CRUD plantillas-word, subir/descargar/eliminar/generar-desde-plantilla-word).
  - **Phantom field**: `legajoService.Documento.numero_referencia` (líneas 21, 45) — el modelo `DigitalDocument` NO tiene ese campo. Si el form lo enviara, DRF lo ignoraría silenciosamente.
  - **Cross-app dependency**: `contractsService` (Task 5) invoca `/api/v1/documents/documents/generar-certificado/`, `generar-contrato/`, `generar-adenda/` — **TODOS rotos por los bugs documentados arriba**. Sin frontend de adendas (Task 5), sin frontend de generar reporte.
  - **Lint warnings (5)**: `GestionDocumentosPage.tsx` (líneas 20-21: `TIPO_DOCUMENTO_LABELS`/`CATEGORIA_LABELS` import sin uso), `LegajoPage.tsx` (línea 503: `EmpleadoRow` interface sin uso; línea 542: `any`), `PlantillasDocumentosPage.tsx` (línea 8: `Badge` import sin uso). 0 errores tsc.

#### Templates (`apps/api/templates/`)
**5 directorios + 17 archivos HTML** (verificado vía Glob 2026-05-09):

| Directorio | Archivos | Generado por |
|---|---|---|
| `contratos/` | `contrato_base.html`, `contrato_fijo.html`, `contrato_cas.html`, `contrato_728.html`, `contrato_276.html` (5) | `TemplateService.generar_contrato` con `PLANTILLAS_CONTRATO` map. `contrato_fijo.html` NO está mapeado (huérfano). `contrato_base.html` es fallback. |
| `adendas/` | `adenda_base.html` (1) | `TemplateService.generar_adenda` con `PLANTILLAS_ADENDA` map (4 tipos → mismo archivo base; lógica por tipo dentro del template). |
| `certificados/` | `certificado_laboral.html`, `certificado_trabajo.html`, `constancia_laboral.html` (3) | `TemplateService.generar_certificado`. `certificado_laboral.html` NO está mapeado en `PLANTILLAS_CERTIFICADO` (huérfano legacy). |
| `reportes/` | `reporte_contratos.html`, `reporte_empleado.html`, `reporte_vacaciones_empleado.html` (3) | `reporte_contratos.html` invocado por `template_service.generar_reporte_html`. `reporte_empleado.html` invocado por `apps.employees.services.employee_report_service` (Task 4). `reporte_vacaciones_empleado.html` invocado por `apps.time_off.services` (Task 7+). |
| `emails/` | `bienvenida.html`, `documento_rechazado.html`, `onboarding_aprobado.html`, `onboarding_observado.html`, `vacaciones_solicitud.html` (5) | Emails enviados por `apps.core.tasks.send_email_html_task` desde diversos servicios: identity (`bienvenida`), documents (`documento_rechazado`), onboarding (`onboarding_*`), time_off (`vacaciones_solicitud`). |

**Templates huérfanos (no mapeados a ningún tipo):** `contratos/contrato_fijo.html`, `certificados/certificado_laboral.html`. **Sin documentar** si son legacy stale o reservados para uso futuro. Bug deuda P3.

**Plantillas Word (.docx)**: NO viven en el repo. Se generan/cargan en `media/plantillas_word/%Y/` por `seed_plantillas_default` o por usuario via `subir_plantilla_word`. `DocumentTemplate.archivo` apunta al storage.

#### Tests
- `apps/api/tests/test_documentos_model.py` — 6 tests `TestTamanoArchivoLegible`. **6/6 PASAN** (verificado 2026-05-09). Cubre la property `tamano_archivo_legible` (B/KB/MB/GB, idempotente, cero, no muta).
- `apps/api/tests/test_documentos_digitales_onboarding.py` — 4 tests `TestDocumentosDigitalesOnboardingEmployee`. **4/4 PASAN**. Cubre: empleado puede listar sus propios docs, response incluye `archivo_url`, empleado NO ve docs de otro empleado (aislación non-HR), filtro `es_version_actual`.
- ❌ NO existe `apps/documents/tests/` (in-app tests).
- ❌ NO hay tests para tenant isolation de DigitalDocument/DocumentTemplate.
- ❌ NO hay tests para PDFGenerator (cadena xhtml2pdf/WeasyPrint/ReportLab).
- ❌ NO hay tests para WordTemplateService (replace de `{{VAR}}` en .docx).
- ❌ NO hay tests para `DocumentGenerationViewSet` (ningún endpoint de generar-contrato/adenda/certificado/reporte/desde-plantilla-word). Por eso los **9+ bugs L3.11 declarados arriba pasan invisibles a CI**.
- ❌ NO hay tests para `subir_institucional`, `validar`, `rechazar` actions del DocumentosDigitalesViewSet.
- ❌ NO hay tests para versioning (`crear_nueva_version`, `_generar_nueva_version`, `es_version_actual`).
- ❌ NO hay tests para alertas de vencimiento (`proximos_vencer`, `marcar_como_vencido`, cron task).

### Gaps vs INTRANET legacy

VYNTIA documents es **paritario campo-por-campo absoluto** con el legacy en ambos modelos. Sin pérdida funcional vs legacy. Plantillas HTML/email son idénticas (17 templates legacy = 17 templates VYNTIA, sin diferencias en nombres o ubicación).

| Feature legacy | Ubicación legacy | Estado en VYNTIA | Tipo | Prioridad propuesta | Nota |
|---|---|---|:---:|:---:|---|
| Modelo `DocumentosDigitales` (AutoField PK `documento_id`) | `D:/INTRANET/back/app_rrhh/models/documentos_digitales.py:23` | Migrado a `DigitalDocument` con UUID `id`, paridad campo-por-campo absoluta. Tabla `documentos_digitales` preservada. | done | — | Sin pérdida funcional. **Cambio breaking**: `documento_id` → `id` rompe consumers (ver bugs). |
| Modelo `PlantillaDocumento` (AutoField PK `plantilla_id`) | `D:/INTRANET/back/app_rrhh/models/plantilla_documento.py:9` | Migrado a `DocumentTemplate` con UUID `id`. Tabla `app_rrhh_plantilla_documento` preservada. db_columns legacy: `fecha_creacion`, `creada_por_id`. | done | — | Sin pérdida funcional. Cambio breaking igual. |
| Audit `fecha_actualizacion` field name | `documentos_digitales.py:189` | Renombrado a `updated_at` con `db_column='fecha_actualizacion'`. | done | — | Compat con datos importados. |
| Audit `fecha_creacion` field name (PlantillaDocumento) | `plantilla_documento.py:38` | Renombrado a `created_at` con `db_column='fecha_creacion'`. | done | — | Compat. |
| Audit `creada_por` FK (PlantillaDocumento) | `plantilla_documento.py:39-45` | Renombrado a `created_by` con `db_column='creada_por_id'`. **Pero el ViewSet aún usa kwarg `creada_por`** (ver bugs). | partial | P1 | Bug L3.11. |
| FK a `Empleado`/`Usuario`/`DatosFamiliares` (legacy strings) | `documentos_digitales.py:108-110, 152-156, 162-166, 173-177, 190-194` | Actualizadas a `'employees.Employee'`, `'identity.User'`, `'employees.FamilyMember'`. | done | — | Lazy strings preservadas para evitar import circular. |
| Manager `DocumentosDigitalesManager` | `D:/INTRANET/back/app_rrhh/managers.py` | Comentado en VYNTIA (igual que legacy). | partial | P3 | Implementar o eliminar. |
| 17 templates HTML (contratos, adendas, certificados, reportes, emails) | `D:/INTRANET/back/templates/**/*.html` | **Migración byte-by-byte completa**: idénticos archivos en `D:/VYNTIA/apps/api/templates/`. | done | — | Sin diff entre legacy y VYNTIA. |
| Plantillas Word `.docx` defaults | Sin equivalente en repo legacy | `apps/documents/management/commands/seed_plantillas_default.py` regenera 4 defaults via python-docx. | done | — | Mejora vs legacy. |

**Sin gaps funcionales**: el split L3.11 es renombre puro. Los bugs declarados en este chapter NO son regresiones funcionales del legacy — son artefactos del rename incompleto (consumers stale).

### Gaps vs maestro

El maestro § 3 Módulo **03.5 (Legajos digitales)** define un dossier digital completo con índice, búsqueda full-text, retention policy, version history, document categories, signing workflows, e-firma. **Esta sección audita SOLO la entidad DigitalDocument + DocumentTemplate**. Los flujos completos de "Legajos digitales" (search index, retention, e-firma, audit trail completo) son scope de **Task 11 (Module 03 gaps)**.

| Capability del maestro (§ 03.5 / DigitalDocument entity) | Estado en VYNTIA | Prioridad |
|---|---|:---:|
| Almacenamiento file FK por empleado | ✅ `DigitalDocument.empleado` FK + `archivo` FileField. | — |
| Tipo y categoría de documento (taxonomía) | ✅ 32 tipos + 11 categorías. Más rica que típica taxonomía SaaS. Adecuada al sector público peruano. | — |
| Versioning (versión actual + historial) | ✅ `version`, `documento_padre` self-FK, `es_version_actual`, `crear_nueva_version()`. | — |
| Estados de validación (workflow aprobado/rechazado/pendiente_revision) | ✅ `estado_documento` + `validar_documento`/`rechazar_documento`. | — |
| Niveles de acceso (público/restringido/confidencial/muy_confidencial) | ✅ `nivel_acceso` con 4 niveles. **Pero**: NO se enforce en el ViewSet — `get_queryset` no filtra por nivel_acceso vs role del usuario. Un empleado puede listar docs `confidencial` propios pero sin gate cross-area. | P2 |
| Firma electrónica del documento | ❌ No implementado. `requiere_firma_digital` BooleanField existe (línea 212) pero sin servicio de firma. | P1 (sub-proyecto) |
| Búsqueda full-text por palabras clave | ⚠️ Parcial. `palabras_clave` CharField CSV + `buscar_por_palabras_clave` classmethod usan `icontains`. **NO hay índice full-text** (PostgreSQL `tsvector`). Performance se degrada >10k docs. | P2 |
| Vencimiento con alertas (cron) | ⚠️ Parcial. `fecha_vencimiento`, `proximos_vencer` action lista, pero **NO hay celery task que envíe email automático** ni que actualice `estado_documento='vencido'` automáticamente. `marcar_como_vencido()` requiere invocación manual. | P2 |
| Retention policy (eliminación automática post-N años) | ❌ No implementado. SUNAFIL exige conservar documentos laborales por ≥5 años post-cese; CAS exige 4. NO hay model field `fecha_eliminacion_programada` ni cron. | P1 (compliance) |
| Auditoría completa (quién accedió/descargó cuándo) | ❌ Sólo se registra `validado_por`/`subido_por`/`digitalizado_por`. **NO hay log de accesos/descargas** (DocumentAccessLog). Crítico para documentos confidenciales. | P1 (compliance + LPD Perú) |
| Encriptación at-rest para documentos `confidencial`/`muy_confidencial` | ❌ Archivos guardados en disk planos. Sin S3 SSE-KMS, sin pgcrypto. | P1 (LPD Perú) |
| Categoría taxonomy específica del maestro | ✅ La taxonomía VYNTIA ya cubre "personal/laboral/medico/legal/administrativo/capacitacion/evaluacion/remuneraciones/ubicacion/otros". | — |
| Document templates (.docx + .html) | ✅ `DocumentTemplate` (Word) + 17 HTML files. Variables interpoladas via `{{VAR}}` o Django `{{ var }}`. | — |
| OCR para PDFs/imágenes escaneadas | ❌ No implementado. Imágenes (`es_imagen`) y PDFs se almacenan sin texto extraído. | P3 |
| Generación PDF en producción | ❌ ReportLab stub no genera contenido real (cadena xhtml2pdf/WeasyPrint inestable en Windows). En Linux/Docker sí funciona pero tests no cubren. | P1 (Module 03 deployment) |
| Generación Word con datos institucionales correctos por tenant | ❌ `WordTemplateService.construir_variables_empleado` hardcodea EMPRESA_NOMBRE/RUC/DIRECCION (líneas 119-123). No lee `Company.get_config(tenant)`. | P1 (C-multitenancy) |
| Carga masiva (bulk upload) | ⚠️ Parcial. `subir_institucional` acepta `archivos[]` lista, pero sin progreso, sin retry, sin batch-size limit. Para boletas mensuales (250+ archivos) timeoutea. | P2 |
| Compresión / thumbnails | ❌ No implementado. Imágenes >5MB se almacenan tal cual. Sin lazy-load thumbnails en `LegajoPage`. | P3 |
| Categorías por sub-proceso (vinculación, formación, evaluación, desvinculación, etc.) | ⚠️ Parcial. La taxonomía existe (32 tipos) pero NO está agrupada por proceso del maestro § 03 (Vinculación → cert_estudios + contrato + RIT, Desvinculación → carta_cese + liquidacion). Pendiente de UI grouping. | P3 |
| `DigitalDocument.contrato` FK directo (relación contract↔documento) | ❌ No existe. La relación es indirecta: `Contract.documento_generado` BooleanField (sólo flag). Para encontrar el PDF del contrato hay que filtrar `DigitalDocument.empleado=contrato.empleado, tipo='contrato_trabajo', fecha_subida` cercana — frágil. Asimétrico con `ContractAmendment.documento_generado` que SÍ es FileField. | P2 |

### Bugs y deuda técnica conocidos

Pytest documents: 10/10 PASAN (4 onboarding + 6 modelo). PERO: cobertura limitada a 1 modelo property + 4 endpoints; los 25+ bugs declarados están latentes.

| Bug | Ubicación | Causa | Tipo | Prioridad |
|---|---|---|:---:|:---:|
| `DocumentGenerationViewSet.generar_contrato` invoca `Contract` lookup con kwarg `contrato_id=...` | `api/v1/app_rrhh/document_generation_views.py:110` | Rename L3.11 incompleto. Contract ya no tiene `contrato_id` (es `id` UUID). **Endpoint `POST /generar-contrato/` roto al 100% — lanza FieldError**. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.generar_contrato` lee `contrato_id = request.data.get("id")` | `document_generation_views.py:98` | El cliente envía `id` del contrato, pero el field name es engañoso (debería ser `contrato_id` o `contract_id`). Frontend `contractsService.generarContratoPdf` confirma usa `id`. Funcional, pero confuso. | ⚠️ deuda API contract | P3 |
| `DocumentGenerationViewSet.generar_contrato` accede `documento.documento_id` línea 148 | `document_generation_views.py:148` | DigitalDocument tras renombre L3.11 tiene `id` UUID. AttributeError → lanza 500 al guardar. **Endpoint roto al 100%**. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.generar_adenda` accede `documento.documento_id` línea 245 | `document_generation_views.py:245` | Idem. Endpoint serializa con AttributeError. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.generar_certificado` invoca `Employee` lookup con kwarg `empleado_id=...` | `document_generation_views.py:318` | Rename L3.11 incompleto. Employee ya no tiene `empleado_id`. **Endpoint roto al 100%**. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.generar_certificado` accede `documento.documento_id` línea 367 | `document_generation_views.py:367` | Idem. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.generar_reporte` accede `documento.documento_id` línea 474 | `document_generation_views.py:474` | Idem. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.listar_plantillas_word` accede `p.plantilla_id` línea 543 | `document_generation_views.py:543` | DocumentTemplate post-rename tiene `id` UUID. AttributeError. **Endpoint roto al 100%**. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.subir_plantilla_word` crea con `creada_por=request.user` línea 595 | `document_generation_views.py:595` | El field renombrado es `created_by`. **TypeError: unexpected keyword argument 'creada_por'**. **Endpoint roto al 100%**. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.subir_plantilla_word` accede `plantilla.plantilla_id` línea 600 | `document_generation_views.py:600` | AttributeError. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.eliminar_plantilla_word` URL pattern `[0-9]+` | `document_generation_views.py:616` | Regex sólo matchea integers. UUIDs nunca matchean. **Endpoint inalcanzable** — siempre 404. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.descargar_plantilla_word` URL pattern `[0-9]+` + `plantilla_id` kwarg | `document_generation_views.py:631-639` | Idem regex. + `plantilla.plantilla_id` AttributeError línea 639. **Endpoint inalcanzable**. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.generar_desde_plantilla_word` lee TRES IDs del MISMO query param `'id'` | `document_generation_views.py:666-668` | Copy-paste bug: `plantilla_id = request.data.get("id")`, `empleado_id = request.data.get("id")`, `contrato_id = request.data.get("id")`. **Funcionalmente roto** — el cliente debe enviar UN único valor "id" interpretable como cualquiera de los 3. + lookups `plantilla_id=...`/`empleado_id=...`/`contrato_id=...` (líneas 675, 681, 695) usan campos legacy. **Endpoint roto al 100%**. | 🐛 bug crítico L3.11 | P1 |
| `DocumentGenerationViewSet.generar_desde_plantilla_word` accede `documento.documento_id` línea 740 | `document_generation_views.py:740` | AttributeError. | 🐛 bug crítico L3.11 | P1 |
| `template_service.py:216` accede `getattr(contrato, 'numero_adenda', None)` | `apps/documents/services/template_service.py:216` | Bug L3.10.3 stale (split Contract/Amendment). Contract no tiene `numero_adenda`. Silencioso pero stale — ya documentado en Task 5 contracts. | 🐛 bug L3.10.3 | P1 |
| `template_service.py:230` invoca `contrato.get_estado_display()` | `apps/documents/services/template_service.py:230` | El campo es `status` con `db_column='estado'`. Django auto-genera `get_status_display`, NO `get_estado_display`. **AttributeError** en cualquier render de contrato. | 🐛 bug crítico | P1 |
| `template_service.py:254` chequea `if contrato.creado_por_id else ...` | `apps/documents/services/template_service.py:254` | El field es `created_by` con db_column `creado_por_id`. El atributo Python es `created_by_id`, NO `creado_por_id`. **AttributeError** en render de contratos. | 🐛 bug crítico | P1 |
| `template_service.py:433` invoca `c.numero_contrato or c.contrato_id` | `apps/documents/services/template_service.py:433` | Contract post-rename tiene `id` UUID. **AttributeError** en `_generar_reporte_html_fallback` cuando `numero_contrato` es vacío. | 🐛 bug L3.11 | P1 |
| `template_service.py:439` invoca `c.get_estado_display()` | `apps/documents/services/template_service.py:439` | Mismo bug status/estado. AttributeError. | 🐛 bug crítico | P1 |
| `template_service._obtener_datos_institucion` invoca `Company.get_config(tenant=None)` | `apps/documents/services/template_service.py:324` | TODO inline ack. Todos los documentos generados rinden datos del tenant `None` (default seed) en lugar del tenant del request. **Bug seguridad C-multitenancy**: si tenant_a y tenant_b comparten instancia, se cruzan datos institucionales. | 🐛 bug C-multitenancy | P1 |
| `word_template_service.py:139` accede `contrato.numero_adenda` directo | `apps/documents/services/word_template_service.py:139` | Bug L3.10.3 stale. AttributeError crítico — ya documentado en Task 5. | 🐛 bug crítico L3.10.3 | P1 |
| `word_template_service.py:175` filtra `Contract.objects.filter(estado='ACTIVO')` | `apps/documents/services/word_template_service.py:175` | Field es `status`. FieldError en `construir_variables_certificado(incluir_salario=True)`. | 🐛 bug L3.10.3 | P1 |
| `word_template_service.py:119-123` hardcodea `EMPRESA_NOMBRE`, `EMPRESA_RUC`, `EMPRESA_DIRECCION`, `CIUDAD` | `apps/documents/services/word_template_service.py:119-123` | NO consulta `Company.get_config(tenant)`. Cualquier .docx generado tiene "Institución Pública / 20123456789 / Av. Principal 123". **Asimetría con TemplateService** que sí (mal-)consulta `Company.get_config`. | 🐛 bug C-multitenancy | P1 |
| `pdf_generator.generar_pdf_adenda` invoca `template_service.generar_adenda(contrato_id, tipo_adenda)` | `apps/documents/services/pdf_generator.py:137-139` | Post-split L3.10.3, `template_service.generar_adenda` espera **adenda_id (UUID de ContractAmendment)**, no contrato_id. La signature se rompió pero pdf_generator no actualizó. **Documentos de adenda generan con datos del contrato padre, no de la adenda.** | 🐛 bug L3.10.3 | P1 |
| `pdf_generator._guardar_documento_digital` crea DigitalDocument SIN tenant | `apps/documents/services/pdf_generator.py:482-495` | No setea `tenant`. Cualquier PDF generado queda con `tenant=NULL` (orphan). Idéntico patrón cross-app. | 🐛 bug C-multitenancy | P1 |
| `DocumentosDigitalesViewSet.subir_institucional` crea DigitalDocument SIN tenant | `api/v1/rrhh/views.py:2285-2304` | No setea `tenant` en `DigitalDocument.objects.create(...)`. Documentos institucionales subidos quedan con tenant=NULL. | 🐛 bug C-multitenancy | P1 |
| `DocumentosDigitalesViewSet.perform_create` no asigna tenant | `views.py:2034-2049` | Patrón cross-app. ningun ViewSet de documents asigna tenant. | 🐛 bug C-multitenancy | P1 |
| `DocumentosDigitalesViewSet.get_queryset` no filtra por tenant | `views.py:2072-2138` | Confianza 100% en RLS+middleware. Sin defense-in-depth. | 🐛 bug C-multitenancy | P1 |
| `DocumentosDigitalesViewSet.get_queryset` filtra por `empleado=user.empleado` para non-HR | `views.py:2078-2082` | Implementación correcta, pero **NO chequea `nivel_acceso` vs role**: un empleado puede ver sus propios docs marcados `confidencial`/`muy_confidencial` sin restricción. La lógica del modelo (nivel_seguridad) no se aplica en queryset. | ⚠️ deuda lógica | P2 |
| Frontend `Documento.numero_referencia` field | `apps/web/src/features/documents/services/legajoService.ts:21, 45` | El modelo `DigitalDocument` NO tiene `numero_referencia`. Phantom field. Si form lo enviara, DRF lo ignoraría. | ⚠️ deuda tipos | P3 |
| Frontend lint (5 warnings) | `GestionDocumentosPage.tsx:20-21`, `LegajoPage.tsx:503,542`, `PlantillasDocumentosPage.tsx:8` | Imports unused + 1 `any`. Cleanup trivial. | ⚠️ deuda lint | P3 |
| URL conflict: `DocumentosDigitalesViewSet` registrado con prefix `documents` Y `app_rrhh.document_generation_urls` montado en `documents/` | `api/v1/documents/urls.py:11-16` | Ambos producen URLs bajo `/api/v1/documents/documents/`. El detail-route del ViewSet (`<uuid>/`) puede conflictuar con custom actions del DocumentGenerationViewSet (`generar-contrato/` etc.). DRF evita conflicto formal porque el ViewSet sólo expone `<uuid>` UUID-format y las acciones son strings, pero **el path naming es inusual** y dificulta legibilidad/seguridad. | ⚠️ deuda URL | P2 |
| Templates huérfanos `contratos/contrato_fijo.html` y `certificados/certificado_laboral.html` | `apps/api/templates/` | NO mapeados a ningún tipo en `PLANTILLAS_CONTRATO`/`PLANTILLAS_CERTIFICADO`. Sin documentación si son legacy stale o reservados futuros. | ⚠️ deuda docs | P3 |
| `DigitalDocument.estadisticas_por_tipo` classmethod no filtra tenant | `models/digital_document.py:546-557` | `cls.objects.filter(...)` sin tenant. Si se invoca desde shell o desde reporte, cuenta cross-tenant. | 🐛 bug C-multitenancy | P2 |
| `DigitalDocument.documentos_vencidos`/`proximos_a_vencer`/`pendientes_validacion` classmethods no filtran tenant | `models/digital_document.py:484-501` | Idem. Si un cron invoca `documentos_vencidos()`, marca como vencidos cross-tenant. | 🐛 bug C-multitenancy | P2 |
| Sin tests para `DocumentGenerationViewSet` | — | Por eso los 14+ bugs L3.11 declarados arriba pasan invisibles. | ⚠️ deuda tests | P1 |
| Sin tests para `PDFGenerator` cadena de motores | — | Cualquier regresión en xhtml2pdf/WeasyPrint/ReportLab pasa silenciosa. ReportLab stub se invoca en Windows sin warning visible al test. | ⚠️ deuda tests | P2 |
| `DocumentTemplate` sin constraint de unicidad `(tenant, tipo, nombre)` | `models/document_template.py:58-62` | Dos plantillas idénticas pueden coexistir en el mismo tenant. Probable que se quieran deduplicar. | ⚠️ deuda | P3 |
| Custom managers comentados | `digital_document.py:16, 215`; `document_template.py` | Decisión pendiente. | ⚠️ deuda | P3 |
| Sin `apps/documents/tests/` | — | Tests viven en `apps/api/tests/test_documentos_*.py`. Co-locate como B.2 cleanup. | ⚠️ deuda | P3 |
| Sin retention policy / auditoría de descargas | — | Crítico para compliance LPD Perú + SUNAFIL. | ❌ missing | P1 |

Sin errores TS para `features/documents` (verificado con `tsc --noEmit -p tsconfig.app.json`). 5 warnings ESLint (listados arriba).

### Tenant-readiness

| Concern | Status | Comment |
|---|:---:|---|
| `DigitalDocument` has tenant FK | ✅ | `digital_document.py:110-117` — nullable=true. Sin composite unique con tenant (suficiente porque empleado ya está taggeado). |
| `DocumentTemplate` has tenant FK | ✅ | `document_template.py:28-35` — nullable=true. **NO hay constraint per-tenant** sobre `(tenant, tipo, nombre)` — defense-in-depth ausente. |
| Composite unique constraint sobre `(tenant, ...)` para DigitalDocument | ⚠️ | `unique_together = (empleado, tipo_documento, numero_documento, version)` — implícito vía empleado. Sin defense-in-depth si hay bug de cross-tenant employee. |
| `DocumentosDigitalesViewSet.get_queryset` filtra por tenant | ❌ | `views.py:2072-2138` — NO filtra por tenant. Confianza 100% en RLS+middleware. Sin defense-in-depth. |
| `DocumentosDigitalesViewSet.perform_create` asigna tenant automáticamente | ❌ | `views.py:2034-2049` — NO setea tenant. Si frontend no lo envía, queda `tenant=NULL`. **Bug seguridad C P1**. |
| `DocumentosDigitalesViewSet.subir_institucional` setea tenant | ❌ | `views.py:2285-2304` — `DigitalDocument.objects.create(...)` sin tenant. Idem orphan. |
| `DocumentGenerationViewSet.*` (todos los `generar-*`) setea tenant en DigitalDocument creado | ❌ | Todos los `DigitalDocument.objects.create(...)` (líneas 131, 230, 352, 725) NO setean tenant. PDFs generados quedan orphan. |
| `pdf_generator._guardar_documento_digital` setea tenant | ❌ | `pdf_generator.py:482-495` — sin tenant. Idem. |
| `TemplateService._obtener_datos_institucion` lee `Company.get_config(tenant=request.tenant)` | ❌ | `template_service.py:324` — hardcoded `tenant=None`. **TODO acknowledged in code**. Documentos rinden datos del tenant default. |
| `WordTemplateService.construir_variables_empleado` lee company config por tenant | ❌ | `word_template_service.py:119-123` — EMPRESA_* hardcoded. NO consulta Company.get_config en absoluto. **Bug C-multitenancy**. |
| File storage segregado por tenant | ❌ | `MEDIA_ROOT = BASE_DIR / "media"`. Upload paths: `documentos_empleados/%Y/%m/`, `plantillas_word/%Y/`, `adendas/%Y/`. **NO incluyen tenant en el path**. Filesystem-level: archivos de tenant_a y tenant_b conviven en el mismo directorio. Si un usuario tiene URL del archivo (`/media/documentos_empleados/2026/05/foo.pdf`) y el web server sirve `/media/` sin auth wall, **leak cross-tenant directo via URL adivinada**. **Bug seguridad serio**. |
| `DocumentTemplate` per-tenant vs system-wide | ⚠️ | Diseño ambiguo: tenant FK es nullable (líneas 28-35). **NO hay flag** que indique "system template (tenant=NULL)" vs "tenant-owned (tenant=X)". `seed_plantillas_default` siembra con tenant=NULL — se asume system-wide. ViewSet no filtra ni por tenant ni por NULL. Resultado: tenant_b ve las plantillas creadas por tenant_a. **Bug seguridad** + decisión arquitectural pendiente para B.1+. |
| Test de aislación tenant para DigitalDocument/DocumentTemplate | ❌ | `tests/test_tenant_isolation.py` no incluye casos de estos modelos. |
| Multi-tenant en frontend | ✅ | El frontend confía en host+JWT. Subdominio determina tenant. URLs de archivos del backend son las únicas que sí podrían leakear (ver bullet anterior). |
| PDF generation context per-tenant | ❌ | `TemplateService` y `WordTemplateService` no aceptan tenant param. Si tenant_a genera PDF y tenant_b ejecuta paralelo, ambos rinden el mismo `Company.get_config(tenant=None)`. |

### Notas

- **15+ bugs L3.11 stale en `DocumentGenerationViewSet`.** El renombre `documento_id`/`plantilla_id`/`empleado_id`/`contrato_id` → `id` UUID rompió **TODOS** los endpoints de generación de documentos. `generar-contrato`, `generar-certificado`, `subir-plantilla-word`, `eliminar-plantilla-word`, `descargar-plantilla-word`, `generar-desde-plantilla-word` están **funcionalmente al 100% rotos** (lanzan FieldError/AttributeError/TypeError o son inalcanzables por regex URL). `generar-adenda` y `generar-reporte` están medio-rotos (responden pero con AttributeError al construir el payload de éxito). **Esta es la peor regresión documentada en cualquier chapter del audit hasta ahora**: la app entera de documentos está prácticamente inoperante. Ningún test cubre estos endpoints, por eso pasan a CI verde. **P1 priority absoluta para B.1 fast-track**.
- **`apps/api/api/v1/app_rrhh/document_generation_views.py` no fue migrado en L3.11.** Per CLAUDE.md, este archivo es el "active document generation entry point" y fue dejado en `app_rrhh/` (legacy folder) con re-mount en `/api/v1/documents/documents/`. **Decisión arquitectural inconsistente**: el modelo se renombró, el ViewSet `DocumentosDigitalesViewSet` también, pero `DocumentGenerationViewSet` quedó congelado en estado pre-rename. Necesita ser migrado a `apps/api/api/v1/documents/views.py` (que actualmente NO existe — sólo hay `urls.py`).
- **Asimetría `Company.get_config` entre TemplateService y WordTemplateService.** El primero llama `Company.get_config(tenant=None)` (con TODO ack); el segundo NO consulta `Company.get_config` en absoluto y hardcodea valores ficticios. Cualquier reconciliación C.3 multi-tenancy debe arreglar ambos en el mismo PR.
- **File storage segregation gap CRÍTICO.** `MEDIA_ROOT` es flat — todos los tenants comparten directorio. Si en producción se sirve `/media/*` sin auth wall (default Django dev server), tenant_b puede adivinar URLs de tenant_a. **Mitigación urgente**: o (a) prefijar tenant_id en `upload_to` del FileField, o (b) servir media via signed URLs S3, o (c) interceptar serving de `/media/` con auth+tenant filter middleware. **Decision para ADRS Task 12**.
- **Cadena de generación PDF inestable en Windows.** xhtml2pdf falla con `@page counter()` (mitigado por `_strip_unsupported_css`); WeasyPrint falla con dependencias GTK no disponibles en Windows; ReportLab funciona pero genera **stub** ("DOCUMENTO GENERADO. Contenido del documento generado desde plantilla.") sin contenido real. Esto se ack-ea en log warning línea 234-237 pero no se surface al usuario. En producción Linux/Docker la cadena debería funcionar — **pero NO hay test que lo verifique**. Bug latente de despliegue.
- **`DocumentTemplate` ambigüedad system vs per-tenant.** Tenant FK nullable + sin flag explícito + sin filtro en ViewSet = todos los tenants ven todas las plantillas. **Decisión arquitectural pendiente**: ¿es DocumentTemplate sistema-wide (con plantillas globales que tenants pueden usar/sobrescribir) o per-tenant exclusivo? El maestro § 03.5 sugiere per-tenant con override jerárquico — implementación pendiente.
- **Templates HTML legacy son paritarios.** Los 17 archivos HTML están idénticos byte-by-byte entre `D:/INTRANET/back/templates/` y `D:/VYNTIA/apps/api/templates/`. La migración fue copy-paste exitoso. **Pero**: `contrato_fijo.html` y `certificado_laboral.html` NO están mapeados a ningún tipo en los servicios — son huérfanos. Decisión P3: documentar como "deprecated" o reactivar.
- **Templates Django `{% %}` multi-line gotcha.** Per CLAUDE.md, "Django's template lexer does not support multi-line `{% %}` or `{{ }}` tags". Las 17 plantillas no han sido auditadas para verificar que cumplen esta regla. Si alguno tiene tag multi-línea, falla en runtime al renderizar.
- **Riesgos al tocar documents en B.1/B.2.** (1) `db_table='documentos_digitales'` y `'app_rrhh_plantilla_documento'` son referencia para datos importados. (2) `DigitalDocument.empleado` FK CASCADE — eliminar Employee borra cascade su legajo entero (incluyendo boletas históricas). (3) `DigitalDocument.documento_padre` FK CASCADE — eliminar versión padre borra todas las versiones hijo. (4) `DigitalDocument.familiar` FK SET_NULL — OK. (5) Los archivos físicos en `media/documentos_empleados/` NO se borran cuando se elimina el `DigitalDocument` (Django no elimina files de FileField al delete). Acumulación silenciosa de orphan files. (6) Cross-app: `Contract.documento_generado` BooleanField, `ContractAmendment.documento_generado` FileField (asimetría documentada en Task 5). (7) Plantillas `apps/api/templates/contratos/` y `adendas/` consumidas por contracts; `certificados/` por employees; `reportes/reporte_empleado.html` por employees; `reportes/reporte_contratos.html` por contracts.
- **Preparación para Module 03 sub-procesos (Task 11).** `DigitalDocument` es el ancla del **legajo digital § 03.5**. En Task 11 se inventarían los flujos completos (índice full-text, retention policy, e-firma, audit trail, OCR, document categories agrupadas por sub-proceso, decision matrix de gaps de retention compliance SUNAFIL/LPD Perú). Esta sección sólo cubrió las entidades + bugs L3.11. La generación de PDFs en producción (xhtml2pdf vs WeasyPrint vs ReportLab) y la decisión arquitectural sobre `DocumentTemplate` system-vs-tenant son piezas mayores pendientes para B.1+.

## App: onboarding

### Estado actual en VYNTIA (post-A+C)

#### Modelos
- `OnboardingProcess` (file: `apps/api/apps/onboarding/models/onboarding_process.py:9`, 186 líneas) — proceso de incorporación de un nuevo empleado, OneToOne con `Employee` y `User`. db_table preservada del legacy: `onboarding_empleado`.
  - Campos clave: `id` UUID PK (line 21); `tenant` FK→`tenancy.Tenant` (line 24, **null=True** transitorio C.1, pendiente NOT NULL en C.3 — ver tenant-readiness); `empleado` OneToOne→`employees.Employee` cascade (line 34); `usuario` OneToOne→`identity.User` cascade (line 39); `estado_onboarding` choices (`pendiente_datos`/`pendiente_documentos`/`pendiente_validacion`/`observado`/`completado`, line 46); 7 booleans de checklist (`datos_personales_completos`, `datos_laborales_completos`, `dni_subido`, `declaraciones_juradas_subidas`, `certificados_academicos_subidos`, `certificados_trabajo_subidos`, `documentos_familiares_subidos`, lines 53-59); validación RRHH (`validado_por`, `fecha_validacion`, `observaciones`, lines 62-70); branding email (`email_bienvenida_enviado`, `fecha_email_bienvenida`, lines 73-74); timestamps (`fecha_inicio`, `fecha_completado`, `updated_at` con db_column legacy `fecha_actualizacion`, lines 77-79).
  - Tenant FK: ⚠️ presente pero **null=True** y **`related_name='+'`** (sin reverse accessor) — la migración 0002 no agregó constraint NOT NULL ni unique-per-tenant. Sin migración de backfill detectada.
  - Manager: default `objects` (no `TenantManager`).
  - Properties calculadas:
    - `progreso_porcentaje` (line 94) — % completitud sobre los 7 booleans.
    - `progreso_aprobado` (line 109) — % de `DigitalDocument` aprobados por RRHH (queries `apps.documents.models.DigitalDocument`).
    - `items_pendientes` (line 130) — lista de strings legibles.
    - `esta_completo` (line 149).
  - Métodos: `marcar_completado(validado_por)` (line 161), `marcar_observado(observaciones)` (line 169), `actualizar_estado()` (line 175 — recalcula estado según booleans).

#### Servicios
- `OnboardingService` (file: `apps/api/apps/onboarding/services/onboarding_service.py:65`) — orquestador de flujo completo. Statics:
  - `generar_username(nombres, apellido)` (line 86) — primera-letra-nombre + apellido_paterno con anti-colisión global (NOT tenant-scoped, ver tenant-readiness).
  - `generar_password_temporal()` (line 110) — 12 chars, alfabeto restringido sin caracteres ambiguos.
  - `enviar_email_bienvenida(usuario, password_temporal)` (line 119) — render `emails/bienvenida.{html,txt}`, dispatch via Celery `send_email_html_task` con fallback síncrono cuando `EMAIL_BACKEND` es console/locmem/filebased o cuando Celery no está disponible. Subject: `"Bienvenido a VYNTIA"` (line 141, OK), from_email: `settings.DEFAULT_FROM_EMAIL` con default `noreply@vyntia.pe`. **El template HTML/TXT renderizado todavía dice "Intranet" — ver bugs.**
  - `crear_onboarding_completo(empleado_data, created_by)` (line 209, `@transaction.atomic`) — crea Employee → User → asigna rol `Employee/empleado` → crea OnboardingProcess → envía email. **NO inyecta `tenant` en ninguno de los modelos creados** (Employee, User, OnboardingProcess) — ver tenant-readiness.
  - `actualizar_estado_onboarding(empleado_id)` (line 303) — recalcula los 7 booleans inspeccionando `DigitalDocument` activos del empleado, llama `actualizar_estado()`, protege estados avanzados (`pendiente_validacion`/`en_revision`/`observado`) de retroceder. Acepta indistintamente `empleado_id` o `onboarding_id` (PK) — ambigüedad documentada en docstring.
  - `obtener_documentos_pendientes(empleado_id)` (line 422) — devuelve lista de tipos faltantes según diccionario `DOCUMENTOS_REQUERIDOS` (lines 20-62).
  - `corregir_correo_personal(onboarding_id, nuevo_correo)` (line 458) — actualiza `Employee.correo_personal` + `User.email`.
  - `reenviar_email_bienvenida(onboarding_id, nuevo_password=True)` (line 480) — opcionalmente regenera password. **Bug:** usa `.get(onboarding_id=onboarding_id)` en línea 488, pero el modelo VYNTIA usa `id` UUID (no `onboarding_id`) — heredado del legacy y no actualizado en L3. Verificable por test fallido.
  - `validar_onboarding(onboarding_id, validado_por, observaciones="")` (line 525) — aprueba todos los `DigitalDocument` `pendiente_revision`, activa el User (de `pendiente`→`activo`), marca completado.
- `OnboardingNotificationService` (mismo archivo, line 560) — envía emails transaccionales:
  - `notificar_documento_rechazado(onboarding, documento, motivo)` (line 564) — render `emails/documento_rechazado.{html,txt}`. Subject: `f"Documento rechazado: {documento.nombre_documento}"` (sin marca VYNTIA en subject — OK funcionalmente).
  - `notificar_onboarding_aprobado(onboarding)` (line 583) — render `emails/onboarding_aprobado.{html,txt}`. Subject: `"¡Tu onboarding ha sido aprobado!"`.
  - `notificar_onboarding_observado(onboarding, observaciones)` (line 601) — render `emails/onboarding_observado.{html,txt}`. Subject: `"Tu onboarding requiere correcciones"`.
  - Las 3 funciones delegan en `OnboardingService._enviar_notificacion()` (line 515) que intenta Celery con fallback síncrono inmediato, **silenciando excepciones** (try/except sin log) — riesgo silencioso si Celery falla y el SMTP también.
- ❌ **NO existe `apps/onboarding/services/onboarding_notification_service.py`** como archivo separado — `OnboardingNotificationService` vive dentro de `onboarding_service.py`. La importación `from apps.onboarding.services import OnboardingNotificationService` funciona porque `services/__init__.py` re-exporta ambas clases.

#### Endpoints REST
Routed at `/api/v1/onboarding/processes/` via `apps/api/api/v1/onboarding/urls.py` (16 líneas) — registra `OnboardingViewSet` que **vive en `api/v1/rrhh/views.py:2337`** (no en `api/v1/onboarding/views.py`, que **no existe**). Esto es un L3.x deuda — el bounded context `onboarding` aún importa la ViewSet del módulo legacy `rrhh/views.py` (~510 líneas dedicadas a onboarding ahí). Lo mismo aplica para serializers (en `api/v1/rrhh/serializers.py:1213-1319`). Ver Notas.
- `GET /api/v1/onboarding/processes/` — list (RRHH-gated via `RRHHPermission` + `@require_hr()` line 2384).
- `POST /api/v1/onboarding/processes/` — `OnboardingIniciarSerializer` (serializers.py:1271) → `crear_onboarding_completo`.
- `GET /api/v1/onboarding/processes/{id}/` — retrieve, autenticado; non-HR solo ve el suyo (line 2417 — manual ownership check, no `tenant` filter).
- `GET /api/v1/onboarding/processes/mi-onboarding/` — `mi_onboarding` action (line 2434, `@require_authenticated()`) — devuelve onboarding del request.user, recalcula estado al vuelo.
- `POST /api/v1/onboarding/processes/{id}/validar/` — `validar` action (line 2462) — accepts `accion=aprobar|rechazar` + `observaciones`. Dispara notificación `OnboardingNotificationService` envuelto en try/except silente.
- `POST /api/v1/onboarding/processes/{id}/documentos/{doc_id}/aprobar/` — `aprobar_documento` (line 2510). HR-only.
- `POST /api/v1/onboarding/processes/{id}/documentos/{doc_id}/rechazar/` — `rechazar_documento` (line 2539). Requiere `motivo` no vacío.
- `POST /api/v1/onboarding/processes/{id}/reenviar_email/` — `reenviar_email` (line 2584). **Llama `OnboardingService.reenviar_email_bienvenida(onboarding.pk)` que internamente busca por `onboarding_id=...` (campo inexistente) → causa 404. Bug L3.x.**
- `POST /api/v1/onboarding/processes/{id}/corregir-correo/` — `corregir_correo` (line 2607) — actualiza correo + reenvía email. (Test in red, ver bugs.)
- `POST /api/v1/onboarding/processes/{id}/actualizar-estado/` — `actualizar_estado` (line 2637).
- `POST /api/v1/onboarding/processes/subir-foto/` — `subir_foto` (line 2658, MultiPart) — empleado en onboarding sube foto JPG/PNG; ruta_fotografia se actualiza en Employee.
- `POST /api/v1/onboarding/processes/subir-documento/` — `subir_documento` (line 2724, MultiPart) — PDF only, mapping interno `_TIPO_CATEGORIA_MAP` (line 2735) cubre 17 tipos. Crea o versiona `DigitalDocument` con estado `pendiente_revision`.

#### UI (frontend)
- **Páginas** (`apps/web/src/features/onboarding/pages/`):
  - `OnboardingAdminPage.tsx` (1047 líneas) — vista RRHH: lista de onboardings, drilldown de un proceso, aprobar/rechazar documentos, validar onboarding, reenviar email, corregir correo. Componente monolítico — candidato a refactor en B.5.
  - `OnboardingEmployeePage.tsx` (113 líneas) — vista del empleado en onboarding: tabs personal/familiar/académico/laboral con upload zones.
  - `OnboardingPage.tsx` (5 líneas) — wrapper que renderiza `OnboardingEmployeePage`.
- **Componentes** (`apps/web/src/features/onboarding/components/`):
  - `DocumentPreviewModal.tsx`, `DocumentUploadZone.tsx` — UI de upload + preview.
  - `OnboardingCompleteBanner.tsx`, `OnboardingProgressBar.tsx`, `OnboardingSectionStatus.tsx` — estado visual.
  - `OnboardingTabPersonal.tsx`, `OnboardingTabFamiliar.tsx`, `OnboardingTabAcademico.tsx`, `OnboardingTabLaboral.tsx` — tabs por sección.
  - `__tests__/` — tests vitest.
- **Servicios** (`apps/web/src/features/onboarding/services/`):
  - `onboardingService.ts` (124 líneas) — `getMiOnboarding`, `getAll`, `getById`, `crear`, `validar`, `reenviarEmail`, `actualizarEstado`. Endpoint `/api/v1/onboarding/processes/{id}/reenviar_email/` usa `_` (underscore) mientras que el backend lo expone con guion bajo en route name (DRF default — OK).
  - `onboardingDataService.ts` — wrappers para `family-members`, `academic-records`, `certifications` y `documents/documents` (consume endpoints de `employees` y `documents`).
  - `onboardingUploadService.ts` (54 líneas) — `uploadFoto`, `uploadDocument`, `subirDocumento` (tres funciones que apuntan al **mismo** endpoint `/subir-documento/` con firmas distintas — duplicación, ver bugs); incluye `corregirCorreo`.
- **Tipos** (`apps/web/src/features/onboarding/types/onboarding.ts`): `EstadoOnboarding`, 15 valores de `TipoDocumento`, `OnboardingStatus`, `UploadDocumentResponse`, `SectionStatus`. Helper `computeAlert()` (alerta cuando `last_login` null y `fecha_email_bienvenida` ≥ 5 días).
- `index.ts` re-exporta todo (`components/`, `pages/`, `services/`, `types/`).

#### Tests
- ❌ **NO existe `apps/api/apps/onboarding/tests/`** — sin tests in-app del bounded context.
- Los tests viven en el directorio root `apps/api/tests/`:
  - `tests/test_onboarding_api.py` — endpoint coverage (validar, corregir-correo, subir-foto/documento, aprobar/rechazar, mi-onboarding). **2 tests fallan (ver bugs).**
  - `tests/test_onboarding_service.py` — service-level (crear_onboarding_completo, actualizar_estado_onboarding, validar_onboarding, generar_username con colisiones, password temporal).
  - `tests/test_onboarding_self_update.py` — empleado actualizando sus propios datos. **1 test falla — empleado puede patchear campos restringidos (security bug).**
  - `tests/test_documentos_digitales_onboarding.py` — flujo completo upload → estado → aprobación.
- Resultado pytest scoped: **28 passed, 2 failed**.

### Gaps vs INTRANET legacy

VYNTIA portó el código de onboarding desde INTRANET de forma básicamente paritaria — el modelo es idéntico (`db_table='onboarding_empleado'` preservada, mismos campos, mismos métodos). El servicio `OnboardingService` legacy tiene 622 líneas vs 618 en VYNTIA — diferencias menores (rutas de import, nombres de modelos EN). Los 8 templates de email son idénticos byte-a-byte salvo el nombre de subject "Bienvenido a VYNTIA" (que se setea en código, no en template).

| Feature legacy | Ubicación legacy | Estado en VYNTIA | Tipo | Prioridad propuesta | Nota |
|---|---|---|:---:|:---:|---|
| Modelo `OnboardingEmpleado` con AutoField PK | `D:/INTRANET/back/app_rrhh/models/onboarding.py:7` | Renombrado a `OnboardingProcess` con UUID PK + `tenant` FK | done | — | Paridad funcional total. |
| `db_table = 'onboarding_empleado'` legacy | line 70 | Preservada (line 82) | done | — | OK para BC. |
| `progreso_aprobado` query a DigitalDocument | line 96 | Replicado (line 109) con import EN-renamed (`apps.documents.models.DigitalDocument`) | done | — | OK. |
| Servicio `OnboardingService` con 622 líneas | `D:/INTRANET/back/app_rrhh/services/onboarding_service.py` | Replicado en `apps/api/apps/onboarding/services/onboarding_service.py` (618 líneas) | done | — | Paridad casi total. |
| `OnboardingViewSet` en legacy `api/v1/rrhh/views.py:2319` | legacy mismo path | Conservada en `apps/api/api/v1/rrhh/views.py:2337` (no migrada a `api/v1/onboarding/views.py`) | partial | P1 | L3.x consumer move pendiente — el bounded context `onboarding` no es self-contained. |
| Templates de email `bienvenida/documento_rechazado/onboarding_aprobado/onboarding_observado` (HTML+TXT) | `D:/INTRANET/back/templates/emails/` | **Copiados sin rebrand** a `apps/api/templates/emails/` | bug | **P0** | 11 strings "Intranet" en templates VYNTIA — ver branding. |
| Tests legacy `tests/test_onboarding_*.py` | `D:/INTRANET/back/tests/` | Migrados a `apps/api/tests/test_onboarding_*.py` | done | — | 2 fallan en VYNTIA (ver bugs). |
| Endpoint `/api/v1/onboarding/processes/{id}/corregir-correo/` | (no existía explícitamente como test rojo en legacy) | Implementado en VYNTIA pero el test `TestCorregirCorreo::test_corregir_correo_updates_email` falla con 400 | bug | P0 | Validación rechaza el body, no responde 200. |
| Permitir empleado actualizar sus propios datos restringidos | (legacy también vulnerable) | `test_employee_cannot_patch_restricted_fields` falla con 200 (debe ser 403) | bug security | **P0** | Empleado en onboarding puede patchear `nombres_empleado`, `apellido_paterno` — backend no bloquea. |

### Gaps vs maestro

Maestro § 3 módulo 03.3 (Inducción) — RPE 265-2017-SERVIR-PE — cubre el plan de inducción **general + específica** para sector público con seguimiento de asistencia y certificados. **Esta auditoría se limita al `OnboardingProcess` existente.** El gap completo (inducción formal, plan general/específico, certificados de finalización, registro de asistencia) se evalúa en Task 11 (Maestro gaps — Module 03).

Sin embargo, vale notar lo que el modelo actual **no captura**:
- ❌ No hay concepto de "plan de inducción" — solo checklist de documentos.
- ❌ No hay tracking de asistencia a sesiones.
- ❌ No hay generación de certificado de inducción (RPE 265-2017 lo exige).
- ❌ No hay distinción entre inducción general (institución) e inducción específica (puesto).
- ❌ No hay retención obligatoria del expediente de inducción (legajo SERVIR).

VYNTIA `OnboardingProcess` es funcionalmente un **checklist de documentos administrativos pre-incorporación**, no un proceso de inducción en sentido SERVIR. La distinción es importante para el discovery del módulo 03.3 en B.11.

### Bugs y deuda técnica conocidos

**Tests fallidos (2):**

| Test | Síntoma | Causa raíz | Prioridad | Fase propuesta |
|---|---|---|:---:|:---:|
| `tests/test_onboarding_api.py::TestCorregirCorreo::test_corregir_correo_updates_email` | Esperaba 200/201, recibió 400 | El endpoint `corregir-correo` retorna 400 — probablemente el `try/except` exterior captura una excepción interna (el viewset llama directamente `onboarding.empleado.save()` y luego `OnboardingService.reenviar_email_bienvenida(onboarding.pk)` que **internamente filtra por `onboarding_id` — campo que no existe en el modelo VYNTIA** (es `id`); raises `OnboardingProcess.DoesNotExist` → returns None → endpoint responde error 500 que se mapea a 400 vía `APIResponse.error`). | P0 | B.5 |
| `tests/test_onboarding_self_update.py::TestEmpleadoSelfUpdate::test_employee_cannot_patch_restricted_fields` | Esperaba 403, recibió 200 | El employee endpoint permite que un empleado patchee `nombres_empleado`/`apellido_paterno` durante onboarding — falta restricción de campos editables por el self (debería bloquear identidad inmutable). Bug security. | **P0 security** | B.5 |

**Bugs latentes (no cubiertos por test):**

1. 🐛 **`OnboardingService.reenviar_email_bienvenida`** (line 488) usa `.get(onboarding_id=onboarding_id)` pero el modelo VYNTIA tiene PK `id` UUID — heredado del legacy `OnboardingEmpleado.onboarding_id`. **Cualquier llamada al endpoint `/reenviar_email/` o `/corregir-correo/` que dependa de esto silenciosamente retorna None.** — P0, B.5.
2. 🐛 **Email branding incompleto** — los 4 templates HTML + 1 TXT contienen 11 ocurrencias de "Intranet" / "Intranet RRHH":
   - `bienvenida.html` lines 6, 29, 35, 71
   - `bienvenida.txt` lines 1, 6, 36
   - `documento_rechazado.html` line 39
   - `onboarding_aprobado.html` line 36
   - `onboarding_observado.html` line 38
   El subject está rebrandado en código (`"Bienvenido a VYNTIA"`) pero el cuerpo del email que llega al empleado dice "Bienvenido a la Intranet — Sistema de Recursos Humanos". **Daño de marca directo en el primer touchpoint del empleado.** — **P0**, B.5.
3. 🐛 **Generación de username NO es tenant-scoped** (line 104): `User.objects.filter(username=username).exists()` busca en todo el sistema. Si dos tenants tienen empleados llamados igual, el segundo recibe `jdoe1`, `jdoe2`, etc. — username "fugitivo" entre tenants, y peor: **un atacante puede enumerar usuarios de otros tenants** observando el sufijo asignado. — P1, B.2 (identity polish) o B.5.
4. 🐛 **`OnboardingNotificationService` silencia excepciones** (line 522): el `try/except Exception: ...` en `_enviar_notificacion` cae a síncrono pero **no loguea** si SMTP también falla — pérdida silenciosa de notificaciones. — P1, B.5.
5. 🐛 **Polimorfismo de `actualizar_estado_onboarding`** (line 303): acepta `empleado_id` o `onboarding_id` indistintamente con doble try/except. Sospechoso — facilita bugs de lookup. Refactor a dos métodos separados. — P2, B.5.
6. 🐛 **Frontend `onboardingUploadService.ts` tiene 3 funciones (`uploadDocument`, `subirDocumento`, `uploadFoto`) que apuntan al mismo endpoint `/subir-documento/`** con firmas y semánticas diferentes. Duplicación + confusión. — P2, B.5.
7. 🐛 **`OnboardingAdminPage.tsx` 1047 líneas** — componente monolítico con 5 `any` lints (lines 87, 424, 624, 870, 887 + import de `CardHeader`/`CardTitle` no usados). — P2, B.5.

**Lint warnings/errors específicos** (de `npm run lint`):

| Archivo | Severidad | Mensaje | Línea | Fase |
|---|---|---|---|---|
| `OnboardingAdminPage.tsx` | error | `'CardHeader' / 'CardTitle' is defined but never used` | 3:29, 3:41 | B.5 |
| `OnboardingAdminPage.tsx` | error | `Unexpected any. Specify a different type` (×5) | 87:117, 424:23, 624:19, 870:79, 887:68 | B.5 |
| `onboardingService.ts` | error | `Unexpected any. Specify a different type` | 76:29 | B.5 |
| `OnboardingSectionStatus.tsx` | warning | `Fast refresh only works when a file only exports components` | 11:17 | B.5 |

**tsc:** 0 errores en `features/onboarding`.

### Tenant-readiness

| Concern | Status | Comment |
|---|:---:|---|
| `OnboardingProcess.tenant` FK | ⚠️ | Presente (line 24) pero **null=True, related_name='+'** — sin enforcement NOT NULL ni unique-per-tenant. Migración 0002 no agrega backfill. |
| ViewSet `get_queryset` filtra por tenant | ❌ | `OnboardingViewSet.get_queryset()` (rrhh/views.py:2377) **NO filtra por `request.tenant`** — solo aplica filtro por `estado`. Un usuario RRHH del tenant A puede listar onboardings del tenant B si tiene la URL/PK. |
| ViewSet `perform_create` injecta tenant | ❌ | `OnboardingViewSet` **no define** `perform_create`/`perform_update`. La creación pasa por `OnboardingService.crear_onboarding_completo()` que **tampoco** asigna `tenant` ni a Employee ni a User ni a OnboardingProcess. Cross-tenant leak risk en C.3+. |
| `retrieve` ownership check | ⚠️ | Manual (line 2417): rechaza si `onboarding.usuario_id != user.pk`. **No verifica que `onboarding.tenant == request.tenant`.** Un superadmin cross-tenant podría ver onboardings de otro tenant. |
| Username generation cross-tenant | 🐛 | `User.objects.filter(username=username).exists()` (line 104) **no acota por tenant** → enumeración cross-tenant. Ver bug #3. |
| Notificaciones — tenant en email | ❌ | `from_email` viene de `settings.DEFAULT_FROM_EMAIL` (global), no por-tenant. `frontend_url` viene de `settings.FRONTEND_URL` — debería ser `https://{tenant.subdomain}.vyntia.pe/login` para deep-linking correcto post-C.4 (subdomain routing). |
| Email branding rebrand | 🐛 | 11 strings "Intranet" en 5 archivos de template — cruza branding de proyecto. Ver bug #2. |
| Asignación de rol `Employee/empleado` | ⚠️ | `crear_onboarding_completo` (line 262) busca el Role globalmente con `Role.objects.filter(nombre_rol__in=["Employee","empleado"])`; con `Role.tenant` FK, podría asignar el rol del **tenant equivocado**. Sin verificación de tenant en el filtro. |
| Documentos linkados (DigitalDocument) | inherit | Todas las queries de documentos (`progreso_aprobado`, `actualizar_estado_onboarding`, `validar_onboarding`) filtran sólo por `empleado=...` — heredan el tenant scoping (o falta del mismo) del app `documents`. Ver capítulo `documents`: filesystem cross-tenant leak risk aplica a uploads de onboarding. |

**Resumen tenant-readiness:** ❌ **No tenant-ready**. Tareas mínimas para B.5:
1. Tenant FK NOT NULL + backfill (alinear con C.3 cuando suceda).
2. ViewSet `get_queryset` filter por `request.tenant`.
3. ViewSet `perform_create` injecta `request.tenant` en Employee, User, OnboardingProcess.
4. Username uniqueness scoped a `(tenant, username)` (también afecta a User model — coordinar con identity B.2).
5. Role lookup filtrado por `tenant`.
6. `frontend_url` por-tenant (subdominio).
7. Rebrand templates VYNTIA (bug #2).

### Notas

- **Decisión heredada de A+C:** `OnboardingViewSet` y sus serializers todavía residen en `api/v1/rrhh/views.py` y `api/v1/rrhh/serializers.py` — el split L3.x del bounded context onboarding **no se completó del lado API**. El módulo `api/v1/onboarding/` solo tiene `urls.py` que importa la ViewSet desde rrhh. Esto es exactamente el mismo patrón que documents (DocumentGenerationViewSet) y contracts (L3.10.3 stale consumers) — un "L3.x consumer audit" acumulado para B.5.

- **Riesgo de tocar onboarding en B.5:** el flujo `crear_onboarding_completo` toca **3 modelos cross-app** (Employee, User, OnboardingProcess) en una transacción atómica, además de envío de email. Cualquier cambio de tenant scoping requiere migrar los 3 sin romper el rollback. Recomendación: probar en staging con datos sintéticos antes de tocar producción.

- **Notification flow documentado:**
  ```
  RRHH dispatcha acción (validar/rechazar/upload) →
    OnboardingViewSet action (rrhh/views.py) →
      [opcional] OnboardingService.actualizar_estado_onboarding →
      OnboardingNotificationService.notificar_* →
        OnboardingService._enviar_notificacion →
          Celery send_email_html_task.apply_async() (async)
            └─ fallback: EmailMultiAlternatives.send() (síncrono, mismo request)
  ```
  Templates: `apps/api/templates/emails/{bienvenida,documento_rechazado,onboarding_aprobado,onboarding_observado}.{html,txt}`.

- **Pasos rastreados en OnboardingProcess:** datos personales (Employee fields completos), datos laborales (DatosLaborales activo via cross-app FK), upload DNI, declaraciones juradas, certificados académicos, certificados de trabajo, documentos familiares, validación final RRHH (manual, valida toda la pila de DigitalDocument `pendiente_revision`). **No incluye:** capacitación (RPE 265-2017), firma electrónica de bienvenida, asignación de equipo/usuario AD, onboarding de manager (assignar mentor), tareas de período de prueba (B.11).

- **Cobertura de test razonable** (28 passed) — el dominio onboarding es de los mejor cubiertos en VYNTIA. Los 2 fallos son específicos y reproducibles. Sin embargo, la ausencia de `apps/onboarding/tests/` significa que los tests no migraron al bounded context (tech debt cross-app, B.5).

## Cross-cutting deuda técnica

Tres baselines técnicos pre-existentes documentados aquí; deben cerrarse o reclasificarse explícitamente como wontfix antes de cerrar B. Cada item se atribuye a un app + propone fase de cierre.

### Pytest pre-existing failures (7)

Capturados en B.0 audit del baseline post-Foundation. Todos son asuntos de auth (4), onboarding (2), o integración de API (1). Raíces: fixtures DRF/pytest incompatibles, lógica faltante de restricción de campos (onboarding), endpoints incompletos.

| # | Test | App | Causa | Fase propuesta |
|---|------|-----|-------|:--------------:|
| 1 | `tests/test_auth_api.py::LoginAPITest::test_login_datos_faltantes` | identity | Fixture DRF/pytest: client.post() no valida campos faltantes en request.data (bypass DRF parsing) | B.1 |
| 2 | `tests/test_auth_api.py::LoginAPITest::test_login_usuario_bloqueado` | identity | Mismo: request.data no propagado a serializer validation | B.1 |
| 3 | `tests/test_auth_api.py::LogoutAPITest::test_logout_token_invalido` | identity | Mismo fixture bug: token validation en LogoutView ignora request.data | B.1 |
| 4 | `tests/test_auth_api.py::UserProfileAPITest::test_actualizar_perfil_exitoso` | identity | PATCH actualización no persiste nombres_usuario campo: ViewSet no llama `serializer.save()` o `user.save()` | B.1 |
| 5 | `tests/test_auth_api.py::AuthAPISecurityTest::test_multiples_intentos_login_fallidos` | identity | `intentos_fallidos` counter no se incrementa en fallos; LoginAttempt model insertable pero ViewSet no consulta/actualiza | B.2 |
| 6 | `tests/test_onboarding_api.py::TestCorregirCorreo::test_corregir_correo_updates_email` | onboarding | Endpoint `/corregir-correo/` planificado (Wave 1) pero no existe; test RED por spec incompleta | B.3 |
| 7 | `tests/test_onboarding_self_update.py::TestEmpleadoSelfUpdate::test_employee_cannot_patch_restricted_fields` | onboarding | Validación faltante: employee PATCH no bloquea `nombres_empleado`, `apellido_paterno`, etc. (security regression); debe 403 | B.3 |

Causas raíz agrupadas:
- **4 auth fixture bugs (B.1):** client.post() no respeta DRF serializer validation. Remedio: actualizar fixtures para usar `rest_framework.test.APIRequestFactory` o simular `request.data` en test setup.
- **1 auth counter (B.2):** LoginAttempt model existe pero nunca se consulta en ViewSet. Remedio: integrar counter en login endpoint + test.
- **2 onboarding spec gaps (B.3):** Wave 1 incompleta (corregir-correo) + validación de restricción de campos. Remedio: implementar endpoint + add field restriction decorator/permission.

### TS errors (1)

| # | File | Error | Acción propuesta | Fase |
|---|------|-------|------------------|:----:|
| 1 | `apps/web/src/generated/api/models/BlankEnum.ts:6:5` | `error TS1132: Enum member expected` (enum BlankEnum malformed: vacío con `;` colgante) | Regenerar con `openapi-typescript@latest` (issue en openapi-typescript-codegen v0.x con enums vacíos); O añadir ESLint ignore-rule `/* eslint-disable @typescript-eslint/no-empty-enum */` | B.1 |

### Lint warnings (641 total)

Distribución por directorio post-C:

| Directorio | Count | Categoría dominante | Remedio | Fase |
|------------|------:|-------|--------:|:-----:|
| `src/generated/api/` | 202 | auto-generated (no-explicit-any 202x; ignorar) | Agregar regla ESLint: ignore `src/generated/` o añadir `.eslintignore` | B.1 |
| `src/features/employees/` | 16 | no-explicit-any (Tab*.tsx), no-unused-vars (hooks) | Tipificar any (request/response payloads); remover vars no usadas | B.4 |
| `src/features/identity/` | 15 | no-explicit-any (auth, menu, roles) | Tipificar any; aplicar strict mode gradual | B.1 |
| `src/features/time-off/` | 13 | no-explicit-any (vacation forms, rules) | Tipificar enums/dtos; remove unused | B.5 |
| `src/shared/ui/` | 6 | no-explicit-any (shadcn/ui wrappers) | Tipificar input/output | B.1 |
| `src/features/organization/` | 6 | no-explicit-any (department forms) | Tipificar | B.2 |
| `src/shared/layout/` | 5 | no-unused-vars, no-explicit-any (Header, Sidebar) | Remover imports no usados | B.1 |
| `src/features/auth/` | 4 | no-explicit-any (services, context) | Tipificar API responses (APIResponse<User>) | B.1 |
| `src/shared/api/` | 3 | no-explicit-any (menuService) | Tipificar | B.1 |
| `src/features/payroll/` | 3 | no-explicit-any | Tipificar | B.5 |
| `src/features/onboarding/` | 3 | no-explicit-any | Tipificar | B.3 |
| `src/features/documents/` | 3 | no-explicit-any, no-unused-vars | Tipificar | B.5 |
| `src/shared/hooks/`, `src/shared/components/`, otros | 9 | mixto | Tipificar | B.1 |

**Recomendación de categorización:**
- **B.1 (polish baseline):** Absorbe 235+ warnings (generated/ ignore-rule, 5 archivos identity+shared tipificar, BlankEnum.ts fix, UI+layout). Justificación: cross-cutting infra, visibility rápida.
- **B.2-B.5:** Absorben 406 warnings (employees 16 → B.4, organization 6 → B.2, time-off 13 → B.5, onboarding 3 → B.3, payroll 3 → B.5, docs 3 → B.5). Justificación: contexto de app, prioridad con features.

**Estrategia de remedio:**
1. **B.1 lint ignore (fase inicial):** Agregar `.eslintignore` con `src/generated/` para remover 202 warnings instantáneamente (auto-generated, no valor).
2. **Migración gradual:** Restar 202 de 641 = 439 reales. Atacar B.1 cross-cutting (40-50 warnings) en 2-3h de typing. Resto mapea a phases.
3. **No regresión:** Fijar `npm run lint` en CI post-B.1; bloquear PRs con warnings nuevas.

### Resumen recomendaciones

**Pytest:** Mapear 7 failures a B.1/B.2/B.3 (ver tabla arriba). Tres categorías: fixture bugs (B.1), counter (B.2), onboarding spec (B.3).

**TypeScript:** 1 error auto-generated (BlankEnum) → fix regenerate o ignore-rule en B.1.

**Lint:** 641 warnings; 202 auto-generated (ignore); 439 reales. Estrategia: fix 40-50 B.1 cross-cutting en 2-3h (identity, shared, ui). Resto mapea a app phases 20-50 warnings cada una (0.5-1h per phase).

**Baseline preservación:** Post-Foundation, 161 pytest passed. B.0 acepta 7 failures pre-existentes (fixture bugs + spec incompleta); B.1+ cierra. Lint baseline 641; B.1 → 439 (ignore generated); B.2-5 → 0 (target, no regression).

## Maestro gaps — Module 01 (Policies)

### Maestro requirements (§ 3.139-152, `docs/modulos/01_planificacion_politicas.md`)
- Gestor documental de políticas (versionado, aprobación, difusión, derogación)
- Plan estratégico anual de RRHH con objetivos, KPIs y presupuesto
- Workforce planning (proyección de headcount, plan de sucesión, análisis de brechas)
- Matriz de cumplimiento normativo (MTPE / SUNAFIL / MINSA / SERVIR / SUNAT) con alertas de vencimiento
- Cobertura SERVIR procesos 1 (Estrategias / políticas) y 2 (Planificación de RR.HH.)

### Entities required (per maestro)
| Entity | Purpose |
|--------|---------|
| `Policy` | Política con metadatos (título, sector, tipo: CORPORATIVA / RRHH / SST / RIT / ETICA / DIRECTIVA, vigencia) |
| `PolicyVersion` | Histórico versionado con aprobaciones y trazabilidad de cambios |
| `PolicyApprovalFlow` | Flujo elaboración → revisión legal → revisión SST → aprobación gerencial |
| `PolicyPublication` | Publicación con difusión al portal del empleado |
| `PolicyAcknowledgment` | Acuse de recibo del colaborador (auditable) |
| `HRStrategicPlan` | Plan anual con objetivos estratégicos y presupuesto |
| `StrategicObjective` + `KPI` | Objetivos con metas y mediciones periódicas |
| `WorkforcePlan` + `HeadcountProjection` | Proyección de plantilla por área × periodo |
| `SuccessionPlan` + `KeyPosition` + `SuccessorCandidate` | Plan de sucesión para puestos clave |
| `ComplianceMatrix` + `ComplianceObligation` + `Evidence` | Matriz normativa con responsables, deadlines, evidencias |

### Current state in VYNTIA
**Zero implementation.** Confirmed via grep across `apps/api/apps/`:
- No `apps/policies/` Django app
- No models, no serializers, no views, no URLs
- Matches found only in `apps/tenancy/rls/policies.py` — these are PostgreSQL Row-Level-Security policies (multi-tenancy infra), NOT HR policies. Unrelated.
- No frontend feature folder (`features/policies/` does not exist)

### Current state in INTRANET legacy
**Zero implementation.** Confirmed via grep across `D:/INTRANET/back/app_rrhh/`. Legacy never built Module 01. The only "policy" string matches are inside multi-tenant infra terminology — none are HR policies.

### Estimated work
- **New Django app** `apps/policies/` (follows the bounded-context pattern from Foundation L3)
- ~10 tenant-scoped models extending `TenantScopedModel` (Policy, PolicyVersion, PolicyApprovalFlow, PolicyPublication, PolicyAcknowledgment, HRStrategicPlan, StrategicObjective, KPI, WorkforcePlan, ComplianceMatrix + supporting tables)
- CRUD endpoints + serializers + filters + permissions (`apps/policies/permissions.py`)
- Document upload + storage backend (uses **ADR-B.4** storage decision)
- Approval workflow engine (uses **ADR-B.3** workflow decision — same engine that B.10 vinculación and B.13 desplazamiento will reuse)
- Versioning logic (uses **ADR-B.7** versioning decision)
- Frontend `features/policies/` with list / detail / version-history / acknowledgment-tracking pages
- Compliance dashboard (consumes ComplianceMatrix; surfaces vencimientos)
- Tests: model + endpoint + isolation tests + acknowledgment audit trail
- **Tier comercial:** Pro (per maestro § 150)
- Estimated effort: ~2.5 weeks single-engineer

### Phase mapping
- Single phase: **B.15 — Policies module (greenfield)** — last functional phase before B.16 close-out

### Dependencies
- ADR-B.4 (document storage) decided before B.15
- ADR-B.3 (approval workflows) decided before B.15 — workflow engine should land in B.10 or B.13 to be reused here
- ADR-B.7 (versioning) decided before B.15
- B.1 polish-baseline merged (clean foundation, lint at zero)
- B.5 polish-documents merged (since Policy reuses document-upload patterns from `apps/documents`)
- B.6 (Position) is NOT a hard dependency — Policy references roles by string, not by FK

### Cross-cutting research items (raised here, deferred)
- Public-sector PEI / POI / PDP integration (maestro § 7) — deferred to follow-up; not B-scope
- ANPD declaration of policy data (Ley 29733) — covered by ADR-B.2 audit trail decision


## Maestro gaps — Module 02 (Organization extended)

### Already implemented in `organization` app (per Task 3)
- **Department** (`Area` legacy) — areas / unidades organizativas planas, con FK a Company
- **Location** (`Ubicacion` legacy) — sedes / ubicaciones físicas
- **CompanyConfig** (`ConfiguracionEmpresa` legacy) — configuración global por empresa/tenant

That covers a thin slice of "organigrama plano" but **none of the puesto / banda / CCF / MPP / CPE requirements**.

### Maestro requirements not yet implemented (§ 3.156-171, `docs/modulos/02_organizacion_trabajo.md`)
| Entity | Purpose | Sector | Phase |
|--------|---------|--------|:-----:|
| `Position` | Catálogo maestro de puestos (definición, distinto de la plaza ocupada) | both | B.6 |
| `PositionProfile` | Job description (misión, funciones, competencias, requisitos) | both | B.6 |
| `OccupationalCategory` | Tabla 10 SUNAT (ejecutivo / empleado / obrero) | both | B.6 |
| `CIUOCode` | Tabla 9 SUNAT — ocupación CIUO-08 OIT | both | B.6 |
| `OrgUnit` | Estructura jerárquica navegable (DIRECCION / GERENCIA / OFICINA / AREA / EQUIPO) — extiende Department con jerarquía + parentUnit | both | B.6 |
| `Plaza` | Posición asignada (OCUPADA / VACANTE / CONGELADA) ligada a Position + Employee | both | B.6 |
| `PositionRiskProfile` | Perfil de riesgos del puesto (vínculo a SST futuro) | both | B.6 |
| `CategoryFunctionTable (CCF)` | Cuadro Categorías y Funciones — **obligatorio Ley 30709** igualdad salarial | private (LCT) | B.7 |
| `Category` + `ObjectiveCriteria` | Categorías jerárquicas con criterios objetivos (responsabilidad, esfuerzo, condiciones, complejidad) | private (LCT) | B.7 |
| `SalaryBand` | Banda (mín / punto medio / máx) por categoría + análisis de equidad interna | private (LCT) | B.7 |
| `MPP (Manual Perfiles de Puestos)` | Documento maestro de perfiles del CPE | public (SERVIR) | B.8 |
| `CPE (Cuadro de Puestos de la Entidad)` | Documento normativo SERVIR — Ley 30057 | public (SERVIR) | B.8 |
| `CAP (Cuadro de Asignación de Personal)` | Documento provisional 276/728 público | public (276/728-pub) | B.8 |

### Legacy parity gaps (from grep on D:/INTRANET/back/app_rrhh/)
Legacy stored "cargo" only as a free-text `CharField` on:
- `datos_laborales.cargo_empleado` (max_length=100)
- `contratos_adendas.cargo` (max_length=100)
- `remuneracion.cargo` (max_length=100)
- `configuracion_empresa.cargo_representante`

**No catalog**, no relational integrity, no profile, no salary bands, no CCF, no MPP, no CPE, no orgchart. Each cargo is typed by hand, can be misspelled, no historical tracking. Legacy is therefore non-compliant with **Ley 30709** (private sector salary equality law that requires CCF).

VYNTIA inherits the same gap — `EmploymentData` model still uses string `cargo`. **Migration to Position FK** is part of B.6.

### Estimated work per phase

#### B.6 — Position + OrgChart + Plaza (~2 weeks)
- 7 models with tenant FK (Position, PositionProfile, OccupationalCategory, CIUOCode, OrgUnit, Plaza, PositionRiskProfile)
- Reference catalogs: Tabla 9 SUNAT (CIUO-08 OIT) seed data; Tabla 10 SUNAT seed data
- OrgChart UI (frontend lib decision in **ADR-B.8**) — drag-drop reordering, parent-child traversal, búsqueda jerárquica, exportación PDF
- Migration: **EmploymentData.cargo (string) → EmploymentData.position (FK)** with data backfill script
- `ContratosAdendas.cargo` migration to FK
- Plaza assignment: OCUPADA / VACANTE / CONGELADA states with workflow

#### B.7 — CCF + SalaryBand (~1.5 weeks)
- Compliance with **Ley 30709** (D.S. 002-2018-TR reglamento)
- May require legal review of CCF structure
- Análisis de brechas salariales por género/edad/antigüedad — reporte auto-generado para fiscalización SUNAFIL
- Plan de nivelación automático sugerido
- Importación masiva desde Excel (plantilla predefinida)

#### B.8 — MPP + CPE + CAP (~1.5 weeks)
- Public-sector schema following **SERVIR** norms (Ley 30057)
- Distinct UI flow gated by `tenant.sector === 'public'` (**ADR-B.6**)
- Niveles SP-DS / SP-EJ / SP-ES / SP-AP / RE / FP / EC clasificación
- Generación de documento normativo descargable PDF para registro en SERVIR

### Phase mapping summary
- **B.6** Position + OrgChart + Plaza → both sectors
- **B.7** CCF + SalaryBand → private (LCT)
- **B.8** MPP + CPE + CAP → public (SERVIR / 276)

### Dependencies
- B.3 polish-organization done (clean baseline on Department / Location / CompanyConfig)
- **ADR-B.6** (sector gating SERVIR vs LCT in UI) decided before B.7 and B.8
- **ADR-B.7** (versioning of Position; estructura org versionada por `effective_date`) decided before B.6 — this is critical because § 5.1 maestro requires "consultas a fecha" sobre la estructura
- **ADR-B.8** (org chart frontend lib) decided before B.6
- B.6 is a **hard dependency for B.9 (Selección)** and **B.10 (Vinculación)** in Module 03 — the recruitment process is for a Position; the contract references a Position

### Cross-cutting research items (raised here, deferred)
- Migration plan for legacy `cargo` strings → Position FK (data quality: how many distinct strings? canonicalization needed?). Captured in B.6 plan.
- Análisis de equidad salarial Ley 30709 — requires legal review during B.7 plan


## Maestro gaps — Module 03 (Employment lifecycle)

Module 03 has 7 sub-procesos covering SERVIR procesos 5-13 (excluyendo 10 asistencia → M08 y 12 disciplinario → M09). Status of each in VYNTIA + legacy:

| Sub-proceso | Maestro § | VYNTIA | Legacy | Phase |
|-------------|-----------|:------:|:------:|:-----:|
| 03.1 Selección | proceso con fases, criterios, evaluaciones | ❌ | ❌ | B.9 |
| 03.2 Vinculación | contrato + firma electrónica + T-Registro SUNAT | ⚠️ Contract existe; T-Registro y firma faltan | partial (Contract sí; sin T-Registro) | B.10 |
| 03.3 Inducción | plan general + específica RPE 265-2017-SERVIR-PE | ⚠️ OnboardingProcess existe; compliance RPE 265 sin verificar | partial | B.11 |
| 03.4 Período de prueba | seguimiento, extensión, evaluación | ❌ Sin model de probation | ❌ | B.11 |
| 03.5 Legajos | expediente digital con índice / búsqueda / retención / control de acceso granular | ⚠️ DocumentFile existe; full legajo (13 secciones obligatorias) missing | partial | B.12 |
| 03.6 Desplazamiento | rotación, encargatura, destaque, comisión, permuta, designación, transferencia | ❌ | ❌ | B.13 |
| 03.7 Desvinculación | renuncia, cese, despido, liquidación de beneficios sociales | ❌ | ❌ (no models de cese; legacy nunca lo construyó) | B.14 |

### Sub-proceso details

#### 03.1 Selección (B.9)
**Maestro requirement (§ 2):** proceso de selección con fases, criterios, evaluaciones, convocatoria pública (sector público) con bases oficiales y plazos de transparencia.
**Required entities:** `PersonnelRequisition`, `JobPosting`, `JobApplication`, `Candidate`, `SelectionStage`, `CandidateEvaluation`, `MeritRanking`.
**Sector público SERVIR flow:** 13 pasos obligatorios (publicación 7 días hábiles mínimo, evaluación curricular eliminatoria, prueba de conocimientos nota mínima 14/20, etc.) — ver maestro § 2.3.
**Estimated work:** ~2 weeks (7 models + flow + UI).
**Dependencies:** **B.6 Position is hard dependency** (a selection process is for a specific Position). B.7 SalaryBand is soft dependency (for advertised salary range).
**Note on Module 11 (ATS avanzado):** B.9 implements the basic SERVIR-compliant selección. M11 ATS is a separate Pro-tier module deferred to a later sub-project.

#### 03.2 Vinculación + T-Registro (B.10)
**Maestro requirement (§ 3):** generación automática de contrato según régimen + tipo, firma electrónica, registro T-Registro SUNAT, EsSalud, AFP/ONP, entrega de documentos obligatorios (RIT, Reglamento SST, Código de ética, política de protección de datos con consentimiento expreso, manual de funciones).
**Current VYNTIA state:** Contract model exists (per Task 4); no T-Registro integration; no e-signature; no automated document bundle on hire.
**Required new work:**
- T-Registro API client (SUNAT integration) — archivo de texto plano según Anexo 3 SUNAT, validación con PVS, plazo: hasta el primer día de prestación efectiva
- `TRegistroDeclaration` model linked to Contract
- DocumentSignature model + signature flow UI
- Hiring document bundle automation (asignar RIT, Reglamento SST, etc. con acuse)
- Validación de **desnaturalización** Art. 77 LPCL (tope conjunto 5 años contratos modales → indeterminado)
**ADR addition needed:** **T-Registro API integration design** — sandbox vs producción, rate limits, error retry, manejo de validaciones SUNAT, almacenamiento del archivo .txt generado.
**Estimated work:** ~2 weeks.
**Dependencies:** B.5 polish-contracts done, B.6 Position done.

#### 03.3 Inducción + 03.4 Período de prueba (B.11)
**Maestro requirement 03.3 (§ 4):** plan de inducción general + específica + técnica según **RPE 265-2017-SERVIR-PE**. Material multimedia, asignación de buddy/mentor, evaluación post-inducción, certificado de finalización. Sector público: inducción puede ser en lengua originaria.
**Maestro requirement 03.4 (§ 5):** seguimiento, extensión, evaluación de período de prueba con plazos por régimen:
- 728 común: 3 meses
- 728 calificado: 6 meses (con pacto escrito)
- 728 dirección/confianza: 12 meses (con pacto escrito)
- MYPE pequeña: 3 meses
- CAS: no aplica
- 276: 3 años para Carrera (concurso previo)

**Current VYNTIA state:** `OnboardingProcess` covers some of 03.3 but compliance with RPE 265 NOT verified (missing fields likely: certificado de finalización, plan general vs específica explícitos, fechas obligatorias, mentor assignment, evaluación post-inducción). Nothing for 03.4 — no Probation model, no alertas de vencimiento, no evaluación, no flujo de ratificación / no renovación.
**Required new work:**
- `InductionPlan`, `InductionTask`, `InductionMaterial`, `InductionMentor`, `InductionEvaluation` (extender OnboardingProcess o reemplazar)
- `ProbationPeriod` model with régimen, fecha inicio, plazo, evaluación, decisión (ratificación / no renovación), notificación
- Alertas configurables (30 días antes, 15 días antes de vencer)
- RPE 265 compliance fields auditables
**Estimated work:** ~1.5 weeks.
**Dependencies:** B.10 done (Probation triggers from Vinculación).

#### 03.5 Legajos (B.12)
**Maestro requirement (§ 6):** expediente digital con **13 secciones obligatorias** (datos personales, académicos, experiencia laboral, contrato + addendas, declaraciones juradas, identidad + CUSPP, historial de puestos, evaluaciones, capacitaciones, reconocimientos, sanciones, licencias, exámenes médicos *acceso restringido permlevel 9*, accidentes laborales *acceso restringido*, documentos de cese). Upload con OCR, clasificación automática, firma electrónica, versionado, **control de acceso granular por tipo de documento**, búsqueda full-text, exportación consolidada PDF, retención mínima 5 años post-cese. Cumplimiento Ley 29733 (cifrado AES-256 datos sensibles, ANPD, ARCO, portabilidad).
**Current VYNTIA state:** `DocumentFile` model exists (per Task 5) but it's un upload simple sin estructura de legajo. No 13-section index, no permission levels granulares por tipo, no retention policy, no audit trail de acceso, no full-text search, no exportación consolidada.
**Required new work:**
- `DigitalDossier` (unique per employee), `DossierSection` (13 secciones predefinidas + extensibles por tenant), `DossierDocument` con metadata
- `DocumentAccessLog` (audit trail — usa **ADR-B.2** decisión de auditoría)
- Permission level enforcement (ADR-B.3 workflows — algunos docs requieren approval para visualizar)
- Retention policy enforcement (5 años mínimo post-cese, ANPD compliance)
- Full-text search (PostgreSQL `tsvector` o Elasticsearch — decisión de implementación en plan)
- Exportación consolidada (PDF unificado) — reusa el PDFGenerator existente
- Cifrado AES-256 para sub-secciones marcadas como sensibles (médicos, accidentes)
**Estimated work:** ~1.5 weeks.
**Dependencies:** B.5 polish-documents done, ADR-B.2 (audit trail) decided, ADR-B.4 (storage) decided.

#### 03.6 Desplazamiento (B.13)
**Maestro requirement (§ 7):** rotación, encargatura, destaque, comisión de servicios, permuta, designación, transferencia (D.Leg. 276 y normas SERVIR). Cada tipo con duración, remuneración, plazo, prórroga; resolución administrativa generada automáticamente; flujo aprobaciones (jefe directo → RRHH → titular); notificación a Tesorería si afecta planilla.
**Current VYNTIA state:** ❌ Nothing.
**Required new work:**
- `Displacement` model with `tipo` enum (los 7 tipos), `DisplacementOrigin` (puesto / entidad), `DisplacementDestination` (puesto / entidad), `DisplacementResolution`, `DisplacementExtension`
- Approval flow (uses **ADR-B.3** workflow engine — tercer reuso)
- Generación automática de resolución administrativa PDF
- Cálculo de afectación remunerativa (encargatura asume puesto encargado, destaque origen asume + viáticos, designación asume cargo designado)
- Notificación a payroll (M04) si afecta planilla
**Sector note:** Designación + Encargatura + Destaque + Comisión + Transferencia son **principalmente sector público SERVIR** (Ley 30057). Permuta y Rotación aplican a ambos sectores. UI gated by `tenant.sector === 'public'` para los públicos exclusivos (**ADR-B.6**).
**Estimated work:** ~2 weeks.
**Dependencies:** B.6 Position done (los desplazamientos referencian Position origen y destino).

#### 03.7 Desvinculación + liquidación (B.14)
**Maestro requirement (§ 8):** registro de cese con causal y fecha, motor de liquidación automática, generación de documentos (carta aceptación renuncia, Liquidación BBSS, **Certificado de Trabajo obligatorio Art. 45 LPCL**, constancia no adeudo), bloqueo de accesos, recepción entregables, pago en plazo legal **48 horas máximo**, baja T-Registro, baja EsSalud, comunicación AFP, archivo legajo CERRADO (retención 5 años).
**Causales por régimen:**
- 728: renuncia voluntaria, mutuo disenso, cumplimiento de plazo, fallecimiento, invalidez absoluta, jubilación, despido (causa justa), **despido arbitrario** (1.5 rem/año, tope 12 rem), despido por falta grave
- 276: renuncia, fallecimiento, jubilación, cese justificado (PAD), destitución (PAD), incapacidad permanente, inhabilitación
- CAS: no renovación, resolución por causa grave, mutuo acuerdo, fallecimiento

**Current VYNTIA state:** ❌ Nothing. Confirmed via grep — no Cese / Liquidación / Termination / Severance / Despido / Renuncia models in VYNTIA. Legacy is also empty (only string matches in unrelated contexts).
**Required new work:**
- `Termination` model with type enum + causal + régimen + fecha
- `SeveranceSettlement` model with cálculo automático **mínimo legal** per **ADR-B.9**:
  - **CTS proporcional** (1 sueldo/año, prorrateo último periodo)
  - **Vacaciones truncas** (días no gozados × jornal)
  - **Gratificación trunca** (proporcional al semestre, fiestas patrias / navidad)
  - **Indemnización por despido arbitrario** (1.5 sueldos / año, tope 12 sueldos)
- `WorkCertificate` con generación automática Art. 45 LPCL (sin información desfavorable, sin calificaciones subjetivas, sin motivos de cese)
- `ExitInterview`, `HandoverChecklist`, `SystemsOffboarding` (integración IT)
- Baja T-Registro (reusa cliente del B.10)
- Pago en plazo legal 48h con alerta SLA
**Sub-proyecto D extends with:** AFP/ONP detraction completa, Renta 5ta, multi-régimen 728/CAS/276/MYPE/Agrario/Microempresa, integración full payroll (motor multi-régimen Strategy Pattern). B.14 entrega cálculo mínimo legal; D entrega motor de planilla peruano completo.
**Estimated work:** ~2 weeks (model + minimum calc + UI).
**Dependencies:** B.5 polish-contracts done, B.10 done (T-Registro client reuse), B.12 done (legajo se cierra al cese).

### Total estimated work for Module 03
**~11-13 weeks across 6 phases (B.9-B.14).** Largest module in B by far. Plan B carga aproximadamente 60% de su esfuerzo en Module 03; el resto se reparte entre Module 01 (B.15) y Module 02 (B.6-B.8).

### Cross-cutting research items (raised here, deferred to ADRs or follow-up)
- **T-Registro API integration design** — drafted in B.10 plan, may require new ADR (call it ADR-B.10)
- **RPE 265-2017-SERVIR-PE compliance specifics** — legal review during B.11 plan
- **Severance B-vs-D demarcation** — captured in **ADR-B.9** (drafts in Task 14c)
- **Sector-specific UI handling** for desplazamiento types — covered by **ADR-B.6**
- **Workflow engine reuse** across vinculación, desplazamiento, policies (B.10 / B.13 / B.15) — covered by **ADR-B.3**
- **Document audit trail** for legajo accesos — covered by **ADR-B.2**
- **Versioning of contract amendments and dossier sections** — covered by **ADR-B.7**

### Module 11 ATS — out of B scope
Maestro Module 11 (Reclutamiento ATS avanzado, multiposting) is referenced in 03.1 but is a **separate Pro-tier module** deferred to a future sub-project. B.9 only implements the SERVIR-compliant selección base + integración con Module 02 Position. ATS avanzado (multiposting, scoring algorítmico, scheduling, video-entrevista) NO está en B.
