# Generated manually - 2026-02-17
# Agrega soporte para menú jerárquico en la tabla de módulos:
# - modulo_padre: FK self-referencial para submenús
# - permisos_requeridos: permisos separados por coma para control de visibilidad

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app_rrhh', '0002_remove_permiso_permiso_modulo__e0d3af_idx_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='modulos',
            name='modulo_padre',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='submodulos',
                to='app_rrhh.modulos',
                db_column='modulo_padre_id',
                verbose_name='Módulo padre',
            ),
        ),
        migrations.AddField(
            model_name='modulos',
            name='permisos_requeridos',
            field=models.CharField(
                blank=True,
                max_length=500,
                null=True,
                verbose_name='Permisos requeridos',
                help_text='Nombres de permisos separados por coma. Vacío = visible para todos los autenticados.',
            ),
        ),
    ]
