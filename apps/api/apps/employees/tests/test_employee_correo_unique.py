"""Tests for Employee.correo_personal per-tenant uniqueness (B.4 #21)."""

import pytest
from django.db import IntegrityError, transaction


def _make_tenant(slug, name, admin_user):
    """Helper: create a Tenant with required fields."""
    from apps.tenancy.models import Tenant
    return Tenant.objects.create(
        slug=slug,
        name=name,
        ruc="20999999999",
        plan="starter",
        status="active",
        created_by=admin_user,
    )


def _make_admin(username):
    """Helper: create a minimal staff user."""
    from apps.identity.models import User
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        password="testpass",
    )


@pytest.mark.django_db
class TestEmployeeCorreoPersonalUnique:
    def test_two_tenants_can_have_same_correo_personal(self):
        from apps.employees.models import Employee

        admin = _make_admin("admin_cp21a")
        ta = _make_tenant("cp-ta21", "CP TA21", admin)
        tb = _make_tenant("cp-tb21", "CP TB21", admin)

        Employee.objects.create(
            tenant=ta,
            nombres_empleado="A21",
            apellido_paterno="X",
            apellido_materno="Y",
            numero_documento="11111121",
            tipo_documento="DNI",
            estado_empleado="activo",
            correo_personal="shared21@example.com",
        )
        # Same correo in different tenant — must succeed
        Employee.objects.create(
            tenant=tb,
            nombres_empleado="B21",
            apellido_paterno="X",
            apellido_materno="Y",
            numero_documento="22222221",
            tipo_documento="DNI",
            estado_empleado="activo",
            correo_personal="shared21@example.com",
        )

    def test_same_tenant_blocks_duplicate_correo_personal(self):
        from apps.employees.models import Employee

        admin = _make_admin("admin_cp21b")
        tc = _make_tenant("cp-tc21", "CP TC21", admin)
        Employee.objects.create(
            tenant=tc,
            nombres_empleado="C1_21",
            apellido_paterno="X",
            apellido_materno="Y",
            numero_documento="33333321",
            tipo_documento="DNI",
            estado_empleado="activo",
            correo_personal="dup21@example.com",
        )
        with pytest.raises(IntegrityError):
            with transaction.atomic():
                Employee.objects.create(
                    tenant=tc,
                    nombres_empleado="C2_21",
                    apellido_paterno="X",
                    apellido_materno="Y",
                    numero_documento="44444421",
                    tipo_documento="DNI",
                    estado_empleado="activo",
                    correo_personal="dup21@example.com",
                )

    def test_empty_correo_personal_does_not_collide_across_tenants(self):
        """Partial-index condition: empty correos shouldn't enforce unique."""
        from apps.employees.models import Employee

        admin = _make_admin("admin_cp21c")
        td = _make_tenant("cp-td21", "CP TD21", admin)
        # Two employees in same tenant with no email — should both be allowed
        Employee.objects.create(
            tenant=td,
            nombres_empleado="D1_21",
            apellido_paterno="X",
            apellido_materno="Y",
            numero_documento="55555521",
            tipo_documento="DNI",
            estado_empleado="activo",
            correo_personal="",
        )
        Employee.objects.create(
            tenant=td,
            nombres_empleado="D2_21",
            apellido_paterno="X",
            apellido_materno="Y",
            numero_documento="66666621",
            tipo_documento="DNI",
            estado_empleado="activo",
            correo_personal="",
        )
