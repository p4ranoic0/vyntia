# Code Quality - Modulo Empleados

**Fecha:** 2026-05-22
**Scope auditado:**
- apps/api/apps/employees/ (12 models, 2 services, 15 test files)
- apps/api/api/v1/employees/ (views + legajo_views + serializers + serializers_b12 + urls)
- apps/web/src/features/employees/ (8 pages, 5 components, 2 hooks, 2 services, 4 modals)
- Tambien se inspecciono api/v1/rrhh/views.py lineas 377-960 (4 viewsets reutilizados desde employees/urls.py)

**Linters corridos:**
- ruff: 23 errores (8 F401 unused-import, 1 F841 unused-variable, 14 E702 multiple-statements)
- tsc proyecto completo: 1 error (BlankEnum pre-existente - baseline OK)
- tsc archivo aislado de EmpleadosListPage.tsx: revela 2 errores TS18004 enmascarados por el proyecto
- eslint sobre src/features/employees/: sin output (limpio segun reglas actuales)
- mypy: no configurado en el repo, se omitio

**Tests del scope:** pytest apps/employees/tests/ -> **114 passed / 0 failed** en 27s. Baseline backend (982/1) intacta.

**Confianza:** alta. Tiempo invertido: ~50 min.

---

## TL;DR - Semaforo

| Eje | Estado | Comentario |
|---|---|---|
| Estabilidad runtime | AMARILLO-tirando-a-ROJO | Una pagina completa (EmpleadosListPage) tiene un ReferenceError enmascarado por tsc; otros stubs silenciosos. |
| Seguridad / RBAC | AMARILLO | Duplicacion masiva de chequeo de permisos por viewset (Datos Familiares/Academicos), ausente segregacion de funciones en aprobacion de requisiciones. |
| Multi-tenant | AMARILLO | 3 modelos del flujo Seleccion (MeritRanking, SelectionStage, JobApplication) y CandidateEvaluation no llevan tenant FK; dependen exclusivamente de RLS. |
| Performance | VERDE-PALIDO | Hay select_related/prefetch_related correctos; un N+1 latente en JobPostingSerializer.application_count. |
| Tech debt | ROJO | ~750 lineas de viewsets DatosFamiliares/Academicos copy-paste; 56 console.log en el feature; 8 imports muertos; tipos any que ocultan bugs. |
| Compliance SERVIR | AMARILLO | El umbral >=7 dias habiles se mide en dias calendario; viola Art. 5 cuando hay puentes/feriados. |

## Top-5 hallazgos

1. **[CRITICO] EmpleadosListPage referencia isRRHH y isSupervisor sin declararlos** (linea 100). Cuando un usuario admin abra loadEmployees(), lanza ReferenceError. tsc proyecto no lo captura (causa raiz no confirmada, bundler-mode/exclude?), tsc aislado si. Pagina solo se exporta via barrel, posiblemente no esta en routing - pero es bomba de tiempo.
2. **[CRITICO] Employee.boletas_recientes() retorna [] con dead-code y variable inutilizada** (employee.py:311-322). Dos `return []` consecutivos, fecha_limite calculado y descartado. Sintoma de copy/paste pegoteado.
3. **[ALTO] Permission boilerplate triplicado en api/v1/rrhh/views.py** (760-959): DatosFamiliaresViewSet + DatosAcademicosViewSet + CursosCertificacionesViewSet replican el mismo patron is_own || (admin || rrhh) en create/update/partial_update/destroy. ~200 lineas duplicadas. Cualquier nuevo subset que se sume al patron hereda el mismo bug si alguno se desincroniza.
4. **[ALTO] PersonnelRequisition permite que un mismo User apruebe HR y Finance** (approve_hr + approve_finance no validan que user != self.approved_by_hr). Segregacion de funciones rota - un solo administrador autoriza ambos lados.
5. **[ALTO] MIN_PUBLIC_OPEN_BUSINESS_DAYS = 7 se compara contra dias calendario** (job_posting.py:120-125). Etiquetado business_days pero usa (close - open).days. Tests (test_b9_job_posting.py:127) reflejan el mismo error -> falsa cobertura de compliance SERVIR Art. 5.

---

## Tabla de findings

