# -*- coding: utf-8 -*-
"""
Tests de Integración del Sistema de Autenticación

Este módulo contiene tests que verifican el funcionamiento completo
del sistema de autenticación, incluyendo la interacción entre
usuarios, roles, permisos y áreas.
"""

import pytest
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.utils import timezone
from datetime import datetime, timedelta

from app_rrhh.models import (
    Usuario, Rol, Permiso, RolPermisos, UsuarioRoles, Area
)


class AuthSystemIntegrationTest(TestCase):
    """Tests de integración del sistema completo de autenticación."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        # Crear área de prueba
        self.area_rrhh = Area.objects.create(
            nombre_organo='Recursos Humanos',
            nombre_unidad_organica='Gestión de Personal',
            siglas_area='RRHH',
            descripcion_area='Área de gestión de recursos humanos',
            estado_area='activa'
        )
        
        # Crear permisos de prueba
        self.permiso_leer = Permiso.objects.create(
            nombre_permiso='Leer Empleados',
            descripcion_permiso='Permiso para leer información de empleados',
            modulo_id=1,
            tipo_permiso='leer'
        )
        
        self.permiso_escribir = Permiso.objects.create(
            nombre_permiso='Escribir Empleados',
            descripcion_permiso='Permiso para modificar información de empleados',
            modulo_id=1,
            tipo_permiso='actualizar'
        )
        
        self.permiso_admin = Permiso.objects.create(
            nombre_permiso='Administrar Sistema',
            descripcion_permiso='Permiso de administración completa',
            modulo_id=2,
            tipo_permiso='ejecutar'
        )
        
        # Crear roles de prueba
        self.rol_empleado = Rol.objects.create(
            nombre_rol='Empleado',
            descripcion_rol='Rol básico para empleados',
            nivel_jerarquico=1
        )
        
        self.rol_supervisor = Rol.objects.create(
            nombre_rol='Supervisor',
            descripcion_rol='Rol para supervisores de área',
            nivel_jerarquico=2
        )
        
        self.rol_admin = Rol.objects.create(
            nombre_rol='Administrador',
            descripcion_rol='Rol de administrador del sistema',
            nivel_jerarquico=3
        )
        
        # Asignar permisos a roles
        RolPermisos.objects.create(
            rol=self.rol_empleado,
            permiso=self.permiso_leer
        )
        
        RolPermisos.objects.create(
            rol=self.rol_supervisor,
            permiso=self.permiso_leer
        )
        
        RolPermisos.objects.create(
            rol=self.rol_supervisor,
            permiso=self.permiso_escribir
        )
        
        RolPermisos.objects.create(
            rol=self.rol_admin,
            permiso=self.permiso_leer
        )
        
        RolPermisos.objects.create(
            rol=self.rol_admin,
            permiso=self.permiso_escribir
        )
        
        RolPermisos.objects.create(
            rol=self.rol_admin,
            permiso=self.permiso_admin
        )
    
    def test_creacion_usuario_completo_con_roles(self):
        """Test de creación completa de usuario con asignación de roles."""
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username='juan.perez',
            email='juan.perez@empresa.com',
            password='password123',
            nombres_usuario='Juan Carlos',
            apellidos_usuario='Pérez García'
        )
        
        # Verificar que el usuario se creó correctamente
        self.assertTrue(usuario.is_active)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        
        # Asignar rol de empleado
        usuario_rol = UsuarioRoles.objects.create(
            usuario=usuario,
            rol=self.rol_empleado,

            fecha_asignacion=timezone.now(),
            fecha_expiracion=timezone.now() + timedelta(days=365)
        )
        
        # Verificar que el rol se asignó correctamente
        self.assertTrue(usuario_rol.es_activo)
        self.assertEqual(usuario.roles_activos().count(), 1)
        self.assertIn(self.rol_empleado, usuario.roles_activos())
    
    def test_autenticacion_usuario_con_permisos(self):
        """Test de autenticación y verificación de permisos."""
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username='maria.gonzalez',
            email='maria.gonzalez@empresa.com',
            password='password456',
            nombres_usuario='María Elena',
            apellidos_usuario='González López',

        )
        
        # Asignar rol de supervisor
        UsuarioRoles.objects.create(
            usuario=usuario,
            rol=self.rol_supervisor,
            estado_asignacion='activo',
            fecha_asignacion=timezone.now(),
            fecha_expiracion=timezone.now() + timedelta(days=365)
        )
        
        # Autenticar usuario
        user_authenticated = authenticate(
            username='maria.gonzalez',
            password='password456'
        )
        
        # Verificar autenticación exitosa
        self.assertIsNotNone(user_authenticated)
        self.assertEqual(user_authenticated.username, 'maria.gonzalez')
        
        # Verificar permisos del usuario
        permisos_usuario = usuario.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_usuario)
        self.assertIn(self.permiso_escribir, permisos_usuario)
        self.assertNotIn(self.permiso_admin, permisos_usuario)
    
    def test_escalacion_permisos_multiple_roles(self):
        """Test de escalación de permisos con múltiples roles."""
        # Crear usuario con nivel de acceso total
        usuario = Usuario.objects.create_user(
            username='admin.sistema',
            email='admin@empresa.com',
            password='admin123',
            nombres_usuario='Administrador',
            apellidos_usuario='del Sistema',
            nivel_acceso='total'
        )
        
        # Asignar múltiples roles
        UsuarioRoles.objects.create(
            usuario=usuario,
            rol=self.rol_empleado,
            estado_asignacion='activo',
            fecha_asignacion=timezone.now(),
            fecha_expiracion=timezone.now() + timedelta(days=365)
        )
        
        UsuarioRoles.objects.create(
            usuario=usuario,
            rol=self.rol_admin,
            estado_asignacion='activo',
            fecha_asignacion=timezone.now(),
            fecha_expiracion=timezone.now() + timedelta(days=365)
        )
        
        # Verificar que tiene todos los permisos
        permisos_usuario = usuario.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_usuario)
        self.assertIn(self.permiso_escribir, permisos_usuario)
        self.assertIn(self.permiso_admin, permisos_usuario)
        
        # Verificar nivel de acceso
        self.assertEqual(usuario.nivel_acceso_texto, 'Acceso Total')
    
    def test_expiracion_roles_y_permisos(self):
        """Test de expiración de roles y su efecto en permisos."""
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username='temporal.user',
            email='temporal@empresa.com',
            password='temp123',
            nombres_usuario='Usuario',
            apellidos_usuario='Temporal'
        )
        
        # Asignar rol con fecha de expiración pasada
        UsuarioRoles.objects.create(
            usuario=usuario,
            rol=self.rol_supervisor,

            fecha_asignacion=timezone.now() - timedelta(days=30),
            fecha_expiracion=timezone.now() - timedelta(days=1)  # Expirado
        )
        
        # Verificar que no tiene roles activos
        self.assertEqual(usuario.roles_activos().count(), 0)
        
        # Verificar que no tiene permisos activos
        permisos_usuario = usuario.permisos_activos()
        self.assertEqual(len(permisos_usuario), 0)
    
    def test_desactivacion_rol_y_efecto_permisos(self):
        """Test de desactivación de rol y su efecto en permisos de usuarios."""
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username='affected.user',
            email='affected@empresa.com',
            password='affected123',
            nombres_usuario='Usuario',
            apellidos_usuario='Afectado'
        )
        
        # Asignar rol activo
        UsuarioRoles.objects.create(
            usuario=usuario,
            rol=self.rol_empleado,

            fecha_asignacion=timezone.now(),
            fecha_expiracion=timezone.now() + timedelta(days=365)
        )
        
        # Verificar que inicialmente tiene permisos
        permisos_iniciales = usuario.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_iniciales)
        
        # Desactivar el rol
        self.rol_empleado.desactivar()
        
        # Verificar que ya no tiene permisos activos
        permisos_finales = usuario.permisos_activos()
        self.assertEqual(len(permisos_finales), 0)
    
    def test_integridad_sistema_completo(self):
        """Test de integridad del sistema completo de autenticación."""
        # Crear múltiples usuarios con diferentes roles
        usuarios_data = [
            {
                'username': 'empleado1',
                'email': 'emp1@empresa.com',
                'password': 'emp123',
                'nombres_usuario': 'Empleado',
                'apellidos_usuario': 'Uno',
                'rol': self.rol_empleado
            },
            {
                'username': 'supervisor1',
                'email': 'sup1@empresa.com',
                'password': 'sup123',
                'nombres_usuario': 'Supervisor',
                'apellidos_usuario': 'Uno',
                'rol': self.rol_supervisor
            },
            {
                'username': 'admin1',
                'email': 'admin1@empresa.com',
                'password': 'admin123',
                'nombres_usuario': 'Admin',
                'apellidos_usuario': 'Uno',
                'rol': self.rol_admin
            }
        ]
        
        usuarios_creados = []
        
        # Crear usuarios y asignar roles
        for data in usuarios_data:
            usuario = Usuario.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password'],
                nombres_usuario=data['nombres_usuario'],
                apellidos_usuario=data['apellidos_usuario']
            )
            
            UsuarioRoles.objects.create(
                usuario=usuario,
                rol=data['rol'],
                fecha_asignacion=timezone.now(),
                fecha_expiracion=timezone.now() + timedelta(days=365)
            )
            
            usuarios_creados.append(usuario)
        
        # Verificar que cada usuario tiene los permisos correctos
        empleado = usuarios_creados[0]
        supervisor = usuarios_creados[1]
        admin = usuarios_creados[2]
        
        # Empleado: solo lectura
        permisos_empleado = empleado.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_empleado)
        self.assertNotIn(self.permiso_escribir, permisos_empleado)
        self.assertNotIn(self.permiso_admin, permisos_empleado)
        
        # Supervisor: lectura y escritura
        permisos_supervisor = supervisor.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_supervisor)
        self.assertIn(self.permiso_escribir, permisos_supervisor)
        self.assertNotIn(self.permiso_admin, permisos_supervisor)
        
        # Admin: todos los permisos
        permisos_admin = admin.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_admin)
        self.assertIn(self.permiso_escribir, permisos_admin)
        self.assertIn(self.permiso_admin, permisos_admin)
        
        # Verificar conteos totales
        self.assertEqual(Usuario.objects.count(), 3)
        self.assertEqual(UsuarioRoles.objects.filter(estado_asignacion='activo').count(), 3)
        self.assertEqual(RolPermisos.objects.count(), 6)  # 3 roles con diferentes permisos
    
    def test_cambio_area_usuario_y_permisos(self):
        """Test de cambio de área de usuario y mantenimiento de permisos."""
        # Crear segunda área
        area_finanzas = Area.objects.create(
            nombre_organo='Finanzas',
            nombre_unidad_organica='Contabilidad',
            siglas_area='FIN',
            descripcion_area='Área de finanzas y contabilidad',
            estado_area='activa'
        )
        
        # Crear usuario
        usuario = Usuario.objects.create_user(
            username='mobile.user',
            email='mobile@empresa.com',
            password='mobile123',
            nombres_usuario='Usuario',
            apellidos_usuario='Móvil'
        )
        
        # Asignar rol en área RRHH
        rol_rrhh = UsuarioRoles.objects.create(
            usuario=usuario,
            rol=self.rol_supervisor,
            estado_asignacion='activo',
            fecha_asignacion=timezone.now(),
            fecha_expiracion=timezone.now() + timedelta(days=365)
        )
        
        # Verificar permisos iniciales
        permisos_iniciales = usuario.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_iniciales)
        self.assertIn(self.permiso_escribir, permisos_iniciales)
        
        # Cambiar a área de finanzas (reactivar el mismo rol)
        rol_rrhh.estado_asignacion = 'inactivo'
        rol_rrhh.save()
        
        # Reactivar el rol existente
        rol_rrhh.estado_asignacion = 'activo'
        rol_rrhh.save()
        
        # Verificar que mantiene los mismos permisos
        permisos_finales = usuario.permisos_activos()
        self.assertIn(self.permiso_leer, permisos_finales)
        self.assertIn(self.permiso_escribir, permisos_finales)
        
        # Verificar que solo tiene un rol activo
        self.assertEqual(usuario.roles_activos().count(), 1)
        self.assertEqual(usuario.roles_activos().first(), self.rol_supervisor)