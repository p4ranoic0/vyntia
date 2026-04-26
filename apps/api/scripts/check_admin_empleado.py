#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from app_rrhh.models import Usuario, Empleado

try:
    # Obtener el usuario admin
    usuario_admin = Usuario.objects.get(username='admin')
    print(f"Usuario: {usuario_admin.username}")
    print(f"Usuario ID: {usuario_admin.usuario_id}")
    print(f"Empleado ID en Usuario: {usuario_admin.empleado_id}")
    
    # Verificar si tiene empleado asociado
    if hasattr(usuario_admin, 'empleado') and usuario_admin.empleado:
        empleado = usuario_admin.empleado
        print(f"Empleado asociado: {empleado.nombres_empleado} {empleado.apellido_paterno} {empleado.apellido_materno}")
        print(f"Empleado ID: {empleado.empleado_id}")
        
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
        print("Usuario admin NO tiene empleado asociado")
        
        # Verificar si existe el empleado con ID 9
        try:
            empleado_9 = Empleado.objects.get(empleado_id=9)
            print(f"Empleado ID 9 existe: {empleado_9.nombres_empleado} {empleado_9.apellido_paterno} {empleado_9.apellido_materno}")
            print(f"Usuario asociado al empleado 9: {empleado_9.usuario if hasattr(empleado_9, 'usuario') else 'Ninguno'}")
        except Empleado.DoesNotExist:
            print("Empleado con ID 9 no existe")
            
except Usuario.DoesNotExist:
    print("Usuario admin no encontrado")
except Exception as e:
    print(f"Error: {e}")