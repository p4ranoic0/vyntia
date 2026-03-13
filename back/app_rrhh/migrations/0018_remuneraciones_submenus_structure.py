from django.db import migrations


def apply_remuneraciones_structure(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    remuneraciones = (
        Modulos.objects.filter(nombre_modulo="Remuneraciones")
        .order_by("modulo_id")
        .first()
    )

    if not remuneraciones:
        max_top_order = (
            Modulos.objects.filter(modulo_padre__isnull=True)
            .order_by("-orden_visualizacion")
            .values_list("orden_visualizacion", flat=True)
            .first()
        )
        remuneraciones = Modulos.objects.create(
            nombre_modulo="Remuneraciones",
            descripcion_modulo="Modulo integral de planillas, boletas y reportes",
            icono_modulo="landmark",
            ruta_modulo="/remuneraciones",
            orden_visualizacion=(max_top_order or 0) + 1,
            estado_modulo="activo",
            modulo_padre=None,
            permisos_requeridos="",
        )

    # Remuneraciones debe ser modulo principal con landing propia
    remuneraciones.modulo_padre = None
    remuneraciones.ruta_modulo = "/remuneraciones"
    remuneraciones.descripcion_modulo = (
        "Modulo integral de planillas, boletas y reportes"
    )
    remuneraciones.save(
        update_fields=[
            "modulo_padre",
            "ruta_modulo",
            "descripcion_modulo",
            "fecha_actualizacion",
        ]
    )

    submenu_definitions = [
        {
            "nombre_modulo": "Planillas Mensuales",
            "descripcion_modulo": "Consulta mensual de planillas por modalidad",
            "icono_modulo": "file-text",
            "ruta_modulo": "/remuneraciones/planillas-mensuales",
            "orden_visualizacion": 1,
            "permisos_requeridos": "",
        },
        {
            "nombre_modulo": "Proceso de Planillas",
            "descripcion_modulo": "Proceso de calculo de planilla con datos del empleado",
            "icono_modulo": "file-text",
            "ruta_modulo": "/remuneraciones/proceso-planillas",
            "orden_visualizacion": 2,
            "permisos_requeridos": "",
        },
        {
            "nombre_modulo": "Boletas de Pago",
            "descripcion_modulo": "Generacion y consulta de boletas de pago",
            "icono_modulo": "file-text",
            "ruta_modulo": "/remuneraciones/boletas-pago",
            "orden_visualizacion": 3,
            "permisos_requeridos": "",
        },
        {
            "nombre_modulo": "Reportes",
            "descripcion_modulo": "Reportes mensuales de remuneraciones",
            "icono_modulo": "bar-chart",
            "ruta_modulo": "/remuneraciones/reportes",
            "orden_visualizacion": 4,
            "permisos_requeridos": "",
        },
        {
            "nombre_modulo": "Configuracion",
            "descripcion_modulo": "Tabla maestra AFP, ingresos y descuentos",
            "icono_modulo": "settings",
            "ruta_modulo": "/remuneraciones/configuracion",
            "orden_visualizacion": 5,
            "permisos_requeridos": "",
        },
    ]

    for data in submenu_definitions:
        item = (
            Modulos.objects.filter(ruta_modulo=data["ruta_modulo"])
            .order_by("modulo_id")
            .first()
        )
        if item:
            item.nombre_modulo = data["nombre_modulo"]
            item.descripcion_modulo = data["descripcion_modulo"]
            item.icono_modulo = data["icono_modulo"]
            item.orden_visualizacion = data["orden_visualizacion"]
            item.modulo_padre = remuneraciones
            item.estado_modulo = "activo"
            item.permisos_requeridos = data["permisos_requeridos"]
            item.save(
                update_fields=[
                    "nombre_modulo",
                    "descripcion_modulo",
                    "icono_modulo",
                    "orden_visualizacion",
                    "modulo_padre",
                    "estado_modulo",
                    "permisos_requeridos",
                    "fecha_actualizacion",
                ]
            )
        else:
            Modulos.objects.create(
                nombre_modulo=data["nombre_modulo"],
                descripcion_modulo=data["descripcion_modulo"],
                icono_modulo=data["icono_modulo"],
                ruta_modulo=data["ruta_modulo"],
                orden_visualizacion=data["orden_visualizacion"],
                estado_modulo="activo",
                modulo_padre=remuneraciones,
                permisos_requeridos=data["permisos_requeridos"],
            )


def reverse_remuneraciones_structure(apps, schema_editor):
    Modulos = apps.get_model("app_rrhh", "Modulos")

    remuneraciones = (
        Modulos.objects.filter(nombre_modulo="Remuneraciones")
        .order_by("modulo_id")
        .first()
    )
    if not remuneraciones:
        return

    submenu_routes = [
        "/remuneraciones/planillas-mensuales",
        "/remuneraciones/proceso-planillas",
        "/remuneraciones/boletas-pago",
        "/remuneraciones/reportes",
    ]

    Modulos.objects.filter(
        ruta_modulo__in=submenu_routes, modulo_padre=remuneraciones
    ).delete()

    remuneraciones.ruta_modulo = "/remuneraciones/configuracion"
    remuneraciones.save(update_fields=["ruta_modulo", "fecha_actualizacion"])


class Migration(migrations.Migration):

    dependencies = [
        ("app_rrhh", "0017_restructure_menu_remuneraciones_empleados"),
    ]

    operations = [
        migrations.RunPython(
            apply_remuneraciones_structure, reverse_remuneraciones_structure
        ),
    ]
