# Generated manually - 2026-03-08
# Índices compuestos para mejorar rendimiento RBAC/menu en PostgreSQL

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("app_rrhh", "0009_modulopermiso_pivot"),
    ]

    operations = [
        migrations.AddIndex(
            model_name="modulos",
            index=models.Index(
                fields=["modulo_padre", "estado_modulo", "orden_visualizacion"],
                name="modulos_padre_estado_orden_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="rolpermisos",
            index=models.Index(
                fields=["rol", "permiso", "fecha_asignacion"],
                name="rol_permisos_rol_perm_fec_idx",
            ),
        ),
        migrations.AddIndex(
            model_name="usuarioroles",
            index=models.Index(
                fields=["usuario", "estado_asignacion"],
                name="usuario_roles_usr_estado_idx",
            ),
        ),
    ]
