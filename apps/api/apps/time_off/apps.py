"""AppConfig for the `apps.time_off` Django app — VYNTIA vacations & leave management.

Owns the time-off and vacation entities of the HR system:
- ConfiguracionVacaciones (per-area/employee/cargo vacation rules: days/year, accrual,
  approval levels, fragmentation policy)
- PeriodoVacacional (annual vacation period per employee with corresponding/used/pending days)
- SolicitudVacaciones (vacation request workflow: borrador -> enviada -> aprobada -> en_goce -> finalizada)
- GoceVacaciones (actual vacation enjoyment record with start/end dates and interruptions)
- HistorialSolicitudVacaciones (audit trail of all state transitions on requests)

Owned services (vacation workflow engines):
- vacation_service.py — main vacation request orchestration
- vacation_approval_service.py — jefe + RRHH approval workflow
- vacation_admin_service.py — configuracion/periodo CRUD
- vacation_calculation_service.py — periodo creation, day calculation, advances
- vacation_report_service.py — historical reports and summaries

Owned managers (custom QuerySet methods):
- ConfiguracionVacacionesManager, PeriodoVacacionalManager, SolicitudVacacionesManager,
  GoceVacacionesManager, HistorialSolicitudVacacionesManager (in managers.py)

Bounded context boundary: time_off owns the vacation entitlement, request workflow,
and enjoyment tracking. Personal data lives in `apps.employees`, contract data in
`apps.contracts`, and approval permissions still go through `app_rrhh.permission_service`
(deferred legacy module).

Future split (deferred to L3.10):
- SolicitudVacaciones -> VacationRequest + VacationBalance (model split + data migration)

Future rename (deferred to L3.10):
- ConfiguracionVacaciones -> VacationPolicy
- PeriodoVacacional -> VacationPeriod
- SolicitudVacaciones -> VacationRequest
- GoceVacaciones -> VacationLeave
- HistorialSolicitudVacaciones -> VacationRequestHistory
"""

from django.apps import AppConfig


class TimeOffConfig(AppConfig):
    name = "apps.time_off"
    label = "time_off"
    verbose_name = "VYNTIA Time Off"
