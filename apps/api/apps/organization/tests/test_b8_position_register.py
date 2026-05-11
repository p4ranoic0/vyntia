"""Tests for B.8 PositionRegister + PositionRegisterEntry (CPE + CAP)."""
import pytest
from django.core.exceptions import ValidationError

from apps.organization.models import (
    Department,
    Position,
    PositionRegister,
    PositionRegisterEntry,
)


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test",
        nombre_unidad_organica="Test",
        siglas_area="T",
    )


@pytest.fixture
def position(department):
    return Position.objects.create(
        code="DIR-001",
        name="Director General",
        department=department,
        servir_group="dp",
        servir_level="dp_3",
        salary_tier="principal",
    )


@pytest.fixture
def admin_user(db):
    from apps.identity.models import User
    return User.objects.create(
        username="admin_b8",
        email="admin_b8@test.local",
        tipo_usuario="administrador",
        estado_usuario="activo",
    )


@pytest.fixture
def cpe_register(db):
    return PositionRegister.objects.create(
        register_type="cpe",
        title="CPE 2026 - MEF",
        description="Cuadro de Puestos de la Entidad",
    )


@pytest.fixture
def cap_register(db):
    return PositionRegister.objects.create(
        register_type="cap",
        title="CAP 2026 - MEF",
        description="Cuadro de Asignación de Personal",
    )


@pytest.mark.django_db
class TestPositionRegisterLifecycle:
    def test_cpe_register_defaults(self, cpe_register):
        assert cpe_register.register_type == "cpe"
        assert cpe_register.version == 1
        assert cpe_register.status == "draft"
        assert cpe_register.parent_version is None
        assert cpe_register.approved_at is None
        assert cpe_register.servir_registered_at is None

    def test_cap_register_defaults(self, cap_register):
        assert cap_register.register_type == "cap"
        assert cap_register.status == "draft"

    def test_register_type_choices_cover_cpe_and_cap(self):
        kinds = {k for k, _ in PositionRegister.REGISTER_TYPE_CHOICES}
        assert kinds == {"cpe", "cap"}

    def test_status_choices_include_servir_registered(self):
        statuses = {k for k, _ in PositionRegister.STATUS_CHOICES}
        assert statuses == {
            "draft", "approved", "registered_servir", "superseded", "archived",
        }

    def test_approve_register(self, cpe_register, admin_user):
        cpe_register.approve(user=admin_user)
        cpe_register.refresh_from_db()
        assert cpe_register.status == "approved"
        assert cpe_register.approved_at is not None
        assert cpe_register.approved_by == admin_user
        assert cpe_register.effective_date is not None

    def test_approve_archived_raises(self, cpe_register, admin_user):
        cpe_register.status = "archived"
        cpe_register.save()
        with pytest.raises(ValidationError):
            cpe_register.approve(user=admin_user)

    def test_register_in_servir_only_on_cpe(self, cap_register, admin_user):
        cap_register.approve(user=admin_user)
        with pytest.raises(ValidationError, match="Solo CPE se registra en SERVIR"):
            cap_register.register_in_servir(reference="REF-001")

    def test_register_in_servir_requires_approval(self, cpe_register):
        # draft → cannot register in SERVIR
        with pytest.raises(ValidationError):
            cpe_register.register_in_servir(reference="REF-001")

    def test_register_in_servir_marks_status_and_ref(self, cpe_register, admin_user):
        cpe_register.approve(user=admin_user)
        cpe_register.register_in_servir(reference="SERVIR-2026-MEF-001")
        cpe_register.refresh_from_db()
        assert cpe_register.status == "registered_servir"
        assert cpe_register.servir_registered_at is not None
        assert cpe_register.servir_registration_ref == "SERVIR-2026-MEF-001"


@pytest.mark.django_db
class TestPositionRegisterEntry:
    def test_add_entry_to_cpe_register(self, cpe_register, position):
        entry = PositionRegisterEntry.objects.create(
            register=cpe_register,
            position=position,
            sequence=1,
            plaza_code="MEF-CPE-001",
            plaza_count=1,
            situacion="vacante",
            nivel_organizacional="Alta Dirección",
            nivel_remunerativo="Nivel 5",
        )
        assert entry.register == cpe_register
        assert entry.position == position
        assert entry.situacion == "vacante"
        assert entry.nivel_organizacional == "Alta Dirección"

    def test_add_entry_to_cap_register(self, cap_register, position):
        entry = PositionRegisterEntry.objects.create(
            register=cap_register,
            position=position,
            sequence=1,
            plaza_code="MEF-CAP-001",
            plaza_count=2,
            situacion="ocupada",
            clasificacion_cap="sp_ds",
        )
        assert entry.clasificacion_cap == "sp_ds"
        assert entry.get_clasificacion_cap_display() == "SP-DS - Directivo Superior"
        assert entry.plaza_count == 2

    def test_situation_choices(self):
        situations = {k for k, _ in PositionRegisterEntry.SITUATION_CHOICES}
        assert situations == {"ocupada", "vacante", "prevista"}

    def test_cap_classification_covers_dl_276_groups(self):
        kinds = {k for k, _ in PositionRegisterEntry.CAP_CLASSIFICATION_CHOICES}
        assert kinds == {"fp", "ec", "sp_ds", "sp_ej", "sp_es", "sp_ap", "re"}

    def test_cascade_delete_register_removes_entries(self, cpe_register, position):
        PositionRegisterEntry.objects.create(
            register=cpe_register, position=position, sequence=1,
        )
        PositionRegisterEntry.objects.create(
            register=cpe_register, position=position, sequence=2,
        )
        assert PositionRegisterEntry.objects.filter(register=cpe_register).count() == 2
        cpe_register.delete()
        assert PositionRegisterEntry.objects.count() == 0

    def test_position_protect_blocks_position_delete(self, cpe_register, position):
        from django.db.models import ProtectedError
        PositionRegisterEntry.objects.create(
            register=cpe_register, position=position, sequence=1,
        )
        with pytest.raises(ProtectedError):
            position.delete()

    def test_unique_constraint_per_tenant_register_type(self):
        constraint_names = {c.name for c in PositionRegister._meta.constraints}
        assert "unique_position_register_title_version_per_tenant" in constraint_names
