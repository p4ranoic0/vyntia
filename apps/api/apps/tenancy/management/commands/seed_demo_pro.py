"""Seed a demo Pro tenant with realistic Peruvian HR data.

This command provisions a deterministic, idempotent tenant + admin + 15 empleados
with contracts, families, academic records, plus a B.9 ATS sample (candidates +
posting + applications) and B.12 digital dossiers for the first 3 employees.

The goal is to make manual exploration, specialist-agent audits, and demos
more legible than an empty database.

Usage:
    python manage.py seed_demo_pro [--fresh]

Flags:
    --fresh   Delete existing demo-pro tenant data first (employees, contracts,
              dossiers, candidates, postings, requisitions, departments,
              memberships, users specific to this tenant, and the tenant
              itself), then reseed. Other tenants are NOT touched.

Re-runnable without --fresh: every resource is upserted (get_or_create /
update_or_create). The stdout ends with a single line
`SEED_OUTPUT: {...json...}` with credentials and entity ids so callers
(agents, tests, scripts) can navigate the data without scraping the DB.

See: docs/agent-reports/pm/2026-05-22-empleados.md (motivated this seed).
"""
from __future__ import annotations

import json
from datetime import date, time, timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.contracts.models import Contract, EmploymentData
from apps.documents.models import DigitalDossier, DocumentAccessLog
from apps.documents.services import dossier_service
from apps.employees.models import (
    AcademicRecord,
    Candidate,
    CandidateEvaluation,
    Employee,
    FamilyMember,
    JobApplication,
    JobPosting,
    MeritRanking,
    PersonnelRequisition,
    SelectionStage,
)
from apps.employees.services import compute_merit_ranking
from apps.identity.models import Permission, Role, RolePermission, User, UserRole
from apps.organization.models import Department, Position
from apps.tenancy.models import Tenant, TenantMembership


# === Constants ===

TENANT_SLUG = "demo-pro"
TENANT_NAME = "Demo Vyntia Pro S.A.C."
TENANT_RUC = "20512345678"

STAFF_USERNAME = "vyntia_demo_seed_staff"
STAFF_EMAIL = "seed-pro@vyntia.pe"

ADMIN_USERNAME = "admin_demo_pro"
ADMIN_EMAIL = "admin@demo-pro.vyntia.pe"
ADMIN_PASSWORD = "DemoProAdmin123!"

RRHH_USERNAME = "rrhh_demo_pro"
RRHH_EMAIL = "rrhh@demo-pro.vyntia.pe"
RRHH_PASSWORD = "DemoProRRHH123!"

# Role names MUST match apps.core.constants.Roles. The audit catched the seed
# using "Admin"/"RRHH" which never satisfied @require_hr (case-sensitive).
ROLE_ADMIN = "Administrador RRHH"  # core.constants.Roles.ADMIN_RRHH
ROLE_RRHH = "Analista RRHH"        # core.constants.Roles.ANALISTA_RRHH

# Departments to create (siglas, nombre_unidad_organica)
DEPARTMENTS = [
    ("GG", "Gerencia General"),
    ("RRHH", "Recursos Humanos"),
    ("TI", "Tecnología de la Información"),
    ("FIN", "Finanzas y Contabilidad"),
    ("COM", "Comercial y Ventas"),
    ("OPE", "Operaciones"),
]

# Positions per department (code, name, category)
POSITIONS = [
    ("GG-01", "Gerente General", "directivo", "GG"),
    ("RRHH-01", "Jefe de RRHH", "funcionario", "RRHH"),
    ("RRHH-02", "Analista de RRHH", "profesional", "RRHH"),
    ("TI-01", "Jefe de TI", "funcionario", "TI"),
    ("TI-02", "Desarrollador Senior", "profesional", "TI"),
    ("TI-03", "Desarrollador Junior", "profesional", "TI"),
    ("FIN-01", "Contador Senior", "profesional", "FIN"),
    ("FIN-02", "Asistente Contable", "tecnico", "FIN"),
    ("COM-01", "Ejecutivo Comercial", "profesional", "COM"),
    ("OPE-01", "Supervisor de Operaciones", "profesional", "OPE"),
]

