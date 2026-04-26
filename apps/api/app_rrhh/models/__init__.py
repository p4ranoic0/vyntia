# -*- coding: utf-8 -*-
"""
Modelos de la aplicación de Recursos Humanos

Estructura modular de modelos para mejorar la organización y mantenibilidad del código.
Cada archivo contiene modelos relacionados funcionalmente.
"""

# Importar todos los modelos para mantener compatibilidad
# from .contratos import ContratoAdenda  # Comentado para evitar conflicto de tabla
from .configuracion_uit import ConfiguracionUit
from .onboarding import OnboardingEmpleado
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
from .vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    # Modelos de vacaciones
    "ConfiguracionVacaciones",
    "PeriodoVacacional",
    "SolicitudVacaciones",
    "GoceVacaciones",
    "HistorialSolicitudVacaciones",
    # Modelo de onboarding
    "OnboardingEmpleado",
    # Modelos de remuneraciones
    "ConfiguracionAfp",
    "ConfiguracionRemuneracion",
    "ConfiguracionUit",
    "PlanillaMensual",
    "DetallePlanilla",
    "ConceptoPlanilla",
    "DescuentoMasivo",
    "BoletaPago",
    "CalendarioPago",
]
