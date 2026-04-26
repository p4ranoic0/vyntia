# -*- coding: utf-8 -*-
"""
Comando de gestión: audit_rbac
Realiza auditoría completa del sistema RBAC para detectar inconsistencias.

Uso:
    python manage.py audit_rbac
    python manage.py audit_rbac --verbose
"""

from apps.identity.models import (
    ModuloPermiso,
    Modulos,
    Permiso,
    Rol,
    RolPermisos,
    Usuario,
    UsuarioRoles,
)
from django.core.management.base import BaseCommand
from django.db.models import Count, Q


class Command(BaseCommand):
    help = "Audita integridad del sistema RBAC: permisos, roles, modulos y usuarios"

    def add_arguments(self, parser):
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Muestra detalles completos de cada hallazgo",
        )
        parser.add_argument(
            "--fix-orphans",
            action="store_true",
            help="Elimina permisos huerfanos automaticamente",
        )

    def handle(self, *args, **options):
        verbose = options.get("verbose", False)
        fix_orphans = options.get("fix_orphans", False)

        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write(
            self.style.HTTP_INFO("AUDITORIA RBAC - Sistema de Permisos y Menus")
        )
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write("")

        # Contadores generales
        self._show_summary()

        # 1. Permisos huérfanos (no vinculados a ningún módulo)
        orphan_perms = self._check_orphan_permissions(verbose, fix_orphans)

        # 2. Módulos sin permisos asignados
        modules_no_perms = self._check_modules_without_permissions(verbose)

        # 3. Módulos con permisos_requeridos CSV pero sin pivot
        modules_csv_no_pivot = self._check_csv_not_synced(verbose)

        # 4. Roles sin permisos asignados
        roles_no_perms = self._check_roles_without_permissions(verbose)

        # 5. Usuarios activos sin roles
        users_no_roles = self._check_users_without_roles(verbose)

        # 6. Usuarios con roles inactivos
        users_inactive_roles = self._check_users_with_inactive_roles(verbose)

        # 7. Permisos duplicados por nombre
        duplicate_perms = self._check_duplicate_permissions(verbose)

        # Resumen final
        self._show_final_summary(
            orphan_perms,
            modules_no_perms,
            modules_csv_no_pivot,
            roles_no_perms,
            users_no_roles,
            users_inactive_roles,
            duplicate_perms,
        )

    def _show_summary(self):
        """Muestra contadores generales del sistema."""
        total_modulos = Modulos.objects.count()
        total_modulos_activos = Modulos.objects.filter(estado_modulo="activo").count()
        total_permisos = Permiso.objects.count()
        total_modulo_permisos = ModuloPermiso.objects.count()
        total_roles = Rol.objects.count()
        total_roles_activos = Rol.objects.filter(estado_rol="activo").count()
        total_usuarios = Usuario.objects.filter(estado_usuario="activo").count()

        self.stdout.write(self.style.SUCCESS("[*] Resumen General"))
        self.stdout.write(
            f"   Modulos: {total_modulos_activos}/{total_modulos} activos"
        )
        self.stdout.write(f"   Permisos: {total_permisos}")
        self.stdout.write(f"   Relaciones Modulo-Permiso: {total_modulo_permisos}")
        self.stdout.write(f"   Roles: {total_roles_activos}/{total_roles} activos")
        self.stdout.write(f"   Usuarios: {total_usuarios}")
        self.stdout.write("")

    def _check_orphan_permissions(self, verbose, fix_orphans):
        """Detecta permisos no vinculados a ningún módulo."""
        orphan_perms = Permiso.objects.annotate(
            num_modulos=Count("modulos_relacionados")
        ).filter(num_modulos=0)
        count = orphan_perms.count()

        if count > 0:
            self.stdout.write(self.style.WARNING(f"[!] Permisos huerfanos: {count}"))
            if verbose:
                for perm in orphan_perms:
                    self.stdout.write(
                        f"   - {perm.nombre_permiso} (ID: {perm.permiso_id})"
                    )

            if fix_orphans:
                deleted_count, _ = orphan_perms.delete()
                self.stdout.write(
                    self.style.SUCCESS(
                        f"   [OK] Eliminados {deleted_count} permisos huerfanos"
                    )
                )
        else:
            self.stdout.write(self.style.SUCCESS("[OK] Sin permisos huerfanos"))

        self.stdout.write("")
        return count

    def _check_modules_without_permissions(self, verbose):
        """Detecta módulos activos sin permisos asignados."""
        modules_no_perms = (
            Modulos.objects.filter(estado_modulo="activo")
            .annotate(num_permisos=Count("modulo_permisos"))
            .filter(num_permisos=0)
        )
        count = modules_no_perms.count()

        if count > 0:
            self.stdout.write(
                self.style.WARNING(f"[!] Modulos activos sin permisos: {count}")
            )
            if verbose:
                for mod in modules_no_perms:
                    self.stdout.write(
                        f"   - {mod.nombre_modulo} (Ruta: {mod.ruta_modulo or 'N/A'})"
                    )
        else:
            self.stdout.write(
                self.style.SUCCESS("[OK] Todos los modulos activos tienen permisos")
            )

        self.stdout.write("")
        return count

    def _check_csv_not_synced(self, verbose):
        """Detecta módulos con permisos_requeridos CSV pero sin pivot."""
        modules_csv = (
            Modulos.objects.filter(
                ~Q(permisos_requeridos="") & ~Q(permisos_requeridos__isnull=True)
            )
            .annotate(num_pivot=Count("modulo_permisos"))
            .filter(num_pivot=0)
        )
        count = modules_csv.count()

        if count > 0:
            self.stdout.write(
                self.style.WARNING(f"[!] Modulos con CSV no sincronizado: {count}")
            )
            if verbose:
                for mod in modules_csv:
                    self.stdout.write(
                        f"   - {mod.nombre_modulo}: {mod.permisos_requeridos}"
                    )
            self.stdout.write(
                self.style.HTTP_INFO(
                    "   [i] Ejecuta 'python manage.py seed_menu' para sincronizar"
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("[OK] Todos los CSV sincronizados con pivot")
            )

        self.stdout.write("")
        return count

    def _check_roles_without_permissions(self, verbose):
        """Detecta roles activos sin permisos asignados."""
        roles_no_perms = (
            Rol.objects.filter(estado_rol="activo")
            .annotate(num_permisos=Count("permisos_asignados"))
            .filter(num_permisos=0)
        )
        count = roles_no_perms.count()

        if count > 0:
            self.stdout.write(
                self.style.WARNING(f"[!] Roles activos sin permisos: {count}")
            )
            if verbose:
                for rol in roles_no_perms:
                    self.stdout.write(
                        f"   - {rol.nombre_rol} (Codigo: {rol.codigo_rol})"
                    )
        else:
            self.stdout.write(
                self.style.SUCCESS("[OK] Todos los roles activos tienen permisos")
            )

        self.stdout.write("")
        return count

    def _check_users_without_roles(self, verbose):
        """Detecta usuarios activos sin roles asignados."""
        users_no_roles = (
            Usuario.objects.filter(estado_usuario="activo", tipo_usuario="empleado")
            .annotate(num_roles=Count("roles_asignados"))
            .filter(num_roles=0)
        )
        count = users_no_roles.count()

        if count > 0:
            self.stdout.write(
                self.style.WARNING(f"[!] Usuarios activos sin roles: {count}")
            )
            if verbose:
                for user in users_no_roles[:10]:  # Limitar a 10 para no saturar
                    self.stdout.write(f"   - {user.username} ({user.get_full_name()})")
                if count > 10:
                    self.stdout.write(f"   ... y {count - 10} mas")
        else:
            self.stdout.write(
                self.style.SUCCESS("[OK] Todos los usuarios activos tienen roles")
            )

        self.stdout.write("")
        return count

    def _check_users_with_inactive_roles(self, verbose):
        """Detecta usuarios con todos sus roles inactivos."""
        users_inactive = (
            Usuario.objects.filter(estado_usuario="activo", tipo_usuario="empleado")
            .annotate(
                total_roles=Count("roles_asignados"),
                active_roles=Count(
                    "roles_asignados",
                    filter=Q(roles_asignados__estado_asignacion="activo"),
                ),
            )
            .filter(total_roles__gt=0, active_roles=0)
        )
        count = users_inactive.count()

        if count > 0:
            self.stdout.write(
                self.style.WARNING(f"[!] Usuarios con roles inactivos: {count}")
            )
            if verbose:
                for user in users_inactive[:10]:
                    self.stdout.write(f"   - {user.username} ({user.get_full_name()})")
                if count > 10:
                    self.stdout.write(f"   ... y {count - 10} mas")
        else:
            self.stdout.write(
                self.style.SUCCESS("[OK] Sin usuarios con todos sus roles inactivos")
            )

        self.stdout.write("")
        return count

    def _check_duplicate_permissions(self, verbose):
        """Detecta permisos con nombres duplicados."""
        duplicates = (
            Permiso.objects.values("nombre_permiso")
            .annotate(count=Count("permiso_id"))
            .filter(count__gt=1)
        )
        count = duplicates.count()

        if count > 0:
            self.stdout.write(self.style.ERROR(f"[X] Permisos duplicados: {count}"))
            if verbose:
                for dup in duplicates:
                    perms = Permiso.objects.filter(nombre_permiso=dup["nombre_permiso"])
                    ids = ", ".join(str(p.permiso_id) for p in perms)
                    self.stdout.write(f"   - {dup['nombre_permiso']}: IDs {ids}")
        else:
            self.stdout.write(self.style.SUCCESS("[OK] Sin permisos duplicados"))

        self.stdout.write("")
        return count

    def _show_final_summary(
        self,
        orphan_perms,
        modules_no_perms,
        modules_csv_no_pivot,
        roles_no_perms,
        users_no_roles,
        users_inactive_roles,
        duplicate_perms,
    ):
        """Muestra resumen final de hallazgos."""
        self.stdout.write(self.style.HTTP_INFO("=" * 70))
        self.stdout.write(self.style.HTTP_INFO("RESUMEN DE HALLAZGOS"))
        self.stdout.write(self.style.HTTP_INFO("=" * 70))

        total_issues = (
            orphan_perms
            + modules_no_perms
            + modules_csv_no_pivot
            + roles_no_perms
            + users_no_roles
            + users_inactive_roles
            + duplicate_perms
        )

        if total_issues == 0:
            self.stdout.write(
                self.style.SUCCESS("[OK] Sistema RBAC en perfecto estado!")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"[!] Total de hallazgos: {total_issues}")
            )
            self.stdout.write("")
            self.stdout.write("[i] Recomendaciones:")
            if modules_csv_no_pivot > 0:
                self.stdout.write(
                    "   - Ejecuta 'python manage.py seed_menu' para sincronizar"
                )
            if orphan_perms > 0:
                self.stdout.write(
                    "   - Usa '--fix-orphans' para eliminar permisos huerfanos"
                )
            if duplicate_perms > 0:
                self.stdout.write(
                    "   - Revisa y consolida permisos duplicados manualmente"
                )
            if users_no_roles > 0 or users_inactive_roles > 0:
                self.stdout.write("   - Asigna roles a usuarios o actualiza su estado")

        self.stdout.write("")