# 15 Peruvian empleados: (nombres, apellido_paterno, apellido_materno, genero, dni_offset, position_code, sueldo, hire_year_offset)
EMPLOYEES = [
    ("Carlos Alberto", "Quispe", "Mamani", "masculino", 1, "GG-01", 15000, -5),
    ("María Lucía", "García", "Torres", "femenino", 2, "RRHH-01", 8500, -4),
    ("Ana Patricia", "Flores", "Vargas", "femenino", 3, "RRHH-02", 4200, -2),
    ("Luis Fernando", "Rodríguez", "Castro", "masculino", 4, "TI-01", 9200, -3),
    ("José Miguel", "Huamán", "Vilca", "masculino", 5, "TI-02", 6500, -1),
    ("Pedro Andrés", "Apaza", "Condori", "masculino", 6, "TI-02", 6200, -2),
    ("Rosa Carmen", "Pérez", "Ramírez", "femenino", 7, "TI-03", 3800, 0),
    ("Sofía Beatriz", "Mendoza", "Salazar", "femenino", 8, "FIN-01", 5500, -3),
    ("Ricardo Daniel", "Núñez", "Espinoza", "masculino", 9, "FIN-02", 2400, -1),
    ("Patricia Elena", "Loayza", "Bermúdez", "femenino", 10, "COM-01", 4500, -2),
    ("Andrés Sebastián", "Cárdenas", "Yupanqui", "masculino", 11, "COM-01", 4300, 0),
    ("Carmen Rosa", "Choque", "Sullca", "femenino", 12, "OPE-01", 4800, -4),
    ("Miguel Ángel", "Saavedra", "Linares", "masculino", 13, "TI-03", 3500, 0),
    ("Lucía Esperanza", "Tello", "Pacheco", "femenino", 14, "RRHH-02", 4100, -1),
    ("Juan Carlos", "Mejía", "Atoche", "masculino", 15, "FIN-02", 2600, -2),
]

# 5 B.9 candidates: (nombres, apellidos, dni_offset, email)
CANDIDATES = [
    ("Diego", "Vásquez Núñez", 50, "diego.vasquez@candidato.test"),
    ("Valeria", "Romero Quispe", 51, "valeria.romero@candidato.test"),
    ("Javier", "Aliaga Vega", 52, "javier.aliaga@candidato.test"),
    ("Isabel", "Castañeda Rojas", 53, "isabel.castaneda@candidato.test"),
    ("Sebastián", "Paredes Soto", 54, "sebastian.paredes@candidato.test"),
]


def _dni(offset: int) -> str:
    """Synthetic Peruvian DNI in 7XXXXXXX range (unassigned by RENIEC)."""
    return f"7000{offset:04d}"


def _email_personal(nombres: str, ape_pat: str) -> str:
    nombre = nombres.split()[0].lower()
    apellido = ape_pat.lower()
    return f"{nombre}.{apellido}@personal-demo.test"


