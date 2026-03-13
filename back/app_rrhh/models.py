# -*- coding: utf-8 -*-
"""
Modelos de la aplicación de Recursos Humanos

Este archivo ahora importa todos los modelos desde la estructura modular.
Los modelos están organizados en archivos separados dentro del directorio models/
para mejorar la organización y mantenibilidad del código.
"""

# Importar todos los modelos desde la estructura modular
from .models import *

# Todos los modelos han sido migrados a la estructura modular
# Ver directorio models/ para las definiciones individuales:
# - area.py: Modelo Area
# - empleado.py: Modelo Empleado
# - datos_laborales.py: Modelo DatosLaborales
# - ubicacion.py: Modelo HistorialUbicaciones
# - usuario.py: Modelo Usuario
# - datos_familiares.py: Modelo DatosFamiliares
# - datos_academicos.py: Modelo DatosAcademicos
# - documentos_digitales.py: Modelo DocumentosDigitales
# - vacaciones.py: Modelos de vacaciones
# - permisos.py: Modelos de permisos
# - contratos.py: Modelos de contratos
# - roles.py: Modelos Rol y Permiso
# - sistema.py: Modelos Modulos, RolPermisos, UsuarioRoles

# Mantener compatibilidad con importaciones existentes
# Los modelos están disponibles a través de models/__init__.py