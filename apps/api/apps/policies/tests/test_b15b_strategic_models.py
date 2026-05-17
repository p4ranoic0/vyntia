"""Tests for B.15b HRStrategicPlan + StrategicObjective + KPI models."""
from datetime import date
from decimal import Decimal

import pytest

from apps.identity.models import User
from apps.policies.models import HRStrategicPlan, KPI, StrategicObjective


@pytest.fixture
def owner(db):
    return User.objects.create(
        username='strat_owner', email='strat@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def plan(owner):
    return HRStrategicPlan.objects.create(
        name='Plan 2026', fiscal_year=2026,
        period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
        owner_user=owner,
    )


@pytest.mark.django_db
class TestHRStrategicPlan:
    def test_create_default_draft(self, plan):
        assert plan.status == 'draft'
        assert 'Plan 2026' in str(plan)

    def test_unique_name_per_year_per_tenant(self, owner):
        from apps.tenancy.models import Tenant
        t = Tenant.objects.create(
            slug='acme-strat', name='ACME', ruc='20100000002',
            plan='starter', status='active', created_by=owner,
        )
        HRStrategicPlan.objects.create(
            tenant=t, name='X', fiscal_year=2026,
            period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
            owner_user=owner,
        )
        with pytest.raises(Exception):
            HRStrategicPlan.objects.create(
                tenant=t, name='X', fiscal_year=2026,
                period_start=date(2026, 1, 1), period_end=date(2026, 12, 31),
                owner_user=owner,
            )


@pytest.mark.django_db
class TestStrategicObjective:
    def test_unique_code_per_plan(self, plan, owner):
        StrategicObjective.objects.create(
            plan=plan, code='OE-01', title='Reducir rotación', weight=Decimal('30'),
        )
        with pytest.raises(Exception):
            StrategicObjective.objects.create(
                plan=plan, code='OE-01', title='Otro', weight=Decimal('20'),
            )

    def test_str(self, plan):
        o = StrategicObjective.objects.create(
            plan=plan, code='OE-02', title='Mejorar engagement', weight=Decimal('40'),
        )
        assert 'OE-02' in str(o)


@pytest.mark.django_db
class TestKPI:
    def test_progress_pct_basic(self, plan):
        obj = StrategicObjective.objects.create(
            plan=plan, code='OE-01', title='Rotación', weight=Decimal('100'),
        )
        kpi = KPI.objects.create(
            objective=obj, name='Rotación anual', target=Decimal('10'), actual=Decimal('8'),
        )
        assert kpi.progress_pct() == Decimal('80.00')

    def test_progress_pct_caps_at_100(self, plan):
        obj = StrategicObjective.objects.create(
            plan=plan, code='OE-01', title='X', weight=Decimal('100'),
        )
        kpi = KPI.objects.create(
            objective=obj, name='X', target=Decimal('5'), actual=Decimal('20'),
        )
        assert kpi.progress_pct() == Decimal('100')

    def test_progress_pct_zero_target(self, plan):
        obj = StrategicObjective.objects.create(
            plan=plan, code='OE-01', title='X', weight=Decimal('100'),
        )
        kpi = KPI.objects.create(
            objective=obj, name='X', target=Decimal('0'), actual=Decimal('5'),
        )
        assert kpi.progress_pct() == Decimal('0')

    def test_progress_pct_negative_actual(self, plan):
        obj = StrategicObjective.objects.create(
            plan=plan, code='OE-01', title='X', weight=Decimal('100'),
        )
        kpi = KPI.objects.create(
            objective=obj, name='X', target=Decimal('10'), actual=Decimal('-3'),
        )
        assert kpi.progress_pct() == Decimal('0')

    def test_str_includes_name_status(self, plan):
        obj = StrategicObjective.objects.create(
            plan=plan, code='OE-01', title='X', weight=Decimal('100'),
        )
        kpi = KPI.objects.create(
            objective=obj, name='Engagement score', target=Decimal('80'),
        )
        s = str(kpi)
        assert 'Engagement' in s and 'on_track' in s
