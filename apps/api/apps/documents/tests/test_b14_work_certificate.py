"""Tests for B.14 WorkCertificate model + service."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.contracts.models import Contract, Termination
from apps.documents.models import WorkCertificate
from apps.documents.services import work_certificate_service
from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Legal', siglas_area='LEG', estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='76767676', tipo_documento='DNI',
        nombres_empleado='Beatriz', apellido_paterno='Lozada',
        apellido_materno='Iglesias', fecha_nacimiento=date(1986, 9, 9),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B14WC-001', tipo_documento='LEY_728_INDETERMINADO',
        fecha_inicio=date.today() - timedelta(days=300),
        salario_bruto=Decimal('3200.00'), cargo='Abogada', status='ACTIVO',
    )


@pytest.fixture
def termination(contract, employee):
    return Termination.objects.create(
        contract=contract, employee=employee,
        regimen='728', causal='renuncia',
        fecha_cese=date.today(),
        motivo='Renuncia voluntaria con preaviso',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b14wc', email='hr_b14wc@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def tenant_a(db, hr_user):
    from apps.tenancy.models import Tenant
    return Tenant.objects.create(
        slug='tenant-b14-wc', name='Acme B14', ruc='20111111112',
        plan='starter', status='active', created_by=hr_user,
    )


@pytest.mark.django_db
class TestWorkCertificate:
    def test_unique_number_per_tenant(self, termination, employee, contract, tenant_a):
        WorkCertificate.objects.create(
            tenant=tenant_a,
            termination=termination, employee=employee, contract=contract,
            numero_constancia='CTR-2026-0001', fecha_emision=date.today(),
        )
        contract2 = Contract.objects.create(
            empleado=employee, area=contract.area,
            numero_contrato='CON-B14WC-002', tipo_documento='LEY_728_INDETERMINADO',
            fecha_inicio=date.today(),
            salario_bruto=Decimal('2000.00'), cargo='Asesora', status='ACTIVO',
        )
        term2 = Termination.objects.create(
            tenant=tenant_a,
            contract=contract2, employee=employee,
            regimen='728', causal='renuncia', fecha_cese=date.today(),
        )
        with pytest.raises(Exception):
            WorkCertificate.objects.create(
                tenant=tenant_a,
                termination=term2, employee=employee, contract=contract2,
                numero_constancia='CTR-2026-0001', fecha_emision=date.today(),
            )


@pytest.mark.django_db
class TestWorkCertificateService:
    def test_render_html_includes_employee_and_motivo(self, termination):
        html = work_certificate_service.render_certificate_html(termination)
        assert 'Beatriz' in html
        assert 'Abogada' in html
        assert 'Renuncia voluntaria' in html

    def test_generate_certificate_persists_row_with_snapshots(self, termination, hr_user):
        cert = work_certificate_service.generate_certificate(termination, user=hr_user)
        assert cert.pk is not None
        assert cert.cargo_snapshot == 'Abogada'
        assert cert.sueldo_snapshot == Decimal('3200.00')
        assert cert.signed_by == hr_user
        assert cert.numero_constancia.startswith('CTR-')
        # Idempotente: re-llamarlo no duplica.
        cert2 = work_certificate_service.generate_certificate(termination, user=hr_user)
        assert cert.pk == cert2.pk
