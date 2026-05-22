# Code Quality - Empleados (segunda corrida con BD poblada)

**Fecha:** 2026-05-22  
**Scope:** mismo que la primera corrida (apps/api/apps/employees/, api/v1/employees/, api/v1/rrhh/views.py 377-960, apps/web/src/features/employees/)  
**Modo:** runtime - tenant demo-pro con 15 empleados / 5 candidatos / 1 posting / 5 applications / 3 dossiers.  
**Referencia previa:** docs/agent-reports/code-quality/2026-05-22-empleados.md. No se duplican hallazgos ya documentados; se confirman, refutan o se reportan nuevos.

**Linters / tests corridos:**
- pytest apps/employees/tests/ --no-cov -> **114 passed** (baseline employees scope intacto).
- pytest --collect-only -> 1003 tests recolectados (consistente con baseline backend).
- npx tsc --noEmit -p tsconfig.app.json -> 1 error pre-existente (BlankEnum). Baseline intacta.
- Eslint y ruff no se re-corrieron (cambios cero desde la primera auditoria).

**Tiempo invertido:** ~45 min. **Confianza:** alta.

---

## TL;DR - Semaforo (actualizado tras runtime)

| Eje | Antes | Ahora | Comentario |
|---|---|---|---|
| Estabilidad runtime | AMBAR-ROJO | **AMBAR (rebajado)** | EmpleadosListPage es DEAD CODE (no esta enrutado en App.tsx). El ReferenceError de isRRHH/isSupervisor no afecta a producto en vivo. |
| Seguridad / RBAC | AMBAR | **ROJO (escalado)** | Confirmado runtime: el mismo usuario puede aprobar HR y Finanzas. El seed REQ-DEMO-001 queda en status=approved SIN aprobadores (hr=None, fin=None) - bypassea por completo el workflow. Dos bugs separados. |
| Multi-tenant | AMBAR | AMBAR | Sin cambios. RLS opera correctamente bajo tenant_context(). |
| Performance | VERDE-PALIDO | **ROJO (escalado)** | NUEVO: EmpleadoViewSet.list() devuelve 15 empleados con 73 queries (cold). N+1 visible: 31x datos_laborales, 16x area, 16x historial_ubicaciones. prefetch_related esta DEFINIDO pero los helpers en serializer no lo usan. |
| Tech debt | ROJO | ROJO | Sin cambios. |
| Compliance SERVIR | AMBAR | **CONFIRMADO en runtime** | Sintetico: posting con open=2026-05-01, close=2026-05-08 (7 dias calendario = ~5 habiles) pasa la validacion. |

## Top hallazgos (nuevos / confirmados-en-runtime)

1. **[CRIT - CONFIRMADO RUNTIME] PersonnelRequisition: dual-control roto + seed bypassea workflow.** Test ejecutado en demo-pro (apps/employees/models/personnel_requisition.py:120-148): req.approve_hr(user=admin) seguido de req.approve_finance(user=admin) deja approved_by_hr_id == approved_by_finance_id == admin.id y status=approved. Adicionalmente, el seed seed_demo_pro.py:553 crea la requisicion con status=approved DIRECTAMENTE, sin pasar por approve_hr/approve_finance, dejando hr=None / fin=None / approved_at=None. Dos bugs distintos: (a) ausencia de validacion user != self.approved_by_hr; (b) ausencia de invariant status=approved => approved_by_hr_id IS NOT NULL AND approved_by_finance_id IS NOT NULL (CHECK constraint o save() guard).

2. **[ALTO - NUEVO en runtime] N+1 confirmado en EmpleadoListSerializer.** Con 15 empleados, la list view consumio **73 queries** (cold). Patron:
   - 31x SELECT FROM datos_laborales WHERE empleado_id=? AND estado_datos=activo (helper obj.datos_laborales_actuales() llamado 2 veces por fila, en get_ubicacion_actual y get_datos_laborales_resumen).
   - 16x SELECT FROM area WHERE id=? (acceso a .area derivado del datos_laborales recien fetcheado, fuera del prefetch_related).
   - 16x SELECT FROM historial_ubicaciones WHERE empleado=? AND estado_ubicacion=activo (helper obj.ubicacion_actual()).
   - Causa raiz: EmpleadoViewSet.queryset prefetches datos_laborales__area y historial_ubicaciones__area_destino, pero Employee.datos_laborales_actuales() y Employee.ubicacion_actual() construyen QuerySets nuevos via EmploymentData.objects.filter(empleado=self,...) y LocationHistory.objects.filter(empleado=self,...), bypaseando el prefetch. Con 100 empleados esto escala a ~470 queries.

