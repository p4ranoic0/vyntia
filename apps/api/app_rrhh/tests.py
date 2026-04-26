from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from datetime import datetime, timedelta
import json

from .models import (
    Empleado, DatosFamiliares, DatosAcademicos,
    DatosLaborales,
)
from apps.organization.models import Area, HistorialUbicaciones
from apps.identity.models import Usuario, Rol, Permiso


class BaseAPITestCase(APITestCase):
    """Base test case with common setup for API tests."""
    
    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        
        # Create test area
        self.area = Area.objects.create(
            nombre_organo="Gerencia de Tecnología",
            nombre_unidad_organica="Desarrollo de Software",
            siglas_area="GTS",
            descripcion_area="Área de desarrollo de software",
            estado_area='activa'
        )
        
        # Create test employee
        self.empleado = Empleado.objects.create(
            nombres_empleado="Juan Carlos",
            apellido_paterno="García",
            apellido_materno="López",
            numero_documento="12345678",
            fecha_nacimiento=datetime(1990, 5, 15).date(),
            genero_empleado="masculino",
            estado_civil="soltero",
            direccion_domicilio="Av. Principal 123",
            distrito_domicilio="Lima",
            telefono_celular="987654321",
            correo_personal="juan.garcia@email.com",
            es_padre_familia=False,
            entidad_bancaria="BCP",
            numero_cuenta_bancaria="1234567890",
            estado_empleado='activo'
        )
        
        # Create test user
        self.usuario = Usuario.objects.create_user(
            nombre_usuario="testuser",
            correo_institucional="test@empresa.com",
            password="testpass123",
            empleado=self.empleado,
            estado_usuario='activo'
        )
        
        # Create admin employee first
        self.admin_empleado = Empleado.objects.create(
            nombres_empleado="Admin",
            apellido_paterno="Sistema",
            apellido_materno="Test",
            numero_documento="00000001",
            fecha_nacimiento="1980-01-01",
            genero_empleado="masculino",
            estado_civil="soltero",
            direccion_domicilio="Dirección Admin",
            distrito_domicilio="Lima",
            provincia_domicilio="Lima",
            departamento_domicilio="Lima",
            telefono_celular="999000001",
            correo_personal="admin@test.com",
            entidad_bancaria="BCP",
            numero_cuenta_bancaria="1234567890123456",
            numero_cci="00212345678901234567",
            sistema_pensiones="ONP",
            estado_empleado="activo"
        )
        
        # Create admin user
        self.admin_user = Usuario.objects.create(
            nombre_usuario="admin",
            correo_institucional="admin@empresa.com",
            empleado=self.admin_empleado,
            estado_usuario="activo"
        )
        self.admin_user.set_password("admin123")
        self.admin_user.save()
        
        # Create roles
        self.admin_rol, _ = Rol.objects.get_or_create(
            nombre_rol="Administrador",
            defaults={
                'descripcion_rol': 'Acceso completo al sistema',
                'estado_rol': 'activo'
            }
        )
        
        self.rrhh_rol, _ = Rol.objects.get_or_create(
            nombre_rol="RRHH",
            defaults={
                'descripcion_rol': 'Gestión de recursos humanos',
                'estado_rol': 'activo'
            }
        )
        
        # Assign admin role to admin user
        from apps.identity.models import UsuarioRoles
        UsuarioRoles.objects.get_or_create(
            usuario=self.admin_user,
            rol=self.admin_rol,
            defaults={
                'fecha_asignacion': timezone.now().date(),
                'estado_asignacion': 'activo'
            }
        )
    
    def authenticate(self, user=None):
        """Authenticate user for API requests."""
        if user is None:
            user = self.usuario
        self.client.force_authenticate(user=user)
    
    def authenticate_admin(self):
        """Authenticate admin user for API requests."""
        self.client.force_authenticate(user=self.admin_user)


