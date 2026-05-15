"""Tests for B.10 tregistro_service (Anexo 3 + PVS validation)."""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.contracts.models import Contract, TRegistroDeclaration
from apps.contracts.services import tregistro_service
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
        numero_documento='10101010', tipo_documento='DNI',
        nombres_empleado='Ana', apellido_paterno='Lopez',
        apellido_materno='Vega', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def contract(employee, department):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato='CON-B10-TS-001',
        tipo_documento='LEY_728_FIJO',
        fecha_inicio=date.today(),
        fecha_fin=date.today() + timedelta(days=365),
        salario_bruto=Decimal('3000.00'),
        cargo='Analista', status='ACTIVO',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_ts', email='hr_ts@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


def _make_declaration(contract, employee, **overrides):
    defaults = dict(
        contract=contract, employee=employee,
        employer_ruc='20123456789', employer_razon_social='ACME SAC',
        worker_doc_type='01', worker_doc_number='10101010',
        worker_apellido_paterno='Lopez', worker_apellido_materno='Vega',
        worker_nombres='Ana', worker_birth_date=date(1990, 1, 1),
        worker_gender='F', worker_nationality_code='604',
        contract_start_date=date.today(),
        contract_end_date=date.today() + timedelta(days=365),
        work_modality_code='SBT', regimen_laboral_code='728',
        regimen_pensionario='snp', regimen_salud='essalud',
        remuneracion_basica=Decimal('3000.00'),
    )
    defaults.update(overrides)
    return TRegistroDeclaration.objects.create(**defaults)


@pytest.mark.django_db
class TestBuildAnexo3Txt:
    def test_header_format(self, contract, employee):
        d = _make_declaration(contract, employee)
        txt = tregistro_service.build_anexo3_txt(d)
        first_line = txt.split('\n')[0]
        assert first_line.startswith('H|TRREG|20123456789|ACME SAC|alta|')

    def test_includes_worker_contract_regimen_compensation_trailer(
        self, contract, employee,
    ):
        d = _make_declaration(contract, employee)
        txt = tregistro_service.build_anexo3_txt(d)
        lines = txt.split('\n')
        assert lines[0].startswith('H|')
        assert lines[1].startswith('W|01|10101010|Lopez|Vega|Ana|')
        assert lines[2].startswith('C|')
        assert lines[3].startswith('R|snp|')
        assert lines[4].startswith('S|3000.00|48')
        assert lines[5] == 'T|COUNT|1'

    def test_end_date_open_uses_sentinel(self, contract, employee):
        d = _make_declaration(contract, employee, contract_end_date=None)
        txt = tregistro_service.build_anexo3_txt(d)
        c_line = [
            line for line in txt.split('\n') if line.startswith('C|')
        ][0]
        assert '|99999999|' in c_line


@pytest.mark.django_db
class TestValidatePvs:
    def test_clean_declaration_passes(self, contract, employee):
        d = _make_declaration(contract, employee)
        assert tregistro_service.validate_pvs(d) == []

    def test_flags_wrong_ruc_length(self, contract, employee):
        d = _make_declaration(contract, employee, employer_ruc='123')
        errors = tregistro_service.validate_pvs(d)
        assert any('employer_ruc' in e for e in errors)

    def test_flags_invalid_doc_number_length(self, contract, employee):
        d = _make_declaration(contract, employee, worker_doc_number='123')
        errors = tregistro_service.validate_pvs(d)
        assert any('worker_doc_number' in e for e in errors)

    def test_flags_spp_missing_provider_and_cuspp(self, contract, employee):
        d = _make_declaration(
            contract, employee,
            regimen_pensionario='spp', pension_provider_code='', cuspp='',
        )
        errors = tregistro_service.validate_pvs(d)
        assert any('pension_provider_code' in e for e in errors)
        assert any('cuspp' in e for e in errors)

    def test_flags_eps_missing_code(self, contract, employee):
        d = _make_declaration(
            contract, employee, regimen_salud='eps', eps_code='',
        )
        errors = tregistro_service.validate_pvs(d)
        assert any('eps_code' in e for e in errors)

    def test_flags_underage_worker(self, contract, employee):
        d = _make_declaration(
            contract, employee, worker_birth_date=date.today() - timedelta(days=365 * 17),
        )
        errors = tregistro_service.validate_pvs(d)
        assert any('≥18 years' in e for e in errors)

    def test_flags_unknown_modality(self, contract, employee):
        d = _make_declaration(contract, employee, work_modality_code='XXX')
        errors = tregistro_service.validate_pvs(d)
        assert any('work_modality_code' in e for e in errors)

    def test_flags_end_before_start(self, contract, employee):
        d = _make_declaration(
            contract, employee,
            contract_end_date=date.today() - timedelta(days=10),
        )
        errors = tregistro_service.validate_pvs(d)
        assert any('contract_end_date' in e for e in errors)


@pytest.mark.django_db
class TestLifecycle:
    def test_validate_and_persist_clean_flips_to_validated(
        self, contract, employee,
    ):
        d = _make_declaration(contract, employee)
        out = tregistro_service.validate_and_persist(d.id)
        assert out.status == 'validated'
        assert out.pvs_errors == []
        assert out.anexo3_txt.startswith('H|TRREG|')

    def test_validate_and_persist_with_errors_stays_draft(
        self, contract, employee,
    ):
        d = _make_declaration(contract, employee, employer_ruc='bad')
        out = tregistro_service.validate_and_persist(d.id)
        assert out.status == 'draft'
        assert any('employer_ruc' in e for e in out.pvs_errors)

    def test_submit_declaration_runs_validate_then_submits(
        self, contract, employee, hr_user,
    ):
        d = _make_declaration(contract, employee)
        out = tregistro_service.submit_declaration(d.id, user=hr_user, reference='REF-1')
        assert out.status == 'submitted'
        assert out.sunat_reference == 'REF-1'
        assert out.submitted_by == hr_user
        assert out.anexo3_txt  # was generated

    def test_submit_blocks_when_errors(
        self, contract, employee, hr_user,
    ):
        d = _make_declaration(contract, employee, employer_ruc='bad')
        out = tregistro_service.submit_declaration(d.id, user=hr_user, reference='REF-2')
        assert out.status == 'draft'
        assert out.pvs_errors
