"""Seed JobFactor + JobSubfactor per R.M. 243-2018-TR.

Canonical 4-factor + subfactor list from the guía metodológica. Idempotent.
"""
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.compensation.models import JobFactor, JobSubfactor


FACTORS = [
    # (kind, name, description, weight)
    ('competencias', 'Competencias', 'Conocimientos, habilidades y experiencia requeridas por el puesto.', Decimal('25.00')),
    ('responsabilidad', 'Responsabilidad', 'Responsabilidad por personas, bienes, decisiones y resultados.', Decimal('30.00')),
    ('esfuerzo', 'Esfuerzo', 'Esfuerzo físico, mental, visual y emocional requerido por el puesto.', Decimal('20.00')),
    ('condiciones', 'Condiciones de Trabajo', 'Condiciones ambientales, de riesgo y disponibilidad horaria.', Decimal('25.00')),
]


SUBFACTORS = [
    # (factor_kind, code, name, description, max_score)
    # Competencias
    ('competencias', 'COMP_CONOC', 'Conocimientos', 'Formación académica y conocimientos técnicos requeridos.', 100),
    ('competencias', 'COMP_HAB', 'Habilidades', 'Habilidades técnicas y conductuales requeridas.', 100),
    ('competencias', 'COMP_EXP', 'Experiencia', 'Años y tipo de experiencia profesional requerida.', 100),

    # Responsabilidad
    ('responsabilidad', 'RESP_PERS', 'Por personas', 'Responsabilidad sobre el personal que dirige o coordina.', 100),
    ('responsabilidad', 'RESP_BIEN', 'Por bienes', 'Responsabilidad por bienes, activos o recursos materiales.', 100),
    ('responsabilidad', 'RESP_DEC', 'Por decisiones', 'Nivel de autonomía y consecuencia de las decisiones.', 100),
    ('responsabilidad', 'RESP_RESU', 'Por resultados', 'Responsabilidad por resultados, metas y objetivos del puesto.', 100),

    # Esfuerzo
    ('esfuerzo', 'ESF_FIS', 'Físico', 'Esfuerzo físico requerido (postura, manejo de cargas, desplazamiento).', 100),
    ('esfuerzo', 'ESF_MEN', 'Mental', 'Esfuerzo mental requerido (concentración, análisis, resolución).', 100),
    ('esfuerzo', 'ESF_VIS', 'Visual', 'Esfuerzo visual requerido (lectura prolongada, pantallas, detalles finos).', 100),
    ('esfuerzo', 'ESF_EMO', 'Emocional', 'Esfuerzo emocional (interacción con público, manejo de quejas, conflictos).', 100),

    # Condiciones de Trabajo
    ('condiciones', 'COND_AMB', 'Ambiente', 'Condiciones ambientales (temperatura, ruido, ventilación, iluminación).', 100),
    ('condiciones', 'COND_RIE', 'Riesgo', 'Nivel de riesgo del puesto (físico, químico, biológico, ergonómico).', 100),
    ('condiciones', 'COND_DISP', 'Disponibilidad', 'Disponibilidad horaria requerida (turnos, guardias, viajes).', 100),
]


class Command(BaseCommand):
    help = "Seed JobFactor + JobSubfactor per R.M. 243-2018-TR (Ley 30709)."

    @transaction.atomic
    def handle(self, *args, **options):
        created_factors = 0
        updated_factors = 0
        for kind, name, desc, weight in FACTORS:
            obj, created = JobFactor.objects.update_or_create(
                kind=kind,
                defaults={'name': name, 'description': desc, 'weight': weight, 'is_active': True},
            )
            if created:
                created_factors += 1
            else:
                updated_factors += 1

        factor_by_kind = {f.kind: f for f in JobFactor.objects.all()}

        created_subs = 0
        updated_subs = 0
        for factor_kind, code, name, desc, max_score in SUBFACTORS:
            factor = factor_by_kind.get(factor_kind)
            if factor is None:
                self.stderr.write(self.style.WARNING(
                    f"Skipping subfactor {code}: factor {factor_kind} not found."
                ))
                continue
            obj, created = JobSubfactor.objects.update_or_create(
                code=code,
                defaults={
                    'factor': factor,
                    'name': name,
                    'description': desc,
                    'max_score': max_score,
                    'is_active': True,
                },
            )
            if created:
                created_subs += 1
            else:
                updated_subs += 1

        self.stdout.write(self.style.SUCCESS(
            f"Factors: {created_factors} created, {updated_factors} updated. "
            f"Subfactors: {created_subs} created, {updated_subs} updated."
        ))
