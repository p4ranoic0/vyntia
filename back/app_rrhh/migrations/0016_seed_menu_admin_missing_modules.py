from django.db import migrations


def add_missing_admin_modules(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    admin_module = Modulos.objects.filter(nombre_modulo="Administración").first()
    if not admin_module:
        return

    modules_to_add = [
        {
            "nombre_modulo": "Contratos",
            "descripcion_modulo": "Gestion de contratos y adendas",
            "icono_modulo": "file-text",
            "ruta_modulo": "/contratos",
            "permisos_requeridos": "gestionar_usuarios",
        },
        {
            "nombre_modulo": "Gestion Documentos",
            "descripcion_modulo": "Gestion de documentos digitales del personal",
            "icono_modulo": "file-check",
            "ruta_modulo": "/legajo/gestion",
            "permisos_requeridos": "gestionar_usuarios",
        },
        {
            "nombre_modulo": "Onboarding",
            "descripcion_modulo": "Gestion del proceso de incorporacion",
            "icono_modulo": "user-plus",
            "ruta_modulo": "/onboarding/admin",
            "permisos_requeridos": "gestionar_usuarios",
        },
    ]

    max_order = (
        Modulos.objects.filter(modulo_padre=admin_module)
        .order_by("-orden_visualizacion")
        .values_list("orden_visualizacion", flat=True)
        .first()
    )
    next_order = (max_order or 0) + 1

    for module_data in modules_to_add:
        exists = Modulos.objects.filter(
            ruta_modulo=module_data["ruta_modulo"],
            modulo_padre=admin_module,
        ).exists()
        if exists:
            continue

        Modulos.objects.create(
            nombre_modulo=module_data["nombre_modulo"],
            descripcion_modulo=module_data["descripcion_modulo"],
            icono_modulo=module_data["icono_modulo"],
            ruta_modulo=module_data["ruta_modulo"],
            orden_visualizacion=next_order,
            estado_modulo="activo",
            modulo_padre=admin_module,
            permisos_requeridos=module_data["permisos_requeridos"],
        )
        next_order += 1


def remove_missing_admin_modules(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")
    routes = ["/contratos", "/legajo/gestion", "/onboarding/admin"]
    Modulos.objects.filter(ruta_modulo__in=routes).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("app_rrhh", "0015_seed_menu_remuneraciones"),
    ]

    operations = [
        migrations.RunPython(add_missing_admin_modules, remove_missing_admin_modules),
    ]
