#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vyntia.settings.development')
django.setup()

from apps.employees.models import Employee
from apps.identity.models import User

try:
    # Obtener el usuario admin
    usuario_admin = User.objects.get(username='admin')
    print(f"User: {usuario_admin.username}")
    print(f"User ID: {usuario_admin.usuario_id}")
    print(f"Employee ID en User: {usuario_admin.empleado_id}")
    
    # Verificar si tiene empleado asociado
    if hasattr(usuario_admin, 'empleado') and usuario_admin.empleado:
        empleado = usuario_admin.empleado
        print(f"Employee asociado: {empleado.nombres_empleado} {empleado.apellido_paterno} {empleado.apellido_materno}")
        print(f"Employee ID: {empleado.empleado_id}")
        
        # Verificar datos laborales
        datos_laborales = empleado.datos_laborales_actuales()
        if datos_laborales:
            print(f"Datos laborales actuales: {datos_laborales}")
            if datos_laborales.area:
                print(f"Área: {datos_laborales.area.nombre_completo}")
            else:
                print("Sin área asignada en datos laborales")
        else:
            print("Sin datos laborales actuales")
    else:
        print("User admin NO tiene empleado asociado")
        
        # Verificar si existe el empleado con ID 9
        try:
            empleado_9 = Employee.objects.get(empleado_id=9)
            print(f"Employee ID 9 existe: {empleado_9.nombres_empleado} {empleado_9.apellido_paterno} {empleado_9.apellido_materno}")
            print(f"User asociado al empleado 9: {empleado_9.usuario if hasattr(empleado_9, 'usuario') else 'Ninguno'}")
        except Employee.DoesNotExist:
            print("Employee con ID 9 no existe")
            
except User.DoesNotExist:
    print("User admin no encontrado")
except Exception as e:
    print(f"Error: {e}")