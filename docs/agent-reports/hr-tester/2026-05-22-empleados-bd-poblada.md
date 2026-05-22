# HR Tester — Empleados (BD poblada, runtime execution)

**Fecha:** 2026-05-22 (segunda corrida)
**Invocado por:** `/vyntia-test-hr empleados con BD demo-pro poblada`
**Spec consultada:** `docs/superpowers/specs/2026-05-09-vyntia-B-vyntia-core-functional-design.md`
**Corrida previa:** `docs/agent-reports/hr-tester/2026-05-22-empleados.md` (audit estático)
**Casos ejecutados:** 7 (todos runtime, no estático) | **Confianza:** alta
**Tiempo invertido:** ~45 min
**Baseline:** no regresado (no se modificó código, solo script temporal)
**Setup:** DB `bd_vyntia` PostgreSQL real, tenant `demo-pro` con 15 empleados peruanos seedados, ejecutado vía Django ORM + `rest_framework.test.APIClient`.
**Workaround usado:** monkey-patch a `psycopg2.connect` para inyectar `options='-c lc_messages=C'` (sin esto el server PG en Windows ES-PE responde el FATAL en cp1252 y rompe utf-8 decoding).

---

## TL;DR — verdict por caso

| # | Caso | Estado | Severidad para D-Pay | CONFIRMA / REFUTA / NUEVO |
|---|---|---|---|---|
| 0 | Seed roles vs `Roles.HR_ROLES` | ❌ ROTO | ALTO | **NUEVO** — demo users (Admin/RRHH) no pueden POST empleados |
| 1 | DNI validation on POST (duplicado, 7-dig, letras) | ❌ ROTO | CRÍTICO | **CONFIRMA** audit previo |
| 2 | `calcular_vacaciones_pendientes` por régimen | ❌ HARDCODED | CRÍTICO | **CONFIRMA** audit previo |
| 3 | Locación de servicios en queries de planilla | ⚠️ FUGA | CRÍTICO | **CONFIRMA** audit previo |
| 4a | Tenant isolation `/employees/` | ✅ AISLA | — | **REFUTA** sospecha previa (filtra OK) |
| 4b | Tenant isolation `/selection-stages/` | ❌ FUGA | CRÍTICO | **NUEVO** — confirma sospecha audit, peor de lo esperado |
| 5 | B.9 JobApplication transitions (legales e ilegales) | ✅ FUNCIONA | — | **REFUTA** preocupación; state machine respetada |
| 6 | PDF reporte empleado | ❌ ROTO (2 bugs) | ALTO | **NUEVO** — `carrera_especialidad` + module not found |
| 7 | Practicante 16-17 años (Ley 28518) | ❌ ROTO + EXTRA | CRÍTICO | **REFUTA** audit (rechaza <18 NO se aplica); **NUEVO** acepta hasta niño 15 años |

**Veredicto global:** El audit previo subestimó la severidad. Hay **5 bugs CRÍTICOS** runtime-confirmados que **bloquean D-Pay** y **2 bugs ALTOS** adicionales. La buena noticia: la state machine de B.9 funciona, y `/api/v1/employees/` filtra por tenant correctamente. La mala noticia: el seed `demo-pro` mismo crea un escenario donde sus usuarios NO pueden crear empleados por inconsistencia de nombres de rol, y dos bugs de Ley 28518 (DNI sin validación + edad mínima sin enforcement) habilitan datos ilegales que llegarán a planilla y T-Registro.

---

## CASE 0 (NUEVO) — Seed roles mismatch

**Observación inesperada durante warmup:**
```
admin_demo_pro roles: ['Admin']
rrhh_demo_pro  roles: ['RRHH']
```
Pero `apps/core/constants.py` define `Roles.HR_ROLES = ['Super Administrador','Administrador RRHH','Analista RRHH','Jefe de Area']`. Y `@require_hr()` en `EmpleadoViewSet.create/update` chequea **case-sensitive** estos exact strings.

