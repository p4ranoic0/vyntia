"""Payroll models — re-exports for backward-compatible imports."""

from .configuracion_uit import ConfiguracionUit
from .remuneracion import (
    BoletaPago,
    CalendarioPago,
    ConceptoPlanilla,
    ConfiguracionAfp,
    ConfiguracionRemuneracion,
    DescuentoMasivo,
    DetallePlanilla,
    PlanillaMensual,
)

__all__ = [
    "BoletaPago",
    "CalendarioPago",
    "ConceptoPlanilla",
    "ConfiguracionAfp",
    "ConfiguracionRemuneracion",
    "ConfiguracionUit",
    "DescuentoMasivo",
    "DetallePlanilla",
    "PlanillaMensual",
]
