from django.db import migrations


def restructure_modules(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    admin_module = (
        Modulos.objects.filter(
            nombre_modulo="Administración", modulo_padre__isnull=True
        )
        .order_by("modulo_id")
        .first()
    )
    empleados_module = (
        Modulos.objects.filter(nombre_modulo="Empleados", modulo_padre__isnull=True)
        .order_by("modulo_id")
        .first()
    )

    # Remuneraciones pasa a ser modulo principal
    remuneraciones = (
        Modulos.objects.filter(ruta_modulo="/remuneraciones/configuracion")
        .order_by("modulo_id")
        .first()
    )
    if remuneraciones:
        max_top_order = (
            Modulos.objects.filter(modulo_padre__isnull=True)
            .exclude(modulo_id=remuneraciones.modulo_id)
            .order_by("-orden_visualizacion")
            .values_list("orden_visualizacion", flat=True)
            .first()
        )
        remuneraciones.modulo_padre = None
        remuneraciones.orden_visualizacion = max((max_top_order or 0) + 1, 6)
        remuneraciones.save(
            update_fields=["modulo_padre", "orden_visualizacion", "fecha_actualizacion"]
        )

    # Contratos y Onboarding pasan a Empleados
    if empleados_module:
        empleados_max_order = (
            Modulos.objects.filter(modulo_padre=empleados_module)
            .order_by("-orden_visualizacion")
            .values_list("orden_visualizacion", flat=True)
            .first()
        )
        next_order = (empleados_max_order or 0) + 1

        for route in ["/contratos", "/onboarding/admin"]:
            module = (
                Modulos.objects.filter(ruta_modulo=route).order_by("modulo_id").first()
            )
            if not module:
                continue
            module.modulo_padre = empleados_module
            module.orden_visualizacion = next_order
            module.save(
                update_fields=[
                    "modulo_padre",
                    "orden_visualizacion",
                    "fecha_actualizacion",
                ]
            )
            next_order += 1

    # Si por datos historicos existiera Remuneraciones como hijo de Administracion duplicado,
    # se prioriza mantener una sola entrada por ruta.
    if admin_module and remuneraciones:
        duplicates = Modulos.objects.filter(
            ruta_modulo="/remuneraciones/configuracion",
            modulo_padre=admin_module,
        ).exclude(modulo_id=remuneraciones.modulo_id)
        duplicates.delete()


def reverse_restructure_modules(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    admin_module = (
        Modulos.objects.filter(
            nombre_modulo="Administración", modulo_padre__isnull=True
        )
        .order_by("modulo_id")
        .first()
    )
    empleados_module = (
        Modulos.objects.filter(nombre_modulo="Empleados", modulo_padre__isnull=True)
        .order_by("modulo_id")
        .first()
    )

    remuneraciones = (
        Modulos.objects.filter(ruta_modulo="/remuneraciones/configuracion")
        .order_by("modulo_id")
        .first()
    )
    if admin_module and remuneraciones:
        admin_max_order = (
            Modulos.objects.filter(modulo_padre=admin_module)
            .exclude(modulo_id=remuneraciones.modulo_id)
            .order_by("-orden_visualizacion")
            .values_list("orden_visualizacion", flat=True)
            .first()
        )
        remuneraciones.modulo_padre = admin_module
        remuneraciones.orden_visualizacion = (admin_max_order or 0) + 1
        remuneraciones.save(
            update_fields=["modulo_padre", "orden_visualizacion", "fecha_actualizacion"]
        )

    if empleados_module and admin_module:
        admin_max_order = (
            Modulos.objects.filter(modulo_padre=admin_module)
            .order_by("-orden_visualizacion")
            .values_list("orden_visualizacion", flat=True)
            .first()
        )
        next_order = (admin_max_order or 0) + 1

        for route in ["/contratos", "/onboarding/admin"]:
            module = (
                Modulos.objects.filter(ruta_modulo=route).order_by("modulo_id").first()
            )
            if not module:
                continue
            module.modulo_padre = admin_module
            module.orden_visualizacion = next_order
            module.save(
                update_fields=[
                    "modulo_padre",
                    "orden_visualizacion",
                    "fecha_actualizacion",
                ]
            )
            next_order += 1


class Migration(migrations.Migration):

    dependencies = [
        ("app_rrhh", "0016_seed_menu_admin_missing_modules"),
    ]

    operations = [
        migrations.RunPython(restructure_modules, reverse_restructure_modules),
    ]
