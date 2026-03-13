# Generated migration - Add UIT configuration and renta cuarta suspension

from decimal import Decimal

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_rrhh", "0019_planillas_remuneraciones_models"),
    ]

    operations = [
        # Crear tabla ConfiguracionUit
        migrations.CreateModel(
            name="ConfiguracionUit",
            fields=[
                (
                    "configuracion_uit_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("anio", models.PositiveIntegerField(help_text="Año fiscal (YYYY)")),
                (
                    "valor_uit",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Valor de la UIT en soles para el año fiscal",
                        max_digits=10,
                    ),
                ),
                (
                    "tope_renta_cuarta_uit",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("45.00"),
                        help_text="Tope de exoneración en UITs (generalmente 45 UITs)",
                        max_digits=5,
                    ),
                ),
                (
                    "porcentaje_renta_cuarta",
                    models.DecimalField(
                        decimal_places=2,
                        default=Decimal("8.00"),
                        help_text="Porcentaje de retención de renta de 4ta categoría",
                        max_digits=5,
                    ),
                ),
                (
                    "estado",
                    models.CharField(
                        choices=[("activo", "Activo"), ("inactivo", "Inactivo")],
                        default="activo",
                        max_length=20,
                    ),
                ),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                ("fecha_actualizacion", models.DateTimeField(auto_now=True)),
                (
                    "creado_por",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="configuraciones_uit_creadas",
                        to="app_rrhh.usuario",
                    ),
                ),
            ],
            options={
                "db_table": "configuracion_uit",
                "ordering": ["-anio"],
            },
        ),
        # Agregar índices y constraints a ConfiguracionUit
        migrations.AddIndex(
            model_name="configuracionuit",
            index=models.Index(fields=["anio"], name="app_rrhh_co_anio_idx"),
        ),
        migrations.AddIndex(
            model_name="configuracionuit",
            index=models.Index(fields=["estado"], name="app_rrhh_co_estado_idx"),
        ),
        migrations.AddConstraint(
            model_name="configuracionuit",
            constraint=models.UniqueConstraint(
                fields=["anio"], name="uniq_configuracion_uit_anio"
            ),
        ),
        # Agregar campos a DetallePlanilla para suspensión de renta cuarta
        migrations.AddField(
            model_name="detalleplanilla",
            name="tiene_suspension_renta_cuarta",
            field=models.BooleanField(
                default=False,
                help_text="Indica si el empleado presentó suspensión de retención de renta de 4ta categoría",
            ),
        ),
        migrations.AddField(
            model_name="detalleplanilla",
            name="tope_suspension_anual",
            field=models.DecimalField(
                decimal_places=2,
                default=Decimal("0.00"),
                help_text="Monto acumulado anual para control de tope de suspensión",
                max_digits=12,
            ),
        ),
        migrations.AddField(
            model_name="detalleplanilla",
            name="estado_laboral",
            field=models.CharField(
                choices=[
                    ("activo", "Activo"),
                    ("licencia", "De Licencia"),
                    ("suspendido", "Suspendido"),
                    ("descanso_medico", "Descanso Médico"),
                ],
                default="activo",
                help_text="Estado laboral del empleado en el periodo",
                max_length=20,
            ),
        ),
        # Agregar campo a Empleado para control de suspensión
        migrations.AddField(
            model_name="empleado",
            name="tiene_suspension_renta_cuarta_vigente",
            field=models.BooleanField(
                default=False,
                help_text="Indica si tiene suspensión de renta de 4ta categoría vigente",
            ),
        ),
        migrations.AddField(
            model_name="empleado",
            name="fecha_inicio_suspension_renta",
            field=models.DateField(
                blank=True,
                null=True,
                help_text="Fecha inicio de suspensión de renta 4ta",
            ),
        ),
        migrations.AddField(
            model_name="empleado",
            name="fecha_fin_suspension_renta",
            field=models.DateField(
                blank=True, null=True, help_text="Fecha fin de suspensión de renta 4ta"
            ),
        ),
        migrations.AddField(
            model_name="empleado",
            name="documento_suspension_renta",
            field=models.FileField(
                blank=True,
                null=True,
                upload_to="suspensiones_renta/%Y/",
                help_text="Documento de suspensión de retención SUNAT",
            ),
        ),
        # Insertar datos iniciales de UIT
        migrations.RunSQL(
            sql="""
                INSERT INTO configuracion_uit (anio, valor_uit, tope_renta_cuarta_uit, porcentaje_renta_cuarta, estado, fecha_creacion, fecha_actualizacion)
                VALUES 
                    (2024, 5150.00, 45.00, 8.00, 'inactivo', NOW(), NOW()),
                    (2025, 5350.00, 45.00, 8.00, 'inactivo', NOW(), NOW()),
                    (2026, 5150.00, 45.00, 8.00, 'activo', NOW(), NOW());
            """,
            reverse_sql="DELETE FROM configuracion_uit WHERE anio IN (2024, 2025, 2026);",
        ),
    ]
