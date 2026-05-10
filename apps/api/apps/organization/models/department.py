# -*- coding: utf-8 -*-
"""
Modelo Department - Gestión de áreas organizacionales

Contiene la definición del modelo Department que representa las unidades organizacionales
de la institución, incluyendo su jerarquía y estructura.
"""

import uuid

from django.db import models
from django.utils import timezone
# from ..managers import AreaManager  # Comentado temporalmente para migraciones


class Department(models.Model):
    """Modelo para gestionar las áreas organizacionales de la institución.

    Post-B.6: Department is the canonical OrgUnit per Maestro Module 02. The
    `unit_type` field discriminates DIRECCION/GERENCIA/SUBGERENCIA/OFICINA/AREA/
    EQUIPO (legacy areas default to 'AREA'). `cost_center` ties the unit to
    accounting reporting.
    """

    ESTADO_AREA_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('reestructuracion', 'Reestructuración'),
    ]

    # Org unit type (B.6, Maestro § 2.1)
    UNIT_TYPE_CHOICES = [
        ('direccion', 'Dirección'),
        ('gerencia', 'Gerencia'),
        ('subgerencia', 'Subgerencia'),
        ('oficina', 'Oficina'),
        ('area', 'Área'),
        ('equipo', 'Equipo'),
    ]

    # Campos principales
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    tenant = models.ForeignKey(
        "tenancy.Tenant",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        db_index=True,
        related_name="+",
    )

    # Información organizacional
    nombre_organo = models.CharField(max_length=150, default='SIN ESPECIFICAR')
    nombre_unidad_organica = models.CharField(max_length=150, default='SIN ESPECIFICAR')
    siglas_area = models.CharField(max_length=20, default='TEMP')
    descripcion_area = models.TextField(null=True, blank=True)
    jefe_area = models.CharField(max_length=150, null=True, blank=True)

    # OrgUnit characteristics (B.6)
    unit_type = models.CharField(
        max_length=20,
        choices=UNIT_TYPE_CHOICES,
        default='area',
        db_index=True,
        help_text='Type of organizational unit per Maestro Module 02.',
    )
    cost_center = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text='Accounting cost center identifier.',
    )

    # Jerarquía organizacional
    area_padre = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, db_column='area_padre_id')
    nivel_jerarquico = models.IntegerField(default=1)

    # Información presupuestal y estadística
    codigo_presupuestal = models.CharField(max_length=20, null=True, blank=True)
    total_empleados = models.IntegerField(default=0)

    # Campos de control
    estado_area = models.CharField(max_length=20, choices=ESTADO_AREA_CHOICES, default='activo')
    created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_creacion')
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')
    
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
        constraints = [
            models.UniqueConstraint(
                fields=["tenant", "siglas_area"],
                name="unique_department_siglas_per_tenant",
            ),
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
        return self.department_set.exists()
    
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
        from apps.contracts.models import EmploymentData
        return EmploymentData.objects.filter(
            area=self,
            estado_datos='activo'
        ).count()

    def empleados_activos(self):
        """Obtiene empleados activos en el área."""
        from apps.employees.models import Employee
        return Employee.objects.filter(
            datos_laborales__area=self,
            datos_laborales__estado_datos='activo',
            estado_empleado='activo'
        ).distinct()
    
    def subareas_activas(self):
        """Obtiene sub-áreas activas."""
        return self.department_set.filter(estado_area='activo')

    def todas_las_subareas(self):
        """Obtiene todas las sub-áreas recursivamente."""
        subareas = list(self.department_set.all())
        for subarea in self.department_set.all():
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