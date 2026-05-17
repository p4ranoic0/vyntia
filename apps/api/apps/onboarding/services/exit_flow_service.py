"""exit_flow_service — coordinación operativa del cese (B.14).

Una sola entry-point `scaffold_exit_flow(termination)` crea los 3 hijos
operativos (ExitInterview, HandoverChecklist + 4 items default,
SystemsOffboarding con 6 systems checks default). Resto del API son
operaciones de transición individuales que las pages frontend invocan.

See Module 03.7 of docs/modulos/03_gestion_empleo.md and BACKLOG #126.
"""
from __future__ import annotations

from django.db import transaction

from apps.onboarding.models import (
    ExitInterview,
    HandoverChecklist,
    HandoverItem,
    SystemsOffboarding,
)


DEFAULT_HANDOVER_ITEMS = [
    {
        'kind': 'proyecto',
        'name': 'Proyectos en curso',
        'description': 'Listado y estado actual de proyectos asignados',
        'is_required': True,
        'order': 1,
    },
    {
        'kind': 'documento',
        'name': 'Documentación y archivos',
        'description': 'Carpetas, manuales, plantillas y entregables',
        'is_required': True,
        'order': 2,
    },
    {
        'kind': 'equipo',
        'name': 'Equipos y activos físicos',
        'description': 'Laptop, periféricos, fundas, mobiliario asignado',
        'is_required': True,
        'order': 3,
    },
    {
        'kind': 'acceso',
        'name': 'Accesos y credenciales',
        'description': 'Llaves, badges, tarjetas de acceso físico',
        'is_required': True,
        'order': 4,
    },
]

DEFAULT_SYSTEMS_CHECKS = {
    'correo': False,
    'vpn': False,
    'erp': False,
    'ad': False,
    'badge': False,
    'llaves': False,
}


@transaction.atomic
def scaffold_exit_flow(termination, *, user=None) -> dict:
    """Create ExitInterview + HandoverChecklist (+4 items) + SystemsOffboarding.

    Idempotente: si ya existen, los reutiliza.
    """
    tenant = termination.tenant

    interview, _ = ExitInterview.objects.get_or_create(
        termination=termination,
        defaults={'tenant': tenant},
    )

    checklist, checklist_created = HandoverChecklist.objects.get_or_create(
        termination=termination,
        defaults={'tenant': tenant},
    )
    if checklist_created:
        HandoverItem.objects.bulk_create([
            HandoverItem(
                checklist=checklist,
                kind=item['kind'],
                name=item['name'],
                description=item['description'],
                is_required=item['is_required'],
                order=item['order'],
            )
            for item in DEFAULT_HANDOVER_ITEMS
        ])

    systems, systems_created = SystemsOffboarding.objects.get_or_create(
        termination=termination,
        defaults={
            'tenant': tenant,
            'checks': DEFAULT_SYSTEMS_CHECKS.copy(),
        },
    )
    if systems_created and not systems.checks:
        systems.checks = DEFAULT_SYSTEMS_CHECKS.copy()
        systems.save(update_fields=['checks', 'updated_at'])

    return {
        'interview': interview,
        'checklist': checklist,
        'systems_offboarding': systems,
    }


def mark_interview_done(
    interview: ExitInterview, *,
    answers, sentiment, comments='', interviewer=None, interview_date=None,
) -> ExitInterview:
    interview.mark_completed(
        answers=answers,
        sentiment=sentiment,
        comments=comments,
        interviewer=interviewer,
        interview_date=interview_date,
    )
    return interview


def mark_item_delivered(
    item: HandoverItem, *, user=None, notes='',
) -> HandoverItem:
    item.mark_delivered(user=user, notes=notes)
    return item


def mark_item_no_aplica(item: HandoverItem, *, notes='') -> HandoverItem:
    item.mark_no_aplica(notes=notes)
    return item


def complete_handover(
    checklist: HandoverChecklist, *,
    signed_by_outgoing, signed_by_incoming,
) -> HandoverChecklist:
    checklist.mark_completed(
        signed_by_outgoing=signed_by_outgoing,
        signed_by_incoming=signed_by_incoming,
    )
    return checklist


def complete_systems_offboarding(
    offboarding: SystemsOffboarding, *,
    checks, user=None, notes='',
) -> SystemsOffboarding:
    offboarding.mark_completed(checks=checks, user=user, notes=notes)
    return offboarding