**Repro:**
```python
c = APIClient(HTTP_HOST='demo-pro.testserver')
c.force_login(User.objects.get(username='admin_demo_pro'))
r = c.post('/api/v1/employees/', {...payload válido...}, format='json')
# r.status_code == 403
# r.json()['error_code'] == 'INSUFFICIENT_PERMISSIONS'
```

**Por qué importa:** El admin y el RRHH del demo NO pueden dar de alta empleados vía API tal como vienen seedados. El `RRHHPermission` sí los acepta (porque case-insensitive incluye "admin"/"rrhh"), pero el decorador `@require_hr` los rechaza. Para que la corrida pueda probar el create flow tuve que `admin.is_superuser = True` en transacción rollback.

**Severidad:** ALTO. La demo `demo-pro` no es funcional out-of-the-box para escribir empleados — único bypass es ser superusuario, lo que el seed no establece.

**Fix recomendado:** seed debe crear roles con los nombres canónicos de `Roles.HR_ROLES`, o el decorador debe ser case-insensitive y aceptar sinónimos.

---

## CASE 1 — DNI validation on POST (runtime CONFIRMADO)

| Sub-caso | DNI | Status | Persistió | Veredicto |
|---|---|---|---|---|
| 1a | `70000001` (duplicado de seed) | **409** IntegrityError | No (bloqueado por DB constraint) | ⚠️ Funciona pero feo UX |
| 1b | `1234567` (7 dígitos) | **201 CREATED** | **SÍ persistió** (rollback en test) | ❌ ROTO |
| 1c | `ABC12345` (con letras) | **201 CREATED** | **SÍ persistió** (rollback en test) | ❌ ROTO |

**Evidencia (output real):**
```
--- 1b: POST DNI '1234567' (7 digits — invalid Peruvian DNI) ---
  status=201
  body={"id": "f6b1c498-f024-4059-b685-30ca191dcd29", ... "numero_documento": "1234567", ...}
  PERSISTED in DB? True

--- 1c: POST DNI 'ABC12345' (letters — invalid) ---
  status=201
  body={"id": "9125aade-2d05-441a-b9c0-b162806c1ccf", ... "numero_documento": "ABC12345", ...}
  PERSISTED in DB? True
```

**Causa raíz:** `EmpleadoCreateSerializer` (en `api/v1/rrhh/serializers.py:677`) NO tiene `validate_numero_documento`. Solo el `EmpleadoUpdateSerializer` la tiene (líneas 538-556). La validación de 8 dígitos + numérico está exclusivamente en update.

**Impacto para D-Pay:** Empleados con DNI inválido (7 dígitos, letras, valores absurdos) pasan al sistema. Al generar T-Registro/PLAME, SUNAT rechaza la declaración mensual y bloquea cierre de planilla. CRÍTICO.

**Repro mínimo:**
```python
serializer = EmpleadoCreateSerializer(data={
    "numero_documento": "ABC12345",  # cualquier basura no-numérica
    "tipo_documento": "DNI",
    "nombres_empleado": "X", "apellido_paterno": "X", "apellido_materno": "X",
    "correo_personal": "x@y.com", "genero_empleado": "masculino",
    "fecha_nacimiento": "1990-01-01",
    "area_inicial": "<uuid-área-válida>",
    "datos_laborales": {...mínimos...},
})
assert serializer.is_valid()  # ❌ debería ser False, es True
```

---

## CASE 2 — Vacaciones por régimen (runtime CONFIRMADO hardcoded)

**Empleado de prueba:** Carlos Quispe (DNI 70000001), fecha_ingreso=2021-05-22, antiguedad=5 años, régimen original `'728'`.

**Resultado:**
```
regimen=728       calcular_vacaciones_pendientes() = 150
regimen=276       calcular_vacaciones_pendientes() = 150  (cambio en savepoint rollback)
regimen=practicas calcular_vacaciones_pendientes() = 150  (cambio en savepoint rollback)
```

