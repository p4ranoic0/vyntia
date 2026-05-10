"""Tests for B.6 Position model with ADR-B.7 versioning."""
import pytest
from django.core.exceptions import ValidationError

from apps.organization.models import Department, Position


@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_organo="Test Dirección",
        nombre_unidad_organica="Test Unidad",
        siglas_area="TST",
        unit_type="direccion",
    )


@pytest.mark.django_db
class TestPositionCreate:
    def test_create_position_with_required_fields(self, department):
        pos = Position.objects.create(
            code="ANA-001",
            name="Analista I",
            department=department,
        )
        assert pos.version == 1
        assert pos.is_current is True
        assert pos.parent_version is None
        assert pos.is_active is True

    def test_position_str_includes_code_and_version(self, department):
        pos = Position.objects.create(
            code="ANA-001",
            name="Analista I",
            department=department,
        )
        s = str(pos)
        assert "ANA-001" in s
        assert "v1" in s
        assert "Analista I" in s


@pytest.mark.django_db
class TestPositionVersioning:
    def test_create_new_version_increments_version_number(self, department):
        v1 = Position.objects.create(
            code="ANA-001",
            name="Analista I",
            department=department,
        )
        v2 = v1.create_new_version(name="Analista II")
        assert v2.version == 2
        assert v2.parent_version == v1

    def test_create_new_version_flips_is_current(self, department):
        v1 = Position.objects.create(
            code="ANA-001",
            name="Analista I",
            department=department,
        )
        v2 = v1.create_new_version(name="Analista II")
        v1.refresh_from_db()
        assert v1.is_current is False
        assert v2.is_current is True

    def test_create_new_version_applies_field_changes(self, department):
        v1 = Position.objects.create(
            code="ANA-001",
            name="Analista I",
            department=department,
        )
        v2 = v1.create_new_version(name="Analista Senior")
        assert v2.name == "Analista Senior"
        # Unchanged fields are inherited
        assert v2.department == department
        assert v2.code == "ANA-001"

    def test_cannot_version_non_current_position(self, department):
        v1 = Position.objects.create(
            code="ANA-001",
            name="Analista I",
            department=department,
        )
        v1.create_new_version(name="Analista II")
        # v1 is now non-current; trying to version it again should fail
        with pytest.raises(ValidationError):
            v1.create_new_version(name="Hacker")

    def test_unique_code_version_per_tenant_constraint_declared(self):
        """Constraint exists on Position._meta — actual enforcement is per
        PostgreSQL NULL-aware uniqueness (rows with tenant=NULL are not subject
        to the constraint per SQL spec, which is intentional for the transitory
        C.1 nullable phase)."""
        constraint_names = {c.name for c in Position._meta.constraints}
        assert "unique_position_code_version_per_tenant" in constraint_names

    def test_successors_relation(self, department):
        v1 = Position.objects.create(
            code="ANA-001",
            name="Analista I",
            department=department,
        )
        v2 = v1.create_new_version(name="Analista II")
        v2.create_new_version(name="Analista III")
        # v1's direct successor is v2; v2's is v3
        assert v1.successors.count() == 1
        assert v1.successors.first() == v2
        assert v1.has_successors is True
