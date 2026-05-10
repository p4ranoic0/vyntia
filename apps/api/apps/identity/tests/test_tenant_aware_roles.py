"""Tests for tenant-scoped roles_activos/permisos_activos (B.2 #48)."""

import pytest

from apps.tenancy.context import tenant_context


@pytest.mark.django_db
class TestRolesActivosTenantFilter:
    def _setup_two_tenants_with_roles(self):
        from apps.tenancy.models import Tenant
        from apps.identity.models import User, Role
        from apps.identity.models.rbac import UserRole

        # Need a staff user for created_by (Tenant requires it)
        staff = User.objects.create_user(
            username="iso_tar_staff",
            email="iso_tar@vyntia.pe",
            password="testpass123",
        )

        ta = Tenant.objects.create(
            slug="tar-ta", name="TAR Tenant A", ruc="20111111901",
            plan="starter", status="active", created_by=staff,
        )
        tb = Tenant.objects.create(
            slug="tar-tb", name="TAR Tenant B", ruc="20111111902",
            plan="starter", status="active", created_by=staff,
        )

        user = User(username="multi_tar", email="m@m.local", is_active=True, estado_usuario="activo")
        user.set_password("x")
        user.save()

        role_a = Role.objects.create(nombre_rol="OnlyA_TAR", estado_rol="activo", tenant=ta)
        role_b = Role.objects.create(nombre_rol="OnlyB_TAR", estado_rol="activo", tenant=tb)

        UserRole.objects.create(usuario=user, rol=role_a, estado_asignacion="activo", tenant=ta)
        UserRole.objects.create(usuario=user, rol=role_b, estado_asignacion="activo", tenant=tb)

        return user, ta, tb

    def test_roles_activos_filters_by_current_tenant(self):
        user, ta, tb = self._setup_two_tenants_with_roles()

        with tenant_context(ta):
            roles_a = list(user.roles_activos().values_list("nombre_rol", flat=True))

        with tenant_context(tb):
            roles_b = list(user.roles_activos().values_list("nombre_rol", flat=True))

        assert "OnlyA_TAR" in roles_a and "OnlyB_TAR" not in roles_a
        assert "OnlyB_TAR" in roles_b and "OnlyA_TAR" not in roles_b

    def test_roles_activos_returns_all_when_no_tenant_context(self):
        user, ta, tb = self._setup_two_tenants_with_roles()
        all_roles = set(user.roles_activos().values_list("nombre_rol", flat=True))
        assert "OnlyA_TAR" in all_roles
        assert "OnlyB_TAR" in all_roles


@pytest.mark.django_db
class TestPermisosActivosTenantFilter:
    def test_permisos_activos_filters_by_current_tenant(self):
        from apps.tenancy.models import Tenant
        from apps.identity.models import User, Role, Permission
        from apps.identity.models.rbac import UserRole, RolePermission

        # Need a staff user for created_by (Tenant requires it)
        staff = User.objects.create_user(
            username="iso_pat_staff",
            email="iso_pat@vyntia.pe",
            password="testpass123",
        )

        ta = Tenant.objects.create(
            slug="pat-ta", name="PAT Tenant A", ruc="20111112001",
            plan="starter", status="active", created_by=staff,
        )
        tb = Tenant.objects.create(
            slug="pat-tb", name="PAT Tenant B", ruc="20111112002",
            plan="starter", status="active", created_by=staff,
        )

        user = User(username="pmulti_pat", email="pm@m.local", is_active=True, estado_usuario="activo")
        user.set_password("x")
        user.save()

        role_a = Role.objects.create(nombre_rol="PA_PAT", estado_rol="activo", tenant=ta)
        role_b = Role.objects.create(nombre_rol="PB_PAT", estado_rol="activo", tenant=tb)

        perm_a = Permission.objects.create(
            nombre_permiso="perm_a_pat", modulo="empleados",
            tipo_permiso="leer", estado_permiso="activo", tenant=ta,
        )
        perm_b = Permission.objects.create(
            nombre_permiso="perm_b_pat", modulo="empleados",
            tipo_permiso="leer", estado_permiso="activo", tenant=tb,
        )

        RolePermission.objects.create(rol=role_a, permiso=perm_a, tenant=ta)
        RolePermission.objects.create(rol=role_b, permiso=perm_b, tenant=tb)

        UserRole.objects.create(usuario=user, rol=role_a, estado_asignacion="activo", tenant=ta)
        UserRole.objects.create(usuario=user, rol=role_b, estado_asignacion="activo", tenant=tb)

        with tenant_context(ta):
            perms_a = set(user.permisos_activos().values_list("nombre_permiso", flat=True))
        with tenant_context(tb):
            perms_b = set(user.permisos_activos().values_list("nombre_permiso", flat=True))

        assert perms_a == {"perm_a_pat"}
        assert perms_b == {"perm_b_pat"}
