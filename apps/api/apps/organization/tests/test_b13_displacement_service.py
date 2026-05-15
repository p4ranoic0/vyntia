"""Tests for B.13 displacement_service."""
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department, Displacement
from apps.organization.services import displacement_service


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='80808080', tipo_documento='DNI',
        nombres_empleado='Lucía', apellido_paterno='Sosa',
        apellido_materno='Cruz', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def origen(db):
    return Department.objects.create(
        nombre_unidad_organica='Tesorería', siglas_area='TES', estado_area='activa',
    )


@pytest.fixture
def destino(db):
    return Department.objects.create(
        nombre_unidad_organica='Logística', siglas_area='LOG', estado_area='activa',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b13_svc', email='hr_b13_svc@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


def _approved_displacement(employee, origen, destino, hr_user):
    d = Displacement.objects.create(
        employee=employee, kind='encargatura',
        origen_department=origen, destino_department=destino,
        start_date=date.today(), end_date=date.today() + timedelta(days=180),
        justification='Refuerzo temporal de equipo',
        resolution_number='RES-2026-001',
        requested_by=hr_user,
    )
    d.submit()
    d.approve_supervisor(user=hr_user)
    d.approve_hr(user=hr_user)
    d.approve_titular(user=hr_user)
    return d


@pytest.mark.django_db
class TestRenderResolutionHtml:
    def test_includes_employee_name(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        html = displacement_service.render_resolution_html(d.id)
        assert employee.nombres_empleado in html
        assert employee.apellido_paterno in html

    def test_includes_resolution_number(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        html = displacement_service.render_resolution_html(d.id)
        assert 'RES-2026-001' in html

    def test_includes_kind_display(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        html = displacement_service.render_resolution_html(d.id)
        assert 'Encargatura' in html

    def test_includes_origen_destino_departments(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        html = displacement_service.render_resolution_html(d.id)
        assert origen.nombre_unidad_organica in html
        assert destino.nombre_unidad_organica in html

    def test_includes_justification(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        html = displacement_service.render_resolution_html(d.id)
        assert 'Refuerzo temporal' in html

    def test_includes_servir_276_reference(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        html = displacement_service.render_resolution_html(d.id)
        assert 'SERVIR' in html
        assert '276' in html


@pytest.mark.django_db
class TestExtendDisplacement:
    def test_extends_active(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        d.activate()
        new_end = d.end_date + timedelta(days=90)
        ext = displacement_service.extend_displacement(
            displacement_id=d.id,
            new_end_date=new_end,
            reason='Prórroga aprobada por necesidad de servicio',
            granted_by=hr_user,
            resolution_number='RES-2026-002',
        )
        d.refresh_from_db()
        assert ext.id is not None
        assert d.end_date == new_end
        assert ext.resolution_number == 'RES-2026-002'

    def test_cannot_extend_non_active(self, employee, origen, destino, hr_user):
        d = _approved_displacement(employee, origen, destino, hr_user)
        # Still 'approved', not 'active'
        with pytest.raises(ValidationError):
            displacement_service.extend_displacement(
                displacement_id=d.id,
                new_end_date=date.today() + timedelta(days=365),
                reason='X',
                granted_by=hr_user,
            )

    def test_extend_validates_new_end_after_previous(
        self, employee, origen, destino, hr_user,
    ):
        d = _approved_displacement(employee, origen, destino, hr_user)
        d.activate()
        with pytest.raises(ValidationError):
            displacement_service.extend_displacement(
                displacement_id=d.id,
                new_end_date=d.end_date - timedelta(days=10),
                reason='X', granted_by=hr_user,
            )
