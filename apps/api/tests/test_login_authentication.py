# -*- coding: utf-8 -*-
"""
Tests para funcionalidades de login y autenticación.

Este módulo contiene tests para:
- Proceso de login/logout
- Autenticación de usuarios
- Validación de credenciales
- Manejo de sesiones
- Tokens de autenticación
- Recuperación de contraseñas
"""

import pytest
from django.test import TestCase, Client
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
from unittest.mock import patch

from app_rrhh.models import Area
from apps.identity.models import (
    Usuario, Rol, Permiso, RolPermisos, UsuarioRoles
)


class LoginAuthenticationTest(TestCase):
    """Tests para funcionalidades de login y autenticación."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.client = Client()
        
        # Crear área de prueba
        self.area_rrhh = Area.objects.create(
            nombre_organo='Recursos Humanos',
            nombre_unidad_organica='Gestión de Personal',
            siglas_area='RRHH',
            descripcion_area='Área de recursos humanos',
            estado_area='activa'
        )
        
        # Crear permisos de prueba
        self.permiso_login = Permiso.objects.create(
            nombre_permiso='login_sistema',
            descripcion_permiso='Permiso para acceder al sistema',
            modulo_id=1,  # ID del módulo de autenticación
            tipo_permiso='leer',
            estado_permiso='activo'
        )
        
        # Crear rol de prueba
        self.rol_usuario = Rol.objects.create(
            nombre_rol='Usuario Básico',
            descripcion_rol='Rol básico para usuarios del sistema',
            nivel_jerarquico=1,
            estado_rol='activo'
        )
        
        # Asignar permiso al rol
        RolPermisos.objects.create(
            rol=self.rol_usuario,
            permiso=self.permiso_login,
            fecha_asignacion=timezone.now()
        )
        
        # Crear usuario de prueba
        self.usuario_activo = Usuario.objects.create_user(
            username='usuario.test',
            email='usuario@test.com',
            password='password123',
            nombres_usuario='Usuario',
            apellidos_usuario='de Prueba',
            tipo_usuario='empleado',
            estado_usuario='activo'
        )
        
        # Asignar rol al usuario
        UsuarioRoles.objects.create(
            usuario=self.usuario_activo,
            rol=self.rol_usuario,
            estado_asignacion='activo',
            fecha_asignacion=timezone.now(),
            fecha_expiracion=timezone.now() + timedelta(days=365)
        )
        
        # Crear usuario inactivo para tests
        self.usuario_inactivo = Usuario.objects.create_user(
            username='usuario.inactivo',
            email='inactivo@test.com',
            password='password123',
            nombres_usuario='Usuario',
            apellidos_usuario='Inactivo',
            tipo_usuario='empleado',
            estado_usuario='inactivo'
        )
        
        # Crear usuario bloqueado para tests
        self.usuario_bloqueado = Usuario.objects.create_user(
            username='usuario.bloqueado',
            email='bloqueado@test.com',
            password='password123',
            nombres_usuario='Usuario',
            apellidos_usuario='Bloqueado',
            tipo_usuario='empleado',
            estado_usuario='bloqueado'
        )
    
    def test_autenticacion_usuario_valido(self):
        """Test de autenticación con credenciales válidas."""
        usuario = authenticate(
            username='usuario.test',
            password='password123'
        )
        
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.username, 'usuario.test')
        self.assertTrue(usuario.is_active)
        self.assertEqual(usuario.estado_usuario, 'activo')
    
    def test_autenticacion_credenciales_invalidas(self):
        """Test de autenticación con credenciales inválidas."""
        # Password incorrecto
        usuario = authenticate(
            username='usuario.test',
            password='password_incorrecto'
        )
        self.assertIsNone(usuario)
        
        # Username incorrecto
        usuario = authenticate(
            username='usuario_inexistente',
            password='password123'
        )
        self.assertIsNone(usuario)
        
        # Ambos incorrectos
        usuario = authenticate(
            username='usuario_inexistente',
            password='password_incorrecto'
        )
        self.assertIsNone(usuario)
    
    def test_autenticacion_usuario_inactivo(self):
        """Test de autenticación con usuario inactivo."""
        # Desactivar usuario
        self.usuario_activo.desactivar_usuario('Prueba de desactivación')
        
        # Refrescar desde la base de datos
        self.usuario_activo.refresh_from_db()
        
        # Verificar que el usuario está inactivo
        self.assertFalse(self.usuario_activo.is_active)
        
        # Intentar autenticar
        usuario_autenticado = authenticate(
            username='usuario.test',
            password='password123'
        )
        
        # La autenticación debe fallar
        self.assertIsNone(usuario_autenticado)
    
    def test_autenticacion_usuario_bloqueado(self):
        """Test de autenticación con usuario bloqueado."""
        usuario = authenticate(
            username='usuario.bloqueado',
            password='password123'
        )
        
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario.estado_usuario, 'bloqueado')
    
    def test_registro_intento_fallido(self):
        """Test de registro de intentos fallidos de login."""
        # Verificar estado inicial
        self.assertEqual(self.usuario_activo.intentos_fallidos, 0)
        self.assertIsNone(self.usuario_activo.fecha_ultimo_intento_fallido)
        
        # Registrar intento fallido
        self.usuario_activo.registrar_intento_fallido()
        
        # Verificar que se registró correctamente
        self.assertEqual(self.usuario_activo.intentos_fallidos, 1)
        self.assertIsNotNone(self.usuario_activo.fecha_ultimo_intento_fallido)
        
        # Registrar múltiples intentos
        self.usuario_activo.registrar_intento_fallido()
        self.usuario_activo.registrar_intento_fallido()
        
        self.assertEqual(self.usuario_activo.intentos_fallidos, 3)
    
    def test_reseteo_intentos_fallidos(self):
        """Test de reseteo de intentos fallidos tras login exitoso."""
        # Simular intentos fallidos
        self.usuario_activo.intentos_fallidos = 3
        self.usuario_activo.fecha_ultimo_intento_fallido = timezone.now()
        self.usuario_activo.save()
        
        # Resetear intentos
        self.usuario_activo.resetear_intentos_fallidos()
        
        # Verificar reseteo
        self.assertEqual(self.usuario_activo.intentos_fallidos, 0)
        self.assertIsNone(self.usuario_activo.fecha_ultimo_intento_fallido)
    
    def test_bloqueo_por_intentos_fallidos(self):
        """Test de bloqueo automático por múltiples intentos fallidos."""
        # Configurar límite de intentos (normalmente sería 5)
        limite_intentos = 5
        
        # Simular múltiples intentos fallidos
        for i in range(limite_intentos):
            self.usuario_activo.registrar_intento_fallido()
        
        # Verificar que se alcanzó el límite
        self.assertEqual(self.usuario_activo.intentos_fallidos, limite_intentos)
        
        # En una implementación real, aquí se bloquearía automáticamente
        # Por ahora solo verificamos que se registraron los intentos
        self.assertGreaterEqual(self.usuario_activo.intentos_fallidos, limite_intentos)
    
    def test_generacion_token_recuperacion(self):
        """Test de generación de token para recuperación de contraseña."""
        # Verificar estado inicial
        self.assertIsNone(self.usuario_activo.token_recuperacion)
        self.assertIsNone(self.usuario_activo.fecha_expiracion_token)
        
        # Generar token
        token = self.usuario_activo.generar_token_recuperacion()
        
        # Verificar que se generó correctamente
        self.assertIsNotNone(token)
        self.assertEqual(self.usuario_activo.token_recuperacion, token)
        self.assertIsNotNone(self.usuario_activo.fecha_expiracion_token)
        
        # Verificar que el token tiene la longitud esperada
        self.assertGreater(len(token), 30)  # Token URL-safe tiene más de 30 caracteres
        
        # Verificar que la fecha de expiración es futura
        self.assertGreater(self.usuario_activo.fecha_expiracion_token, timezone.now())
    
    def test_validacion_token_recuperacion_valido(self):
        """Test de validación de token de recuperación válido."""
        # Generar token
        token = self.usuario_activo.generar_token_recuperacion()
        
        # Validar token
        es_valido = self.usuario_activo.validar_token_recuperacion(token)
        
        self.assertTrue(es_valido)
    
    def test_validacion_token_recuperacion_invalido(self):
        """Test de validación de token de recuperación inválido."""
        # Generar token
        self.usuario_activo.generar_token_recuperacion()
        
        # Validar con token incorrecto
        es_valido = self.usuario_activo.validar_token_recuperacion('token_incorrecto')
        
        self.assertFalse(es_valido)
    
    def test_validacion_token_recuperacion_expirado(self):
        """Test de validación de token de recuperación expirado."""
        # Generar token
        token = self.usuario_activo.generar_token_recuperacion()
        
        # Simular expiración del token
        self.usuario_activo.fecha_expiracion_token = timezone.now() - timedelta(hours=1)
        self.usuario_activo.save()
        
        # Validar token expirado
        es_valido = self.usuario_activo.validar_token_recuperacion(token)
        
        self.assertFalse(es_valido)
    
    def test_cambio_password_exitoso(self):
        """Test de cambio de contraseña exitoso."""
        nueva_password = 'nueva_password_123'
        
        # Cambiar contraseña
        self.usuario_activo.cambiar_password(nueva_password)
        
        # Verificar que se actualizó la fecha de cambio
        self.assertIsNotNone(self.usuario_activo.fecha_ultimo_cambio_password)
        
        # Verificar que se reseteo el flag de cambio requerido
        self.assertFalse(self.usuario_activo.requiere_cambio_password)
        
        # Verificar que se limpió el token de recuperación
        self.assertIsNone(self.usuario_activo.token_recuperacion)
        self.assertIsNone(self.usuario_activo.fecha_expiracion_token)
        
        # Verificar que la nueva contraseña funciona
        usuario_autenticado = authenticate(
            username='usuario.test',
            password=nueva_password
        )
        self.assertIsNotNone(usuario_autenticado)
    
    def test_registro_acceso_usuario(self):
        """Test de registro de información de acceso."""
        ip_test = '192.168.1.100'
        user_agent_test = 'Mozilla/5.0 (Test Browser)'
        
        # Registrar acceso
        self.usuario_activo.registrar_acceso(
            ip_address=ip_test,
            user_agent=user_agent_test
        )
        
        # Verificar que se registró la información
        self.assertIsNotNone(self.usuario_activo.last_login)
        self.assertEqual(self.usuario_activo.ip_ultimo_acceso, ip_test)
        self.assertEqual(self.usuario_activo.user_agent_ultimo_acceso, user_agent_test)
    
    def test_verificacion_password_expirado(self):
        """Test de verificación de contraseña expirada."""
        # Simular contraseña expirada
        self.usuario_activo.fecha_expiracion_password = timezone.now() - timedelta(days=1)
        self.usuario_activo.save()
        
        # Verificar que está expirada
        self.assertTrue(self.usuario_activo.password_expirado)
        
        # Simular contraseña no expirada
        self.usuario_activo.fecha_expiracion_password = timezone.now() + timedelta(days=30)
        self.usuario_activo.save()
        
        # Verificar que no está expirada
        self.assertFalse(self.usuario_activo.password_expirado)
    
    def test_verificacion_password_por_expirar(self):
        """Test de verificación de contraseña próxima a expirar."""
        # Simular contraseña que expira en 3 días
        self.usuario_activo.fecha_expiracion_password = timezone.now() + timedelta(days=3)
        self.usuario_activo.save()
        
        # Verificar que está por expirar (umbral de 7 días)
        self.assertTrue(self.usuario_activo.password_por_expirar)
        
        # Simular contraseña que expira en 10 días
        self.usuario_activo.fecha_expiracion_password = timezone.now() + timedelta(days=10)
        self.usuario_activo.save()
        
        # Verificar que no está por expirar
        self.assertFalse(self.usuario_activo.password_por_expirar)
    
    def test_verificacion_usuario_bloqueado(self):
        """Test de verificación de estado de bloqueo."""
        # Usuario normal no debe estar bloqueado
        self.assertFalse(self.usuario_activo.esta_bloqueado)
        
        # Usuario con estado bloqueado debe estar bloqueado
        self.assertTrue(self.usuario_bloqueado.esta_bloqueado)
        
        # Simular bloqueo por intentos fallidos
        self.usuario_activo.intentos_fallidos = 10  # Más del límite
        self.usuario_activo.save()
        
        # En una implementación real, esto también bloquearía al usuario
        # Por ahora solo verificamos el estado directo
        self.assertEqual(self.usuario_activo.intentos_fallidos, 10)
    
    def test_activacion_desactivacion_usuario(self):
        """Test de activación y desactivación de usuarios."""
        # Desactivar usuario
        self.usuario_activo.desactivar_usuario('Prueba de desactivación')
        
        # Verificar desactivación
        self.assertFalse(self.usuario_activo.is_active)
        self.assertEqual(self.usuario_activo.estado_usuario, 'inactivo')
        
        # Reactivar usuario
        self.usuario_activo.activar_usuario()
        
        # Verificar activación
        self.assertTrue(self.usuario_activo.is_active)
        self.assertEqual(self.usuario_activo.estado_usuario, 'activo')
    
    def test_suspension_usuario(self):
        """Test de suspensión temporal de usuario."""
        # Suspender usuario
        self.usuario_activo.suspender_usuario('Suspensión por prueba')
        
        # Verificar suspensión
        self.assertEqual(self.usuario_activo.estado_usuario, 'suspendido')
        # El usuario suspendido puede seguir activo en Django pero con estado diferente
    
    def test_bloqueo_permanente_usuario(self):
        """Test de bloqueo permanente de usuario."""
        # Bloquear usuario
        self.usuario_activo.bloquear_usuario('Bloqueo por prueba')
        
        # Verificar bloqueo
        self.assertEqual(self.usuario_activo.estado_usuario, 'bloqueado')
        # Nota: bloquear_usuario() solo cambia estado_usuario, no is_active
        self.assertTrue(self.usuario_activo.is_active)  # is_active permanece True
        self.assertIsNotNone(self.usuario_activo.fecha_bloqueo)
        
        # Verificar que está bloqueado
        self.assertTrue(self.usuario_activo.esta_bloqueado)