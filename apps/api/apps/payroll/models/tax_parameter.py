"""
Modelo para configuración de la UIT (Unidad Impositiva Tributaria).
Usadopara cálculos de ESSALUD CAS y topes de renta de 4ta categoría.
"""

import uuid
from decimal import Decimal

from django.db import models


class TaxParameter(models.Model):
    """Configuración de la UIT vigente por periodo."""

    ESTADO_CHOICES = [
        ("activo", "Activo"),
        ("inactivo", "Inactivo"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    anio = models.PositiveIntegerField(help_text="Año fiscal (YYYY)")
    valor_uit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Valor de la UIT en soles para el año fiscal",
    )
    tope_renta_cuarta_uit = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("45.00"),
        help_text="Tope de exoneración en UITs (generalmente 45 UITs)",
    )
    porcentaje_renta_cuarta = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("8.00"),
        help_text="Porcentaje de retención de renta de 4ta categoría",
    )
    status = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="activo", db_column="estado")

    # Auditoría
    created_at = models.DateTimeField(auto_now_add=True, db_column="fecha_creacion")
    updated_at = models.DateTimeField(auto_now=True, db_column="fecha_actualizacion")
    created_by = models.ForeignKey(
        "identity.User",
        on_delete=models.PROTECT,
        related_name="configuraciones_uit_creadas",
        null=True,
        blank=True,
        db_column="creado_por",
    )

    class Meta:
        db_table = "configuracion_uit"
        indexes = [
            models.Index(fields=["anio"]),
            models.Index(fields=["status"]),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["anio"], name="uniq_configuracion_uit_anio"
            ),
        ]
        ordering = ["-anio"]

    def __str__(self):
        return f"UIT {self.anio}: S/ {self.valor_uit}"

    @property
    def tope_renta_cuarta_soles(self):
        """Calcula el tope de exoneración en soles."""
        return self.valor_uit * self.tope_renta_cuarta_uit

    @property
    def essalud_cas_mensual(self):
        """Calcula el aporte ESSALUD para CAS (9% del 45% de UIT)."""
        return (self.valor_uit * Decimal("0.45") * Decimal("0.09")) / Decimal("12")
