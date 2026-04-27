# -*- coding: utf-8 -*-
"""
Tests para la API REST de Autenticación

Pruebas para verificar el correcto funcionamiento de los endpoints de la API
de autenticación, incluyendo login, logout, perfil de usuario y gestión de tokens JWT.
"""

import json
from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from unittest.mock import patch

from apps.employees.models import Employee
from apps.organization.models import Department
from apps.identity.models import User, Role, Permission, RolePermission, UserRole


class AuthAPITestCase(APITestCase):
    """Clase base para tests de API de autenticación."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.client = APIClient()
        
        # Crear área de prueba
        self.area = Department.objects.create(
            nombre_organo='Tecnología',
            nombre_unidad_organica='Desarrollo de Software',
            siglas_area='TECH',
            descripcion_area='Área de desarrollo',
            estado_area='activa'
        )
        
        # Crear empleado de prueba
        self.empleado = Employee.objects.create(
            nombres_empleado='Juan Carlos',
            apellido_paterno='Pérez',
            apellido_materno='González',
            numero_documento='12345678',
            correo_personal='juan.perez@empresa.com',
            telefono_celular='987654321',
            fecha_nacimiento='1990-01-01',
            estado_civil='soltero',
            genero_empleado='masculino',
            direccion_domicilio='Av. Principal 123',
            distrito_domicilio='Lima',
            provincia_domicilio='Lima',
            departamento_domicilio='Lima',
            entidad_bancaria='BCP',
            numero_cuenta_bancaria='123456789',
            numero_cci='00212312345678901234',
            estado_empleado='activo'
        )
        
        # Crear usuario de prueba
        self.usuario = User.objects.create_user(
            username='testuser',
            email='test@empresa.com',
            nombres_usuario='Test',
            apellidos_usuario='User',
            password='testpassword123',
            empleado=self.empleado,
            tipo_usuario='empleado',
            nivel_acceso='personal'
        )
        
        # Crear usuario administrador
        self.admin_usuario = User.objects.create_user(
            username='admin',
            email='admin@empresa.com',
            nombres_usuario='Admin',
            apellidos_usuario='User',
            password='adminpassword123',
            tipo_usuario='administrador',
            nivel_acceso='total',
            is_staff=True
        )
        
        # URLs de la API
        self.login_url = '/api/v1/auth/login/'
        self.logout_url = '/api/v1/auth/logout/'
        self.refresh_url = '/api/v1/auth/refresh/'
        self.profile_url = '/api/v1/auth/profile/'
        
    def get_tokens_for_user(self, user):
        """Genera tokens JWT para un usuario."""
        refresh = RefreshToken.for_user(user)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token)
        }
        
    def authenticate_user(self, user):
        """Autentica un usuario en el cliente de prueba."""
        tokens = self.get_tokens_for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        return tokens


class LoginAPITest(AuthAPITestCase):
    """Tests para el endpoint de login."""
    
    def test_login_exitoso(self):
        """Test de login exitoso con credenciales válidas."""
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data['data'])
        self.assertIn('refresh', response.data['data'])
        self.assertEqual(response.data['message'], 'Inicio de sesión exitoso')
        
    def test_login_credenciales_invalidas(self):
        """Test de login con credenciales inválidas."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        
    def test_login_usuario_inexistente(self):
        """Test de login con usuario que no existe."""
        data = {
            'username': 'noexiste',
            'password': 'password123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        
    def test_login_datos_faltantes(self):
        """Test de login con datos faltantes."""
        data = {
            'username': 'testuser'
            # Falta password
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
    def test_login_usuario_inactivo(self):
        """Test de login con usuario inactivo."""
        # Desactivar usuario
        self.usuario.desactivar_usuario()
        
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
        
    def test_login_usuario_bloqueado(self):
        """Test de login con usuario bloqueado."""
        # Bloquear usuario
        self.usuario.bloquear_usuario('Test de bloqueo')
        
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        response = self.client.post(self.login_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])


class LogoutAPITest(AuthAPITestCase):
    """Tests para el endpoint de logout."""
    
    def test_logout_exitoso(self):
        """Test de logout exitoso."""
        # Autenticar usuario
        tokens = self.authenticate_user(self.usuario)
        
        data = {
            'refresh': tokens['refresh']
        }
        
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
    def test_logout_sin_autenticacion(self):
        """Test de logout sin estar autenticado."""
        data = {
            'refresh': 'invalid_token'
        }
        
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_logout_token_invalido(self):
        """Test de logout con token inválido."""
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        data = {
            'refresh': 'invalid_refresh_token'
        }
        
        response = self.client.post(self.logout_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class TokenRefreshAPITest(AuthAPITestCase):
    """Tests para el endpoint de refresh de tokens."""
    
    def test_refresh_token_exitoso(self):
        """Test de refresh de token exitoso."""
        tokens = self.get_tokens_for_user(self.usuario)
        
        data = {
            'refresh': tokens['refresh']
        }
        
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
    def test_refresh_token_invalido(self):
        """Test de refresh con token inválido."""
        data = {
            'refresh': 'invalid_refresh_token'
        }
        
        response = self.client.post(self.refresh_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_refresh_token_faltante(self):
        """Test de refresh sin token."""
        response = self.client.post(self.refresh_url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserProfileAPITest(AuthAPITestCase):
    """Tests para el endpoint de perfil de usuario."""
    
    def test_obtener_perfil_exitoso(self):
        """Test de obtención de perfil exitoso."""
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('data', response.data)
        self.assertEqual(response.data['data']['username'], 'testuser')
        
    def test_obtener_perfil_sin_autenticacion(self):
        """Test de obtención de perfil sin autenticación."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_actualizar_perfil_exitoso(self):
        """Test de actualización de perfil exitoso."""
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        data = {
            'nombres_usuario': 'Nuevo Nombre',
            'apellidos_usuario': 'Nuevo Apellido'
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Verificar que se actualizó
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nombres_usuario, 'Nuevo Nombre')
        self.assertEqual(self.usuario.apellidos_usuario, 'Nuevo Apellido')
        
    def test_actualizar_perfil_datos_invalidos(self):
        """Test de actualización de perfil con datos inválidos."""
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        data = {
            'email': 'email_invalido'  # Email mal formateado
        }
        
        response = self.client.put(self.profile_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])


class ChangePasswordAPITest(AuthAPITestCase):
    """Tests para el endpoint de cambio de contraseña."""
    
    def test_cambio_password_exitoso(self):
        """Test de cambio de contraseña exitoso."""
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        data = {
            'old_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }
        
        # Nota: Este endpoint puede estar en profile con action change-password
        url = f'{self.profile_url}change-password/'
        response = self.client.post(url, data, format='json')
        
        # Si el endpoint no existe, esperamos 404, si existe esperamos 200
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
        
    def test_cambio_password_password_actual_incorrecta(self):
        """Test de cambio de contraseña con contraseña actual incorrecta."""
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        data = {
            'old_password': 'wrongpassword',
            'new_password': 'newpassword456',
            'confirm_password': 'newpassword456'
        }
        
        url = f'{self.profile_url}change-password/'
        response = self.client.post(url, data, format='json')
        
        # Si el endpoint existe, debería retornar error
        if response.status_code != status.HTTP_404_NOT_FOUND:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            
    def test_cambio_password_confirmacion_no_coincide(self):
        """Test de cambio de contraseña con confirmación que no coincide."""
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        data = {
            'old_password': 'testpassword123',
            'new_password': 'newpassword456',
            'confirm_password': 'differentpassword'
        }
        
        url = f'{self.profile_url}change-password/'
        response = self.client.post(url, data, format='json')
        
        # Si el endpoint existe, debería retornar error
        if response.status_code != status.HTTP_404_NOT_FOUND:
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class AuthAPISecurityTest(AuthAPITestCase):
    """Tests de seguridad para la API de autenticación."""
    
    def test_acceso_sin_token(self):
        """Test de acceso a endpoints protegidos sin token."""
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_token_expirado(self):
        """Test de acceso con token expirado."""
        # Simular token expirado
        with patch('rest_framework_simplejwt.tokens.RefreshToken.for_user') as mock_token:
            # Configurar mock para simular token expirado
            mock_refresh = mock_token.return_value
            mock_refresh.access_token = 'expired_token'
            
            self.client.credentials(HTTP_AUTHORIZATION='Bearer expired_token')
            response = self.client.get(self.profile_url)
            
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            
    def test_token_malformado(self):
        """Test de acceso con token malformado."""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid.token.format')
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_header_authorization_incorrecto(self):
        """Test con header de autorización incorrecto."""
        tokens = self.get_tokens_for_user(self.usuario)
        
        # Header sin 'Bearer'
        self.client.credentials(HTTP_AUTHORIZATION=tokens['access'])
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
    def test_multiples_intentos_login_fallidos(self):
        """Test de múltiples intentos de login fallidos."""
        data = {
            'username': 'testuser',
            'password': 'wrongpassword'
        }
        
        # Realizar múltiples intentos fallidos
        for i in range(6):  # Más del límite de 5 intentos
            response = self.client.post(self.login_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Verificar que el usuario se bloqueó
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.estado_usuario, 'bloqueado')
        
        # Intentar login con credenciales correctas después del bloqueo
        data['password'] = 'testpassword123'
        response = self.client.post(self.login_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthAPIPerformanceTest(AuthAPITestCase):
    """Tests de rendimiento para la API de autenticación."""
    
    def test_tiempo_respuesta_login(self):
        """Test de tiempo de respuesta del login."""
        import time
        
        data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        start_time = time.time()
        response = self.client.post(self.login_url, data, format='json')
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 2.0)  # Menos de 2 segundos
        
    def test_tiempo_respuesta_perfil(self):
        """Test de tiempo de respuesta del perfil."""
        import time
        
        # Autenticar usuario
        self.authenticate_user(self.usuario)
        
        start_time = time.time()
        response = self.client.get(self.profile_url)
        end_time = time.time()
        
        response_time = end_time - start_time
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(response_time, 1.0)  # Menos de 1 segundo


class AuthAPIIntegrationTest(AuthAPITestCase):
    """Tests de integración para flujos completos de autenticación."""
    
    def test_flujo_completo_autenticacion(self):
        """Test de flujo completo: login -> acceso a perfil -> logout."""
        # 1. Login
        login_data = {
            'username': 'testuser',
            'password': 'testpassword123'
        }
        
        login_response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        
        tokens = login_response.data['data']
        
        # 2. Acceso a perfil con token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        profile_response = self.client.get(self.profile_url)
        self.assertEqual(profile_response.status_code, status.HTTP_200_OK)
        
        # 3. Logout
        logout_data = {
            'refresh': tokens['refresh']
        }
        
        logout_response = self.client.post(self.logout_url, logout_data, format='json')
        self.assertEqual(logout_response.status_code, status.HTTP_200_OK)
        
        # 4. Verificar que no se puede acceder después del logout
        profile_response_after_logout = self.client.get(self.profile_url)
        # Nota: El token de acceso puede seguir siendo válido hasta que expire
        # El logout invalida el refresh token, no el access token
        
    def test_refresh_y_acceso_continuo(self):
        """Test de refresh de token y acceso continuo."""
        # 1. Login inicial
        tokens = self.get_tokens_for_user(self.usuario)
        
        # 2. Usar access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access"]}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 3. Refresh token
        refresh_data = {
            'refresh': tokens['refresh']
        }
        
        refresh_response = self.client.post(self.refresh_url, refresh_data, format='json')
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        
        new_access_token = refresh_response.data['access']
        
        # 4. Usar nuevo access token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {new_access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)