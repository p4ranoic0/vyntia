"""Payroll services — re-exports for backward-compatible imports.

Calculation engines for the Peruvian payroll workflow.
"""

from .descuento_masivo_service import DescuentoMasivoService
from .planilla_calculo_service import PlanillaCalculoService

__all__ = [
    "DescuentoMasivoService",
    "PlanillaCalculoService",
]