Los **tres regímenes devuelven idéntico** = 5 × 30 = 150 días.

**Esto rompe:**
- **MyPE (Ley 28015):** 15 días/año, no 30. Cliente MyPE tendrá vacaciones inflated 2x → indemnización vacacional Ley 31188 incorrecta.
- **Prácticas (Ley 28518):** NO genera derecho a vacaciones acumulativas. Solo 15 días si jornada ≥ 12 meses.
- **CAS (Decreto 1057):** 30 días pero régimen especial — no se mezcla con 728 en planilla.

**Código fuente:**
`apps/contracts/models/employment_data.py:284-296`
```python
def calcular_vacaciones_pendientes(self):
    dias_por_ano = 30  # ← hardcoded
    anos_completos = self.antiguedad_anos
    dias_acumulados = anos_completos * dias_por_ano
    return dias_acumulados
```

**Impacto D-Pay:** Cualquier cálculo de compensación por vacaciones no gozadas será incorrecto para todo cliente que no sea régimen 728 estándar. CRÍTICO.

---

## CASE 3 — Locación de servicios mezclada en planilla queries (CONFIRMADO)

**Setup:** Creé (en tx rollback) un `EmploymentData` con `tipo_contrato='locacion'`, `regimen_laboral='locacion'`, `estado_datos='activo'`, asociado a un empleado existente del demo-pro.

**Queries probadas:**
```
Naive 'all active' query (tenant=demo-pro):           count = 16  (era 15)
Includes the locador we just created?                  True
Safe filter (exclude locacion/consultoria):            count = 15
Delta = 1 locadores/consultores
```

**Interpretación:**
- `EmploymentData.objects.filter(tenant=t, estado_datos='activo')` — query usado típicamente para planilla — INCLUYE locadores.
- Para excluirlos, el código de planilla DEBE filtrar explícitamente `.exclude(regimen_laboral__in=['locacion','consultoria'])`.
- No existe ningún check estructural que evite que un EmploymentData con `regimen_laboral='locacion'` viva en `datos_laborales` (la tabla que la lógica de planilla 728/MyPE consulta).

**Impacto D-Pay:** Si Pay no agrega exclusión explícita, declarará locadores (4ta categoría) como trabajadores 5ta → SUNAT rechaza el PLAME. Además SUNAFIL podría considerarlo "desnaturalización de locación" (riesgo legal para el cliente).

**Mitigación inmediata:** El módulo D-Pay debe construir sus queryset base con exclusion list, o (mejor) crear un manager personalizado `EmploymentData.objects.payroll_eligible()`.

**Lo que NO probé y queda para v3:** ¿FamilyMember y AcademicRecord también se permiten para locadores? Si sí, la UI muestra como si fuera empleado regular.

---

## CASE 4 — Tenant isolation runtime (PARCIALMENTE OK, 1 LEAK CRÍTICO)

**Setup:** Creé `audit-other-temp` tenant + `audit_other_admin` user con membership + role "Administrador RRHH" en transacción rollback. Autenticado vía `APIClient(HTTP_HOST='audit-other-temp.testserver')`.

### 4a — `/api/v1/employees/` ✅ AISLA OK

```
GET /api/v1/employees/ as other_admin -> status=200
items returned: 0
demo-pro DNIs LEAKED to other_admin: 0
```

`EmpleadoViewSet` extiende `TenantAwareViewSetMixin`, el filter `queryset.filter(tenant=request.tenant)` funciona. **REFUTA la sospecha del audit previo.**

### 4b — `/api/v1/selection-stages/` ❌ LEAK CRÍTICO

```
GET /api/v1/selection-stages/?posting=<demo-pro uuid> -> status=200
items: 3
```

**`audit_other_admin` (de otro tenant) recibió 3 selection stages que pertenecen a una posting de demo-pro.**

