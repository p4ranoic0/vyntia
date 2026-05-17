"""Tests for B.14 Termination model (Module 03.7)."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.contracts.models import Contract, Termination, TRegistroDeclaration
from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='RRHH', siglas_area='RH', estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='71717171', tipo_documento='DNI',
        nombres_empleado='Diana', apellido_paterno='Cabrera',
        apellido_materno='Vega', fecha_nacimiento=date(1985, 3, 3),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14-001', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=730),
        salario_bruto=Decimal('3500.00'), cargo='Coordinadora', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b14t', email='hr_b14t@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestTerminationModel:
    def test_create_defaults(self, contract, employee):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        assert t.status == 'draft'
        assert t.regimen == '728'

    def test_mark_in_progress_only_from_draft(self, contract, employee, hr_user):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        t.mark_in_progress(user=hr_user)
        t.refresh_from_db()
        assert t.status == 'in_progress'
        assert t.initiated_by == hr_user
        with pytest.raises(ValidationError):
            t.mark_in_progress(user=hr_user)

    def test_mark_completed_from_in_progress(self, contract, employee, hr_user):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        t.mark_in_progress(user=hr_user)
        t.mark_completed(user=hr_user)
        t.refresh_from_db()
        assert t.status == 'completed'
        assert t.completed_by == hr_user
        assert t.completed_at is not None

    def test_mark_liquidated_requires_completed(self, contract, employee, hr_user):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        with pytest.raises(ValidationError):
            t.mark_liquidated(user=hr_user)
        t.mark_in_progress(user=hr_user)
        t.mark_completed(user=hr_user)
        t.mark_liquidated(user=hr_user)
        t.refresh_from_db()
        assert t.status == 'liquidated'

    def test_mark_baja_tregistro_done_links_declaration(self, contract, employee, hr_user):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        t.mark_in_progress(user=hr_user)
        t.mark_completed(user=hr_user)
        declaration = TRegistroDeclaration.objects.create(
            declaration_type='baja', contract=contract, employee=employee,
            employer_ruc='20100000001', employer_razon_social='Acme',
            worker_doc_number='71717171', worker_apellido_paterno='Cabrera',
            worker_nombres='Diana', worker_birth_date=date(1985, 3, 3),
            contract_start_date=contract.fecha_inicio, work_modality_code='001',
        )
        t.mark_baja_tregistro_done(declaration=declaration)
        t.refresh_from_db()
        assert t.status == 'baja_t_registro_done'
        assert t.baja_t_registro_id == declaration.id

    def test_cancel_requires_reason(self, contract, employee, hr_user):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        with pytest.raises(ValidationError):
            t.cancel(reason='', user=hr_user)
        t.cancel(reason='Empleado se arrepintió', user=hr_user)
        t.refresh_from_db()
        assert t.status == 'cancelled'
        assert t.cancelled_reason == 'Empleado se arrepintió'

    def test_cancel_blocked_from_baja_done(self, contract, employee, hr_user):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        t.mark_in_progress(user=hr_user)
        t.mark_completed(user=hr_user)
        declaration = TRegistroDeclaration.objects.create(
            declaration_type='baja', contract=contract, employee=employee,
            employer_ruc='20100000001', employer_razon_social='Acme',
            worker_doc_number='71717171', worker_apellido_paterno='Cabrera',
            worker_nombres='Diana', worker_birth_date=date(1985, 3, 3),
            contract_start_date=contract.fecha_inicio, work_modality_code='001',
        )
        t.mark_baja_tregistro_done(declaration=declaration)
        with pytest.raises(ValidationError):
            t.cancel(reason='ya tarde', user=hr_user)

    def test_baja_tregistro_overdue_48h_false_when_recent(self, contract, employee, hr_user):
        t = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        t.mark_in_progress(user=hr_user)
        t.mark_completed(user=hr_user)
        t.refresh_from_db()
        assert t.baja_tregistro_overdue_48h is False
        assert t.hours_since_completion is not None
        assert t.hours_since_completion >= 0