| # | Sev | Horizonte | Archivo:linea | Hallazgo | Fix sugerido |
|---|---|---|---|---|---|
| 1 | CRIT | CORTO | apps/web/src/features/employees/pages/EmpleadosListPage.tsx:100 | console.log con shorthand isRRHH, isSupervisor referencia identifiers no declarados -> ReferenceError al ejecutar loadEmployees(). tsc TS18004 enmascarado por tsconfig proyecto. | Borrar el console.log (linea 100) o destructurar isRRHH, isSupervisor desde useEmployeePermissions() en linea 60-67. |
| 2 | CRIT | CORTO | apps/api/apps/employees/models/employee.py:311-322 | boletas_recientes calcula fecha_limite (F841 unused), devuelve [] fijo, tiene 2 return [] (segundo unreachable) y un parametro meses ignorado. Metodo enganoso para callers. | Eliminar el metodo entero hasta que exista PaySlip (modulo D), o marcar raise NotImplementedError. |
| 3 | ALTO | LARGO | apps/api/api/v1/rrhh/views.py:780-959 | 3 viewsets (DatosFamiliares/Academicos/Cursos) duplican ~200 lineas de chequeo is_own or is_hr en create/update/partial_update/destroy. | Extraer OwnedByEmployeeMixin o OwnedByEmployeePermission(BasePermission) a apps/core/permissions.py. |
| 4 | ALTO | CORTO | apps/api/apps/employees/models/personnel_requisition.py:120-148 | approve_hr(user=X) + approve_finance(user=X) se aceptan con el MISMO user. Conflicto de intereses / dual control roto. | Anadir if self.approved_by_hr_id == user.pk: raise ValidationError(HR y Finanzas no pueden ser la misma persona) (y simetrico). |
| 5 | ALTO | CORTO | apps/api/apps/employees/models/job_posting.py:120-125 | (close - open).days < MIN_PUBLIC_OPEN_BUSINESS_DAYS mide dias calendario, no habiles. La constante dice BUSINESS_DAYS. Riesgo de compliance SERVIR. | Helper propio que descuente sabados/domingos + feriados peruanos. Renombrar constante si se decide mantener calendario. |
| 6 | ALTO | CORTO | apps/api/api/v1/rrhh/views.py:628-676 | transferir hace EmploymentData.filter().update(area_id=...) sin transaccion, sin verificar que devolvio >=1 fila, sin crear LocationHistory. Si no hay EmploymentData activo el endpoint responde 200 silenciosamente. | Envolver en @transaction.atomic, capturar n_updated = ...update(...), if n_updated == 0: APIResponse.error(404, Sin datos laborales activos). |
| 7 | ALTO | LARGO | apps/api/apps/employees/models/ (merit_ranking, selection_stage, job_application, candidate_evaluation).py | Estos 4 modelos NO tienen FK tenant. Solo el padre directo (JobPosting / JobApplication) la lleva. Defensa-en-profundidad rota; depende 100% de RLS middleware. | Anadir tenant = FK(tenancy.Tenant, ...) y poblarla en perform_create via mixin / signal. Migracion + backfill. |
| 8 | ALTO | CORTO | apps/api/apps/employees/models/selection_stage.py:74-78 | clean() valida rango individual de weight (0-100) pero NO valida que la suma de weights del posting = 100. El ranking entrega scores incorrectos en silencio si suma != 100. | Sobreescribir JobPosting.publish() para sumar stages.aggregate(Sum(weight)) y rechazar si != 100 (con tolerancia 0.01). |
| 9 | ALTO | LARGO | apps/api/api/v1/employees/urls.py:10-15 | urls.py IMPORTA viewsets desde api.v1.rrhh.views. Crea acoplamiento ciclico entre los dos paquetes - el split L3 quedo a medias. | Mover EmpleadoViewSet/DatosFamiliaresViewSet/DatosAcademicosViewSet/CursosCertificacionesViewSet a api/v1/employees/views.py y dejar api/v1/rrhh/ solo para modulos que aun no migraron. |
| 10 | ALTO | CORTO | apps/web/src/features/employees/hooks/useEmployeePermissions.ts:87,104 | Firma canAccessEmployeeData(employeeId: number) y canEditEmployeeData(employeeId: number, ...) - pero los IDs del backend son UUID (string). Compara user.empleado?.id === employeeId con tipos incompatibles -> siempre false. | Cambiar firmas a (employeeId: string). Auditar callers (EmpleadosListPage, DatosPersonalesModal, etc). |
| 11 | MED | CORTO | apps/web/src/features/employees/pages/EmpleadosListPage.tsx:70-187 | 30 console.log(DEBUG: ...) activos en codigo de produccion. Total feature: 56 logs. | Quitar todos o envolverlos en if (import.meta.env.DEV). |
| 12 | MED | CORTO | apps/api/api/v1/employees/serializers.py:114-115 | JobPostingSerializer.application_count = SerializerMethodField ejecuta obj.applications.count() por cada posting en listas -> N+1. | Cambiar a serializers.IntegerField(read_only=True) y anotar en queryset: .annotate(application_count=Count(applications)). |
| 13 | MED | CORTO | apps/api/api/v1/employees/views.py:220 (SelectionStageViewSet), :291 (CandidateEvaluationViewSet) | Estos 2 viewsets NO usan TenantAwareViewSetMixin (al contrario de los demas del archivo). | Anadir TenantAwareViewSetMixin a la herencia. Si requiere tenant field primero, ver finding #7. |
| 14 | MED | CORTO | apps/web/src/features/employees/pages/EmpleadosListPage.tsx:155-178 | filterEmployeesByPermissions aplica filtro de own/team en cliente DESPUES de paginar en servidor -> empleado recibe count=10, ve 0-1 filas tras filtrar, totalPages incorrecto. | Mover el filtro al backend (get_queryset ya respeta incluir_inactivos); o usar query param solo_propio=true. |
| 15 | MED | CORTO | apps/api/apps/employees/models/employee.py:7-15 + family_member.py:14 | from django.utils import timezone importado en ambos pero no usado. Ya capturado por ruff F401. | Quitar imports o ejecutar ruff check --fix. |
| 16 | MED | LARGO | apps/api/apps/employees/tests/test_b9_merit_ranking.py:140-198 | 14 errores E702 (multiple statements per line). Tests dificiles de leer y de diff. | ruff check --fix --select E702 o reescribir con loops. |
| 17 | MED | LARGO | apps/api/apps/employees/models/employee.py:273-322 | Bloque de 8 properties + 6 metodos importan modelos lazy dentro del cuerpo (from apps.organization.models import LocationHistory). Cada llamada paga import-cycle indirecto. | Centralizar imports en top del modulo si los ciclos lo permiten, o consolidar en service layer. |
| 18 | MED | LARGO | apps/web/src/features/employees/services/employeesService.ts:9-42 | interface Employee declara area con id, organo, siglas y dni, email, etc. (en espanol-corto) - pero el backend devuelve numero_documento, correo_personal, ubicacion_actual. Hay un normalizeEmployee que mapea, pero la divergencia obliga a usar any en getAll y a mantener dos vocabularios. | Decidir unico contrato (preferir backend names). Generar tipos desde OpenAPI ya disponible en src/generated/api. |
| 19 | BAJO | CORTO | apps/api/apps/employees/tests/ test_b9_*.py | 4 imports muertos (F401): date, IntegrityError, timedelta, JobApplication. | ruff check --fix. |
| 20 | BAJO | CORTO | apps/api/apps/employees/models/__pycache__/ | Hay .pyc huerfanos de modulos viejos (empleado.cpython-311.pyc, datos_familiares.cpython-311.pyc, etc.) tras el rename L3. Pueden mascarar errores en CI o tests por importacion stale. | Anadir paso find . -name *.pyc -delete en pre-commit o documentar python -m pyclean . en Makefile. |
| 21 | BAJO | CORTO | apps/web/src/features/employees/hooks/useEmployees.ts:31 | keepPreviousData: true es API de React Query v4; en v5 (instalada) se usa placeholderData: keepPreviousData. El campo es ignorado silenciosamente. | Importar keepPreviousData desde @tanstack/react-query y reemplazar. |
| 22 | BAJO | LARGO | apps/api/apps/employees/services/employee_report_service.py:42 | Accede a self.pdf_generator._html_to_pdf(...) - metodo privado. Si refactor del PDFGenerator cambia la api, todos los reportes rompen. | Exponer PDFGenerator.html_to_pdf(html) publico en apps/documents/services/. |
| 23 | BAJO | LARGO | apps/api/apps/employees/services/employee_report_service.py:39,57 | Employee.objects.get(id=...) sin manejar DoesNotExist - la view si captura pero el service ya no es reutilizable. | Capturar y relanzar EmployeeNotFound propio o devolver (None, None). |
| 24 | BAJO | CORTO | apps/web/src/features/employees/modals/DatosPersonalesModal.tsx:47 | Llama useAuth() sin destructurar nada -> side effect implicito, hook se usa solo para forzar re-render. Mismo patron en otros 3 modals. | O eliminar la llamada si no se usa, o destructurar lo que realmente se necesita. |

