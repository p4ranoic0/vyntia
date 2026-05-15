"""Tests for B.10 TRegistroDeclaration model (SUNAT T-Registro alta/baja)."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from apps.contracts.models import Contract, TRegistroDeclaration
from apps.employees.models import Employee
from apps.identity.models import User
from apps.organization.models import Department


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Recursos Humanos',
        siglas_area='RRHH',
        estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='10101010',
        tipo_documento='DNI',
        nombres_empleado='María',
        apellido_paterno='Quispe',
        apellido_materno='Rojas',
        correo_personal='maria@example.com',
        fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee,
        area=department,
        numero_contrato='CON-B10-001',
        tipo_documento='LEY_728_FIJO',
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=365),
        salario_bruto=Decimal('3000.00'),
        cargo='Analista',
        status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b10', email='hr_b10@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def declaration(contract, employee):
    return TRegistroDeclaration.objects.create(
        contract=contract,
        employee=employee,
        employer_ruc='20123456789',
        employer_razon_social='ACME SAC',
        worker_doc_number=employee.numero_documento,
        worker_apellido_paterno=employee.apellido_paterno,
        worker_apellido_materno=employee.apellido_materno,
        worker_nombres=employee.nombres_empleado,
        worker_birth_date=employee.fecha_nacimiento,
        worker_gender='F',
        contract_start_date=contract.fecha_inicio,
        contract_end_date=contract.fecha_fin,
        work_modality_code='SBT',
        regimen_laboral_code='728',
        remuneracion_basica=Decimal('3000.00'),
    )


@pytest.mark.django_db
class TestTRegistroDeclaration:
    def test_create_alta_defaults(self, declaration):
        assert declaration.id is not None
        assert declaration.declaration_type == 'alta'
        assert declaration.status == 'draft'
        assert declaration.regimen_pensionario == 'snp'
        assert declaration.regimen_salud == 'essalud'
        assert declaration.jornada_horas_semanales == 48
        assert declaration.pvs_errors == []

    def test_string_repr_contains_doc_number(self, declaration):
        s = str(declaration)
        assert declaration.worker_doc_number in s
        assert 'Alta' in s

    def test_mark_validated_promotes_status(self, declaration):
        declaration.mark_validated()
        declaration.refresh_from_db()
        assert declaration.status == 'validated'

    def test_mark_validated_rejects_when_pvs_errors_present(self, declaration):
        declaration.pvs_errors = ['ruc invalid']
        declaration.save(update_fields=['pvs_errors'])
        with pytest.raises(ValidationError):
            declaration.mark_validated()

    def test_mark_submitted_from_draft(self, declaration, hr_user):
        declaration.mark_submitted(user=hr_user, reference='REF-001')
        declaration.refresh_from_db()
        assert declaration.status == 'submitted'
        assert declaration.submitted_by == hr_user
        assert declaration.sunat_reference == 'REF-001'
        assert declaration.submitted_at is not None

    def test_mark_submitted_from_validated(self, declaration, hr_user):
        declaration.mark_validated()
        declaration.mark_submitted(user=hr_user)
        declaration.refresh_from_db()
        assert declaration.status == 'submitted'

    def test_mark_submitted_rejects_from_accepted(self, declaration, hr_user):
        declaration.mark_submitted(user=hr_user)
        declaration.mark_accepted()
        with pytest.raises(ValidationError):
            declaration.mark_submitted(user=hr_user)

    def test_mark_accepted_only_from_submitted(self, declaration, hr_user):
        # draft → accepted is not allowed
        with pytest.raises(ValidationError):
            declaration.mark_accepted()
        declaration.mark_submitted(user=hr_user)
        declaration.mark_accepted(reference='REF-XYZ')
        declaration.refresh_from_db()
        assert declaration.status == 'accepted'
        assert declaration.sunat_reference == 'REF-XYZ'
        assert declaration.sunat_response_at is not None

    def test_mark_rejected_requires_reason(self, declaration, hr_user):
        declaration.mark_submitted(user=hr_user)
        with pytest.raises(ValidationError):
            declaration.mark_rejected(reason='')

    def test_mark_rejected_persists_metadata(self, declaration, hr_user):
        declaration.mark_submitted(user=hr_user)
        declaration.mark_rejected(reason='RUC empleador no encontrado')
        declaration.refresh_from_db()
        assert declaration.status == 'rejected'
        assert declaration.rejection_reason == 'RUC empleador no encontrado'
        assert declaration.sunat_response_at is not None

    def test_unique_active_declaration_per_contract(
        self, contract, employee, hr_user,
    ):
        # Constraint condition is gated on tenant; create a tenant so NULL
        # tenant semantics don't apply.
        from apps.tenancy.models import Tenant
        tenant = Tenant.objects.create(
            slug='test-b10', name='Test B10', ruc='20111111111',
            plan='starter', status='active', created_by=hr_user,
        )
        # First alta gets submitted (active)
        d1 = TRegistroDeclaration.objects.create(
            tenant=tenant,
            contract=contract, employee=employee,
            employer_ruc='20123456789', employer_razon_social='ACME',
            worker_doc_number='10101010',
            worker_apellido_paterno='Quispe',
            worker_nombres='María',
            worker_birth_date=date(1990, 1, 1),
            contract_start_date=date.today(),
            work_modality_code='SBT',
        )
        d1.mark_submitted(user=hr_user)

        # Second alta in submitted/accepted state for the same contract
        # must fail the unique constraint.
        d2 = TRegistroDeclaration.objects.create(
            tenant=tenant,
            contract=contract, employee=employee,
            employer_ruc='20123456789', employer_razon_social='ACME',
            worker_doc_number='10101010',
            worker_apellido_paterno='Quispe',
            worker_nombres='María',
            worker_birth_date=date(1990, 1, 1),
            contract_start_date=date.today(),
            work_modality_code='SBT',
        )
        with pytest.raises(IntegrityError):
            d2.mark_submitted(user=hr_user)

    def test_baja_can_coexist_with_alta(self, contract, employee, hr_user):
        alta = TRegistroDeclaration.objects.create(
            contract=contract, employee=employee, declaration_type='alta',
            employer_ruc='20123456789', employer_razon_social='ACME',
            worker_doc_number='10101010',
            worker_apellido_paterno='Quispe',
            worker_nombres='María',
            worker_birth_date=date(1990, 1, 1),
            contract_start_date=date.today(),
            work_modality_code='SBT',
        )
        alta.mark_submitted(user=hr_user)

        baja = TRegistroDeclaration.objects.create(
            contract=contract, employee=employee, declaration_type='baja',
            employer_ruc='20123456789', employer_razon_social='ACME',
            worker_doc_number='10101010',
            worker_apellido_paterno='Quispe',
            worker_nombres='María',
            worker_birth_date=date(1990, 1, 1),
            contract_start_date=date.today(),
            work_modality_code='SBT',
        )
        # Should not raise — different declaration_type
        baja.mark_submitted(user=hr_user)

    def test_indexes_declared(self):
        index_fields = {tuple(i.fields) for i in TRegistroDeclaration._meta.indexes}
        assert ('tenant', 'status') in index_fields
        assert ('tenant', 'declaration_type') in index_fields
        assert ('contract',) in index_fields
