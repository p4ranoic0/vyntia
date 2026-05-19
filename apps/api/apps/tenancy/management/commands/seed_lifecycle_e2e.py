"""Seed minimal tenant + admin + org catalog needed by the Playwright lifecycle E2E.

This command provisions a deterministic, idempotent state so
`tests/e2e/employment-lifecycle.test.js` can drive a full Module 03 happy path
(hire -> onboarding -> desplazamiento -> cese) against a real local stack.

Usage:
    python manage.py seed_lifecycle_e2e [--settings=vyntia.settings.development]

Re-runnable: every resource is upserted (`get_or_create`/`update_or_create`).
The stdout ends with a single line `SEED_OUTPUT: {...json...}` that the
Playwright test parses to discover credentials and entity ids.

See: docs/operations/run-lifecycle-e2e.md, ADR-B.5, backlog item #132.
"""
import json

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department, Position
from apps.tenancy.models import Tenant, TenantMembership


TENANT_SLUG = "lifecycle"
TENANT_NAME = "Lifecycle E2E Test Co."
TENANT_RUC = "20999999999"
ADMIN_USERNAME = "admin_lifecycle"
ADMIN_EMAIL = "admin@lifecycle.test"
ADMIN_PASSWORD = "LifecyclePass123!"
STAFF_USERNAME = "lifecycle_seed_staff"
STAFF_EMAIL = "seed@vyntia.pe"
DEPT_SIGLAS = "TI"
DEPT_NAME = "Tecnología"
POSITION_CODE = "DEV-SR-01"
POSITION_NAME = "Desarrollador Senior"
ROLE_NAME = "Admin RRHH"


class Command(BaseCommand):
    help = "Seed tenant + admin + minimal org catalog for the Playwright employment-lifecycle E2E."

    @transaction.atomic
    def handle(self, *args, **options):
        staff = self._seed_staff_creator()
        tenant = self._seed_tenant(creator=staff)
        admin = self._seed_admin_user(tenant=tenant)
        self._seed_membership(tenant=tenant, user=admin)
        role = self._seed_role(tenant=tenant)
        self._seed_user_role(tenant=tenant, user=admin, role=role)
        department = self._seed_department(tenant=tenant)
        position = self._seed_position(tenant=tenant, department=department)

        payload = {
            "tenant_id": str(tenant.id),
            "tenant_slug": tenant.slug,
            "tenant_host": f"{tenant.slug}.vyntia.pe",
            "admin_email": admin.email,
            "admin_username": admin.username,
            "admin_password": ADMIN_PASSWORD,
            "department_id": str(department.id),
            "position_id": str(position.id),
            "role_id": str(role.id),
        }
        self.stdout.write(self.style.SUCCESS("Lifecycle E2E seed complete."))
        self.stdout.write(f"SEED_OUTPUT: {json.dumps(payload)}")

    def _seed_staff_creator(self):
        user, created = User.objects.get_or_create(
            username=STAFF_USERNAME,
            defaults={
                "email": STAFF_EMAIL,
                "nombres_usuario": "Lifecycle",
                "apellidos_usuario": "Seed",
                "tipo_usuario": "administrador",
                "is_vyntia_staff": True,
                "is_active": True,
            },
        )
        if created:
            user.set_unusable_password()
            user.save(update_fields=["password"])
            self.stdout.write(f"Created vyntia-staff creator: {user.username}")
        return user

    def _seed_tenant(self, *, creator):
        tenant, created = Tenant.objects.get_or_create(
            slug=TENANT_SLUG,
            defaults={
                "name": TENANT_NAME,
                "ruc": TENANT_RUC,
                "plan": "starter",
                "status": "active",
                "created_by": creator,
            },
        )
        if not created and tenant.status != "active":
            tenant.status = "active"
            tenant.save(update_fields=["status"])
        self.stdout.write(f"{'Created' if created else 'Reused'} tenant: {tenant.slug}")
        return tenant

    def _seed_admin_user(self, *, tenant):
        user, created = User.objects.get_or_create(
            username=ADMIN_USERNAME,
            defaults={
                "email": ADMIN_EMAIL,
                "nombres_usuario": "Admin",
                "apellidos_usuario": "Lifecycle",
                "tipo_usuario": "administrador",
                "nivel_acceso": "total",
                "is_active": True,
            },
        )
        # Always re-stamp password so the seed remains the source of truth
        # across re-runs.
        user.set_password(ADMIN_PASSWORD)
        user.save(update_fields=["password"])
        self.stdout.write(f"{'Created' if created else 'Updated'} admin user: {user.username}")
        return user

    def _seed_membership(self, *, tenant, user):
        membership, created = TenantMembership.objects.get_or_create(
            tenant=tenant,
            user=user,
            defaults={"role": "admin", "status": "active"},
        )
        if not created and membership.status != "active":
            membership.status = "active"
            membership.save(update_fields=["status"])
        self.stdout.write(
            f"{'Created' if created else 'Reused'} membership: {user.username}@{tenant.slug}"
        )
        return membership

    def _seed_role(self, *, tenant):
        role, created = Role.objects.get_or_create(
            tenant=tenant,
            nombre_rol=ROLE_NAME,
            defaults={
                "descripcion_rol": "Admin RRHH seeded by seed_lifecycle_e2e.",
                "nivel_jerarquico": 1,
                "es_rol_sistema": True,
                "estado_rol": "activo",
            },
        )
        self.stdout.write(f"{'Created' if created else 'Reused'} role: {role.nombre_rol}")
        return role

    def _seed_user_role(self, *, tenant, user, role):
        ur, created = UserRole.objects.get_or_create(
            tenant=tenant,
            usuario=user,
            rol=role,
            defaults={"estado_asignacion": "activo"},
        )
        if not created and ur.estado_asignacion != "activo":
            ur.estado_asignacion = "activo"
            ur.save(update_fields=["estado_asignacion"])
        self.stdout.write(
            f"{'Created' if created else 'Reused'} user-role: {user.username} -> {role.nombre_rol}"
        )
        return ur

    def _seed_department(self, *, tenant):
        department, created = Department.objects.get_or_create(
            tenant=tenant,
            siglas_area=DEPT_SIGLAS,
            defaults={
                "nombre_organo": "Gerencia General",
                "nombre_unidad_organica": DEPT_NAME,
                "unit_type": "gerencia",
                "estado_area": "activo",
                "nivel_jerarquico": 1,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Reused'} department: {department.siglas_area}"
        )
        return department

    def _seed_position(self, *, tenant, department):
        position, created = Position.objects.get_or_create(
            tenant=tenant,
            code=POSITION_CODE,
            version=1,
            defaults={
                "name": POSITION_NAME,
                "department": department,
                "is_current": True,
            },
        )
        self.stdout.write(
            f"{'Created' if created else 'Reused'} position: {position.code} - {position.name}"
        )
        return position
