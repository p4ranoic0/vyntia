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
# - area.py: Modelo Department
# - empleado.py: Modelo Employee
# - datos_laborales.py: Modelo EmploymentData
# - ubicacion.py: Modelo LocationHistory
# - usuario.py: Modelo User
# - datos_familiares.py: Modelo FamilyMember
# - datos_academicos.py: Modelo AcademicRecord
# - documentos_digitales.py: Modelo DigitalDocument
# - vacaciones.py: Modelos de vacaciones
# - permisos.py: Modelos de permisos
# - contratos.py: Modelos de contratos
# - roles.py: Modelos Role y Permission
# - sistema.py: Modelos Module, RolePermission, UserRole

# Mantener compatibilidad con importaciones existentes
# Los modelos están disponibles a través de models/__init__.py