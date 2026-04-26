from django.db import migrations


def add_remuneraciones_menu(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    admin_module = Modulos.objects.filter(nombre_modulo="Administración").first()
    if not admin_module:
        return

    exists = Modulos.objects.filter(
        ruta_modulo="/remuneraciones/configuracion",
        modulo_padre=admin_module,
    ).exists()
    if exists:
        return

    max_order = (
        Modulos.objects.filter(modulo_padre=admin_module)
        .order_by("-orden_visualizacion")
        .values_list("orden_visualizacion", flat=True)
        .first()
    )

    next_order = (max_order or 0) + 1

    Modulos.objects.create(
        nombre_modulo="Remuneraciones",
        descripcion_modulo="Configuración de parámetros de planilla y AFP",
        icono_modulo="landmark",
        ruta_modulo="/remuneraciones/configuracion",
        orden_visualizacion=next_order,
        estado_modulo="activo",
        modulo_padre=admin_module,
        permisos_requeridos="",
    )


def remove_remuneraciones_menu(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")
    Modulos.objects.filter(ruta_modulo="/remuneraciones/configuracion").delete()


class Migration(migrations.Migration):

    dependencies = [
        (
            "app_rrhh",
            "0014_rename_configuracio_afp_nom_d467af_idx_configuraci_afp_nom_8564da_idx_and_more",
        ),
    ]

    operations = [
        migrations.RunPython(add_remuneraciones_menu, remove_remuneraciones_menu),
    ]
