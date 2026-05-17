"""Tests for B.15b services — strategic + workforce + compliance flows."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department, Position
from apps.policies.models import (
    ComplianceObligation,
    HRStrategicPlan,
    SuccessionPlan,
    WorkforcePlan,
)
from apps.policies.services import (
    compliance_service,
    strategic_plan_service,
    workforce_plan_service,
)


@pytest.fixture
def owner(db):
    return User.objects.create(
        username='svc_owner', email='svc@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Operaciones', siglas_area='OPS', estado_area='activa',
    )


@pytest.fixture
def position(db, department):
    return Position.objects.create(
        code='POS-OPS-001', name='Operario',
        department=department,
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='12121212', tipo_documento='DNI',
        nombres_empleado='Carlos', apellido_paterno='Pérez',
        apellido_materno='Loa', fecha_nacimiento=date(1990, 5, 5),
        estado_empleado='activo',
    )


# ---------------- Strategic plan service ----------------

@pytest.mark.django_db
class TestStrategicPlanService:
    def test_create_plan(self, owner):
        p = strategic_plan_service.create_plan(
            tenant=None, name='Plan', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        assert p.status == 'draft'

    def test_create_plan_invalid_period(self, owner):
        with pytest.raises(ValidationError):
            strategic_plan_service.create_plan(
                tenant=None, name='X', fiscal_year=2026,
                period_start=date(2026, 12, 31), period_end=date(2026, 1, 1),
                owner_user=owner,
            )

    def test_add_objective_and_kpi(self, owner):
        plan = strategic_plan_service.create_plan(
            tenant=None, name='P', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        obj = strategic_plan_service.add_objective(
            plan=plan, code='OE-01', title='Reducir rotación', weight=Decimal('50'),
        )
        kpi = strategic_plan_service.add_kpi(
            objective=obj, name='Rotación', target=Decimal('10'), unit='%',
        )
        assert kpi.actual == Decimal('0')
        assert kpi.status == 'on_track'

    def test_update_kpi_actual_derives_status(self, owner):
        plan = strategic_plan_service.create_plan(
            tenant=None, name='P', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        obj = strategic_plan_service.add_objective(
            plan=plan, code='OE-01', title='X', weight=Decimal('100'),
        )
        kpi = strategic_plan_service.add_kpi(
            objective=obj, name='K', target=Decimal('100'),
        )
        strategic_plan_service.update_kpi_actual(kpi=kpi, actual=Decimal('100'))
        kpi.refresh_from_db()
        assert kpi.status == 'done'

        strategic_plan_service.update_kpi_actual(kpi=kpi, actual=Decimal('30'))
        kpi.refresh_from_db()
        assert kpi.status == 'off_track'

    def test_mark_active_then_completed(self, owner):
        plan = strategic_plan_service.create_plan(
            tenant=None, name='P', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        strategic_plan_service.mark_active(plan, user=owner)
        plan.refresh_from_db()
        assert plan.status == 'active'
        assert plan.approved_by == owner

        strategic_plan_service.mark_completed(plan)
        plan.refresh_from_db()
        assert plan.status == 'completed'

    def test_compute_progress_weighted(self, owner):
        plan = strategic_plan_service.create_plan(
            tenant=None, name='P', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        obj_a = strategic_plan_service.add_objective(
            plan=plan, code='OE-A', title='A', weight=Decimal('60'),
        )
        obj_b = strategic_plan_service.add_objective(
            plan=plan, code='OE-B', title='B', weight=Decimal('40'),
        )
        kpi_a = strategic_plan_service.add_kpi(
            objective=obj_a, name='Ka', target=Decimal('100'),
        )
        kpi_b = strategic_plan_service.add_kpi(
            objective=obj_b, name='Kb', target=Decimal('100'),
        )
        strategic_plan_service.update_kpi_actual(kpi=kpi_a, actual=Decimal('100'))  # 100%
        strategic_plan_service.update_kpi_actual(kpi=kpi_b, actual=Decimal('50'))   # 50%
        out = strategic_plan_service.compute_progress(plan)
        # 60% × 100% + 40% × 50% = 60 + 20 = 80
        assert Decimal(out['overall_pct']) == Decimal('80.00')


# ---------------- Workforce plan service ----------------

@pytest.mark.django_db
class TestWorkforcePlanService:
    def test_create_plan_invalid_period(self, owner):
        with pytest.raises(ValidationError):
            workforce_plan_service.create_plan(
                tenant=None, name='X', fiscal_year=2026,
                period_start=date(2026, 12, 31), period_end=date(2026, 1, 1),
                owner_user=owner,
            )

    def test_add_projection_negative_headcount_refused(self, owner):
        plan = workforce_plan_service.create_plan(
            tenant=None, name='P', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        with pytest.raises(ValidationError):
            workforce_plan_service.add_projection(
                plan=plan, current_headcount=-1, projected_headcount=5,
            )

    def test_add_projection_invalid_quarter(self, owner):
        plan = workforce_plan_service.create_plan(
            tenant=None, name='P', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        with pytest.raises(ValidationError):
            workforce_plan_service.add_projection(
                plan=plan, current_headcount=5, projected_headcount=10,
                target_quarter='Q5',
            )

    def test_add_key_position_idempotent(self, owner, position):
        sp = workforce_plan_service.create_succession_plan(
            tenant=None, name='S', fiscal_year=2026, owner_user=owner,
        )
        kp1 = workforce_plan_service.add_key_position(
            succession_plan=sp, position=position, criticality='alta',
        )
        kp2 = workforce_plan_service.add_key_position(
            succession_plan=sp, position=position, criticality='media',
        )
        # idempotente: misma row, criticality NO se sobreescribe (get_or_create defaults).
        assert kp1.pk == kp2.pk

    def test_add_successor_update_or_create(self, owner, position, employee):
        sp = workforce_plan_service.create_succession_plan(
            tenant=None, name='S', fiscal_year=2026, owner_user=owner,
        )
        kp = workforce_plan_service.add_key_position(
            succession_plan=sp, position=position, criticality='alta',
        )
        c1 = workforce_plan_service.add_successor(
            key_position=kp, employee=employee, readiness_level=3,
        )
        c2 = workforce_plan_service.add_successor(
            key_position=kp, employee=employee, readiness_level=1,
        )
        # update_or_create — misma row, readiness ahora 1.
        assert c1.pk == c2.pk
        c2.refresh_from_db()
        assert c2.readiness_level == 1


# ---------------- Compliance service ----------------

@pytest.mark.django_db
class TestComplianceService:
    def test_add_obligation_invalid_source(self, owner):
        m = compliance_service.create_matrix(
            tenant=None, name='M', fiscal_year=2026, owner_user=owner,
        )
        with pytest.raises(ValidationError):
            compliance_service.add_obligation(
                matrix=m, code='X', title='X', source='nasa', frequency='anual',
                next_due_date=date.today(),
            )

    def test_attach_evidence_archivo_requires_file(self, owner):
        m = compliance_service.create_matrix(
            tenant=None, name='M', fiscal_year=2026, owner_user=owner,
        )
        o = compliance_service.add_obligation(
            matrix=m, code='X', title='X', source='sunat',
            frequency='mensual', next_due_date=date.today(),
        )
        with pytest.raises(ValidationError):
            compliance_service.attach_evidence(
                obligation=o, kind='archivo',
            )

    def test_mark_completed_mensual_advances_next_due(self, owner):
        m = compliance_service.create_matrix(
            tenant=None, name='M', fiscal_year=2026, owner_user=owner,
        )
        o = compliance_service.add_obligation(
            matrix=m, code='X', title='X', source='sunat',
            frequency='mensual', next_due_date=date.today() - timedelta(days=2),
        )
        completed_at = timezone.now()
        compliance_service.mark_obligation_completed(
            obligation=o, completed_at=completed_at,
        )
        o.refresh_from_db()
        assert o.last_completed_at is not None
        # Next due should be ~30 days ahead.
        assert (o.next_due_date - completed_at.date()).days == 30
        assert o.status == 'pendiente'

    def test_mark_completed_unica_stays_cumplido(self, owner):
        m = compliance_service.create_matrix(
            tenant=None, name='M', fiscal_year=2026, owner_user=owner,
        )
        o = compliance_service.add_obligation(
            matrix=m, code='Y', title='Y', source='interno',
            frequency='unica', next_due_date=date.today(),
        )
        compliance_service.mark_obligation_completed(obligation=o)
        o.refresh_from_db()
        assert o.status == 'cumplido'

    def test_list_alerts_buckets(self, owner):
        m = compliance_service.create_matrix(
            tenant=None, name='M', fiscal_year=2026, owner_user=owner,
        )
        overdue = compliance_service.add_obligation(
            matrix=m, code='OD', title='Overdue', source='sunat',
            frequency='mensual', next_due_date=date.today() - timedelta(days=5),
        )
        due_soon = compliance_service.add_obligation(
            matrix=m, code='DS', title='Due soon', source='sunat',
            frequency='mensual', next_due_date=date.today() + timedelta(days=10),
        )
        far = compliance_service.add_obligation(
            matrix=m, code='FAR', title='Far', source='sunat',
            frequency='mensual', next_due_date=date.today() + timedelta(days=90),
        )
        alerts = compliance_service.list_alerts(days_ahead=30)
        assert overdue in alerts['overdue']
        assert due_soon in alerts['due_soon']
        assert far not in alerts['overdue'] and far not in alerts['due_soon']

    def test_mark_overdue_obligations(self, owner):
        m = compliance_service.create_matrix(
            tenant=None, name='M', fiscal_year=2026, owner_user=owner,
        )
        o = compliance_service.add_obligation(
            matrix=m, code='Z', title='Z', source='sunat',
            frequency='mensual', next_due_date=date.today() - timedelta(days=10),
        )
        count = compliance_service.mark_overdue_obligations()
        assert count == 1
        o.refresh_from_db()
        assert o.status == 'vencido'
