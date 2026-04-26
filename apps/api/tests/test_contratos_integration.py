# -*- coding: utf-8 -*-
"""
Tests de integración para el sistema de contratos y empleados

Este módulo contiene tests que verifican la integración completa entre
los modelos de empleados, contratos, adendas y el sistema de autenticación.
"""

import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import authenticate

from apps.documents.models import DocumentosDigitales
from apps.contracts.models import (
    ContratosAdendas,
    DatosLaborales,
)
from apps.employees.models import Empleado
from apps.organization.models import Area
from apps.identity.models import Usuario


@pytest.mark.django_db
class TestContratosIntegration(TestCase):
    """Tests de integración para el sistema de contratos."""
    
    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear usuario
        self.usuario = Usuario.objects.create_user(
            username='admin_contratos',
            email='admin@empresa.com',
            password='password123',
            nombres_usuario='Admin',
            apellidos_usuario='Sistema'
        )
        
        # Crear área
        self.area = Area.objects.create(
            nombre_unidad_organica='Recursos Humanos',
            siglas_area='RRHH',
            descripcion_area='Área de gestión de personal',
            estado_area='activa'
        )
        
        # Crear empleado
        self.empleado = Empleado.objects.create(
            numero_documento='12345678',
            tipo_documento='DNI',
            nombres_empleado='Juan Carlos',
            apellido_paterno='Pérez',
            apellido_materno='García',
            correo_personal='juan.perez@empresa.com',
            telefono_celular='987654321',
            fecha_nacimiento=date(1990, 5, 15),
            estado_civil='soltero',
            direccion_domicilio='Av. Principal 123',
            distrito_domicilio='Lima',
            provincia_domicilio='Lima',
            departamento_domicilio='Lima',
            genero_empleado='masculino',
            entidad_bancaria='BCP',
            numero_cuenta_bancaria='1234567890',
            numero_cci='00212345678901234567',
            estado_empleado='activo'
        )
        
        # Crear datos laborales
        self.datos_laborales = DatosLaborales.objects.create(
            empleado=self.empleado,
            area=self.area,
            cargo_empleado='Analista de Sistemas',
            categoria='profesional',
            tipo_contrato='indefinido',
            regimen_laboral='728',
            fecha_ingreso=date.today() - timedelta(days=30),
            fecha_inicio_contrato=date.today() - timedelta(days=30),
            sueldo_basico=Decimal('3500.00'),
            estado_datos='activo'
        )
    
    def test_crear_contrato_inicial(self):
        """Test para crear un contrato inicial."""
        contrato = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-001',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        self.assertEqual(contrato.numero_contrato, 'CON-2024-001')
        self.assertTrue(contrato.es_contrato_inicial)
        self.assertFalse(contrato.es_adenda)
        self.assertTrue(contrato.esta_vigente)
        self.assertEqual(contrato.empleado, self.empleado)
        self.assertEqual(contrato.area, self.area)
    
    def test_crear_adenda_contrato(self):
        """Test para crear una adenda de un contrato existente."""
        # Crear contrato inicial
        contrato_inicial = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-002',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('4022.99'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # Crear adenda salarial
        adenda = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-002',
            numero_adenda='AD-001',
            tipo_documento='ADENDA_SALARIAL',
            fecha_inicio=date.today() + timedelta(days=30),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('4597.70'),  # Resulta en salario_neto exacto  # Aumento salarial
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        self.assertEqual(adenda.numero_contrato, 'CON-2024-002')
        self.assertEqual(adenda.numero_adenda, 'AD-001')
        self.assertFalse(adenda.es_contrato_inicial)
        self.assertTrue(adenda.es_adenda)
        self.assertEqual(adenda.salario_bruto, Decimal('4597.70'))
        
        # Verificar que ambos documentos están relacionados
        adendas = contrato_inicial.obtener_adendas()
        self.assertEqual(adendas.count(), 1)
        self.assertEqual(adendas.first(), adenda)
    
    def test_validaciones_contrato(self):
        """Test para validaciones del modelo de contratos."""
        # Test: Fecha fin debe ser posterior a fecha inicio
        with self.assertRaises(ValidationError):
            contrato = ContratosAdendas(
                empleado=self.empleado,
                area=self.area,
                numero_contrato='CON-2024-003',
                tipo_documento='CONTRATO_FIJO',
                fecha_inicio=date.today(),
                fecha_fin=date.today() - timedelta(days=1),  # Fecha inválida
                salario_bruto=Decimal('4022.99'),  # Resulta en salario_neto exacto
                cargo='Analista',
                creado_por=self.usuario
            )
            contrato.full_clean()
        
        # Test: Contrato indefinido no debe tener fecha fin
        with self.assertRaises(ValidationError):
            contrato = ContratosAdendas(
                empleado=self.empleado,
                area=self.area,
                numero_contrato='CON-2024-004',
                tipo_documento='CONTRATO_INDEFINIDO',
                fecha_inicio=date.today(),
                fecha_fin=date.today() + timedelta(days=365),  # No debe tener fecha fin
                salario_bruto=Decimal('4022.99'),  # Resulta en salario_neto exacto
                cargo='Analista',
                creado_por=self.usuario
            )
            contrato.full_clean()
        
        # Test: Contrato a plazo fijo debe tener fecha fin
        with self.assertRaises(ValidationError):
            contrato = ContratosAdendas(
                empleado=self.empleado,
                area=self.area,
                numero_contrato='CON-2024-005',
                tipo_documento='CONTRATO_FIJO',
                fecha_inicio=date.today(),
                fecha_fin=None,  # Debe tener fecha fin
                salario_bruto=Decimal('3500.00'),
                cargo='Analista',
                creado_por=self.usuario
            )
            contrato.full_clean()
    
    def test_propiedades_calculadas_contrato(self):
        """Test para propiedades calculadas del contrato."""
        contrato = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-006',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=30),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # Test días hasta vencimiento (puede variar por la hora del día)
        self.assertIn(contrato.dias_hasta_vencimiento, [29, 30])
        
        # Test duración en días
        self.assertEqual(contrato.duracion_dias, 30)
        
        # Test duración en meses (aproximada)
        self.assertAlmostEqual(contrato.duracion_meses, 1.0, places=1)
        
        # Test está vigente
        self.assertTrue(contrato.esta_vigente)
        
        # Test está por vencer (dentro de 30 días)
        self.assertTrue(contrato.esta_por_vencer(dias=30))
        self.assertFalse(contrato.esta_por_vencer(dias=15))
    
    def test_contrato_vencido(self):
        """Test para contrato vencido."""
        contrato = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-007',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today() - timedelta(days=60),
            fecha_fin=date.today() - timedelta(days=1),  # Vencido ayer
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        self.assertTrue(contrato.esta_vencido)
        self.assertFalse(contrato.esta_vigente)
        self.assertEqual(contrato.dias_hasta_vencimiento, 0)
    
    def test_generacion_numeros_contrato(self):
        """Test para generación automática de números de contrato."""
        contrato = ContratosAdendas(
            empleado=self.empleado,
            area=self.area,
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # Generar número de contrato
        contrato.generar_numero_contrato()
        self.assertIsNotNone(contrato.numero_contrato)
        self.assertTrue(contrato.numero_contrato.startswith('CON-'))
        
        # Guardar contrato
        contrato.save()
        
        # Crear adenda y generar número
        adenda = ContratosAdendas(
            empleado=self.empleado,
            area=self.area,
            numero_contrato=contrato.numero_contrato,
            numero_adenda='temp',  # Temporal para que no sea considerado contrato inicial
            tipo_documento='ADENDA_SALARIAL',
            fecha_inicio=date.today() + timedelta(days=30),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        numero_adenda = adenda.generar_numero_adenda()
        self.assertEqual(numero_adenda, 'AD-001')
        # Asignar el número generado
        adenda.numero_adenda = numero_adenda
    
    def test_calculo_salario_neto(self):
        """Test para cálculo automático de salario neto."""
        contrato = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-008',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('4597.70'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # Verificar que se calculó el salario neto automáticamente
        self.assertIsNotNone(contrato.salario_neto)
        # Aproximadamente 87% del bruto (13% descuentos) - redondeado a 2 decimales
        expected_neto = (Decimal('4597.70') * Decimal('0.87')).quantize(Decimal('0.01'))
        self.assertEqual(contrato.salario_neto, expected_neto)
    
    def test_integracion_empleado_contrato(self):
        """Test de integración entre empleado y contrato."""
        # Crear múltiples contratos para el mismo empleado
        contrato1 = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-009',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today() - timedelta(days=365),
            fecha_fin=date.today() - timedelta(days=1),
            salario_bruto=Decimal('2873.56'),  # Resulta en salario_neto exacto
            cargo='Analista Junior',
            estado='TERMINADO',
            creado_por=self.usuario
        )
        
        contrato2 = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-010',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # Verificar relación inversa
        contratos_empleado = self.empleado.contratos_adendas.all()
        self.assertEqual(contratos_empleado.count(), 2)
        self.assertIn(contrato1, contratos_empleado)
        self.assertIn(contrato2, contratos_empleado)
        
        # Verificar contrato activo
        contrato_activo = self.empleado.contratos_adendas.filter(estado='ACTIVO').first()
        self.assertEqual(contrato_activo, contrato2)
    
    def test_integracion_area_contratos(self):
        """Test de integración entre área y contratos."""
        # Crear otra área
        area2 = Area.objects.create(
            nombre_unidad_organica='Tecnología',
            siglas_area='TECH',
            descripcion_area='Área de desarrollo',
            estado_area='activa'
        )
        
        # Crear contratos en diferentes áreas
        ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,  # RRHH
            numero_contrato='CON-2024-011',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista RRHH',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=area2,  # Tecnología
            numero_contrato='CON-2024-012',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('4597.70'),  # Resulta en salario_neto exacto
            cargo='Desarrollador',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # Verificar contratos por área
        contratos_rrhh = self.area.contratos_adendas_area.all()
        contratos_tech = area2.contratos_adendas_area.all()
        
        self.assertEqual(contratos_rrhh.count(), 1)
        self.assertEqual(contratos_tech.count(), 1)
        
        self.assertEqual(contratos_rrhh.first().cargo, 'Analista RRHH')
        self.assertEqual(contratos_tech.first().cargo, 'Desarrollador')
    
    def test_integracion_usuario_contratos(self):
        """Test de integración entre usuario y contratos creados."""
        # Crear otro usuario
        usuario2 = Usuario.objects.create_user(
            username='supervisor',
            email='supervisor@empresa.com',
            password='password123',
            nombres_usuario='Supervisor',
            apellidos_usuario='Área'
        )
        
        # Crear contratos con diferentes usuarios
        contrato1 = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-013',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        contrato2 = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-014',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=365),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista',
            estado='ACTIVO',
            creado_por=usuario2
        )
        
        # Verificar contratos creados por cada usuario
        contratos_admin = self.usuario.contratos_creados.all()
        contratos_supervisor = usuario2.contratos_creados.all()
        
        self.assertEqual(contratos_admin.count(), 1)
        self.assertEqual(contratos_supervisor.count(), 1)
        self.assertEqual(contratos_admin.first(), contrato1)
        self.assertEqual(contratos_supervisor.first(), contrato2)
    
    def test_sistema_completo_workflow(self):
        """Test del workflow completo del sistema de contratos."""
        # 1. Crear contrato inicial
        contrato = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato='CON-2024-015',
            tipo_documento='CONTRATO_FIJO',
            fecha_inicio=date.today(),
            fecha_fin=date.today() + timedelta(days=180),
            salario_bruto=Decimal('3448.28'),  # Resulta en salario_neto exacto
            cargo='Analista de Sistemas',
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # 2. Verificar que puede generar adenda
        self.assertTrue(contrato.puede_generar_adenda())
        
        # 3. Crear adenda de extensión
        adenda_extension = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato=contrato.numero_contrato,
            numero_adenda='AD-001',
            tipo_documento='ADENDA_EXTENSION',
            fecha_inicio=contrato.fecha_fin,
            fecha_fin=contrato.fecha_fin + timedelta(days=180),
            salario_bruto=contrato.salario_bruto,
            cargo=contrato.cargo,
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # 4. Crear adenda salarial
        adenda_salarial = ContratosAdendas.objects.create(
            empleado=self.empleado,
            area=self.area,
            numero_contrato=contrato.numero_contrato,
            numero_adenda='AD-002',
            tipo_documento='ADENDA_SALARIAL',
            fecha_inicio=date.today() + timedelta(days=90),
            fecha_fin=adenda_extension.fecha_fin,
            salario_bruto=Decimal('4597.70'),  # Resulta en salario_neto exacto - Aumento
            cargo=contrato.cargo,
            estado='ACTIVO',
            creado_por=self.usuario
        )
        
        # 5. Verificar el historial completo
        adendas = contrato.obtener_adendas()
        self.assertEqual(adendas.count(), 2)
        
        # 6. Verificar orden cronológico
        adendas_ordenadas = list(adendas.order_by('fecha_creacion'))
        self.assertEqual(adendas_ordenadas[0], adenda_extension)
        self.assertEqual(adendas_ordenadas[1], adenda_salarial)
        
        # 7. Verificar que todas las adendas tienen el mismo número de contrato
        for adenda in adendas:
            self.assertEqual(adenda.numero_contrato, contrato.numero_contrato)
            self.assertEqual(adenda.empleado, contrato.empleado)
        
        # 8. Verificar contrato base desde adenda
        contrato_base = adenda_salarial.obtener_contrato_base()
        self.assertEqual(contrato_base, contrato)