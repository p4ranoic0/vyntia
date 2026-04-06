"""Move Contratos module under Empleados as a submenu item."""

from django.db import migrations


def move_contratos_under_empleados(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    empleados = (
        Modulos.objects.filter(nombre_modulo="Empleados", modulo_padre__isnull=True)
        .order_by("modulo_id")
        .first()
    )
    contratos = (
        Modulos.objects.filter(nombre_modulo="Contratos", modulo_padre__isnull=True)
        .order_by("modulo_id")
        .first()
    )

    if not empleados or not contratos:
        return

    max_child_order = (
        Modulos.objects.filter(modulo_padre=empleados)
        .order_by("-orden_visualizacion")
        .values_list("orden_visualizacion", flat=True)
        .first()
    ) or 0

    contratos.modulo_padre = empleados
    contratos.orden_visualizacion = max_child_order + 1
    contratos.icono_modulo = "file-signature"
    contratos.save(
        update_fields=[
            "modulo_padre",
            "orden_visualizacion",
            "icono_modulo",
            "fecha_actualizacion",
        ]
    )


def reverse_move(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    contratos = Modulos.objects.filter(
        nombre_modulo="Contratos", ruta_modulo="/contratos"
    ).first()
    if contratos:
        contratos.modulo_padre = None
        contratos.orden_visualizacion = 5
        contratos.icono_modulo = "file-check"
        contratos.save(
            update_fields=[
                "modulo_padre",
                "orden_visualizacion",
                "icono_modulo",
                "fecha_actualizacion",
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ("app_rrhh", "0026_alter_datoslaborales_tipo_contrato_and_more"),
    ]

    operations = [
        migrations.RunPython(move_contratos_under_empleados, reverse_move),
    ]
