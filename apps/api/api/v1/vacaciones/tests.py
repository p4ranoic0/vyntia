"""Tests para las APIs de vacaciones."""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta

from app_rrhh.models import (
    ConfiguracionVacaciones, PeriodoVacacional,
    SolicitudVacaciones, GoceVacaciones
)
from apps.employees.models import Empleado
from apps.organization.models import Area
from .validators import (
    VacacionesAPIValidator, VacacionesPermissionValidator,
    VacacionesStateValidator
)
from .serializers import (
    ConfiguracionVacacionesSerializer, PeriodoVacacionalSerializer,
    SolicitudVacacionesSerializer, GoceVacacionesSerializer
)

User = get_user_model()


class VacacionesAPIValidatorTest(TestCase):
    """Tests para VacacionesAPIValidator."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear área
        self.area = Area.objects.create(
            nombre='Tecnología',
            descripcion='Área de tecnología'
        )
        
        # Crear usuario
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            usuario=self.user,
            numero_documento='12345678',
            nombres='Juan',
            apellidos='Pérez',
            area=self.area,
            fecha_ingreso=date.today() - timedelta(days=365)
        )
        
        # Crear configuración
        self.configuracion = ConfiguracionVacaciones.objects.create(
            tipo_configuracion='general',
            dias_por_ano=30,
            creado_por=self.user
        )
        
        # Crear período vacacional
        self.periodo = PeriodoVacacional.objects.create(
            empleado=self.empleado,
            ano_periodo=2024,
            fecha_inicio_periodo=date(2024, 1, 1),
            fecha_fin_periodo=date(2024, 12, 31),
            fecha_vencimiento=date(2025, 12, 31),
            dias_correspondientes=30,
            configuracion=self.configuracion
        )
    
    def test_validate_solicitud_data_valid(self):
        """Test validación exitosa de datos de solicitud."""
        data = {
            'empleado': self.empleado,
            'periodo_vacacional': self.periodo,
            'tipo_solicitud': 'completa',
            'fecha_inicio_solicitud': date.today() + timedelta(days=10),
            'fecha_fin_solicitud': date.today() + timedelta(days=15),
            'dias_solicitados': 5,
            'incluye_fines_semana': False
        }
        
        # No debería lanzar excepción
        try:
            VacacionesAPIValidator.validate_solicitud_data(data)
        except Exception as e:
            self.fail(f"validate_solicitud_data lanzó excepción inesperada: {e}")
    
    def test_validate_solicitud_data_invalid_dates(self):
        """Test validación con fechas inválidas."""
        data = {
            'empleado': self.empleado,
            'periodo_vacacional': self.periodo,
            'fecha_inicio_solicitud': date.today() + timedelta(days=15),
            'fecha_fin_solicitud': date.today() + timedelta(days=10),  # Fecha fin anterior
            'dias_solicitados': 5
        }
        
        with self.assertRaises(Exception):
            VacacionesAPIValidator.validate_solicitud_data(data)
    
    def test_validate_goce_data_valid(self):
        """Test validación exitosa de datos de goce."""
        # Crear solicitud
        solicitud = SolicitudVacaciones.objects.create(
            empleado=self.empleado,
            periodo_vacacional=self.periodo,
            tipo_solicitud='completa',
            fecha_inicio_solicitud=date.today() + timedelta(days=10),
            fecha_fin_solicitud=date.today() + timedelta(days=15),
            dias_solicitados=5,
            estado_solicitud='aprobada',
            creado_por=self.user
        )
        
        data = {
            'solicitud_vacaciones': solicitud,
            'fecha_inicio_goce': date.today() + timedelta(days=10),
            'fecha_fin_goce': date.today() + timedelta(days=15),
            'dias_gozados': 5
        }
        
        # No debería lanzar excepción
        try:
            VacacionesAPIValidator.validate_goce_data(data)
        except Exception as e:
            self.fail(f"validate_goce_data lanzó excepción inesperada: {e}")
    
    def test_validate_configuracion_data_valid(self):
        """Test validación exitosa de datos de configuración."""
        data = {
            'parametro': 'dias_por_ano',
            'valor': '30',
            'tipo_dato': 'entero'
        }
        
        # No debería lanzar excepción
        try:
            VacacionesAPIValidator.validate_configuracion_data(data)
        except Exception as e:
            self.fail(f"validate_configuracion_data lanzó excepción inesperada: {e}")


class VacacionesPermissionValidatorTest(TestCase):
    """Tests para VacacionesPermissionValidator."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear área
        self.area = Area.objects.create(
            nombre='Tecnología',
            descripcion='Área de tecnología'
        )
        
        # Crear usuarios
        self.empleado_user = User.objects.create_user(
            username='empleado',
            email='empleado@example.com',
            password='testpass123'
        )
        
        self.jefe_user = User.objects.create_user(
            username='jefe',
            email='jefe@example.com',
            password='testpass123'
        )
        
        self.rrhh_user = User.objects.create_user(
            username='rrhh',
            email='rrhh@example.com',
            password='testpass123'
        )
        
        # Crear empleados
        self.empleado = Empleado.objects.create(
            usuario=self.empleado_user,
            numero_documento='12345678',
            nombres='Juan',
            apellidos='Pérez',
            area=self.area,
            fecha_ingreso=date.today() - timedelta(days=365)
        )
        
        self.jefe = Empleado.objects.create(
            usuario=self.jefe_user,
            numero_documento='87654321',
            nombres='María',
            apellidos='González',
            area=self.area,
            fecha_ingreso=date.today() - timedelta(days=1000)
        )
        
        # Establecer relación jefe-empleado
        self.empleado.jefe_directo = self.jefe
        self.empleado.save()
        
        # Crear grupo RRHH y asignar usuario
        from django.contrib.auth.models import Group
        rrhh_group, created = Group.objects.get_or_create(name='RRHH')
        self.rrhh_user.groups.add(rrhh_group)
        
        # Crear solicitud
        self.configuracion = ConfiguracionVacaciones.objects.create(
            tipo_configuracion='general',
            dias_por_ano=30,
            creado_por=self.empleado_user
        )
        
        self.periodo = PeriodoVacacional.objects.create(
            empleado=self.empleado,
            ano_periodo=2024,
            fecha_inicio_periodo=date(2024, 1, 1),
            fecha_fin_periodo=date(2024, 12, 31),
            fecha_vencimiento=date(2025, 12, 31),
            dias_correspondientes=30,
            configuracion=self.configuracion
        )
        
        self.solicitud = SolicitudVacaciones.objects.create(
            empleado=self.empleado,
            periodo_vacacional=self.periodo,
            tipo_solicitud='completa',
            fecha_inicio_solicitud=date.today() + timedelta(days=10),
            fecha_fin_solicitud=date.today() + timedelta(days=15),
            dias_solicitados=5,
            estado_solicitud='enviada',
            creado_por=self.empleado_user
        )
    
    def test_can_approve_solicitud_jefe(self):
        """Test que el jefe puede aprobar solicitudes de sus subordinados."""
        can_approve = VacacionesPermissionValidator.can_approve_solicitud(
            self.jefe_user, self.solicitud
        )
        self.assertTrue(can_approve)
    
    def test_can_approve_solicitud_rrhh(self):
        """Test que RRHH puede aprobar solicitudes."""
        can_approve = VacacionesPermissionValidator.can_approve_solicitud(
            self.rrhh_user, self.solicitud
        )
        self.assertTrue(can_approve)
    
    def test_cannot_approve_solicitud_empleado(self):
        """Test que el empleado no puede aprobar su propia solicitud."""
        can_approve = VacacionesPermissionValidator.can_approve_solicitud(
            self.empleado_user, self.solicitud
        )
        self.assertFalse(can_approve)
    
    def test_can_cancel_solicitud_empleado(self):
        """Test que el empleado puede cancelar su propia solicitud."""
        can_cancel = VacacionesPermissionValidator.can_cancel_solicitud(
            self.empleado_user, self.solicitud
        )
        self.assertTrue(can_cancel)
    
    def test_can_modify_configuracion_rrhh(self):
        """Test que RRHH puede modificar configuraciones."""
        can_modify = VacacionesPermissionValidator.can_modify_configuracion(
            self.rrhh_user
        )
        self.assertTrue(can_modify)
    
    def test_cannot_modify_configuracion_empleado(self):
        """Test que el empleado no puede modificar configuraciones."""
        can_modify = VacacionesPermissionValidator.can_modify_configuracion(
            self.empleado_user
        )
        self.assertFalse(can_modify)


