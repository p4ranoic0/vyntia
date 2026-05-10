"""Seed SUNAT Tabla 9 (CIUO-08) + Tabla 10 (occupational category) reference data.

Idempotent — running twice produces the same rows. Safe to run on every deploy
or via Django startup signal.
"""
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.organization.models import CIUOCode, OccupationalCategory


OCCUPATIONAL_CATEGORIES = [
    # (code, name, description)
    ('01', 'Ejecutivo', 'Personal con responsabilidades de dirección estratégica.'),
    ('02', 'Empleado', 'Personal técnico, profesional o administrativo.'),
    ('03', 'Obrero', 'Personal de oficios manuales y operativos.'),
]


# Top-used CIUO-08 4-digit codes for Peruvian payroll. Sourced from SUNAT Tabla 9
# (truncated subset). Full ~430 codes can be loaded in B.6.1 if a tenant needs them.
CIUO_CODES = [
    # Directors and Managers (group 1)
    ('1111', 'Miembros del poder ejecutivo y los cuerpos legislativos', '1 - Directores y gerentes'),
    ('1112', 'Personal directivo de la administración pública', '1 - Directores y gerentes'),
    ('1120', 'Directores generales y gerentes generales', '1 - Directores y gerentes'),
    ('1211', 'Directores financieros', '1 - Directores y gerentes'),
    ('1212', 'Directores de recursos humanos', '1 - Directores y gerentes'),
    ('1213', 'Directores de políticas y planificación', '1 - Directores y gerentes'),
    ('1219', 'Directores de servicios de administración', '1 - Directores y gerentes'),
    ('1221', 'Directores de ventas y comercialización', '1 - Directores y gerentes'),
    ('1222', 'Directores de publicidad y relaciones públicas', '1 - Directores y gerentes'),
    ('1223', 'Directores de investigación y desarrollo', '1 - Directores y gerentes'),
    ('1321', 'Directores de industrias manufactureras', '1 - Directores y gerentes'),
    ('1330', 'Directores de servicios de tecnología de la información', '1 - Directores y gerentes'),
    # Professionals (group 2)
    ('2111', 'Físicos y astrónomos', '2 - Profesionales científicos e intelectuales'),
    ('2120', 'Matemáticos, actuarios y estadísticos', '2 - Profesionales científicos e intelectuales'),
    ('2141', 'Ingenieros industriales y de producción', '2 - Profesionales científicos e intelectuales'),
    ('2142', 'Ingenieros civiles', '2 - Profesionales científicos e intelectuales'),
    ('2143', 'Ingenieros ambientales', '2 - Profesionales científicos e intelectuales'),
    ('2144', 'Ingenieros mecánicos', '2 - Profesionales científicos e intelectuales'),
    ('2145', 'Ingenieros químicos', '2 - Profesionales científicos e intelectuales'),
    ('2146', 'Ingenieros de minas, metalúrgicos y afines', '2 - Profesionales científicos e intelectuales'),
    ('2151', 'Ingenieros electricistas', '2 - Profesionales científicos e intelectuales'),
    ('2152', 'Ingenieros electrónicos', '2 - Profesionales científicos e intelectuales'),
    ('2153', 'Ingenieros en telecomunicaciones', '2 - Profesionales científicos e intelectuales'),
    ('2211', 'Médicos generales', '2 - Profesionales científicos e intelectuales'),
    ('2212', 'Médicos especialistas', '2 - Profesionales científicos e intelectuales'),
    ('2221', 'Profesionales en enfermería', '2 - Profesionales científicos e intelectuales'),
    ('2231', 'Profesionales de medicina tradicional y alternativa', '2 - Profesionales científicos e intelectuales'),
    ('2261', 'Odontólogos', '2 - Profesionales científicos e intelectuales'),
    ('2262', 'Farmacéuticos', '2 - Profesionales científicos e intelectuales'),
    ('2310', 'Profesores universitarios y de la enseñanza superior', '2 - Profesionales científicos e intelectuales'),
    ('2320', 'Profesores de formación profesional', '2 - Profesionales científicos e intelectuales'),
    ('2330', 'Profesores de enseñanza secundaria', '2 - Profesionales científicos e intelectuales'),
    ('2341', 'Maestros de enseñanza primaria', '2 - Profesionales científicos e intelectuales'),
    ('2342', 'Maestros preescolares', '2 - Profesionales científicos e intelectuales'),
    ('2411', 'Contadores', '2 - Profesionales científicos e intelectuales'),
    ('2412', 'Asesores financieros y de inversiones', '2 - Profesionales científicos e intelectuales'),
    ('2413', 'Analistas financieros', '2 - Profesionales científicos e intelectuales'),
    ('2421', 'Analistas de gestión y organización', '2 - Profesionales científicos e intelectuales'),
    ('2422', 'Profesionales en políticas de administración', '2 - Profesionales científicos e intelectuales'),
    ('2423', 'Especialistas en políticas y servicios de personal', '2 - Profesionales científicos e intelectuales'),
    ('2424', 'Especialistas en formación de personal', '2 - Profesionales científicos e intelectuales'),
    ('2431', 'Profesionales de la publicidad y la comercialización', '2 - Profesionales científicos e intelectuales'),
    ('2432', 'Profesionales de relaciones públicas', '2 - Profesionales científicos e intelectuales'),
    ('2433', 'Profesionales de ventas técnicas y médicas', '2 - Profesionales científicos e intelectuales'),
    ('2511', 'Analistas de sistemas', '2 - Profesionales científicos e intelectuales'),
    ('2512', 'Desarrolladores de software', '2 - Profesionales científicos e intelectuales'),
    ('2513', 'Desarrolladores web y multimedia', '2 - Profesionales científicos e intelectuales'),
    ('2514', 'Programadores de aplicaciones', '2 - Profesionales científicos e intelectuales'),
    ('2519', 'Analistas, desarrolladores de software', '2 - Profesionales científicos e intelectuales'),
    ('2521', 'Diseñadores y administradores de bases de datos', '2 - Profesionales científicos e intelectuales'),
    ('2522', 'Administradores de sistemas', '2 - Profesionales científicos e intelectuales'),
    ('2523', 'Profesionales en redes de computadores', '2 - Profesionales científicos e intelectuales'),
    ('2611', 'Abogados', '2 - Profesionales científicos e intelectuales'),
    ('2619', 'Profesionales en derecho', '2 - Profesionales científicos e intelectuales'),
    # Technicians (group 3)
    ('3111', 'Técnicos en ciencias físicas y químicas', '3 - Técnicos y profesionales de nivel medio'),
    ('3112', 'Técnicos en ingeniería civil', '3 - Técnicos y profesionales de nivel medio'),
    ('3113', 'Electrotécnicos', '3 - Técnicos y profesionales de nivel medio'),
    ('3114', 'Técnicos en electrónica', '3 - Técnicos y profesionales de nivel medio'),
    ('3115', 'Técnicos en ingeniería mecánica', '3 - Técnicos y profesionales de nivel medio'),
    ('3119', 'Técnicos en ciencias físicas y la ingeniería', '3 - Técnicos y profesionales de nivel medio'),
    ('3211', 'Técnicos en aparatos de diagnóstico y tratamiento médico', '3 - Técnicos y profesionales de nivel medio'),
    ('3221', 'Profesionales asociados en enfermería', '3 - Técnicos y profesionales de nivel medio'),
    ('3251', 'Asistentes y técnicos odontológicos', '3 - Técnicos y profesionales de nivel medio'),
    ('3252', 'Técnicos en documentación sanitaria', '3 - Técnicos y profesionales de nivel medio'),
    ('3311', 'Agentes bursátiles y cambistas', '3 - Técnicos y profesionales de nivel medio'),
    ('3312', 'Analistas de crédito y préstamos', '3 - Técnicos y profesionales de nivel medio'),
    ('3313', 'Tenedores de libros', '3 - Técnicos y profesionales de nivel medio'),
    ('3314', 'Profesionales de nivel medio en estadística', '3 - Técnicos y profesionales de nivel medio'),
    ('3321', 'Agentes de seguros', '3 - Técnicos y profesionales de nivel medio'),
    ('3322', 'Representantes comerciales', '3 - Técnicos y profesionales de nivel medio'),
    # Clerical (group 4)
    ('4110', 'Oficinistas generales', '4 - Personal de apoyo administrativo'),
    ('4120', 'Secretarios (generales)', '4 - Personal de apoyo administrativo'),
    ('4131', 'Mecanógrafos y operadores de procesamiento de textos', '4 - Personal de apoyo administrativo'),
    ('4132', 'Operadores de entrada de datos', '4 - Personal de apoyo administrativo'),
    ('4211', 'Cajeros de banco', '4 - Personal de apoyo administrativo'),
    ('4212', 'Receptores de apuestas y afines', '4 - Personal de apoyo administrativo'),
    ('4222', 'Operadores de centro de llamadas', '4 - Personal de apoyo administrativo'),
    ('4226', 'Recepcionistas (general)', '4 - Personal de apoyo administrativo'),
    ('4311', 'Auxiliares contables y de cálculo de costos', '4 - Personal de apoyo administrativo'),
    ('4312', 'Empleados de servicios estadísticos, financieros y de seguros', '4 - Personal de apoyo administrativo'),
    ('4321', 'Empleados encargados de existencias', '4 - Personal de apoyo administrativo'),
    ('4322', 'Empleados de servicios de apoyo a la producción', '4 - Personal de apoyo administrativo'),
    ('4323', 'Empleados de servicios de transporte', '4 - Personal de apoyo administrativo'),
    # Service workers (group 5)
    ('5120', 'Cocineros', '5 - Trabajadores de servicios y vendedores'),
    ('5141', 'Peluqueros', '5 - Trabajadores de servicios y vendedores'),
    ('5223', 'Vendedores de tiendas y almacenes', '5 - Trabajadores de servicios y vendedores'),
    ('5311', 'Cuidadores de niños', '5 - Trabajadores de servicios y vendedores'),
    ('5321', 'Auxiliares de servicios de salud', '5 - Trabajadores de servicios y vendedores'),
    ('5411', 'Bomberos', '5 - Trabajadores de servicios y vendedores'),
    ('5412', 'Policías', '5 - Trabajadores de servicios y vendedores'),
    ('5414', 'Guardias de protección', '5 - Trabajadores de servicios y vendedores'),
]


class Command(BaseCommand):
    help = "Seed SUNAT Tabla 9 (CIUO-08) and Tabla 10 (occupational category) reference data."

    @transaction.atomic
    def handle(self, *args, **options):
        # Occupational categories (Tabla 10)
        for code, name, desc in OCCUPATIONAL_CATEGORIES:
            obj, created = OccupationalCategory.objects.update_or_create(
                code=code,
                defaults={'name': name, 'description': desc, 'is_active': True},
            )
            self.stdout.write(
                f"{'Created' if created else 'Updated'} OccupationalCategory {code} - {name}"
            )

        # CIUO codes (Tabla 9)
        for code, name, big_group in CIUO_CODES:
            obj, created = CIUOCode.objects.update_or_create(
                code=code,
                defaults={
                    'name': name,
                    'big_group': big_group,
                    'is_active': True,
                },
            )
            if created:
                self.stdout.write(f"Created CIUOCode {code}")

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(OCCUPATIONAL_CATEGORIES)} occupational categories + "
            f"{len(CIUO_CODES)} CIUO codes."
        ))
