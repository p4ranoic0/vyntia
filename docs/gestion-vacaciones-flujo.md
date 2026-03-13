# Gestion De Vacaciones: Reglas Y Flujo

## Objetivo
Implementar el flujo de vacaciones desde solicitud del empleado hasta autorizacion por jefe inmediato y RRHH, con control por periodos anuales y trazabilidad para contratos historicos.

## Reglas De Negocio Implementadas
- Cada periodo anual genera `30` dias de vacaciones.
- El periodo es por aniversario, no por año calendario.
  - Ejemplo: ingreso/contrato inicia `2025-04-15` => primer periodo `2025-04-15` a `2026-04-14`.
- Un empleado puede tener varios contratos:
  - Las solicitudes nuevas usan el contrato activo.
  - Los periodos historicos quedan consultables para reportes.
  - Cada período queda asociado al contrato correspondiente.
- Adelanto vacacional:
  - Se calcula con `2.5` dias por cada mes cumplido del contrato.
  - Se descuenta lo ya aprobado como `adelanto_vacaciones`.
- Regla de viernes:
  - Si la vacacion inicia o termina viernes, se contabilizan sabado y domingo adicionales en el descuento.
- Se controla por periodo:
  - `dias_gozados`, `dias_pendientes`, `dias_vencidos`.
- Flujo de aprobacion:
  - `borrador` -> `en_revision` (jefe) -> `aprobada_jefe` (si requiere RRHH) -> `aprobada`.
  - Rechazo y cancelacion con motivo y auditoria.

## Arquitectura Aplicada
- Backend (reglas y flujo):
  - `back/app_rrhh/services/vacation_calculation_service.py`
  - `back/app_rrhh/services/vacation_service.py`
  - `back/app_rrhh/services/vacation_approval_service.py`
  - `back/app_rrhh/services/vacation_admin_service.py`
- API vacaciones:
  - `back/api/v1/vacaciones/serializers.py`
  - `back/api/v1/vacaciones/views.py`
  - `back/api/v1/vacaciones/filters.py`
  - `back/api/v1/vacaciones/permissions.py`
- Frontend service (compatibilidad con pantallas actuales):
  - `front/src/services/vacacionesService.ts`

## Endpoints Principales
- Solicitudes:
  - `POST /api/v1/vacaciones/solicitudes/` (crea y envia a aprobacion)
  - `POST /api/v1/vacaciones/solicitudes/{id}/enviar/`
  - `POST /api/v1/vacaciones/solicitudes/{id}/aprobar-jefe/`
  - `POST /api/v1/vacaciones/solicitudes/{id}/aprobar-rrhh/`
  - `POST /api/v1/vacaciones/solicitudes/{id}/cancelar/`
- Pendientes:
  - `GET /api/v1/vacaciones/solicitudes/pendientes-jefe/`
  - `GET /api/v1/vacaciones/solicitudes/pendientes-rrhh/`
  - `GET /api/v1/vacaciones/solicitudes/mis-solicitudes/`
- Periodos:
  - `GET /api/v1/vacaciones/periodos/`
  - `POST /api/v1/vacaciones/periodos/generar-masivo/`
  - `POST /api/v1/vacaciones/periodos/{id}/ajustar-dias/`
- Reportes:
  - `GET /api/v1/vacaciones/reportes/estadisticas/`
  - `GET /api/v1/vacaciones/reportes/dias-vencidos/`
  - `GET /api/v1/vacaciones/reportes/reporte-solicitudes/`
    - Filtro opcional `contrato_id` para reportar por contrato.
  - `GET /api/v1/vacaciones/reportes/reporte-empleado/?empleado_id=...&contrato_id=...`
    - Genera PDF del reporte de vacaciones por empleado.

## Notas Tecnicas
- Se corrigieron referencias a campos inexistentes que rompian serializers, filtros y servicios.
- Se mantuvo compatibilidad en frontend mapeando payloads/respuestas al formato usado por las paginas actuales.
- Los calculos se centralizaron en `VacationCalculationService` para evitar duplicidad.
- Validacion de feriados y descansos medicos puede configurarse por settings:
  - `VACATION_HOLIDAYS = ["YYYY-MM-DD", ...]`
  - `VACATION_MEDICAL_LEAVES = [{"empleado_id": 1, "inicio": "YYYY-MM-DD", "fin": "YYYY-MM-DD"}]`
- Al enviar solicitud con aprobacion de jefe, se envia email automatico al jefe directo.
  - Usa `DEFAULT_FROM_EMAIL` y `FRONTEND_URL` para el enlace al sistema.
