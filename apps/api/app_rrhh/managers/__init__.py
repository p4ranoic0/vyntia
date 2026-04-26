# -*- coding: utf-8 -*-
"""
Managers personalizados para la aplicación de Recursos Humanos

Contiene managers personalizados que proporcionan métodos de consulta
optimizados y funcionalidades específicas para los modelos.
"""

from .contratos_manager import ContratosAdendasManager
from .usuario_manager import UsuarioManager
from .vacation_managers import (
    ConfiguracionVacacionesManager,
    PeriodoVacacionalManager,
    SolicitudVacacionesManager,
    GoceVacacionesManager,
    HistorialSolicitudVacacionesManager
)

__all__ = [
    'ContratosAdendasManager',
    'UsuarioManager',
    'ConfiguracionVacacionesManager',
    'PeriodoVacacionalManager',
    'SolicitudVacacionesManager',
    'GoceVacacionesManager',
    'HistorialSolicitudVacacionesManager',
]