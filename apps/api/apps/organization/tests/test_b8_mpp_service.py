"""Tests for B.8 MPP rendering service (HTML + PDF)."""
import pytest
from django.core.exceptions import ValidationError

from apps.organization.models import (
    Department,
    Position,
    PositionFunction,
    PositionProfile,
    PositionRegister,
    PositionRegisterEntry,
    PositionRequirement,
)
from apps.organization.services import render_mpp_html, render_mpp_pdf


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Ministerio de Economía",
        nombre_unidad_organica="Despacho Ministerial",
        siglas_area="MEF-DM",
    )


@pytest.fixture
def position(department):
    pos = Position.objects.create(
        code="DM-001",
        name="Director General de Asesoría Jurídica",
        department=department,
        servir_group="dp",
        servir_level="dp_3",
        salary_tier="principal",
        familia_puesto="Asesoría jurídica",
    )
    PositionProfile.objects.create(
        position=pos,
        mission="Asesorar jurídicamente al Despacho Ministerial.",
        work_conditions="Sede central, Lima.",
    )
    PositionFunction.objects.create(
        position=pos, description="Emitir opiniones legales", order=1,
    )
    PositionFunction.objects.create(
        position=pos, description="Coordinar con la Procuraduría Pública", order=2,
    )
    PositionRequirement.objects.create(
        position=pos, kind="education",
        description="Título de Abogado colegiado",
    )
    PositionRequirement.objects.create(
        position=pos, kind="experience",
        description="10+ años en sector público",
    )
    return pos


@pytest.fixture
def cpe_with_entry(db, position):
    register = PositionRegister.objects.create(
        register_type="cpe",
        title="CPE 2026 - MEF",
        description="Cuadro de Puestos de la Entidad",
    )
    PositionRegisterEntry.objects.create(
        register=register,
        position=position,
        sequence=1,
        plaza_code="MEF-CPE-001",
        plaza_count=1,
        situacion="vacante",
        nivel_organizacional="Alta Dirección",
        nivel_remunerativo="DP-3",
    )
    return register


@pytest.fixture
def cap_register(db):
    return PositionRegister.objects.create(
        register_type="cap",
        title="CAP 2026 - MEF",
    )


@pytest.mark.django_db
class TestRenderMPPHTML:
    def test_renders_register_title_and_status(self, cpe_with_entry):
        html = render_mpp_html(register_id=cpe_with_entry.id)
        assert "CPE 2026 - MEF" in html
        assert "Borrador" in html
        assert "Manual de Perfiles de Puestos" in html

    def test_renders_position_data(self, cpe_with_entry):
        html = render_mpp_html(register_id=cpe_with_entry.id)
        assert "Director General de Asesoría Jurídica" in html
        assert "DM-001" in html
        assert "MEF-CPE-001" in html

    def test_renders_servir_classification(self, cpe_with_entry):
        html = render_mpp_html(register_id=cpe_with_entry.id)
        assert "Directivo Público" in html  # servir_group display
        assert "DP-3" in html
        assert "Principal" in html  # salary_tier
        assert "Asesoría jurídica" in html  # familia_puesto

    def test_renders_mission_functions_requirements(self, cpe_with_entry):
        html = render_mpp_html(register_id=cpe_with_entry.id)
        assert "Asesorar jurídicamente al Despacho Ministerial." in html
        assert "Emitir opiniones legales" in html
        assert "Coordinar con la Procuraduría Pública" in html
        assert "Título de Abogado colegiado" in html
        assert "10+ años en sector público" in html

    def test_renders_institution_data_when_tenant_provided(self, cpe_with_entry):
        from apps.identity.models import User
        from apps.tenancy.models import Tenant
        creator = User.objects.create(
            username="t_creator", email="t@test.local",
            tipo_usuario="administrador", estado_usuario="activo",
        )
        tenant = Tenant.objects.create(
            slug="mef", name="Ministerio de Economía y Finanzas",
            ruc="20131370645", plan="enterprise", status="active",
            created_by=creator,
        )
        html = render_mpp_html(register_id=cpe_with_entry.id, tenant=tenant)
        assert "Ministerio de Economía y Finanzas" in html
        assert "20131370645" in html

    def test_renders_without_tenant(self, cpe_with_entry):
        html = render_mpp_html(register_id=cpe_with_entry.id, tenant=None)
        assert html  # no exception

    def test_rejects_cap_register(self, cap_register):
        with pytest.raises(ValidationError, match="solo puede generarse a partir de un CPE"):
            render_mpp_html(register_id=cap_register.id)

    def test_empty_cpe_renders_placeholder(self, db):
        empty = PositionRegister.objects.create(
            register_type="cpe", title="Empty CPE",
        )
        html = render_mpp_html(register_id=empty.id)
        assert "El CPE no contiene puestos." in html


@pytest.mark.django_db
class TestRenderMPPPDF:
    def test_renders_pdf_bytes(self, cpe_with_entry):
        pdf = render_mpp_pdf(register_id=cpe_with_entry.id)
        assert isinstance(pdf, (bytes, bytearray))
        assert len(pdf) > 100  # not an empty/stub PDF
        assert pdf[:4] == b"%PDF"  # PDF signature