class Command(BaseCommand):
    help = "Seed Demo Vyntia Pro tenant with realistic Peruvian HR data (admin + 15 empleados + B.9 + B.12)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--fresh",
            action="store_true",
            help="Delete existing demo-pro tenant data first, then reseed.",
        )

    def handle(self, *args, **options):
        fresh = options.get("fresh", False)

        if fresh:
            self._wipe_demo_tenant()

        with transaction.atomic():
            staff = self._seed_staff_creator()
            tenant = self._seed_tenant(staff)
            admin = self._seed_user(
                tenant=tenant,
                username=ADMIN_USERNAME,
                email=ADMIN_EMAIL,
                password=ADMIN_PASSWORD,
                first="Admin",
                last="Demo Pro",
                tipo="administrador",
                membership_role="owner",
                nivel_acceso="total",
            )
            rrhh = self._seed_user(
                tenant=tenant,
                username=RRHH_USERNAME,
                email=RRHH_EMAIL,
                password=RRHH_PASSWORD,
                first="Jefa",
                last="RRHH Demo",
                tipo="rrhh",
                membership_role="admin",
                nivel_acceso="departamental",
            )
            roles = self._seed_roles_and_rbac(tenant, admin, rrhh)
            depts = self._seed_departments(tenant)
            positions = self._seed_positions(tenant, depts)
            empleados = self._seed_employees(tenant, depts, positions)
            self._seed_family_members(tenant, empleados)
            self._seed_academic_records(tenant, empleados)
            candidates = self._seed_candidates(tenant)
            requisition = self._seed_requisition(tenant, depts, positions, rrhh, admin)
            posting, applications, stages = self._seed_posting(
                tenant, requisition, candidates, admin
            )
            evaluations = self._seed_evaluations(applications, stages, rrhh)
            ranking = self._seed_ranking(posting)
            dossiers = self._seed_dossiers(tenant, empleados[:3])

        payload = {
            "tenant_id": str(tenant.id),
            "tenant_slug": tenant.slug,
            "tenant_host": f"{tenant.slug}.vyntia.pe",
            "admin": {
                "username": admin.username,
                "email": admin.email,
                "password": ADMIN_PASSWORD,
            },
            "rrhh": {
                "username": rrhh.username,
                "email": rrhh.email,
                "password": RRHH_PASSWORD,
            },
            "counts": {
                "departments": len(depts),
                "positions": len(positions),
                "employees": len(empleados),
                "family_members": FamilyMember.objects.filter(tenant=tenant).count(),
                "academic_records": AcademicRecord.objects.filter(
                    tenant=tenant
                ).count(),
                "contracts": Contract.objects.filter(tenant=tenant).count(),
                "candidates": len(candidates),
                "requisitions": 1 if requisition else 0,
                "postings": 1 if posting else 0,
                "applications": len(applications),
                "evaluations": len(evaluations),
                "ranking_entries": len(ranking),
                "dossiers": len(dossiers),
            },
        }
        self.stdout.write(self.style.SUCCESS("Demo Pro tenant seed complete."))
        self.stdout.write(f"SEED_OUTPUT: {json.dumps(payload, ensure_ascii=False)}")

    # === Wipe ===

    def _wipe_demo_tenant(self):
        """Delete the demo-pro tenant and ALL its data. Other tenants untouched."""
        try:
            tenant = Tenant.objects.get(slug=TENANT_SLUG)
        except Tenant.DoesNotExist:
            self.stdout.write("--fresh: no existing demo-pro tenant; nothing to wipe.")
            return

        self.stdout.write(f"--fresh: wiping tenant {tenant.slug} ({tenant.id})...")
        # Order matters: delete leaves first to avoid PROTECT violations.
        # Document access log first — it FKs DigitalDocument which FKs Employee.
        DocumentAccessLog.objects.filter(tenant=tenant).delete()
        MeritRanking.objects.filter(posting__tenant=tenant).delete()
        CandidateEvaluation.objects.filter(
            application__posting__tenant=tenant
        ).delete()
        JobApplication.objects.filter(tenant=tenant).delete()
        SelectionStage.objects.filter(posting__tenant=tenant).delete()
        JobPosting.objects.filter(tenant=tenant).delete()
        PersonnelRequisition.objects.filter(tenant=tenant).delete()
        Candidate.objects.filter(tenant=tenant).delete()
        DigitalDossier.objects.filter(tenant=tenant).delete()
        AcademicRecord.objects.filter(tenant=tenant).delete()
        FamilyMember.objects.filter(tenant=tenant).delete()
        Contract.objects.filter(tenant=tenant).delete()
        EmploymentData.objects.filter(tenant=tenant).delete()
        Employee.objects.filter(tenant=tenant).delete()
        Position.objects.filter(tenant=tenant).delete()
        Department.objects.filter(tenant=tenant).delete()
        UserRole.objects.filter(tenant=tenant).delete()
        RolePermission.objects.filter(tenant=tenant).delete()
        Role.objects.filter(tenant=tenant).delete()
        Permission.objects.filter(tenant=tenant).delete()
        TenantMembership.objects.filter(tenant=tenant).delete()
        User.objects.filter(
            username__in=[ADMIN_USERNAME, RRHH_USERNAME]
        ).delete()
        tenant.delete()
        self.stdout.write(self.style.WARNING("--fresh: wipe done."))

    # === Seeders ===

    def _seed_staff_creator(self):
        user, _ = User.objects.get_or_create(
            username=STAFF_USERNAME,
            defaults={
                "email": STAFF_EMAIL,
                "nombres_usuario": "Demo Pro",
                "apellidos_usuario": "Seed",
                "tipo_usuario": "administrador",
                "is_vyntia_staff": True,
                "is_active": True,
            },
        )
        return user

    def _seed_tenant(self, creator):
        tenant, created = Tenant.objects.update_or_create(
            slug=TENANT_SLUG,
            defaults={
                "name": TENANT_NAME,
                "ruc": TENANT_RUC,
                "plan": "pro",
                "status": "active",
                "created_by": creator,
                "max_users": 50,
            },
        )
        return tenant

    def _seed_user(
        self,
        *,
        tenant,
        username,
        email,
        password,
        first,
        last,
        tipo,
        membership_role,
        nivel_acceso="personal",
    ):
        """Idempotent user provisioning.

        `nivel_acceso` defaults to 'personal' (matches User model default) but
        callers should override for admins/RRHH:
          - 'total'         : sees everything (PL 1-9)
          - 'departamental' : sees own department's PL 1-5 (RRHH operativo)
          - 'personal'      : sees own data + PL 1-3 (default; employee role)
        """
        defaults = {
            "email": email,
            "nombres_usuario": first,
            "apellidos_usuario": last,
            "tipo_usuario": tipo,
            "is_active": True,
            "is_staff": True if tipo == "administrador" else False,
            "nivel_acceso": nivel_acceso,
        }
        user, created = User.objects.get_or_create(
            username=username,
            defaults=defaults,
        )
        if created:
            user.set_password(password)
            user.save()
        else:
            # Re-runs: re-sync nivel_acceso in case the seed was upgraded.
            if user.nivel_acceso != nivel_acceso:
                user.nivel_acceso = nivel_acceso
                user.save(update_fields=["nivel_acceso"])
        TenantMembership.objects.update_or_create(
            tenant=tenant,
            user=user,
            defaults={"role": membership_role, "status": "active"},
        )
        return user

    def _seed_roles_and_rbac(self, tenant, admin_user, rrhh_user):
        """Provision global system roles (via setup_roles_permisos) and link the
        demo-pro users to them via tenant-scoped UserRole rows.

        The previous version of this seed created per-tenant duplicates of
        "Administrador RRHH" / "Analista RRHH", which had no RolePermission
        assignments — so `admin.permisos_activos().count() == 0` and every
        @require_permissions endpoint returned 403. Fixed in v3 by delegating
        role+permission+RolePermission creation to the canonical command
        `setup_roles_permisos` (which works at the global scope, tenant=None)
        and pointing UserRole.rol at the global rows.
        """
        # Idempotent: setup_roles_permisos uses get_or_create for everything.
        call_command("setup_roles_permisos", verbosity=0)

        admin_role = Role.objects.get(
            tenant__isnull=True, nombre_rol=ROLE_ADMIN
        )
        rrhh_role = Role.objects.get(
            tenant__isnull=True, nombre_rol=ROLE_RRHH
        )
        UserRole.objects.update_or_create(
            tenant=tenant,
            usuario=admin_user,
            rol=admin_role,
            defaults={"estado_asignacion": "activo"},
        )
        UserRole.objects.update_or_create(
            tenant=tenant,
            usuario=rrhh_user,
            rol=rrhh_role,
            defaults={"estado_asignacion": "activo"},
        )
        return {"admin": admin_role, "rrhh": rrhh_role}

    def _seed_departments(self, tenant):
        out = {}
        for siglas, nombre in DEPARTMENTS:
            dept, _ = Department.objects.update_or_create(
                tenant=tenant,
                siglas_area=siglas,
                defaults={
                    "nombre_organo": "Sede Central",
                    "nombre_unidad_organica": nombre,
                    "unit_type": "area" if siglas != "GG" else "gerencia",
                    "estado_area": "activo",
                },
            )
            out[siglas] = dept
        return out

    def _seed_positions(self, tenant, depts):
        out = {}
        for code, name, category, dept_siglas in POSITIONS:
            dept = depts[dept_siglas]
            pos, _ = Position.objects.update_or_create(
                tenant=tenant,
                code=code,
                version=1,
                defaults={
                    "name": name,
                    "department": dept,
                    "effective_date": date.today(),
                    "is_current": True,
                    "is_active": True,
                    "familia_puesto": category,
                },
            )
            out[code] = pos
        return out

    def _seed_employees(self, tenant, depts, positions):
        empleados = []
        today = date.today()
        for (nombres, ape_pat, ape_mat, genero, dni_off, pos_code, sueldo, year_off) in EMPLOYEES:
            position = positions[pos_code]
            dept = position.department
            dni = _dni(dni_off)
            email = _email_personal(nombres, ape_pat)
            birth = date(1985 + (dni_off % 15), ((dni_off * 3) % 12) + 1, ((dni_off * 7) % 28) + 1)
            empleado, _ = Employee.objects.update_or_create(
                tenant=tenant,
                numero_documento=dni,
                defaults={
                    "tipo_documento": "DNI",
                    "nombres_empleado": nombres,
                    "apellido_paterno": ape_pat,
                    "apellido_materno": ape_mat,
                    "genero_empleado": genero,
                    "correo_personal": email,
                    "fecha_nacimiento": birth,
                    "estado_civil": "casado" if dni_off % 3 == 0 else "soltero",
                    "telefono_celular": f"9{dni_off:08d}",
                    "sistema_pensiones": "AFP INTEGRA" if dni_off % 2 == 0 else "ONP",
                    "tipo_seguro_salud": "ESSALUD",
                    "estado_empleado": "activo",
                },
            )
            empleados.append(empleado)

            hire = today.replace(year=today.year + year_off)
            EmploymentData.objects.update_or_create(
                empleado=empleado,
                fecha_inicio_contrato=hire,
                defaults={
                    "tenant": tenant,
                    "area": dept,
                    "position": position,
                    "cargo_empleado": position.name,
                    "categoria": _category_from_position(pos_code),
                    "tipo_contrato": "indefinido",
                    "regimen_laboral": "728",
                    "fecha_ingreso": hire,
                    "sueldo_basico": Decimal(str(sueldo)),
                    "modalidad_trabajo": "presencial" if dni_off % 2 == 0 else "hibrido",
                    "jornada_laboral": "completa",
                    "horario_entrada": time(9, 0),
                    "horario_salida": time(18, 0),
                    "horas_semanales": Decimal("40.00"),
                    "estado_datos": "activo",
                },
            )

            Contract.objects.update_or_create(
                tenant=tenant,
                numero_contrato=f"CTO-{dni}",
                defaults={
                    "empleado": empleado,
                    "area": dept,
                    "tipo_documento": "LEY_728_INDETERMINADO",
                    "fecha_inicio": hire,
                    "fecha_firma": hire,
                    "salario_bruto": Decimal(str(sueldo)),
                    "cargo": position.name,
                    "jornada_laboral": "COMPLETA",
                    "lugar_trabajo": "Lima, Perú",
                    "horario_trabajo": "L-V 9:00-18:00",
                    "status": "ACTIVO",
                },
            )

        return empleados

    def _seed_family_members(self, tenant, empleados):
        for i, emp in enumerate(empleados):
            if i % 3 == 0:
                # spouse
                FamilyMember.objects.update_or_create(
                    tenant=tenant,
                    empleado=emp,
                    numero_documento=_dni(100 + i),
                    defaults={
                        "nombres_familiar": "Cónyuge de " + emp.nombres_empleado.split()[0],
                        "apellido_paterno": emp.apellido_paterno,
                        "apellido_materno": "Demo",
                        "tipo_documento": "DNI",
                        "fecha_nacimiento": date(1988 + (i % 10), 5, 15),
                        "genero_familiar": "femenino" if emp.genero_empleado == "masculino" else "masculino",
                        "parentesco": "conyuge",
                        "es_dependiente": True,
                    },
                )
            if i % 4 == 0:
                # one child
                FamilyMember.objects.update_or_create(
                    tenant=tenant,
                    empleado=emp,
                    numero_documento=_dni(200 + i),
                    defaults={
                        "nombres_familiar": f"Hijo Menor de {emp.nombres_empleado.split()[0]}",
                        "apellido_paterno": emp.apellido_paterno,
                        "apellido_materno": emp.apellido_materno,
                        "tipo_documento": "DNI",
                        "fecha_nacimiento": date(2015 + (i % 8), 3, 10),
                        "genero_familiar": "masculino" if i % 2 == 0 else "femenino",
                        "parentesco": "hijo",
                        "es_dependiente": True,
                        "es_beneficiario": True,
                    },
                )

    def _seed_academic_records(self, tenant, empleados):
        for i, emp in enumerate(empleados):
            AcademicRecord.objects.update_or_create(
                tenant=tenant,
                empleado=emp,
                nivel_educativo="universitario",
                nombre_carrera="Administración de Empresas" if i % 2 == 0 else "Ingeniería de Sistemas",
                nombre_institucion="Universidad Nacional Mayor de San Marcos" if i % 2 == 0 else "Pontificia Universidad Católica del Perú",
                defaults={
                    "tipo_institucion": "publica" if i % 2 == 0 else "privada",
                    "modalidad_estudio": "presencial",
                    "fecha_inicio": date(2005 + (i % 10), 3, 1),
                    "fecha_fin": date(2010 + (i % 10), 12, 15),
                    "estado_estudios": "completo",
                    "pais_institucion": "Perú",
                },
            )

    def _seed_candidates(self, tenant):
        out = []
        for (nombres, apellidos, dni_off, email) in CANDIDATES:
            c, _ = Candidate.objects.update_or_create(
                tenant=tenant,
                document_type="dni",
                document_number=_dni(dni_off),
                defaults={
                    "first_names": nombres,
                    "last_names": apellidos,
                    "email": email,
                    "phone": f"9{dni_off:08d}",
                    "years_experience": (dni_off % 7) + 1,
                    "highest_education": "Bachiller en Ingeniería de Sistemas",
                    "is_active": True,
                },
            )
            out.append(c)
        return out

    def _seed_requisition(self, tenant, depts, positions, rrhh_user, admin_user):
        """Seed a requisition that goes through the real dual-control workflow
        (rrhh_user approves HR side, admin_user approves Finance side)
        instead of jumping straight to status='approved'. This exercises the
        dual control invariant added in Bloque D.
        """
        position = positions["TI-03"]
        dept = depts["TI"]
        req, created = PersonnelRequisition.objects.update_or_create(
            tenant=tenant,
            code="REQ-DEMO-001",
            defaults={
                "position": position,
                "department": dept,
                "justification": "new_position",
                "justification_notes": "Crecimiento del equipo de desarrollo para nuevo producto.",
                "requested_by": rrhh_user,
                "requested_count": 1,
                "requested_start_date": date.today() + timedelta(days=30),
                "estimated_monthly_cost": Decimal("3800.00"),
            },
        )
        # Walk the real lifecycle: draft → pending_approval → approved.
        # Only fire transitions if we are not already at the terminal state
        # (idempotent re-runs must not re-trigger approvals).
        if req.status not in ("approved", "fulfilled"):
            if req.status == "draft":
                req.submit_for_approval()
            req.approve_hr(user=rrhh_user)
            req.approve_finance(user=admin_user)
        return req

    def _seed_posting(self, tenant, requisition, candidates, admin_user):
        posting, _ = JobPosting.objects.update_or_create(
            tenant=tenant,
            code="POST-DEMO-001",
            defaults={
                "requisition": requisition,
                "title": "Desarrollador Junior - Equipo Web",
                "summary": "Buscamos developer junior con 1-2 años de experiencia en React + Django.",
                "sector_mode": "private",
                "posting_kind": "external",
                "status": "in_evaluation",
                "applications_open_at": date.today() - timedelta(days=20),
                "applications_close_at": date.today() - timedelta(days=5),
                "results_announce_at": date.today() + timedelta(days=10),
                "created_by": admin_user,
            },
        )

        stage_curricular, _ = SelectionStage.objects.update_or_create(
            posting=posting,
            order=1,
            defaults={
                "kind": "curricular",
                "name": "Evaluación curricular",
                "is_eliminatoria": True,
                "min_score": Decimal("11.00"),
                "max_score": Decimal("20.00"),
                "weight": Decimal("20.00"),
            },
        )
        stage_technical, _ = SelectionStage.objects.update_or_create(
            posting=posting,
            order=2,
            defaults={
                "kind": "technical",
                "name": "Prueba técnica",
                "is_eliminatoria": True,
                "min_score": Decimal("12.00"),
                "max_score": Decimal("20.00"),
                "weight": Decimal("40.00"),
            },
        )
        stage_interview, _ = SelectionStage.objects.update_or_create(
            posting=posting,
            order=3,
            defaults={
                "kind": "interview",
                "name": "Entrevista personal",
                "is_eliminatoria": False,
                "min_score": Decimal("11.00"),
                "max_score": Decimal("20.00"),
                "weight": Decimal("40.00"),
            },
        )
        stages = [stage_curricular, stage_technical, stage_interview]

        applications = []
        for i, c in enumerate(candidates):
            status_map = ["in_evaluation", "in_evaluation", "finalist", "eliminated", "received"]
            app, _ = JobApplication.objects.update_or_create(
                posting=posting,
                candidate=c,
                defaults={
                    "tenant": tenant,
                    "status": status_map[i],
                    "cover_letter": f"Estimado equipo, postulo al puesto y aporto {(i % 5) + 1} años de experiencia.",
                },
            )
            applications.append(app)
        return posting, applications, stages

    def _seed_evaluations(self, applications, stages, evaluator):
        """Seed CandidateEvaluation rows for applications past the curricular stage.

        Each non-'received' candidate gets a curricular score; finalists also get
        a technical score. This populates the B.9 ATS demo so MeritRanking can
        actually rank instead of returning empty.
        """
        out = []
        for i, app in enumerate(applications):
            if app.status == "received":
                continue
            # Curricular score (everyone past received)
            score_curr = Decimal("15.00") + Decimal(f"{(i * 0.5):.2f}")
            eval_curr, _ = CandidateEvaluation.objects.update_or_create(
                application=app,
                stage=stages[0],
                defaults={
                    "evaluator": evaluator,
                    "score": score_curr,
                    "notes": f"Evaluación curricular demo — candidato {i + 1}",
                },
            )
            out.append(eval_curr)
            # Technical score (only finalists + in_evaluation reach here)
            if app.status in ("finalist", "in_evaluation"):
                score_tech = Decimal("14.00") + Decimal(f"{(i * 0.7):.2f}")
                eval_tech, _ = CandidateEvaluation.objects.update_or_create(
                    application=app,
                    stage=stages[1],
                    defaults={
                        "evaluator": evaluator,
                        "score": score_tech,
                        "notes": f"Prueba técnica demo — candidato {i + 1}",
                    },
                )
                out.append(eval_tech)
        return out

    def _seed_ranking(self, posting):
        """Compute MeritRanking idempotently via the canonical service."""
        try:
            entries = compute_merit_ranking(posting=posting)
        except Exception as exc:
            self.stdout.write(
                self.style.WARNING(
                    f"MeritRanking skipped: {type(exc).__name__}: {exc}"
                )
            )
            return []
        return entries

    def _seed_dossiers(self, tenant, empleados):
        out = []
        for emp in empleados:
            dossier = dossier_service.build_dossier_for_employee(
                employee=emp, tenant=tenant
            )
            out.append(dossier)
        return out


def _category_from_position(pos_code):
    """Map position code to EmploymentData.categoria."""
    if pos_code == "GG-01":
        return "directivo"
    if pos_code in ("RRHH-01", "TI-01"):
        return "funcionario"
    if pos_code in ("FIN-02",):
        return "tecnico"
    return "profesional"
