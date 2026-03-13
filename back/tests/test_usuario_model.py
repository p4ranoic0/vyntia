# -*- coding: utf-8 -*-
"""
Tests para el modelo Usuario

Pruebas unitarias para verificar el funcionamiento correcto del modelo Usuario,
incluyendo creación, validación, propiedades y métodos.
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import timedelta
import uuid

Usuario = get_user_model()


class UsuarioModelTest(TestCase):
    """Tests para el modelo Usuario."""
    
    def setUp(self):
        """Configuración inicial para cada test."""
        self.usuario_data = {
            'username': 'test_user',
            'email': 'test@example.com',
            'nombres_usuario': 'Juan Carlos',
            'apellidos_usuario': 'Pérez González',
            'tipo_usuario': 'empleado',
            'nivel_acceso': 'personal'
        }
    
    def test_crear_usuario_basico(self):
        """Test para crear un usuario básico."""
        usuario = Usuario.objects.create_user(
            username=self.usuario_data['username'],
            email=self.usuario_data['email'],
            nombres_usuario=self.usuario_data['nombres_usuario'],
            apellidos_usuario=self.usuario_data['apellidos_usuario'],
            password='password123'
        )
        
        self.assertEqual(usuario.username, 'test_user')
        self.assertEqual(usuario.email, 'test@example.com')
        self.assertEqual(usuario.nombres_usuario, 'Juan Carlos')
        self.assertEqual(usuario.apellidos_usuario, 'Pérez González')
        self.assertTrue(usuario.is_active)
        self.assertFalse(usuario.is_staff)
        self.assertFalse(usuario.is_superuser)
        self.assertEqual(usuario.estado_usuario, 'activo')
        self.assertEqual(usuario.nivel_acceso, 'personal')
    
    def test_crear_superusuario(self):
        """Test para crear un superusuario."""
        superuser = Usuario.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            nombres_usuario='Admin',
            apellidos_usuario='Sistema',
            password='admin123'
        )
        
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)
    
    def test_username_unico(self):
        """Test para verificar que el username sea único."""
        usuario1 = Usuario(
            username='unique_user',
            email='user1@example.com',
            nombres_usuario='Usuario',
            apellidos_usuario='Uno'
        )
        usuario1.set_password('password123')
        usuario1.save()
        
        with self.assertRaises(IntegrityError):
            usuario2 = Usuario(
                username='unique_user',  # Username duplicado
                email='user2@example.com',
                nombres_usuario='Usuario',
                apellidos_usuario='Dos'
            )
            usuario2.set_password('password123')
            usuario2.save()
    
    def test_email_unico(self):
        """Test para verificar que el email sea único."""
        usuario1 = Usuario(
            username='user1',
            email='unique@example.com',
            nombres_usuario='Usuario',
            apellidos_usuario='Uno'
        )
        usuario1.set_password('password123')
        usuario1.save()
        
        with self.assertRaises(IntegrityError):
            usuario2 = Usuario(
                username='user2',
                email='unique@example.com',  # Email duplicado
                nombres_usuario='Usuario',
                apellidos_usuario='Dos'
            )
            usuario2.set_password('password123')
            usuario2.save()
    
    def test_propiedades_usuario(self):
        """Test para verificar las propiedades del usuario."""
        usuario = Usuario(
            username='test_props',
            email='props@example.com',
            nombres_usuario='Test',
            apellidos_usuario='Properties',
            tipo_usuario='administrador'
        )
        usuario.set_password('password123')
        usuario.save()
        
        # Test nombre completo
        self.assertEqual(usuario.nombre_completo, 'Test Properties')
        
        # Test propiedades de tipo
        self.assertTrue(usuario.es_administrador)
        self.assertFalse(usuario.es_rrhh)
        self.assertFalse(usuario.es_jefe)
        
        # Test estado activo
        self.assertTrue(usuario.es_activo)
    
    def test_tipos_usuario_validos(self):
        """Test para verificar los tipos de usuario válidos."""
        tipos_validos = ['administrador', 'rrhh', 'jefe', 'empleado', 'consulta', 'invitado']
        
        for tipo in tipos_validos:
            usuario = Usuario(
                username=f'user_{tipo}',
                email=f'{tipo}@example.com',
                nombres_usuario='Test',
                apellidos_usuario='User',
                tipo_usuario=tipo
            )
            usuario.set_password('password123')
            usuario.save()
            
            self.assertEqual(usuario.tipo_usuario, tipo)
    
    def test_niveles_acceso_validos(self):
        """Test para verificar los niveles de acceso válidos."""
        niveles_validos = ['total', 'departamental', 'personal', 'limitado', 'lectura']
        
        for nivel in niveles_validos:
            usuario = Usuario(
                username=f'user_{nivel}',
                email=f'{nivel}@example.com',
                nombres_usuario='Test',
                apellidos_usuario='User',
                nivel_acceso=nivel
            )
            usuario.set_password('password123')
            usuario.save()
            
            self.assertEqual(usuario.nivel_acceso, nivel)
    
    def test_estados_usuario_validos(self):
        """Test para verificar los estados de usuario válidos."""
        estados_validos = ['activo', 'inactivo', 'suspendido', 'bloqueado', 'pendiente']
        
        for estado in estados_validos:
            usuario = Usuario(
                username=f'user_{estado}',
                email=f'{estado}@example.com',
                nombres_usuario='Test',
                apellidos_usuario='User',
                estado_usuario=estado
            )
            usuario.set_password('password123')
            usuario.save()
            
            self.assertEqual(usuario.estado_usuario, estado)
    
    def test_intentos_fallidos(self):
        """Test para el manejo de intentos fallidos de login."""
        usuario = Usuario.objects.create_user(
            username='test_fails',
            email='fails@example.com',
            nombres_usuario='Test',
            apellidos_usuario='Fails',
            password='password123'
        )
        
        # Inicialmente sin intentos fallidos
        self.assertEqual(usuario.intentos_fallidos, 0)
        self.assertFalse(usuario.esta_bloqueado)
        
        # Registrar intento fallido
        usuario.registrar_intento_fallido()
        self.assertEqual(usuario.intentos_fallidos, 1)
        
        # Resetear intentos
        usuario.resetear_intentos_fallidos()
        self.assertEqual(usuario.intentos_fallidos, 0)
    
    def test_token_recuperacion(self):
        """Test para el token de recuperación de contraseña."""
        usuario = Usuario.objects.create_user(
            username='test_token',
            email='token@example.com',
            nombres_usuario='Test',
            apellidos_usuario='Token',
            password='password123'
        )
        
        # Generar token
        token = usuario.generar_token_recuperacion()
        self.assertIsNotNone(token)
        self.assertIsNotNone(usuario.token_recuperacion)
        self.assertIsNotNone(usuario.fecha_expiracion_token)
        
        # Validar token
        self.assertTrue(usuario.validar_token_recuperacion(token))
        self.assertFalse(usuario.validar_token_recuperacion('token_invalido'))
    
    def test_cambio_password(self):
        """Test para el cambio de contraseña."""
        usuario = Usuario.objects.create_user(
            username='test_password',
            email='password@example.com',
            nombres_usuario='Test',
            apellidos_usuario='Password',
            password='password123'
        )
        
        # Cambiar contraseña
        usuario.cambiar_password('nueva_password123')
        
        # Verificar que la contraseña cambió
        self.assertTrue(usuario.check_password('nueva_password123'))
        self.assertFalse(usuario.check_password('password123'))
        self.assertIsNotNone(usuario.fecha_ultimo_cambio_password)
    
    def test_activar_desactivar_usuario(self):
        """Test para activar y desactivar usuarios."""
        usuario = Usuario.objects.create_user(
            username='test_activate',
            email='activate@example.com',
            nombres_usuario='Test',
            apellidos_usuario='Activate',
            password='password123'
        )
        
        # Usuario activo por defecto
        self.assertTrue(usuario.is_active)
        self.assertEqual(usuario.estado_usuario, 'activo')
        
        # Desactivar usuario
        usuario.desactivar_usuario('Test de desactivación')
        self.assertFalse(usuario.is_active)
        self.assertEqual(usuario.estado_usuario, 'inactivo')
        
        # Activar usuario
        usuario.activar_usuario()
        self.assertTrue(usuario.is_active)
        self.assertEqual(usuario.estado_usuario, 'activo')
    
    def test_suspender_bloquear_usuario(self):
        """Test para suspender y bloquear usuarios."""
        usuario = Usuario.objects.create_user(
            username='test_suspend',
            email='suspend@example.com',
            nombres_usuario='Test',
            apellidos_usuario='Suspend',
            password='password123'
        )
        
        # Suspender usuario
        usuario.suspender_usuario('Test de suspensión')
        self.assertEqual(usuario.estado_usuario, 'suspendido')
        
        # Bloquear usuario
        usuario.bloquear_usuario('Test de bloqueo')
        self.assertEqual(usuario.estado_usuario, 'bloqueado')
        self.assertIsNotNone(usuario.fecha_bloqueo)
    
    def test_registrar_acceso(self):
        """Test para registrar acceso del usuario."""
        usuario = Usuario.objects.create_user(
            username='test_access',
            email='access@example.com',
            nombres_usuario='Test',
            apellidos_usuario='Access',
            password='password123'
        )
        
        # Registrar acceso
        ip_test = '192.168.1.1'
        user_agent_test = 'Mozilla/5.0 Test Browser'
        
        usuario.registrar_acceso(ip_test, user_agent_test)
        
        self.assertEqual(usuario.ip_ultimo_acceso, ip_test)
        self.assertEqual(usuario.user_agent_ultimo_acceso, user_agent_test)
        self.assertIsNotNone(usuario.last_login)
    
    def test_metodos_clase(self):
        """Test para los métodos de clase."""
        # Crear usuarios de prueba
        Usuario.objects.create_user(
            username='activo1',
            email='activo1@example.com',
            nombres_usuario='Activo',
            apellidos_usuario='Uno',
            tipo_usuario='empleado',
            password='password123'
        )
        
        Usuario.objects.create_user(
            username='admin1',
            email='admin1@example.com',
            nombres_usuario='Admin',
            apellidos_usuario='Uno',
            tipo_usuario='administrador',
            password='password123'
        )
        
        # Test usuarios activos
        usuarios_activos = Usuario.usuarios_activos()
        self.assertGreaterEqual(usuarios_activos.count(), 2)
        
        # Test usuarios por tipo
        empleados = Usuario.usuarios_por_tipo('empleado')
        self.assertGreaterEqual(empleados.count(), 1)
        
        administradores = Usuario.usuarios_por_tipo('administrador')
        self.assertGreaterEqual(administradores.count(), 1)
    
    def test_str_representation(self):
        """Test para la representación string del usuario."""
        usuario = Usuario.objects.create_user(
            username='test_str',
            email='str@example.com',
            nombres_usuario='Test',
            apellidos_usuario='String',
            password='password123'
        )
        
        expected_str = 'test_str - Test String'
        self.assertEqual(str(usuario), expected_str)
    
    def test_meta_configuracion(self):
        """Test para verificar la configuración Meta del modelo."""
        # Verificar nombre de tabla
        self.assertEqual(Usuario._meta.db_table, 'usuarios')
        
        # Verificar campos requeridos
        self.assertEqual(Usuario.USERNAME_FIELD, 'username')
        self.assertEqual(Usuario.EMAIL_FIELD, 'email')
        self.assertIn('email', Usuario.REQUIRED_FIELDS)
        self.assertIn('nombres_usuario', Usuario.REQUIRED_FIELDS)
        self.assertIn('apellidos_usuario', Usuario.REQUIRED_FIELDS)
        
        # Verificar índices
        index_fields = [index.fields for index in Usuario._meta.indexes]
        expected_indexes = [
            ['username'], ['email'], ['empleado'], ['tipo_usuario'],
            ['estado_usuario'], ['nivel_acceso'], ['is_active'],
            ['last_login'], ['date_joined'], ['intentos_fallidos'], ['fecha_bloqueo']
        ]
        
        for expected_index in expected_indexes:
            self.assertIn(expected_index, index_fields)