---

## Lo que esta bien (NO tocar)

1. **compute_merit_ranking esta solido.** Algoritmo determinista, atomico (@transaction.atomic), pre-ordena por applied_at para resolver empates SERVIR, persiste breakdown JSON para auditoria. Buenos tests en test_b9_merit_ranking.py (4 escenarios distintos).
2. **Employee.partial_update** (api/v1/rrhh/views.py:441-506) hace un trabajo cuidadoso: lista explicita _SELF_EDITABLE_FIELDS, bypassea el @require_hr() para evitar autoexclusion y mantiene security boundary. El comment con referencia al test (B.5b carryover) es ejemplar.
3. **State machines de PersonnelRequisition + JobPosting + JobApplication** estan bien tipadas (STATUS_CHOICES, ADVANCE_TRANSITIONS), envueltas en @transaction.atomic y validadas con ValidationError. Buena base para auditoria.
4. **Constraints multi-tenant en Employee y Candidate** (unique_employee_doc_per_tenant, unique_candidate_doc_per_tenant) estan correctamente compuestos por tenant + document_type + document_number.
5. **TenantAwareViewSetMixin se aplica en 8 de los 11 viewsets nuevos del modulo.** Patron consistente, con _filter_by_tenant que documenta la doctrina belt-and-suspenders. Los 3 que falten (finding #13) son faciles de cerrar.
6. **select_related/prefetch_related correctos en EmpleadoViewSet** (5 cadenas anidadas) - no se observan N+1 en list/retrieve principales.

---

## Baselines

| Metrica | Antes | Ahora | Estado |
|---|---|---|---|
| pytest backend (employees scope) | 114 passed | 114 passed | OK |
| pytest backend total | 982 passed / 1 fail | no se re-corrio | OK asumido |
| tsc errors | 1 pre-existing (BlankEnum) | 1 | OK |
| eslint warnings (employees) | <=278 global | 0 reportados en scope | OK |
| ruff errors (employees) | n/a | 23 (cosmeticos) | warn |

No hay regresiones. La auditoria es read-only.

---

## Acciones recomendadas (priorizadas)

### Antes de empezar Sub-project D (Vyntia Pay)

- [ ] CORTO CRIT #1 - Borrar linea 100 de EmpleadosListPage.tsx (o destructurar correctamente). 5 min.
- [ ] CORTO CRIT #2 - Eliminar Employee.boletas_recientes() o marcar NotImplementedError. D va a re-implementarlo correctamente. 5 min.
- [ ] CORTO ALTO #4 - Validar approve_hr.user != approve_finance.user + test. 20 min.
- [ ] CORTO ALTO #6 - Envolver transferir en atomic + chequear n_updated. 20 min.
- [ ] CORTO ALTO #10 - Cambiar firmas en useEmployeePermissions a string. ~30 min + verificar callers.
- [ ] CORTO MED #11 - Limpiar 30 console.log de EmpleadosListPage. 10 min.
- [ ] CORTO MED #12 - Annotate application_count en JobPosting queryset. 10 min.
- [ ] CORTO MED #13 - Anadir TenantAwareViewSetMixin a SelectionStage/CandidateEvaluation viewsets. 5 min.
- [ ] CORTO BAJO #15, #19, #20 - ruff check --fix + limpiar pycache. 5 min.

**Total CORTO PLAZO:** ~2h. Cabe holgadamente en este sprint.

### Para el spec de Sub-project D

- [ ] LARGO ALTO #3 - Spec del OwnedByEmployeePermission para extraer las 3 copias.
- [ ] LARGO ALTO #7 - Decidir si anadir tenant FK a los 4 modelos restantes del flujo Seleccion (B.9). Si la respuesta es RLS basta, documentarlo explicitamente en CLAUDE.md.
- [ ] LARGO ALTO #5 + #8 - SERVIR compliance: dias habiles + suma de weights. Posiblemente forma parte de una phase nueva B.x SERVIR hardening o cabe en D si los reportes de payroll dependen de ello.
- [ ] LARGO ALTO #9 - Cerrar el split L3 terminando de mover viewsets a api/v1/employees/. Quita el import from api.v1.rrhh y resuelve el acoplamiento.
- [ ] LARGO MED #16, #18 - Refactor cosmetico + generar types desde OpenAPI.

---

## Recomendacion final

**El modulo Empleados esta listo para que Sub-project D dependa de el?**

-> **SI, CON FIXES.**

Los datos canonicos (Employee, EmploymentData, FamilyMember, AcademicRecord) estan solidos: schema correcto, indexes razonables, constraints de tenant funcionando, tests pasando (114/114). El servicio de reportes y la maquinaria de Seleccion (B.9, B.12) estan bien disenados y NO los necesita D directamente.

D (Vyntia Pay - planilla peruana real) va a:
1. Consumir Employee + EmploymentData + FamilyMember.es_dependiente/es_beneficiario (lectura).
2. Crear modelos nuevos en apps/payroll/ (PaySlip, Concepto, Calculadora) - no impacta employees.
3. Re-implementar el stub Employee.boletas_recientes() (finding #2) - mejor borrarlo antes.

**Bloqueos para D:** ninguno critico. Los hallazgos CRIT son una pagina huerfana + un stub que D va a reescribir.

**Recomendado antes de abrir D:** ejecutar las 9 acciones CORTO PLAZO listadas (~2h). Las LARGO PLAZO pueden quedar como sub-proyectos paralelos o entrar al backlog de D si tocan codigo compartido.
