"""Tests for B.13 Displacement + DisplacementExtension."""
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import (
    Department,
    Displacement,
    DisplacementExtension,
)


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='71717171', tipo_documento='DNI',
        nombres_empleado='Iván', apellido_paterno='Castro',
        apellido_materno='Lara', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def origen(db):
    return Department.objects.create(
        nombre_unidad_organica='RRHH', siglas_area='RH', estado_area='activa',
    )


@pytest.fixture
def destino(db):
    return Department.objects.create(
        nombre_unidad_organica='Tesorería', siglas_area='TES', estado_area='activa',
    )


@pytest.fixture
def supervisor(db):
    return User.objects.create(
        username='sup_b13', email='sup_b13@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b13', email='hr_b13@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def titular(db):
    return User.objects.create(
        username='tit_b13', email='tit_b13@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def displacement(employee, origen, destino, hr_user):
    return Displacement.objects.create(
        employee=employee,
        kind='encargatura',
        origen_department=origen,
        destino_department=destino,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=180),
        requested_by=hr_user,
    )


@pytest.mark.django_db
class TestDisplacementLifecycle:
    def test_defaults(self, displacement):
        assert displacement.status == 'draft'
        assert displacement.kind == 'encargatura'

    def test_submit_from_draft(self, displacement):
        displacement.submit()
        displacement.refresh_from_db()
        assert displacement.status == 'pending_supervisor'

    def test_submit_only_from_draft(self, displacement):
        displacement.submit()
        with pytest.raises(ValidationError):
            displacement.submit()

    def test_full_approval_chain(self, displacement, supervisor, hr_user, titular):
        displacement.submit()
        displacement.approve_supervisor(user=supervisor)
        displacement.refresh_from_db()
        assert displacement.status == 'pending_hr'
        assert displacement.approved_by_supervisor == supervisor

        displacement.approve_hr(user=hr_user)
        displacement.refresh_from_db()
        assert displacement.status == 'pending_titular'
        assert displacement.approved_by_hr == hr_user

        displacement.approve_titular(user=titular)
        displacement.refresh_from_db()
        assert displacement.status == 'approved'
        assert displacement.approved_by_titular == titular

    def test_activate_only_from_approved(self, displacement, supervisor, hr_user, titular):
        with pytest.raises(ValidationError):
            displacement.activate()
        displacement.submit()
        displacement.approve_supervisor(user=supervisor)
        displacement.approve_hr(user=hr_user)
        displacement.approve_titular(user=titular)
        displacement.activate()
        displacement.refresh_from_db()
        assert displacement.status == 'active'
        assert displacement.activated_at is not None

    def test_complete_only_from_active(self, displacement, supervisor, hr_user, titular):
        with pytest.raises(ValidationError):
            displacement.complete()
        displacement.submit()
        displacement.approve_supervisor(user=supervisor)
        displacement.approve_hr(user=hr_user)
        displacement.approve_titular(user=titular)
        displacement.activate()
        displacement.complete()
        displacement.refresh_from_db()
        assert displacement.status == 'completed'

    def test_cancel_requires_reason(self, displacement):
        with pytest.raises(ValidationError):
            displacement.cancel(reason='')

    def test_cancel_terminal(self, displacement, supervisor, hr_user, titular):
        displacement.submit()
        displacement.approve_supervisor(user=supervisor)
        displacement.approve_hr(user=hr_user)
        displacement.approve_titular(user=titular)
        displacement.activate()
        displacement.complete()
        with pytest.raises(ValidationError):
            displacement.cancel(reason='X')

    def test_indexes_declared(self):
        index_fields = {tuple(i.fields) for i in Displacement._meta.indexes}
        assert ('tenant', 'status') in index_fields
        assert ('tenant', 'kind') in index_fields

    def test_seven_kinds_available(self):
        kinds = {k for k, _ in Displacement.KINDS}
        assert kinds == {
            'rotacion', 'encargatura', 'destaque', 'comision',
            'designacion', 'transferencia', 'permuta',
        }


@pytest.mark.django_db
class TestDisplacementExtension:
    def test_create(self, displacement):
        ext = DisplacementExtension(
            displacement=displacement,
            previous_end_date=displacement.end_date,
            new_end_date=displacement.end_date + timedelta(days=60),
            reason='Prórroga aprobada',
        )
        ext.clean()
        ext.save()
        assert ext.id is not None

    def test_clean_rejects_invalid_dates(self, displacement):
        ext = DisplacementExtension(
            displacement=displacement,
            previous_end_date=date.today(),
            new_end_date=date.today() - timedelta(days=1),
            reason='X',
        )
        with pytest.raises(ValidationError):
            ext.clean()