class VacacionesStateValidatorTest(TestCase):
    """Tests para VacacionesStateValidator."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear datos básicos
        self.area = Area.objects.create(
            nombre='Tecnología',
            descripcion='Área de tecnología'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.empleado = Empleado.objects.create(
            usuario=self.user,
            numero_documento='12345678',
            nombres='Juan',
            apellidos='Pérez',
            area=self.area,
            fecha_ingreso=date.today() - timedelta(days=365)
        )
        
        self.configuracion = ConfiguracionVacaciones.objects.create(
            tipo_configuracion='general',
            dias_por_ano=30,
            creado_por=self.user
        )
        
        self.periodo = PeriodoVacacional.objects.create(
            empleado=self.empleado,
            ano_periodo=2024,
            fecha_inicio_periodo=date(2024, 1, 1),
            fecha_fin_periodo=date(2024, 12, 31),
            fecha_vencimiento=date(2025, 12, 31),
            dias_correspondientes=30,
            configuracion=self.configuracion
        )
        
        self.solicitud = SolicitudVacaciones.objects.create(
            empleado=self.empleado,
            periodo_vacacional=self.periodo,
            tipo_solicitud='completa',
            fecha_inicio_solicitud=date.today() + timedelta(days=10),
            fecha_fin_solicitud=date.today() + timedelta(days=15),
            dias_solicitados=5,
            estado_solicitud='enviada',
            creado_por=self.user
        )
    
    def test_valid_state_transition(self):
        """Test transición de estado válida."""
        # Crear usuario RRHH
        from django.contrib.auth.models import Group
        rrhh_group, created = Group.objects.get_or_create(name='RRHH')
        self.user.groups.add(rrhh_group)
        
        # No debería lanzar excepción
        try:
            VacacionesStateValidator.validate_solicitud_state_change(
                self.solicitud, 'aprobada', self.user
            )
        except Exception as e:
            self.fail(f"validate_solicitud_state_change lanzó excepción inesperada: {e}")
    
    def test_invalid_state_transition(self):
        """Test transición de estado inválida."""
        with self.assertRaises(Exception):
            VacacionesStateValidator.validate_solicitud_state_change(
                self.solicitud, 'finalizada', self.user  # Estado inválido
            )


class VacacionesSerializerTest(TestCase):
    """Tests para los serializers de vacaciones."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        self.area = Area.objects.create(
            nombre='Tecnología',
            descripcion='Área de tecnología'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.empleado = Empleado.objects.create(
            usuario=self.user,
            numero_documento='12345678',
            nombres='Juan',
            apellidos='Pérez',
            area=self.area,
            fecha_ingreso=date.today() - timedelta(days=365)
        )
    
    def test_configuracion_serializer_valid_data(self):
        """Test serializer de configuración con datos válidos."""
        data = {
            'tipo_configuracion': 'general',
            'dias_por_ano': 30,
            'dias_minimos_solicitud': 1,
            'dias_maximos_solicitud': 30,
            'permite_fraccionamiento': True,
            'min_dias_por_fraccion': 1,
            'creado_por': self.user.id
        }
        
        serializer = ConfiguracionVacacionesSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
    
    def test_configuracion_serializer_invalid_data(self):
        """Test serializer de configuración con datos inválidos."""
        data = {
            'tipo_configuracion': 'general',
            'dias_por_ano': 0,  # Inválido
            'dias_minimos_solicitud': 10,
            'dias_maximos_solicitud': 5,  # Menor que mínimo
            'creado_por': self.user.id
        }
        
        serializer = ConfiguracionVacacionesSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('dias_por_ano', serializer.errors)
        self.assertIn('dias_minimos_solicitud', serializer.errors)