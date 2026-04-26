"""Employees models — re-exports for backward-compatible imports."""

from .cursos_certificaciones import CursosCertificaciones
from .datos_academicos import DatosAcademicos
from .datos_familiares import DatosFamiliares
from .empleado import Empleado

__all__ = [
    "CursosCertificaciones",
    "DatosAcademicos",
    "DatosFamiliares",
    "Empleado",
]
