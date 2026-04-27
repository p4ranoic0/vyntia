"""AppConfig for the `apps.onboarding` Django app — VYNTIA new-employee onboarding.

Owns the onboarding workflow:
- OnboardingProcess (per-employee onboarding state machine: pendiente_datos →
  pendiente_documentos → pendiente_validacion → completado/observado)
  - Tracks completeness checklist: datos_personales, datos_laborales, dni,
    declaraciones_juradas, certificados_academicos, certificados_trabajo,
    documentos_familiares
  - Tracks RRHH validation, welcome-email status, completion timestamps

Owned services (onboarding orchestration):
- onboarding_service.py — contains:
  - OnboardingService: main workflow (crear_onboarding_completo, actualizar_estado_onboarding,
    obtener_documentos_pendientes, reenviar_email_bienvenida, etc.)
  - OnboardingNotificationService: email notifications + status change events

Bounded context boundary: onboarding owns the new-employee setup workflow and
its state machine. Personal data lives in `apps.employees`, document storage
in `apps.documents`. The Celery task `send_email_html_task` lives in
`app_rrhh.tasks` (deferred legacy module — used by both onboarding_service
and other email-sending paths; will be relocated in L3.11 cleanup).

Future rename (deferred to L3.10):
- OnboardingProcess → OnboardingProcess
- OnboardingService → OnboardingProcessService
- OnboardingNotificationService → OnboardingNotificationService (keep — already English)
"""

from django.apps import AppConfig


class OnboardingConfig(AppConfig):
    name = "apps.onboarding"
    label = "onboarding"
    verbose_name = "VYNTIA Onboarding"