**Causa raíz confirmada:** `SelectionStageViewSet` en `api/v1/employees/views.py:220-227` **NO extiende `TenantAwareViewSetMixin`**:
```python
class SelectionStageViewSet(viewsets.ModelViewSet):       # ← sin Mixin
    queryset = SelectionStage.objects.select_related('posting')
    permission_classes = [RRHHPermission]
    filterset_fields = ['posting', 'kind', 'is_eliminatoria']
```
Y `SelectionStage` model **NO tiene FK `tenant`** — solo se relaciona vía `posting → tenant`.

**Impacto:** Cualquier autenticado con rol RRHH puede:
- Listar stages de cualquier convocatoria (incluso de otros tenants).
- Por extensión, **mediante el JoinFilter `posting=<uuid>` enumerar postings de otros tenants** (data discovery).

**Detail-level test:** `GET /api/v1/employees/<demo-pro uuid>/ -> status=404` — aislamiento OK aquí.

**Severidad:** CRÍTICA. Es una **violación de aislamiento multi-tenant**, fundación SaaS del producto. Bloquea release.

### 4c — ORM-level: Manager no filtra por tenant

```
Employee.objects.all() count (no tenant filter):       15
Employee.objects.filter(tenant=demo-pro):              15
Employee.objects.filter(tenant=other_tenant):           0
```

El Employee manager no aplica filtro de tenant automáticamente (esperado — aislamiento es responsabilidad del viewset mixin + RLS middleware). Pero si llegado D-Pay un servicio batch (Celery task) consulta `Employee.objects.all()`, opera cross-tenant. Riesgo MEDIO si se hacen jobs batch sin contexto de tenant.

---

## CASE 5 — B.9 JobApplication transitions ✅

**Posting:** `fc25f19c-9335-4a48-babd-c2a8a9c811f8` ("Desarrollador Junior - Equipo Web"), 5 applications.

**Transiciones válidas testeadas (cada una en su propio savepoint+rollback):**
```
state=in_evaluation -> advance-to(finalist)  -> status=200 ✅
state=in_evaluation -> eliminate             -> status=200 ✅
state=in_evaluation -> withdraw              -> status=200 ✅
```

**Transición ilegal testeada:**
```
state=eliminated -> advance-to(finalist)     -> status=400 ✅
```

La state machine respeta semántica. **REFUTA preocupación del audit previo:** B.9 está bien implementado.

**Note:** la URL es `advance-to`, no `advance` (audit previo asumió el nombre incorrecto). Las llamadas requieren payload `{"new_status": "finalist"}` y `{"reason": "..."}` para eliminate.

---

## CASE 6 — PDF reporte empleado ❌ DOS BUGS BLOQUEANTES

### 6a — `generar_reporte_integral` rompe con template variable inexistente

```
EXCEPTION calling generar_reporte_integral:
  VariableDoesNotExist: Failed lookup for key [carrera_especialidad]
  in <AcademicRecord: Carlos Alberto Quispe Mamani - Universitario:
     Administración de Empresas>
```

**Causa raíz:** `templates/reportes/reporte_empleado.html:534`:
```django
{{ f.nombre_carrera|default:f.carrera_especialidad|default:"-" }}
```
Django evalúa `f.carrera_especialidad` **siempre** (no es lazy), y `AcademicRecord` model NO tiene ese atributo. El `|default:` solo se aplica al primer argumento.

**Impacto:** Cualquier empleado con AcademicRecord (es decir, todos los del seed) NO PUEDE generar reporte integral. Cualquier intento crasha.

### 6b — `generar_reporte_seccion` ImportError

```
EXCEPTION calling generar_reporte_seccion:
  ModuleNotFoundError: No module named 'apps.employees.services.pdf_generator'
```

**Causa raíz:** `employee_report_service.py:24`:
```python
def pdf_generator(self):
    if self._pdf_generator is None:
        from .pdf_generator import PDFGenerator   # ← este archivo no existe en apps/employees/services/
```
El PDF generator vive en `apps/documents/services/pdf_generator.py`, no en `apps/employees/services/`.