3. **[CRIT - CONFIRMADO RUNTIME] Employee.boletas_recientes() es stub silencioso.** Invocado contra empleado real: devuelve [] y NO lanza. Riesgo de carga cognitiva en D - cualquier dev de Vyntia Pay que vea el metodo asumira que existe data y construira UI sobre [].

4. **[CRIT -> MED RECLASIFICADO] EmpleadosListPage.tsx es codigo huerfano.** Confirmado: App.tsx enruta Empleados (mayuscula, Empleados.tsx), NO EmpleadosListPage.tsx. El ReferenceError de isRRHH/isSupervisor (linea 100) sigue existiendo pero ES IMPOSIBLE alcanzarlo desde la app en produccion. El finding cae de CRITICO a MEDIO: es deuda de codigo muerto. Fix: borrar el archivo + barrel export.

5. **[ALTO - CONFIRMADO RUNTIME] SERVIR Art. 5: 7 dias calendario pasa validacion.** Test sintetico: JobPosting(sector_mode=public_servir, open=2026-05-01, close=2026-05-08, bases_url=..., transparency_published=True)._validate_servir_publication_requirements() NO levanta ValidationError. El campo MIN_PUBLIC_OPEN_BUSINESS_DAYS=7 en job_posting.py:121 se compara contra (close-open).days (calendario, no habiles).

---

## Tabla de findings (delta respecto a primera auditoria)