class AuthenticationAPITestCase(BaseAPITestCase):
    """Test cases for authentication endpoints."""
    
    def test_login_success(self):
        """Test successful login."""
        url = reverse('auth:login')
        data = {
            'nombre_usuario': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials."""
        url = reverse('auth:login')
        data = {
            'nombre_usuario': 'testuser',
            'password': 'wrongpassword'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_refresh_token(self):
        """Test token refresh."""
        # First login to get refresh token
        login_url = reverse('auth:login')
        login_data = {
            'nombre_usuario': 'testuser',
            'password': 'testpass123'
        }
        login_response = self.client.post(login_url, login_data, format='json')
        refresh_token = login_response.data['refresh']
        
        # Test refresh
        refresh_url = reverse('auth:token_refresh')
        refresh_data = {'refresh': refresh_token}
        response = self.client.post(refresh_url, refresh_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class AreaAPITestCase(BaseAPITestCase):
    """Test cases for Area endpoints."""
    
    def test_list_areas(self):
        """Test listing areas."""
        self.authenticate()
        url = reverse('api_v1:rrhh:area-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_area(self):
        """Test creating a new area."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:area-list')
        data = {
            'nombre_organo': 'Recursos Humanos',
            'nombre_unidad_organica': 'Gestión de Personal',
            'siglas_area': 'RH',
            'descripcion_area': 'Área de recursos humanos',
            'estado_area': 'activa'
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Area.objects.count(), 2)
    
    def test_get_area_detail(self):
        """Test getting area details."""
        self.authenticate()
        url = reverse('api_v1:rrhh:area-detail', kwargs={'pk': self.area.area_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_organo'], self.area.nombre_organo)
    
    def test_update_area(self):
        """Test updating an area."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:area-detail', kwargs={'pk': self.area.area_id})
        data = {
            'nombre_organo': 'Gerencia de TI Actualizada',
            'nombre_unidad_organica': self.area.nombre_unidad_organica,
            'siglas_area': self.area.siglas_area,
            'descripcion_area': self.area.descripcion_area,
            'estado_area': self.area.estado_area
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.area.refresh_from_db()
        self.assertEqual(self.area.nombre_organo, 'Gerencia de TI Actualizada')
    
    def test_delete_area(self):
        """Test deleting an area."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:area-detail', kwargs={'pk': self.area.area_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.area.refresh_from_db()
        self.assertFalse(self.area.estado_area)


class EmpleadoAPITestCase(BaseAPITestCase):
    """Test cases for Empleado endpoints."""
    
    def test_list_empleados(self):
        """Test listing employees."""
        self.authenticate()
        url = reverse('api_v1:rrhh:empleado-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_empleado(self):
        """Test creating a new employee."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:empleado-list')
        data = {
            'nombres_empleado': 'María Elena',
            'apellido_paterno': 'Rodríguez',
            'apellido_materno': 'Vásquez',
            'numero_documento': '87654321',
            'fecha_nacimiento': '1985-03-20',
            'genero_empleado': 'F',
            'estado_civil': 'C',
            'direccion_domicilio': 'Jr. Los Olivos 456',
            'distrito_domicilio': 'San Isidro',
            'telefono_celular': '912345678',
            'correo_personal': 'maria.rodriguez@email.com',
            'es_padre_familia': True,
            'entidad_bancaria': 'BBVA',
            'numero_cuenta_bancaria': '0987654321',
            'estado_empleado': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Empleado.objects.count(), 2)
    
    def test_get_empleado_detail(self):
        """Test getting employee details."""
        self.authenticate()
        url = reverse('api_v1:rrhh:empleado-detail', kwargs={'pk': self.empleado.empleado_id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombres_empleado'], self.empleado.nombres_empleado)
    
    def test_update_empleado(self):
        """Test updating an employee."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:empleado-detail', kwargs={'pk': self.empleado.empleado_id})
        data = {
            'nombres_empleado': 'Juan Carlos Actualizado',
            'apellido_paterno': self.empleado.apellido_paterno,
            'apellido_materno': self.empleado.apellido_materno,
            'numero_documento': self.empleado.numero_documento,
            'fecha_nacimiento': self.empleado.fecha_nacimiento,
            'genero_empleado': self.empleado.genero_empleado,
            'estado_civil': self.empleado.estado_civil,
            'direccion_domicilio': self.empleado.direccion_domicilio,
            'distrito_domicilio': self.empleado.distrito_domicilio,
            'telefono_celular': self.empleado.telefono_celular,
            'correo_personal': self.empleado.correo_personal,
            'es_padre_familia': self.empleado.es_padre_familia,
            'entidad_bancaria': self.empleado.entidad_bancaria,
            'numero_cuenta_bancaria': self.empleado.numero_cuenta_bancaria,
            'estado_empleado': self.empleado.estado_empleado
        }
        response = self.client.put(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.empleado.refresh_from_db()
        self.assertEqual(self.empleado.nombres_empleado, 'Juan Carlos Actualizado')


class DatosFamiliaresAPITestCase(BaseAPITestCase):
    """Test cases for DatosFamiliares endpoints."""
    
    def setUp(self):
        super().setUp()
        self.datos_familiares = DatosFamiliares.objects.create(
            empleado=self.empleado,
            parentesco='HIJO',
            nombres_familiar='Pedro',
            apellido_paterno_familiar='García',
            apellido_materno_familiar='López',
            fecha_nacimiento_familiar=datetime(2010, 8, 15).date(),
            genero_familiar='M',
            numero_documento_familiar='12345679',
            tipo_documento_familiar='DNI',
            es_beneficiario_seguro=True,
            es_dependiente_economico=True,
            estado_familiar=True
        )
    
    def test_list_datos_familiares(self):
        """Test listing family data."""
        self.authenticate()
        url = reverse('api_v1:rrhh:datos-familiares-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_datos_familiares(self):
        """Test creating family data."""
        self.authenticate()
        url = reverse('api_v1:rrhh:datos-familiares-list')
        data = {
            'empleado': self.empleado.empleado_id,
            'parentesco': 'ESPOSA',
            'nombres_familiar': 'Ana María',
            'apellido_paterno_familiar': 'Pérez',
            'apellido_materno_familiar': 'Silva',
            'fecha_nacimiento_familiar': '1992-12-10',
            'genero_familiar': 'F',
            'numero_documento_familiar': '98765432',
            'tipo_documento_familiar': 'DNI',
            'es_beneficiario_seguro': True,
            'es_dependiente_economico': False,
            'estado_familiar': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DatosFamiliares.objects.count(), 2)


class DatosAcademicosAPITestCase(BaseAPITestCase):
    """Test cases for DatosAcademicos endpoints."""
    
    def setUp(self):
        super().setUp()
        self.datos_academicos = DatosAcademicos.objects.create(
            empleado=self.empleado,
            tipo_formacion='UNIVERSITARIA',
            nombre_institucion='Universidad Nacional',
            carrera_especialidad='Ingeniería de Sistemas',
            fecha_inicio_estudios=datetime(2008, 3, 1).date(),
            fecha_termino_estudios=datetime(2013, 12, 15).date(),
            duracion_horas=4000,
            titulo_obtenido='Ingeniero de Sistemas',
            estado_estudios='COMPLETADO',
            nivel_educativo='SUPERIOR',
            duracion_creditos=200
        )
    
    def test_list_datos_academicos(self):
        """Test listing academic data."""
        self.authenticate()
        url = reverse('api_v1:rrhh:datos-academicos-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_datos_academicos(self):
        """Test creating academic data."""
        self.authenticate()
        url = reverse('api_v1:rrhh:datos-academicos-list')
        data = {
            'empleado': self.empleado.empleado_id,
            'tipo_formacion': 'MAESTRIA',
            'nombre_institucion': 'Universidad Privada',
            'carrera_especialidad': 'MBA',
            'fecha_inicio_estudios': '2014-03-01',
            'fecha_termino_estudios': '2016-12-15',
            'duracion_horas': 1500,
            'titulo_obtenido': 'Master en Administración',
            'estado_estudios': 'COMPLETADO',
            'nivel_educativo': 'POSTGRADO',
            'duracion_creditos': 60
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DatosAcademicos.objects.count(), 2)


class DatosLaboralesAPITestCase(BaseAPITestCase):
    """Test cases for DatosLaborales endpoints."""
    
    def setUp(self):
        super().setUp()
        self.datos_laborales = DatosLaborales.objects.create(
            empleado=self.empleado,
            area=self.area,
            fecha_ingreso=datetime(2020, 1, 15).date(),
            puesto_trabajo='Desarrollador Senior',
            regimen_laboral='CAS',
            condicion_laboral='NOMBRADO',
            correo_institucional='juan.garcia@empresa.com',
            remuneracion_mensual=5000.00,
            estado_laboral=True
        )
    
    def test_list_datos_laborales(self):
        """Test listing labor data."""
        self.authenticate()
        url = reverse('api_v1:rrhh:datos-laborales-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
    
    def test_create_datos_laborales(self):
        """Test creating labor data."""
        self.authenticate_admin()
        
        # Create another employee for this test
        empleado2 = Empleado.objects.create(
            nombres_empleado="María",
            apellido_paterno="López",
            apellido_materno="Vega",
            numero_documento="11223344",
            fecha_nacimiento=datetime(1988, 7, 20).date(),
            genero_empleado="F",
            estado_empleado=True
        )
        
        url = reverse('api_v1:rrhh:datos-laborales-list')
        data = {
            'empleado': empleado2.empleado_id,
            'area': self.area.area_id,
            'fecha_ingreso': '2021-06-01',
            'puesto_trabajo': 'Analista de Sistemas',
            'regimen_laboral': 'CAP',
            'condicion_laboral': 'CONTRATADO',
            'correo_institucional': 'maria.lopez@empresa.com',
            'remuneracion_mensual': 4000.00,
            'estado_laboral': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(DatosLaborales.objects.count(), 2)


class UsuarioAPITestCase(BaseAPITestCase):
    """Test cases for Usuario endpoints."""
    
    def test_list_usuarios(self):
        """Test listing users."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:usuario-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 1)
    
    def test_get_usuario_detail(self):
        """Test getting user details."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:usuario-detail', kwargs={'pk': self.usuario.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_usuario'], self.usuario.nombre_usuario)
    
    def test_user_profile(self):
        """Test getting current user profile."""
        self.authenticate()
        url = reverse('api_v1:rrhh:usuario-profile')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['nombre_usuario'], self.usuario.nombre_usuario)


class APIValidationTestCase(BaseAPITestCase):
    """Test cases for API validation."""
    
    def test_empleado_duplicate_documento(self):
        """Test validation for duplicate document number."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:empleado-list')
        data = {
            'nombres_empleado': 'Test',
            'apellido_paterno': 'Test',
            'apellido_materno': 'Test',
            'numero_documento': self.empleado.numero_documento,  # Duplicate
            'fecha_nacimiento': '1990-01-01',
            'genero_empleado': 'M',
            'estado_empleado': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_area_duplicate_siglas(self):
        """Test validation for duplicate area siglas."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:area-list')
        data = {
            'nombre_organo': 'Test',
            'nombre_unidad_organica': 'Test',
            'siglas_area': self.area.siglas_area,  # Duplicate
            'descripcion_area': 'Test',
            'estado_area': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_invalid_email_format(self):
        """Test validation for invalid email format."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:empleado-list')
        data = {
            'nombres_empleado': 'Test',
            'apellido_paterno': 'Test',
            'apellido_materno': 'Test',
            'numero_documento': '99999999',
            'fecha_nacimiento': '1990-01-01',
            'genero_empleado': 'M',
            'correo_personal': 'invalid-email',  # Invalid format
            'estado_empleado': True
        }
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class APIPermissionTestCase(BaseAPITestCase):
    """Test cases for API permissions."""
    
    def test_unauthenticated_access(self):
        """Test that unauthenticated users cannot access protected endpoints."""
        url = reverse('api_v1:rrhh:empleado-list')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_regular_user_cannot_delete(self):
        """Test that regular users cannot delete resources."""
        self.authenticate()  # Regular user
        url = reverse('api_v1:rrhh:area-detail', kwargs={'pk': self.area.area_id})
        response = self.client.delete(url)
        
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED])
    
    def test_admin_can_delete(self):
        """Test that admin users can delete resources."""
        self.authenticate_admin()
        url = reverse('api_v1:rrhh:area-detail', kwargs={'pk': self.area.area_id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class APISearchFilterTestCase(BaseAPITestCase):
    """Test cases for API search and filtering."""
    
    def setUp(self):
        super().setUp()
        # Create additional test data
        self.empleado2 = Empleado.objects.create(
            nombres_empleado="Ana María",
            apellido_paterno="Rodríguez",
            apellido_materno="Silva",
            numero_documento="87654321",
            fecha_nacimiento=datetime(1985, 3, 20).date(),
            genero_empleado="F",
            estado_empleado=True
        )
    
    def test_search_empleados_by_name(self):
        """Test searching employees by name."""
        self.authenticate()
        url = reverse('api_v1:rrhh:empleado-list')
        response = self.client.get(url, {'search': 'Juan'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['nombres_empleado'], 'Juan Carlos')
    
    def test_filter_empleados_by_gender(self):
        """Test filtering employees by gender."""
        self.authenticate()
        url = reverse('api_v1:rrhh:empleado-list')
        response = self.client.get(url, {'genero_empleado': 'F'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['genero_empleado'], 'F')
    
    def test_ordering_empleados(self):
        """Test ordering employees."""
        self.authenticate()
        url = reverse('api_v1:rrhh:empleado-list')
        response = self.client.get(url, {'ordering': 'apellido_paterno'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)
        # García should come before Rodríguez
        self.assertEqual(response.data['results'][0]['apellido_paterno'], 'García')
        self.assertEqual(response.data['results'][1]['apellido_paterno'], 'Rodríguez')
