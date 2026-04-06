# -*- coding: utf-8 -*-
"""
Comando para cargar configuración base de remuneraciones:
- UIT vigente
- Tasas AFP según SBS
"""

from decimal import Decimal

from django.core.management.base import BaseCommand

from app_rrhh.models import ConfiguracionAfp, ConfiguracionUit


class Command(BaseCommand):
    help = "Carga la configuración base de UIT y tasas AFP para remuneraciones"

    def add_arguments(self, parser):
        parser.add_argument(
            "--vigencia",
            type=str,
            default="2026-03",
            help="Mes de vigencia para AFP (formato YYYY-MM)",
        )
        parser.add_argument(
            "--anio-uit",
            type=int,
            default=2026,
            help="Año fiscal para la UIT",
        )
        parser.add_argument(
            "--valor-uit",
            type=str,
            default="5350.00",
            help="Valor de la UIT en soles",
        )

    def handle(self, *args, **options):
        vigencia = options["vigencia"]
        anio_uit = options["anio_uit"]
        valor_uit = Decimal(options["valor_uit"])

        self._seed_uit(anio_uit, valor_uit)
        self._seed_afp(vigencia)

        self.stdout.write(self.style.SUCCESS("Configuración de remuneraciones cargada exitosamente"))

    def _seed_uit(self, anio, valor_uit):
        obj, created = ConfiguracionUit.objects.update_or_create(
            anio=anio,
            defaults={
                "valor_uit": valor_uit,
                "tope_renta_cuarta_uit": Decimal("45.00"),
                "porcentaje_renta_cuarta": Decimal("8.00"),
                "estado": "activo",
            },
        )
        action = "Creada" if created else "Actualizada"
        self.stdout.write(f"  {action} UIT {anio}: S/ {valor_uit}")

    def _seed_afp(self, vigencia):
        # Tasas AFP según SBS (Marzo 2026)
        afps = [
            {
                "afp_nombre": "HABITAT",
                "aporte_obligatorio_pct": Decimal("10.000"),
                "comision_flujo_pct": Decimal("1.470"),
                "comision_mixta_pct": Decimal("1.250"),
                "prima_seguro_pct": Decimal("1.370"),
                "remuneracion_max_asegurable": Decimal("12209.11"),
            },
            {
                "afp_nombre": "INTEGRA",
                "aporte_obligatorio_pct": Decimal("10.000"),
                "comision_flujo_pct": Decimal("1.550"),
                "comision_mixta_pct": Decimal("0.780"),
                "prima_seguro_pct": Decimal("1.370"),
                "remuneracion_max_asegurable": Decimal("12209.11"),
            },
            {
                "afp_nombre": "PRIMA",
                "aporte_obligatorio_pct": Decimal("10.000"),
                "comision_flujo_pct": Decimal("1.600"),
                "comision_mixta_pct": Decimal("1.250"),
                "prima_seguro_pct": Decimal("1.370"),
                "remuneracion_max_asegurable": Decimal("12209.11"),
            },
            {
                "afp_nombre": "PROFUTURO",
                "aporte_obligatorio_pct": Decimal("10.000"),
                "comision_flujo_pct": Decimal("1.690"),
                "comision_mixta_pct": Decimal("0.680"),
                "prima_seguro_pct": Decimal("1.370"),
                "remuneracion_max_asegurable": Decimal("12209.11"),
            },
        ]

        for afp_data in afps:
            nombre = afp_data.pop("afp_nombre")
            obj, created = ConfiguracionAfp.objects.update_or_create(
                afp_nombre=nombre,
                vigencia_mes=vigencia,
                defaults={**afp_data, "estado": "activo"},
            )
            action = "Creada" if created else "Actualizada"
            self.stdout.write(
                f"  {action} AFP {nombre} ({vigencia}): "
                f"obligatorio={obj.aporte_obligatorio_pct}%, "
                f"flujo={obj.comision_flujo_pct}%, "
                f"mixta={obj.comision_mixta_pct}%, "
                f"prima={obj.prima_seguro_pct}%"
            )