| # nuevo | Sev | Horiz. | Archivo:linea | Estado | Hallazgo / Evidencia runtime |
|---|---|---|---|---|---|
| **N1** | ALTO | CORTO | api/v1/rrhh/serializers.py:632-666 + apps/employees/models/employee.py:273-287 | **NUEVO** | N+1 real: 15 empleados -> 73 queries. get_ubicacion_actual + get_datos_laborales_resumen llaman 2x cada uno a obj.datos_laborales_actuales() y obj.ubicacion_actual(), ambos construyen QuerySets que ignoran el prefetch_related. Fix: usar @cached_property en Employee, o reemplazar helpers por list(self.datos_laborales.all()) en Python; alternativamente anotar la list con Prefetch(datos_laborales, queryset=EmploymentData.objects.filter(estado_datos=activo)) y reescribir helpers para usar self.datos_laborales.all() en vez de .filter(). |
| **N2** | CRIT | CORTO | apps/employees/models/personnel_requisition.py + apps/tenancy/management/commands/seed_demo_pro.py:541-555 | **NUEVO (complementa #4 anterior)** | El seed crea REQ-DEMO-001 con status=approved directo, sin aprobadores (hr=None, fin=None, approved_at=None). El modelo carece de invariant: nada impide approved con aprobadores nulos. Fix: anadir clean() que valide coherencia status / aprobadores; CHECK constraint en migracion; reescribir seed para llamar approve_hr(user=hr_user) + approve_finance(user=finance_user) con usuarios DISTINTOS. |
| **N3** | ALTO | CORTO | apps/tenancy/management/commands/seed_demo_pro.py:541-555 | **NUEVO** | El seed no crea CandidateEvaluations ni MeritRankings (verificado: 0 filas). El posting esta in_evaluation con 3 stages y 5 apps, pero el ranking nunca se ejercita en demo. No bloquea D, pero vacia el showcase comercial. Fix: anadir _seed_evaluations() que invoque compute_merit_ranking. |
| **N4** | MED | CORTO | apps/web/src/features/employees/pages/EmpleadosListPage.tsx + pages/index.ts:8 | **RECLASIFICADO desde CRIT** | El ReferenceError de la primera auditoria es real, pero la pagina NO esta enrutada en App.tsx (la pagina real es Empleados.tsx). Codigo muerto. Fix: borrar EmpleadosListPage.tsx y la linea de export en pages/index.ts. |
| **N5** | MED | CORTO | apps/employees/models/employee.py:281-287 | **NUEVO** | Employee.datos_laborales_actuales() NO usa .select_related(area, jefe_directo) aunque los serializers acceden .area.siglas_area inmediatamente. Cada fila paga +1 query por area. Fix: anadir .select_related(area, jefe_directo) al return. |
| **N6** | BAJO | CORTO | tests | **VERIFICADO** | pytest apps/employees/tests/ 114/114 PASS. pytest --collect-only 1003 tests (vs 1000 documentado en CLAUDE.md - probable +3 desde B16). |

### Findings de la primera auditoria - status update

| # original | Status post-runtime |
|---|---|
| 1 (EmpleadosListPage ReferenceError) | **DEGRADAR a MED.** Codigo huerfano, no enrutado. Ver N4. |
| 2 (boletas_recientes stub) | **CONFIRMADO RUNTIME.** Empleado real devuelve []. Mantener CRIT. |
| 3 (Permission boilerplate triplicado) | Sin cambios. Validacion runtime no aplicable. |
| 4 (PersonnelRequisition dual control roto) | **CONFIRMADO RUNTIME + escalado.** Ver N2 - hay TAMBIEN bug de invariant en el seed. |
| 5 (MIN_PUBLIC_OPEN_BUSINESS_DAYS vs calendar) | **CONFIRMADO RUNTIME.** Sintetico pasa validacion con 7 dias calendario. |
| 6 (transferir sin atomic) | No re-validado runtime. Sin cambios. |
| 7 (4 modelos seleccion sin tenant FK) | Sin cambios. |
| 8 (suma weights no validada) | No re-validado runtime (no hay weights significativos en seed - solo 3 stages stub). |
| 9 (urls.py acoplamiento) | Sin cambios. |
| 10 (canAccessEmployeeData(number) vs UUID) | **CONFIRMADO RUNTIME.** Empleado real tiene id=099caf15-afac-4af4-be63-64966ed02266 (UUID string). El check user.empleado?.id === employeeId con employeeId tipado number siempre seria falso. |
| 11 (56 console.log) | Sin cambios. |
| 12 (JobPostingSerializer.application_count) | **CONFIRMADO RUNTIME (parcial).** Con 1 posting solo +1 query, pero el patron sigue siendo N+1 si crece. |
| 13-24 | Sin cambios. |

---

## Performance: hits totales

| Endpoint | Empleados retornados | Queries cold | Queries cached | Diagnostico |
|---|---|---|---|---|
| GET /api/v1/employees/empleados/?page_size=50 | 15 | **73** | 6 | N+1 severo en serializer (N1) |
| JobPostingSerializer(qs, many=True) | 1 | 2 | 2 | N+1 latente, no amplificado con N=1 |

Conclusion: la list de empleados es la unica vista con N+1 confirmada y severa. Con prefetch_related ya en su lugar, el fix es de baja superficie: corregir los helpers para que usen .datos_laborales.all() (respeta prefetch) en lugar de re-querying.

---

## Suite de tests: status

| Suite | Antes | Ahora | Delta |
|---|---|---|---|
| pytest apps/employees/tests/ --no-cov | 114 passed | **114 passed** | 0 |
| pytest --collect-only (total) | 982 documentado | 1003 collected | +21 (probable B16) |
| frontend tsc -p tsconfig.app.json | 1 (BlankEnum) | **1 (BlankEnum)** | 0 |
| frontend vitest | 178 | no re-corrido | n/a |

No hay regresiones.

---

## Veredicto actualizado: Sub-project D (Vyntia Pay) puede depender de Empleados?

**-> SI, CON FIXES** (mismo veredicto que la primera auditoria, ahora con mas evidencia).

Bloqueos NUEVOS (visibles solo con BD poblada):
1. **CRIT - corregir/eliminar Employee.boletas_recientes() antes de D.** Confirmado runtime. D lo va a re-implementar; mejor borrarlo ya para evitar collision de nombres.
2. **ALTO - arreglar N+1 en EmpleadoListSerializer antes de D.** D va a consumir EmpleadoViewSet.list o variantes para asociar PaySlip <-> Empleado. Si arranca con 73 queries para 15 empleados, escalara muy mal en clientes reales.
3. **CRIT - PersonnelRequisition seed + dual-control.** No bloquea a D directamente (D no usa requisitions), pero bloquea cualquier demo comercial seria - un auditor SERVIR vera un seed con bypass.

No bloqueos para D:
- Los 15 empleados, EmploymentData, FamilyMember estan integros y consultables.
- DigitalDossier (3) y JobPosting (1) funcionan sin errores de signals/integridad.
- 114 tests employees PASS.

Recomendacion antes de abrir D:
- 2h CORTO PLAZO de la auditoria previa (sigue valida)
- + 30min: arreglar N+1 helpers en employee.py:273-287
- + 15min: anadir CHECK / clean() para invariant approved => aprobadores no nulos
- + 5min: borrar EmpleadosListPage.tsx (codigo muerto)

Total ~3h, sigue cabiendo en el sprint actual.

---

## Pregunta para humano

IMPORTANTE: la savepoint de tests runtime no funciono (las mutaciones del test 1 persistieron a la BD pese a transaction.savepoint_rollback - el shell de manage.py no opera dentro de una transaccion outer, asi que savepoint no tiene anidamiento sobre el cual rebobinar). Tuve que ejecutar un script de restauracion explicito para devolver REQ-DEMO-001 al estado seed original (status=approved, hr=None, fin=None, approved_at=None). Confirme que el tenant esta restaurado, pero recomiendo correr `python manage.py seed_demo_pro` una vez mas antes de cualquier demo para garantizar 100% paridad con la fixture original. (Este reporte es read-only del codigo de producto; la mutacion ocurrio en datos seed, no en codigo.)
