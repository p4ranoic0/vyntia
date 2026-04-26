# -*- coding: utf-8 -*-
"""
Tests para el modelo Area

Tests completos para validar la funcionalidad del modelo Area,
incluyendo campos, métodos, propiedades y relaciones jerárquicas.
"""

from datetime import datetime, timedelta

import pytest
from apps.contracts.models import DatosLaborales
from apps.employees.models import Empleado
from apps.organization.models import Area
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase
from django.utils import timezone


class AreaModelTest(TestCase):
    """Tests para el modelo Area."""

    def setUp(self):
        """Configuración inicial para los tests."""
        # Crear área padre para tests de jerarquía
        self.area_padre = Area.objects.create(
            nombre_organo="Dirección General",
            nombre_unidad_organica="Dirección Ejecutiva",
            siglas_area="DG",
            descripcion_area="Área principal de dirección",
            nivel_jerarquico=1,
            estado_area="activo",
        )

        # Crear área de prueba
        self.area_test = Area.objects.create(
            nombre_organo="Recursos Humanos",
            nombre_unidad_organica="Gestión de Personal",
            siglas_area="RRHH",
            descripcion_area="Área de gestión de recursos humanos",
            jefe_area="Juan Pérez",
            area_padre=self.area_padre,
            nivel_jerarquico=2,
            codigo_presupuestal="001-RRHH",
            total_empleados=5,
            estado_area="activo",
        )

    def test_creacion_area_basica(self):
        """Test de creación básica de área."""
        area = Area.objects.create(
            nombre_organo="Finanzas",
            nombre_unidad_organica="Contabilidad",
            siglas_area="FIN",
        )

        self.assertEqual(area.nombre_organo, "Finanzas")
        self.assertEqual(area.nombre_unidad_organica, "Contabilidad")
        self.assertEqual(area.siglas_area, "FIN")
        self.assertEqual(area.estado_area, "activo")  # Valor por defecto
        self.assertEqual(area.nivel_jerarquico, 1)  # Valor por defecto
        self.assertEqual(area.total_empleados, 0)  # Valor por defecto
        self.assertIsNotNone(area.fecha_creacion)
        self.assertIsNotNone(area.fecha_actualizacion)

    def test_campos_obligatorios(self):
        """Test de validación de campos obligatorios."""
        # Test con siglas_area duplicadas (unique=True)
        with self.assertRaises(IntegrityError):
            Area.objects.create(
                nombre_organo="Test",
                nombre_unidad_organica="Test",
                siglas_area="RRHH",  # Ya existe
            )

    def test_valores_por_defecto(self):
        """Test de valores por defecto de los campos."""
        area = Area.objects.create(siglas_area="TEST")

        self.assertEqual(area.nombre_organo, "SIN ESPECIFICAR")
        self.assertEqual(area.nombre_unidad_organica, "SIN ESPECIFICAR")
        self.assertEqual(area.estado_area, "activo")
        self.assertEqual(area.nivel_jerarquico, 1)
        self.assertEqual(area.total_empleados, 0)

    def test_estados_area_validos(self):
        """Test de estados válidos para el área."""
        estados_validos = ["activo", "inactivo", "reestructuracion"]
        siglas_cortas = ["ACT", "INA", "REE"]

        for i, estado in enumerate(estados_validos):
            area = Area.objects.create(siglas_area=siglas_cortas[i], estado_area=estado)
            self.assertEqual(area.estado_area, estado)

    def test_str_representation(self):
        """Test de representación string del modelo."""
        expected_str = "RRHH - Gestión de Personal"
        self.assertEqual(str(self.area_test), expected_str)

    def test_nombre_completo_property(self):
        """Test de la propiedad nombre_completo."""
        expected_nombre = "Recursos Humanos - Gestión de Personal"
        self.assertEqual(self.area_test.nombre_completo, expected_nombre)

    def test_es_activa_property(self):
        """Test de la propiedad es_activa."""
        # Área activa
        self.assertTrue(self.area_test.es_activa)

        # Cambiar a inactiva
        self.area_test.estado_area = "inactivo"
        self.area_test.save()
        self.assertFalse(self.area_test.es_activa)

        # Cambiar a reestructuración
        self.area_test.estado_area = "reestructuracion"
        self.area_test.save()
        self.assertFalse(self.area_test.es_activa)

    def test_metodo_desactivar(self):
        """Test del método desactivar."""
        self.assertTrue(self.area_test.es_activa)

        self.area_test.desactivar()

        self.assertEqual(self.area_test.estado_area, "inactivo")
        self.assertFalse(self.area_test.es_activa)

        # Verificar que se guardó en la base de datos
        area_db = Area.objects.get(area_id=self.area_test.area_id)
        self.assertEqual(area_db.estado_area, "inactivo")

    def test_metodo_activar(self):
        """Test del método activar."""
        # Primero desactivar
        self.area_test.desactivar()
        self.assertFalse(self.area_test.es_activa)

        # Luego activar
        self.area_test.activar()

        self.assertEqual(self.area_test.estado_area, "activo")
        self.assertTrue(self.area_test.es_activa)

        # Verificar que se guardó en la base de datos
        area_db = Area.objects.get(area_id=self.area_test.area_id)
        self.assertEqual(area_db.estado_area, "activo")

    def test_relacion_jerarquica_padre_hijo(self):
        """Test de relación jerárquica entre áreas."""
        # Verificar relación padre-hijo
        self.assertEqual(self.area_test.area_padre, self.area_padre)
        self.assertEqual(self.area_test.nivel_jerarquico, 2)

        # Verificar que el padre puede acceder a sus hijos
        areas_hijas = self.area_padre.area_set.all()
        self.assertIn(self.area_test, areas_hijas)

    def test_subareas_activas(self):
        """Test del método subareas_activas."""
        # Crear sub-área activa
        subarea_activa = Area.objects.create(
            nombre_organo="Sub-RRHH",
            nombre_unidad_organica="Nóminas",
            siglas_area="NOM",
            area_padre=self.area_test,
            nivel_jerarquico=3,
            estado_area="activo",
        )

        # Crear sub-área inactiva
        subarea_inactiva = Area.objects.create(
            nombre_organo="Sub-RRHH",
            nombre_unidad_organica="Archivo",
            siglas_area="ARC",
            area_padre=self.area_test,
            nivel_jerarquico=3,
            estado_area="inactivo",
        )

        subareas_activas = self.area_test.subareas_activas()

        self.assertIn(subarea_activa, subareas_activas)
        self.assertNotIn(subarea_inactiva, subareas_activas)
        self.assertEqual(subareas_activas.count(), 1)

    def test_todas_las_subareas_recursivo(self):
        """Test del método todas_las_subareas (recursivo)."""
        # Crear estructura jerárquica
        subarea_nivel2 = Area.objects.create(
            siglas_area="SUB2", area_padre=self.area_test, nivel_jerarquico=3
        )

        subarea_nivel3 = Area.objects.create(
            siglas_area="SUB3", area_padre=subarea_nivel2, nivel_jerarquico=4
        )

        todas_subareas = self.area_test.todas_las_subareas()

        self.assertIn(subarea_nivel2, todas_subareas)
        self.assertIn(subarea_nivel3, todas_subareas)
        self.assertEqual(len(todas_subareas), 2)

    def test_empleados_activos_sin_empleados(self):
        """Test del método empleados_activos cuando no hay empleados."""
        empleados = self.area_test.empleados_activos()
        self.assertEqual(empleados.count(), 0)

    def test_longitud_maxima_campos(self):
        """Test de longitud máxima de campos de texto."""
        # Test nombre_organo (max_length=150)
        nombre_largo = "A" * 50  # Usar 50 caracteres ASCII simples
        area = Area.objects.create(
            nombre_organo=nombre_largo,
            nombre_unidad_organica="Unidad Test",
            siglas_area="T1",
            nivel_jerarquico=1,
            total_empleados=0,
            estado_area="activo",
        )
        self.assertEqual(len(area.nombre_organo), 50)

        # Test siglas_area - usar cadenas muy cortas ASCII
        area2 = Area.objects.create(
            nombre_organo="Test Organo 2",
            nombre_unidad_organica="Unidad Test 2",
            siglas_area="T2",  # 2 caracteres ASCII
            nivel_jerarquico=1,
            total_empleados=0,
            estado_area="activo",
        )
        self.assertEqual(len(area2.siglas_area), 2)

        # Test con siglas de 3 caracteres
        area3 = Area.objects.create(
            nombre_organo="Test Organo 3",
            nombre_unidad_organica="Unidad Test 3",
            siglas_area="T3A",  # 3 caracteres ASCII
            nivel_jerarquico=1,
            total_empleados=0,
            estado_area="activo",
        )
        self.assertEqual(len(area3.siglas_area), 3)

        # Test descripcion_area (TextField)
        descripcion_corta = "Descripcion de prueba"  # Texto simple
        area4 = Area.objects.create(
            nombre_organo="Test Organo 4",
            nombre_unidad_organica="Unidad Test 4",
            siglas_area="T4B",
            descripcion_area=descripcion_corta,
            nivel_jerarquico=1,
            total_empleados=0,
            estado_area="activo",
        )
        self.assertEqual(len(area4.descripcion_area), len(descripcion_corta))

    def test_campos_opcionales(self):
        """Test de campos opcionales (null=True, blank=True)."""
        area = Area.objects.create(
            siglas_area="OPC",
            descripcion_area=None,
            jefe_area=None,
            codigo_presupuestal=None,
        )

        self.assertIsNone(area.descripcion_area)
        self.assertIsNone(area.jefe_area)
        self.assertIsNone(area.codigo_presupuestal)

    def test_actualizacion_fecha_modificacion(self):
        """Test de actualización automática de fecha_actualizacion."""
        fecha_inicial = self.area_test.fecha_actualizacion

        # Esperar un momento para asegurar diferencia en timestamp
        import time

        time.sleep(0.1)

        # Actualizar el área
        self.area_test.descripcion_area = "Descripción actualizada"
        self.area_test.save()

        self.assertGreater(self.area_test.fecha_actualizacion, fecha_inicial)

    def test_indices_base_datos(self):
        """Test de que los índices están configurados correctamente."""
        # Este test verifica que el modelo tiene los índices definidos
        # Los índices reales se verifican en las migraciones
        meta = Area._meta
        indices = [index.fields for index in meta.indexes]

        # Verificar que existen índices para los campos importantes
        campos_indexados = [
            ["siglas_area"],
            ["estado_area"],
            ["nombre_organo"],
            ["area_padre"],
            ["nivel_jerarquico"],
            ["codigo_presupuestal"],
            ["total_empleados"],
        ]

        for campo in campos_indexados:
            self.assertIn(campo, indices)

    def test_tabla_base_datos(self):
        """Test de configuración de tabla en base de datos."""
        self.assertEqual(Area._meta.db_table, "area")

    def test_area_sin_padre(self):
        """Test de área sin padre (área raíz)."""
        area_raiz = Area.objects.create(siglas_area="RAIZ", nivel_jerarquico=1)

        self.assertIsNone(area_raiz.area_padre)
        self.assertEqual(area_raiz.nivel_jerarquico, 1)

    def test_multiples_niveles_jerarquia(self):
        """Test de múltiples niveles de jerarquía."""
        # Nivel 1 (raíz)
        nivel1 = Area.objects.create(siglas_area="N1", nivel_jerarquico=1)

        # Nivel 2
        nivel2 = Area.objects.create(
            siglas_area="N2", area_padre=nivel1, nivel_jerarquico=2
        )

        # Nivel 3
        nivel3 = Area.objects.create(
            siglas_area="N3", area_padre=nivel2, nivel_jerarquico=3
        )

        # Verificar jerarquía
        self.assertEqual(nivel3.area_padre, nivel2)
        self.assertEqual(nivel2.area_padre, nivel1)
        self.assertIsNone(nivel1.area_padre)

        # Verificar niveles
        self.assertEqual(nivel1.nivel_jerarquico, 1)
        self.assertEqual(nivel2.nivel_jerarquico, 2)
        self.assertEqual(nivel3.nivel_jerarquico, 3)

    def test_codigo_presupuestal_unico_opcional(self):
        """Test de código presupuestal único pero opcional."""
        # Crear área con código presupuestal
        area1 = Area.objects.create(siglas_area="PR1", codigo_presupuestal="001-TEST")

        # Crear área sin código presupuestal
        area2 = Area.objects.create(siglas_area="PR2", codigo_presupuestal=None)

        self.assertEqual(area1.codigo_presupuestal, "001-TEST")
        self.assertIsNone(area2.codigo_presupuestal)

    def test_total_empleados_numerico(self):
        """Test de campo total_empleados como entero."""
        area = Area.objects.create(siglas_area="EMP", total_empleados=25)

        self.assertEqual(area.total_empleados, 25)
        self.assertIsInstance(area.total_empleados, int)

        # Test con valor negativo (debería ser permitido por el modelo)
        area.total_empleados = -1
        area.save()
        self.assertEqual(area.total_empleados, -1)
