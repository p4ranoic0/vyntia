"""Tests for B.14 exit_flow_service + ExitInterview/HandoverChecklist/SystemsOffboarding."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.contracts.models import Contract, Termination
from apps.employees.models import Employee
from apps.identity.models import User
from apps.onboarding.models import (
    ExitInterview,
    HandoverChecklist,
    HandoverItem,
    SystemsOffboarding,
)
from apps.onboarding.services import exit_flow_service
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='TI', siglas_area='TI', estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='75757575', tipo_documento='DNI',
        nombres_empleado='Yamile', apellido_paterno='Tinoco',
        apellido_materno='Salas', fecha_nacimiento=date(1989, 8, 8),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14EXIT-001', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=400),
        salario_bruto=Decimal('4500.00'), cargo='Desarrolladora', status='ACTIVO',
    )


@pytest.fixture
def termination(contract, employee):
    return Termination.objects.create(
        contract=contract, employee=employee,
        regimen='728', causal='renuncia',
        fecha_cese=date.today(),
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b14exit', email='hr_b14exit@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def receiving_user(db):
    return User.objects.create(
        username='recv_b14', email='recv_b14@test.local',
        tipo_usuario='colaborador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestScaffold:
    def test_scaffold_creates_three_entities(self, termination):
        out = exit_flow_service.scaffold_exit_flow(termination)
        assert isinstance(out['interview'], ExitInterview)
        assert isinstance(out['checklist'], HandoverChecklist)
        assert isinstance(out['systems_offboarding'], SystemsOffboarding)
        assert out['checklist'].items.count() == 4
        assert set(out['systems_offboarding'].checks.keys()) == {
            'correo', 'vpn', 'erp', 'ad', 'badge', 'llaves',
        }

    def test_scaffold_is_idempotent(self, termination):
        first = exit_flow_service.scaffold_exit_flow(termination)
        second = exit_flow_service.scaffold_exit_flow(termination)
        assert first['interview'].pk == second['interview'].pk
        assert first['checklist'].items.count() == second['checklist'].items.count()


@pytest.mark.django_db
class TestExitInterviewLifecycle:
    def test_mark_completed_persists_answers(self, termination, hr_user):
        out = exit_flow_service.scaffold_exit_flow(termination)
        interview = out['interview']
        exit_flow_service.mark_interview_done(
            interview,
            answers={'p1': 'positiva', 'p2': 'aprendí mucho'},
            sentiment='positivo',
            comments='Gracias por la oportunidad',
            interviewer=hr_user,
        )
        interview.refresh_from_db()
        assert interview.status == 'completed'
        assert interview.sentiment == 'positivo'
        assert interview.answers['p1'] == 'positiva'

    def test_mark_completed_requires_answers(self, termination, hr_user):
        out = exit_flow_service.scaffold_exit_flow(termination)
        interview = out['interview']
        with pytest.raises(ValidationError):
            exit_flow_service.mark_interview_done(
                interview, answers={}, sentiment='neutral', interviewer=hr_user,
            )


@pytest.mark.django_db
class TestHandoverLifecycle:
    def test_complete_checklist_requires_all_required_items(
        self, termination, hr_user, receiving_user,
    ):
        out = exit_flow_service.scaffold_exit_flow(termination)
        checklist = out['checklist']
        with pytest.raises(ValidationError):
            exit_flow_service.complete_handover(
                checklist,
                signed_by_outgoing=hr_user,
                signed_by_incoming=receiving_user,
            )
        for item in checklist.items.all():
            exit_flow_service.mark_item_delivered(item, user=hr_user)
        exit_flow_service.complete_handover(
            checklist,
            signed_by_outgoing=hr_user,
            signed_by_incoming=receiving_user,
        )
        checklist.refresh_from_db()
        assert checklist.status == 'completed'
        assert checklist.signed_by_incoming == receiving_user

    def test_item_no_aplica_counts_as_resolved(self, termination, hr_user, receiving_user):
        out = exit_flow_service.scaffold_exit_flow(termination)
        checklist = out['checklist']
        items = list(checklist.items.all())
        exit_flow_service.mark_item_no_aplica(items[0], notes='no asignado')
        for item in items[1:]:
            exit_flow_service.mark_item_delivered(item, user=hr_user)
        exit_flow_service.complete_handover(
            checklist,
            signed_by_outgoing=hr_user,
            signed_by_incoming=receiving_user,
        )
        checklist.refresh_from_db()
        assert checklist.status == 'completed'


@pytest.mark.django_db
class TestSystemsOffboarding:
    def test_complete_requires_all_checks_true(self, termination, hr_user):
        out = exit_flow_service.scaffold_exit_flow(termination)
        sysoff = out['systems_offboarding']
        with pytest.raises(ValidationError):
            exit_flow_service.complete_systems_offboarding(
                sysoff,
                checks={'correo': True, 'vpn': False, 'erp': True, 'ad': True, 'badge': True, 'llaves': True},
                user=hr_user,
            )
        exit_flow_service.complete_systems_offboarding(
            sysoff,
            checks={'correo': True, 'vpn': True, 'erp': True, 'ad': True, 'badge': True, 'llaves': True},
            user=hr_user,
            notes='Revocación completada',
        )
        sysoff.refresh_from_db()
        assert sysoff.status == 'completed'
        assert sysoff.completed_by == hr_user