**Severidad:** ALTO. La feature está documentada como funcional (audit previo asumió "smoke OK"). Runtime confirma que **el reporte de empleado simplemente no funciona** en el estado actual. No bloquea D-Pay literalmente pero es feature visible al cliente que NO funciona.

**Recomendación:** Estos dos errores juntos sugieren que `EmployeeReportService` no se ejerce en ningún test automatizado. Reabrir hueco 5 del audit previo como "BLOQUEADOR runtime".

---

## CASE 7 — Practicante <18 años (Ley 28518) — REFUTA y EMPEORA

**Hipótesis del audit previo:** `validate_fecha_nacimiento` bloquea menores de 18 años, lo que rechaza practicantes legales de 16-17.

**Realidad runtime:**
```
17yo (fdn=2009-05-22):              POST status=201 ✅ creado
16yo (fdn=2010-05-22):              POST status=201 ✅ creado
15yo (debería bloquear: ILEGAL):    POST status=201 ✅ creado (ILEGAL)
```

Los TRES se crean exitosamente.

**Causa raíz:** `validate_fecha_nacimiento` existe en `EmpleadoUpdateSerializer` (líneas 580-595), pero **`EmpleadoCreateSerializer` no la usa**, igual que con DNI. Y el modelo `Employee.fecha_nacimiento` es `DateField(null=True, blank=True)` sin validators.

**Doble veredicto:**
- ✅ **Refuta el audit previo:** los practicantes 16-17 SÍ pueden darse de alta (al menos en create flow).
- ❌ **Empeora con NUEVO hallazgo:** se puede dar de alta a un niño de 15 años, lo cual **viola la Ley 28518 art. 5** (edad mínima 16 para PPP) **y la Constitución Política art. 23**.

**Impacto D-Pay:** A SUNAFIL no le importa que la `fecha_nacimiento` esté en BD; lo que importa es que el T-Registro reporte un trabajador menor de 14 años (ilegal absoluto). Pero la **responsabilidad del SaaS** es evitar habilitar esto. Si un cliente reporta y un menor sufre un accidente, hay responsabilidad civil para nuestro cliente, y reputacional para Vyntia.

**Recomendación:** Mover `validate_fecha_nacimiento` a una base mixin / parent serializer. Cambiar regla:
- Si `datos_laborales.tipo_contrato == 'practicas'` y régimen es prácticas pre-profesionales → exigir >= 16.
- En cualquier otro tipo → exigir >= 18.
- Siempre rechazar < 16.

---

## Tests nuevos creados / modificados

- `apps/api/tests/test_audit_temp_hr.py` — **CREADO como temporal, BORRO al final.** Genera la evidencia de este reporte ejecutando 7 casos contra BD real. **No incorporado a la suite permanente** (instrucciones).

## Top huecos pendientes (para hr-tester v3)

- [ ] **B.9 selection-stages tenant scoping** — Después de fix, agregar al opt-in `tenant-isolation.spec.ts` el caso "stages of foreign posting → 404".
- [ ] **Onboarding flow** que reusa `EmpleadoCreateSerializer` — sospecho mismos huecos. No testeado.
- [ ] **CASE 7 con datos_laborales='practicas'** — ¿qué pasa si el régimen es prácticas pero la edad es 35? Reverso del bug.
- [ ] **PDF reporte empleado con SECCIONES** (personal, laboral, academico, familiar) una vez resuelto el ImportError.
- [ ] **FamilyMember dependientes Renta 5ta** — `edad_para_dependencia` property aún sin test (audit anterior, no probé).
- [ ] **CAS (1057)** integral con cálculo de aguinaldo S/300 vs gratificación 1 sueldo.
- [ ] **CTS (TUO DLeg 650)** alta de empleado MyPE + cálculo de ½ CTS.
- [ ] **Tenant isolation manager-level** — ¿hay un job batch que use `Employee.objects.all()` sin tenant filter? `grep -r "Employee.objects.all\(\)" apps/`.
- [ ] **EmploymentData.unique_together = ['empleado','fecha_inicio_contrato']** sin tenant — no testeé colisión runtime cross-tenant.
- [ ] Verificar si `RRHHPermission.is_admin_user` y `EmpleadoPermission` son **case-insensitive** con todos los roles que existen en seeds antiguos.

