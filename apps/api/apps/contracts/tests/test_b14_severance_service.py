"""Tests for B.14 severance_service — 4 formulas + integration."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.contracts.models import Contract, SeveranceSettlement, Termination
from apps.contracts.services import severance_service
from apps.employees.models import Employee
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Ventas', siglas_area='VEN', estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='74747474', tipo_documento='DNI',
        nombres_empleado='Sergio', apellido_paterno='Vélez',
        apellido_materno='Castro', fecha_nacimiento=date(1987, 6, 6),
        estado_empleado='activo',
    )


def _make_contract(employee, department, *, fecha_inicio, sueldo=Decimal('3000.00')):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato=f'CON-B14SEV-{fecha_inicio.toordinal()}',
        tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=fecha_inicio,
        salario_bruto=sueldo, cargo='Vendedor', status='ACTIVO',
    )


@pytest.mark.django_db
class TestSeveranceFormulas:
    def test_compute_full_settlement_renuncia(self, employee, department):
        # 2 años + 1 mes worth of service.
        contract = _make_contract(
            employee, department,
            fecha_inicio=date.today() - timedelta(days=760),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        settlement = severance_service.compute_settlement(term)
        components = {l.component: l for l in settlement.lines.all()}
        assert 'cts' in components
        assert 'vac_truncas' in components
        assert 'grat_trunca' in components
        assert 'indemnizacion' in components
        # Renuncia → indemnización = 0
        assert components['indemnizacion'].amount == Decimal('0.00')
        # Total > 0 (CTS + grat + vacaciones)
        assert settlement.total_amount > Decimal('0')
        assert settlement.status == 'computed'

    def test_indemnizacion_aplica_solo_despido_arbitrario(self, employee, department):
        contract = _make_contract(
            employee, department,
            fecha_inicio=date.today() - timedelta(days=730),
            sueldo=Decimal('4000.00'),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='despido_arbitrario',
            fecha_cese=date.today(),
        )
        settlement = severance_service.compute_settlement(term)
        indemn = settlement.lines.get(component='indemnizacion')
        # 2 años × 4000 × 1.5 = 12000
        assert indemn.amount == Decimal('12000.00')
        assert indemn.base_calculation['aplicable'] is True

    def test_indemnizacion_capped_12_sueldos(self, employee, department):
        # 20 años de antigüedad → cap a 12 sueldos.
        contract = _make_contract(
            employee, department,
            fecha_inicio=date.today() - timedelta(days=365 * 20),
            sueldo=Decimal('2000.00'),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='despido_arbitrario',
            fecha_cese=date.today(),
        )
        settlement = severance_service.compute_settlement(term)
        indemn = settlement.lines.get(component='indemnizacion')
        # 2000 × 12 = 24000 (cap), no 2000 × 1.5 × 20 = 60000
        assert indemn.amount == Decimal('24000.00')

    def test_recompute_is_idempotent(self, employee, department):
        contract = _make_contract(
            employee, department,
            fecha_inicio=date.today() - timedelta(days=200),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        s1 = severance_service.compute_settlement(term)
        first_total = s1.total_amount
        s2 = severance_service.compute_settlement(term)
        assert s1.pk == s2.pk
        assert s2.total_amount == first_total
        assert s2.lines.count() == 4

    def test_vac_truncas_uses_input_dias_when_higher(self, employee, department):
        contract = _make_contract(
            employee, department,
            fecha_inicio=date.today() - timedelta(days=30),
            sueldo=Decimal('3000.00'),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        settlement = severance_service.compute_settlement(
            term, dias_acumulados_no_gozados=Decimal('25'),
        )
        vac = settlement.lines.get(component='vac_truncas')
        # jornal = 100, 25 días → 2500
        assert vac.amount == Decimal('2500.00')


@pytest.mark.django_db
class TestSeveranceServiceMarkPaid:
    def test_mark_paid_promotes_status(self, employee, department):
        contract = _make_contract(
            employee, department,
            fecha_inicio=date.today() - timedelta(days=100),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia',
            fecha_cese=date.today(),
        )
        settlement = severance_service.compute_settlement(term)
        total = settlement.total_amount
        severance_service.mark_paid(settlement, paid_total=total)
        settlement.refresh_from_db()
        assert settlement.status == 'paid'
        assert settlement.paid_amount == total
