"""Tests for B.14 termination_service helpers."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from apps.contracts.models import Contract, Termination, TRegistroDeclaration
from apps.contracts.services import termination_service
from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Operaciones', siglas_area='OPS', estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='73737373', tipo_documento='DNI',
        nombres_empleado='Karla', apellido_paterno='Reyes',
        apellido_materno='Mora', fecha_nacimiento=date(1992, 4, 4),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14SVC-001', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=900),
        salario_bruto=Decimal('5000.00'), cargo='Supervisor', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b14svc', email='hr_b14svc@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.mark.django_db
class TestTerminationService:
    def test_initiate_termination_creates_in_progress(self, contract, hr_user):
        t = termination_service.initiate_termination(
            contract=contract,
            causal='renuncia',
            fecha_cese=date.today(),
            user=hr_user,
        )
        assert t.status == 'in_progress'
        assert t.regimen == '728'
        assert t.causal == 'renuncia'
        assert t.initiated_by == hr_user

    def test_initiate_refuses_inactive_contract(self, contract, hr_user):
        contract.status = 'TERMINADO'
        Contract.objects.filter(pk=contract.pk).update(status='TERMINADO')
        contract.refresh_from_db()
        with pytest.raises(ValidationError):
            termination_service.initiate_termination(
                contract=contract,
                causal='renuncia',
                fecha_cese=date.today(),
                user=hr_user,
            )

    def test_initiate_refuses_duplicate(self, contract, hr_user):
        termination_service.initiate_termination(
            contract=contract,
            causal='renuncia',
            fecha_cese=date.today(),
            user=hr_user,
        )
        with pytest.raises(ValidationError):
            termination_service.initiate_termination(
                contract=contract,
                causal='renuncia',
                fecha_cese=date.today(),
                user=hr_user,
            )

    def test_complete_flips_contract_terminado(self, contract, hr_user):
        t = termination_service.initiate_termination(
            contract=contract,
            causal='renuncia',
            fecha_cese=date.today(),
            user=hr_user,
        )
        termination_service.complete_termination(t, user=hr_user)
        contract.refresh_from_db()
        assert contract.status == 'TERMINADO'
        t.refresh_from_db()
        assert t.status == 'completed'

    def test_liquidate_requires_settlement_paid(self, contract, hr_user):
        from apps.contracts.models import SeveranceSettlement

        t = termination_service.initiate_termination(
            contract=contract,
            causal='renuncia',
            fecha_cese=date.today(),
            user=hr_user,
        )
        termination_service.complete_termination(t, user=hr_user)
        with pytest.raises(ValidationError):
            termination_service.liquidate(t, user=hr_user)
        settlement = SeveranceSettlement.objects.create(
            termination=t, sueldo_base=Decimal('1000.00'),
            total_amount=Decimal('1000.00'),
        )
        settlement.mark_computed(user=hr_user)
        settlement.mark_paid(paid_total=Decimal('1000.00'), user=hr_user)
        termination_service.liquidate(t, user=hr_user)
        t.refresh_from_db()
        assert t.status == 'liquidated'

    def test_mark_baja_tregistro_done_requires_baja_type(self, contract, employee, hr_user):
        t = termination_service.initiate_termination(
            contract=contract,
            causal='renuncia',
            fecha_cese=date.today(),
            user=hr_user,
        )
        termination_service.complete_termination(t, user=hr_user)
        alta = TRegistroDeclaration.objects.create(
            declaration_type='alta', contract=contract, employee=employee,
            employer_ruc='20100000001', employer_razon_social='Acme',
            worker_doc_number='73737373', worker_apellido_paterno='Reyes',
            worker_nombres='Karla', worker_birth_date=date(1992, 4, 4),
            contract_start_date=contract.fecha_inicio, work_modality_code='001',
        )
        with pytest.raises(ValidationError):
            termination_service.mark_baja_tregistro_done(t, declaration=alta)
        baja = TRegistroDeclaration.objects.create(
            declaration_type='baja', contract=contract, employee=employee,
            employer_ruc='20100000001', employer_razon_social='Acme',
            worker_doc_number='73737373', worker_apellido_paterno='Reyes',
            worker_nombres='Karla', worker_birth_date=date(1992, 4, 4),
            contract_start_date=contract.fecha_inicio, work_modality_code='001',
        )
        termination_service.mark_baja_tregistro_done(t, declaration=baja)
        t.refresh_from_db()
        assert t.status == 'baja_t_registro_done'

    def test_list_pending_48h_filters_recent_completions(self, contract, hr_user):
        from django.utils import timezone

        t = termination_service.initiate_termination(
            contract=contract,
            causal='renuncia',
            fecha_cese=date.today(),
            user=hr_user,
        )
        termination_service.complete_termination(t, user=hr_user)
        # Recién completado: NO en la lista.
        assert t not in termination_service.list_pending_baja_tregistro_48h()
        # Backdate completed_at >48h.
        Termination.objects.filter(pk=t.pk).update(
            completed_at=timezone.now() - timedelta(hours=72),
        )
        assert t in list(termination_service.list_pending_baja_tregistro_48h())

    def test_cancel_termination_records_reason(self, contract, hr_user):
        t = termination_service.initiate_termination(
            contract=contract,
            causal='renuncia',
            fecha_cese=date.today(),
            user=hr_user,
        )
        termination_service.cancel_termination(t, reason='Empleado retiró renuncia', user=hr_user)
        t.refresh_from_db()
        assert t.status == 'cancelled'
        assert 'retiró' in t.cancelled_reason
