"""Organization models — re-exports for backward-compatible imports."""

from .area import Area
from .configuracion_empresa import ConfiguracionEmpresa
from .ubicacion import HistorialUbicaciones

__all__ = [
    "Area",
    "ConfiguracionEmpresa",
    "HistorialUbicaciones",
]
