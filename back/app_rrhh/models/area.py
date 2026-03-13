# -*- coding: utf-8 -*-
"""
Modelo Area - Gestión de áreas organizacionales

Contiene la definición del modelo Area que representa las unidades organizacionales
de la institución, incluyendo su jerarquía y estructura.
"""

from django.db import models
from django.utils import timezone
# from ..managers import AreaManager  # Comentado temporalmente para migraciones


class Area(models.Model):
    """Modelo para gestionar las áreas organizacionales de la institución."""
    
    ESTADO_AREA_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('reestructuracion', 'Reestructuración'),
    ]
    
    # Campos principales
    area_id = models.AutoField(primary_key=True)
    
    # Información organizacional
    nombre_organo = models.CharField(max_length=150, default='SIN ESPECIFICAR')
    nombre_unidad_organica = models.CharField(max_length=150, default='SIN ESPECIFICAR')
    siglas_area = models.CharField(max_length=20, unique=True, default='TEMP')
    descripcion_area = models.TextField(null=True, blank=True)
    jefe_area = models.CharField(max_length=150, null=True, blank=True)
    
    # Jerarquía organizacional
    area_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, db_column='area_padre_id')
    nivel_jerarquico = models.IntegerField(default=1)
    
    # Información presupuestal y estadística
    codigo_presupuestal = models.CharField(max_length=20, null=True, blank=True)
    total_empleados = models.IntegerField(default=0)
    
    # Campos de control
    estado_area = models.CharField(max_length=20, choices=ESTADO_AREA_CHOICES, default='activo')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Manager personalizado
    # objects = AreaManager()  # Comentado temporalmente para migraciones
    
    def desactivar(self):
        """Desactiva el área."""
        self.estado_area = 'inactivo'
        self.save()
    
    def activar(self):
        """Activa el área."""
        self.estado_area = 'activo'
        self.save()
    
    class Meta:
        db_table = 'area'  # Nombre real de la tabla en la base de datos
        indexes = [
            models.Index(fields=['siglas_area']),
            models.Index(fields=['estado_area']),
            models.Index(fields=['nombre_organo']),
            models.Index(fields=['area_padre']),
            models.Index(fields=['nivel_jerarquico']),
            models.Index(fields=['codigo_presupuestal']),
            models.Index(fields=['total_empleados']),
        ]
    
    def __str__(self):
        return f"{self.siglas_area} - {self.nombre_unidad_organica}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del área."""
        return f"{self.nombre_organo} - {self.nombre_unidad_organica}"
    
    @property
    def es_activa(self):
        """Verifica si el área está activa."""
        return self.estado_area == 'activo'
    
    @property
    def es_area_raiz(self):
        """Verifica si es un área raíz (sin padre)."""
        return self.area_padre is None
    
    @property
    def tiene_subareas(self):
        """Verifica si tiene sub-áreas."""
        return self.area_set.exists()
    
    @property
    def ruta_jerarquica(self):
        """Obtiene la ruta jerárquica completa."""
        ruta = [self.siglas_area]
        area_actual = self.area_padre
        while area_actual:
            ruta.insert(0, area_actual.siglas_area)
            area_actual = area_actual.area_padre
        return ' > '.join(ruta)
    
    def empleados_activos_count(self):
        """Cuenta empleados activos en el área."""
        from .empleado import Empleado
        from .datos_laborales import DatosLaborales
        return DatosLaborales.objects.filter(
            area=self,
            estado_datos='activo'
        ).count()
    
    def empleados_activos(self):
        """Obtiene empleados activos en el área."""
        from .empleado import Empleado
        from .datos_laborales import DatosLaborales
        return Empleado.objects.filter(
            datos_laborales__area=self,
            datos_laborales__estado_datos='activo',
            estado_empleado='activo'
        ).distinct()
    
    def subareas_activas(self):
        """Obtiene sub-áreas activas."""
        return self.area_set.filter(estado_area='activo')
    
    def todas_las_subareas(self):
        """Obtiene todas las sub-áreas recursivamente."""
        subareas = list(self.area_set.all())
        for subarea in self.area_set.all():
            subareas.extend(subarea.todas_las_subareas())
        return subareas
    
    def empleados_totales_con_subareas(self):
        """Cuenta empleados totales incluyendo sub-áreas."""
        total = self.empleados_activos_count()
        for subarea in self.subareas_activas():
            total += subarea.empleados_totales_con_subareas()
        return total
    
    def actualizar_total_empleados(self):
        """Actualiza el contador de empleados totales."""
        self.total_empleados = self.empleados_activos_count()
        self.save(update_fields=['total_empleados'])