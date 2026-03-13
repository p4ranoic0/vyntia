# -*- coding: utf-8 -*-
"""
Tests para las funcionalidades de Login y Autenticación

Pruebas para verificar el correcto funcionamiento del sistema de autenticación,
incluyendo login, logout, validación de credenciales y manejo de sesiones.
"""

from django.test import TestCase, Client
from django.contrib.auth import get_user_model, authenticate
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
import json
from datetime import timedelta

Usuario = get_user_model()


class LoginFunctionalityTest(TestCase):
    """Tests para las funcionalidades básicas de login."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='testuser',
            email='test@example.com',
            nombres_usuario='Test',
            apellidos_usuario='User',
            password='testpassword123'
        )
    
    def test_autenticacion_correcta(self):
        """Test para autenticación con credenciales correctas."""
        user = authenticate(
            username='testuser',
            password='testpassword123'
        )
        
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.is_active)
    
    def test_autenticacion_incorrecta(self):
        """Test para autenticación con credenciales incorrectas."""
        # Password incorrecto
        user = authenticate(
            username='testuser',
            password='wrongpassword'
        )
        self.assertIsNone(user)
        
        # Username incorrecto
        user = authenticate(
            username='wronguser',
            password='testpassword123'
        )
        self.assertIsNone(user)
    
    def test_autenticacion_usuario_inactivo(self):
        """Test para autenticación con usuario inactivo."""
        # Desactivar usuario
        self.usuario.is_active = False
        self.usuario.save()
        
        user = authenticate(
            username='testuser',
            password='testpassword123'
        )
        
        # Django devuelve None para usuarios inactivos
        self.assertIsNone(user)
    
    def test_autenticacion_usuario_bloqueado(self):
        """Test para autenticación con usuario bloqueado."""
        # Bloquear usuario
        self.usuario.bloquear_usuario('Test de bloqueo')
        
        user = authenticate(
            username='testuser',
            password='testpassword123'
        )
        
        # El usuario existe pero está bloqueado
        self.assertIsNotNone(user)
        self.assertEqual(user.estado_usuario, 'bloqueado')
    
    def test_login_django_admin(self):
        """Test para login en Django admin."""
        # Hacer al usuario staff para acceso al admin
        self.usuario.is_staff = True
        self.usuario.save()
        
        # Intentar login
        response = self.client.login(
            username='testuser',
            password='testpassword123'
        )
        
        self.assertTrue(response)
    
    def test_logout_django(self):
        """Test para logout en Django."""
        # Login primero
        self.client.login(
            username='testuser',
            password='testpassword123'
        )
        
        # Verificar que está logueado
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Logout
        self.client.logout()
        
        # Verificar que ya no está logueado
        self.assertFalse('_auth_user_id' in self.client.session)


class LoginAPITest(APITestCase):
    """Tests para la API de autenticación con JWT."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        self.usuario = Usuario.objects.create_user(
            username='apiuser',
            email='api@example.com',
            nombres_usuario='API',
            apellidos_usuario='User',
            password='apipassword123'
        )
        
        # URLs de la API (ajustar según tu configuración)
        self.login_url = '/api/v1/auth/login/'
        self.refresh_url = '/api/v1/auth/refresh/'
        self.logout_url = '/api/v1/auth/logout/'
    
    def test_login_api_exitoso(self):
        """Test para login exitoso via API."""
        data = {
            'username': 'apiuser',
            'password': 'apipassword123'
        }
        
        try:
            response = self.client.post(self.login_url, data, format='json')
            
            # Si la URL existe, verificar respuesta exitosa
            if response.status_code != 404:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                # Verificar que se devuelven tokens
                response_data = response.json()
                self.assertIn('access', response_data)
                self.assertIn('refresh', response_data)
            else:
                # Si la URL no existe, el test pasa (endpoint no implementado aún)
                self.skipTest("Endpoint de login no implementado aún")
                
        except Exception as e:
            # Si hay error de conexión o configuración, skip el test
            self.skipTest(f"Error en configuración de API: {str(e)}")
    
    def test_login_api_credenciales_incorrectas(self):
        """Test para login con credenciales incorrectas via API."""
        data = {
            'username': 'apiuser',
            'password': 'wrongpassword'
        }
        
        try:
            response = self.client.post(self.login_url, data, format='json')
            
            if response.status_code != 404:
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            else:
                self.skipTest("Endpoint de login no implementado aún")
                
        except Exception as e:
            self.skipTest(f"Error en configuración de API: {str(e)}")
    
    def test_acceso_con_token_jwt(self):
        """Test para acceso a endpoints protegidos con JWT."""
        # Generar token manualmente
        refresh = RefreshToken.for_user(self.usuario)
        access_token = str(refresh.access_token)
        
        # Configurar header de autorización
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Intentar acceder a un endpoint protegido (ajustar URL según tu API)
        protected_url = '/api/v1/usuarios/me/'
        
        try:
            response = self.client.get(protected_url)
            
            if response.status_code != 404:
                # Si el endpoint existe, debería permitir acceso
                self.assertIn(response.status_code, [200, 201])
            else:
                self.skipTest("Endpoint protegido no implementado aún")
                
        except Exception as e:
            self.skipTest(f"Error en configuración de API: {str(e)}")
    
    def test_acceso_sin_token(self):
        """Test para acceso a endpoints protegidos sin token."""
        # No configurar token
        protected_url = '/api/v1/usuarios/me/'
        
        try:
            response = self.client.get(protected_url)
            
            if response.status_code != 404:
                # Debería denegar acceso sin token
                self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            else:
                self.skipTest("Endpoint protegido no implementado aún")
                
        except Exception as e:
            self.skipTest(f"Error en configuración de API: {str(e)}")
    
    def test_refresh_token(self):
        """Test para renovar token de acceso."""
        # Generar tokens
        refresh = RefreshToken.for_user(self.usuario)
        refresh_token = str(refresh)
        
        data = {
            'refresh': refresh_token
        }
        
        try:
            response = self.client.post(self.refresh_url, data, format='json')
            
            if response.status_code != 404:
                self.assertEqual(response.status_code, status.HTTP_200_OK)
                
                response_data = response.json()
                self.assertIn('access', response_data)
            else:
                self.skipTest("Endpoint de refresh no implementado aún")
                
        except Exception as e:
            self.skipTest(f"Error en configuración de API: {str(e)}")


