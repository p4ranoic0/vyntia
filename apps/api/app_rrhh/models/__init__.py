# -*- coding: utf-8 -*-
"""
Modelos de la aplicación de Recursos Humanos

Estructura modular de modelos para mejorar la organización y mantenibilidad del código.
Cada archivo contiene modelos relacionados funcionalmente.
"""

# Importar todos los modelos para mantener compatibilidad
from .area import Area

# from .contratos import ContratoAdenda  # Comentado para evitar conflicto de tabla
from .configuracion_empresa import ConfiguracionEmpresa
from .configuracion_uit import ConfiguracionUit
from .contratos_adendas import ContratosAdendas
from .cursos_certificaciones import CursosCertificaciones
from .datos_academicos import DatosAcademicos
from .datos_familiares import DatosFamiliares
from .datos_laborales import DatosLaborales
from .documentos_digitales import DocumentosDigitales
from .empleado import Empleado
from .onboarding import OnboardingEmpleado
from .plantilla_documento import PlantillaDocumento
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
from .ubicacion import HistorialUbicaciones
from .vacaciones import (
    ConfiguracionVacaciones,
    GoceVacaciones,
    HistorialSolicitudVacaciones,
    PeriodoVacacional,
    SolicitudVacaciones,
)

# Lista de todos los modelos para facilitar importaciones
__all__ = [
    # Modelos principales
    "Area",
    "Empleado",
    "DatosLaborales",
    "HistorialUbicaciones",
    "DatosFamiliares",
    "CursosCertificaciones",
    "DatosAcademicos",
    "DocumentosDigitales",
    # Modelos de vacaciones
    "ConfiguracionVacaciones",
    "PeriodoVacacional",
    "SolicitudVacaciones",
    "GoceVacaciones",
    "HistorialSolicitudVacaciones",
    # Modelos de contratos
    # 'ContratoAdenda',  # Comentado para evitar conflicto de tabla
    "ContratosAdendas",
    # Modelo de onboarding
    "OnboardingEmpleado",
    # Plantillas Word
    "PlantillaDocumento",
    # Configuración de empresa
    "ConfiguracionEmpresa",
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
