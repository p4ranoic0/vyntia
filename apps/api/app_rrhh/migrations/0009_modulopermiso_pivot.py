# Generated manually - 2026-03-08
# Crea tabla pivote modulo_permisos y migra datos desde modulos.permisos_requeridos

import django.db.models.deletion
from django.db import migrations, models


def backfill_modulo_permisos(apps, _schema_editor):
    modulos_model = apps.get_model("app_rrhh", "Modulos")
    permiso_model = apps.get_model("app_rrhh", "Permiso")
    modulo_permiso_model = apps.get_model("app_rrhh", "ModuloPermiso")

    permisos_by_name = {
        permiso.nombre_permiso: permiso.permiso_id
        for permiso in permiso_model.objects.all().only("permiso_id", "nombre_permiso")
    }

    relations = []
    for modulo in modulos_model.objects.exclude(
        permisos_requeridos__isnull=True
    ).exclude(permisos_requeridos=""):
        required_names = {
            item.strip()
            for item in modulo.permisos_requeridos.split(",")
            if item.strip()
        }
        for perm_name in required_names:
            permiso_id = permisos_by_name.get(perm_name)
            if permiso_id:
                relations.append(
                    modulo_permiso_model(
                        modulo_id=modulo.modulo_id, permiso_id=permiso_id
                    )
                )

    if relations:
        modulo_permiso_model.objects.bulk_create(relations, ignore_conflicts=True)


def noop_reverse(_apps, _schema_editor):
    """No-op reverse migration for backfill."""


class Migration(migrations.Migration):

    dependencies = [
        (
            "app_rrhh",
            "0008_rename_permiso_modulo__e0d3af_idx_permiso_modulo_380ffc_idx_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ModuloPermiso",
            fields=[
                (
                    "modulo_permiso_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("fecha_creacion", models.DateTimeField(auto_now_add=True)),
                (
                    "modulo",
                    models.ForeignKey(
                        db_column="modulo_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="modulo_permisos",
                        to="app_rrhh.modulos",
                    ),
                ),
                (
                    "permiso",
                    models.ForeignKey(
                        db_column="permiso_id",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="modulos_relacionados",
                        to="app_rrhh.permiso",
                    ),
                ),
            ],
            options={
                "db_table": "modulo_permisos",
                "unique_together": {("modulo", "permiso")},
            },
        ),
        migrations.AddIndex(
            model_name="modulopermiso",
            index=models.Index(
                fields=["modulo"], name="modulo_perm_modulo__4e2206_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="modulopermiso",
            index=models.Index(
                fields=["permiso"], name="modulo_perm_permiso_2a0908_idx"
            ),
        ),
        migrations.RunPython(backfill_modulo_permisos, noop_reverse),
    ]