---

## Riesgos D-Pay actualizados con prioridad

| Prio | Hueco | Bloqueante? | Notas |
|---|---|---|---|
| 1 | **DNI sin validación en create flow** | SÍ | Bloquea T-Registro, PLAME. Caso 1. |
| 2 | **Hardcoded 30 días vacaciones** | SÍ | Bloquea MyPE, prácticas, CAS. Caso 2. |
| 3 | **Locación de servicios en queries de planilla** | SÍ | Bloquea cliente con consultores. Caso 3. |
| 4 | **Tenant leak en SelectionStageViewSet** | SÍ | Bloquea release SaaS multi-tenant. Caso 4b. **Es fundación, no D-Pay**, pero D-Pay no debe lanzarse antes. |
| 5 | **Edad mínima sin enforcement** | SÍ (legal) | Habilita data ilegal en planilla. Caso 7. |
| 6 | Seed demo roles inconsistentes | NO | UX/onboarding pain pero no bloquea producción. Caso 0. |
| 7 | Reporte empleado roto | NO | Feature visible rota pero no bloquea cálculo de planilla. Caso 6. |

**Antes de iniciar D-Pay:** los items 1-5 deben tener test que falla + fix + test que pasa. Sin esto, cualquier release de planilla es un timebomb regulatorio.

---

## Acciones recomendadas (para el PM, NO ejecutadas por el tester)

- [ ] **CORTO** — Crear mixin `EmpleadoBaseSerializerValidators` con `validate_numero_documento` (8 dígitos numéricos + tenant-scoped unique), `validate_fecha_nacimiento` (edad mínima por tipo_contrato), `validate_correo_personal`. Aplicar a CreateSerializer + UpdateSerializer + OnboardingIniciarSerializer.
- [ ] **CORTO** — Diferenciar `calcular_vacaciones_pendientes()` por régimen: tabla `{'728': 30, 'mype': 15, 'practicas': lambda: 15 if antig>=12meses else 0, '1057': 30}`.
- [ ] **CORTO** — Crear manager `EmploymentData.objects.payroll_eligible()` que excluya `locacion`/`consultoria`.
- [ ] **CORTO** — Hacer `SelectionStageViewSet` extender `TenantAwareViewSetMixin` + considerar agregar FK `tenant` directo al modelo `SelectionStage` para defense-in-depth.
- [ ] **CORTO** — Fix template `reportes/reporte_empleado.html:534` — usar `{{ f.nombre_carrera|default:"-" }}` (sin segundo encadenamiento) o filtros condicionales.
- [ ] **CORTO** — Fix `employee_report_service.py:24` — import desde `apps.documents.services.pdf_generator`.
- [ ] **CORTO** — Reconciliar seed `seed_demo_pro.py` con `Roles.HR_ROLES` (crear "Administrador RRHH" en lugar de "Admin", "Analista RRHH" en lugar de "RRHH").
- [ ] **LARGO** — Agregar suite Playwright `pe-employee-edge-cases.spec.ts` (DNI inválido, edad mínima, regímenes mixtos) para cubrir lo que esta corrida levantó.

---

## Apéndice: comandos de repro

Para re-ejecutar la corrida (requiere `bd_vyntia` PG con seed `demo-pro` cargado):

```bash
cd D:/VYNTIA
source .venv/Scripts/activate
cd apps/api
DB_PASSWORD='Demenci4@' python tests/test_audit_temp_hr.py
```

El script ya fue **BORRADO** después del run para no contaminar la suite.
Si se requiere re-ejecutar, este reporte contiene la lógica completa de cada caso para re-crear el script.