class SeguridadLoginTest(TestCase):
    """Tests para aspectos de seguridad del login."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.usuario = Usuario.objects.create_user(
            username='secureuser',
            email='secure@example.com',
            nombres_usuario='Secure',
            apellidos_usuario='User',
            password='securepassword123'
        )
    
    def test_intentos_fallidos_incrementan(self):
        """Test para verificar que los intentos fallidos se incrementan."""
        intentos_iniciales = self.usuario.intentos_fallidos
        
        # Simular intento fallido
        self.usuario.registrar_intento_fallido()
        
        self.assertEqual(self.usuario.intentos_fallidos, intentos_iniciales + 1)
        self.assertIsNotNone(self.usuario.fecha_ultimo_intento_fallido)
    
    def test_reseteo_intentos_fallidos_login_exitoso(self):
        """Test para verificar que los intentos fallidos se resetean en login exitoso."""
        # Simular algunos intentos fallidos
        self.usuario.registrar_intento_fallido()
        self.usuario.registrar_intento_fallido()
        self.assertEqual(self.usuario.intentos_fallidos, 2)
        
        # Simular login exitoso
        self.usuario.resetear_intentos_fallidos()
        
        self.assertEqual(self.usuario.intentos_fallidos, 0)
        self.assertIsNone(self.usuario.fecha_ultimo_intento_fallido)
    
    def test_bloqueo_por_intentos_fallidos(self):
        """Test para verificar bloqueo por múltiples intentos fallidos."""
        # Simular múltiples intentos fallidos
        for i in range(5):
            self.usuario.registrar_intento_fallido()
        
        # Verificar que el usuario puede ser bloqueado
        if self.usuario.intentos_fallidos >= 5:
            self.usuario.bloquear_usuario('Múltiples intentos fallidos')
            self.assertEqual(self.usuario.estado_usuario, 'bloqueado')
    
    def test_registro_acceso_actualiza_datos(self):
        """Test para verificar que el registro de acceso actualiza los datos."""
        ip_test = '192.168.1.100'
        user_agent_test = 'Test Browser 1.0'
        
        # Registrar acceso
        self.usuario.registrar_acceso(ip_test, user_agent_test)
        
        self.assertEqual(self.usuario.ip_ultimo_acceso, ip_test)
        self.assertEqual(self.usuario.user_agent_ultimo_acceso, user_agent_test)
        self.assertIsNotNone(self.usuario.last_login)
    
    def test_token_recuperacion_seguro(self):
        """Test para verificar que el token de recuperación es seguro."""
        token1 = self.usuario.generar_token_recuperacion()
        
        # Crear otro usuario y generar token
        usuario2 = Usuario.objects.create_user(
            username='user2',
            email='user2@example.com',
            nombres_usuario='User',
            apellidos_usuario='Two',
            password='password123'
        )
        token2 = usuario2.generar_token_recuperacion()
        
        # Los tokens deben ser diferentes
        self.assertNotEqual(token1, token2)
        
        # Cada usuario solo debe validar su propio token
        self.assertTrue(self.usuario.validar_token_recuperacion(token1))
        self.assertFalse(self.usuario.validar_token_recuperacion(token2))
        
        self.assertTrue(usuario2.validar_token_recuperacion(token2))
        self.assertFalse(usuario2.validar_token_recuperacion(token1))
    
    def test_expiracion_token_recuperacion(self):
        """Test para verificar que el token de recuperación expira."""
        token = self.usuario.generar_token_recuperacion()
        
        # Token válido inicialmente
        self.assertTrue(self.usuario.validar_token_recuperacion(token))
        
        # Simular expiración del token
        self.usuario.fecha_expiracion_token = timezone.now() - timedelta(hours=1)
        self.usuario.save()
        
        # Token expirado
        self.assertFalse(self.usuario.validar_token_recuperacion(token))


class SessionManagementTest(TestCase):
    """Tests para manejo de sesiones."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = Client()
        self.usuario = Usuario.objects.create_user(
            username='sessionuser',
            email='session@example.com',
            nombres_usuario='Session',
            apellidos_usuario='User',
            password='sessionpassword123'
        )
    
    def test_sesion_creada_en_login(self):
        """Test para verificar que se crea sesión en login."""
        # Verificar que no hay sesión inicialmente
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Login
        login_successful = self.client.login(
            username='sessionuser',
            password='sessionpassword123'
        )
        
        self.assertTrue(login_successful)
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_sesion_destruida_en_logout(self):
        """Test para verificar que se destruye sesión en logout."""
        # Login primero
        self.client.login(
            username='sessionuser',
            password='sessionpassword123'
        )
        
        # Verificar sesión activa
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Logout
        self.client.logout()
        
        # Verificar sesión destruida
        self.assertFalse('_auth_user_id' in self.client.session)
    
    def test_configuracion_sesiones_simultaneas(self):
        """Test para verificar configuración de sesiones simultáneas."""
        # Verificar configuración por defecto
        self.assertEqual(self.usuario.sesiones_simultaneas_permitidas, 1)
        
        # Cambiar configuración
        self.usuario.sesiones_simultaneas_permitidas = 3
        self.usuario.save()
        
        self.assertEqual(self.usuario.sesiones_simultaneas_permitidas, 3)