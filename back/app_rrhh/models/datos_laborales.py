# -*- coding: utf-8 -*-
"""
Modelo DatosLaborales - Gestión de información laboral de empleados

Contiene la definición del modelo DatosLaborales que almacena toda la información
laboral, contractual y de puesto de los empleados.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db import models
from django.utils import timezone

# from ..managers import DatosLaboralesManager  # Comentado temporalmente para migraciones


class DatosLaborales(models.Model):
    """Modelo para gestionar la información laboral de los empleados."""
    
    TIPO_CONTRATO_CHOICES = [
        ('CAS', 'CAS - Contrato Administrativo de Servicios'),
        ('CAP', 'CAP - Cuadro de Asignación de Personal'),
        ('indefinido', 'Indefinido'),
        ('temporal', 'Temporal'),
        ('practicas', 'Prácticas'),
        ('consultoria', 'Consultoría'),
        ('locacion', 'Locación de Servicios'),
    ]
    
    MODALIDAD_TRABAJO_CHOICES = [
        ('presencial', 'Presencial'),
        ('remoto', 'Remoto'),
        ('hibrido', 'Híbrido'),
    ]
    
    JORNADA_LABORAL_CHOICES = [
        ('completa', 'Tiempo Completo'),
        ('parcial', 'Tiempo Parcial'),
        ('por_horas', 'Por Horas'),
    ]
    
    ESTADO_DATOS_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('suspendido', 'Suspendido'),
    ]
    
    REGIMEN_LABORAL_CHOICES = [
        ('276', 'Decreto Legislativo 276'),
        ('728', 'Decreto Legislativo 728'),
        ('1057', 'Decreto Legislativo 1057 (CAS)'),
        ('locacion', 'Locación de Servicios'),
        ('consultoria', 'Consultoría'),
        ('practicas', 'Prácticas'),
    ]
    
    CATEGORIA_CHOICES = [
        ('directivo', 'Directivo'),
        ('funcionario', 'Funcionario'),
        ('profesional', 'Profesional'),
        ('tecnico', 'Técnico'),
        ('auxiliar', 'Auxiliar'),
        ('practicante', 'Practicante'),
        ('consultor', 'Consultor'),
    ]
    
    # Campos principales
    dato_laboral_id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(
        'Empleado',
        on_delete=models.CASCADE,
        related_name='datos_laborales'
    )
    area = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        related_name='empleados_laborales'
    )
    
    # Información del puesto
    cargo_empleado = models.CharField(max_length=100)
    codigo_puesto = models.CharField(max_length=20, null=True, blank=True)
    nivel_puesto = models.CharField(max_length=10, null=True, blank=True)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    
    # Información contractual
    tipo_contrato = models.CharField(max_length=20, choices=TIPO_CONTRATO_CHOICES)
    regimen_laboral = models.CharField(max_length=20, choices=REGIMEN_LABORAL_CHOICES)
    modalidad_trabajo = models.CharField(max_length=15, choices=MODALIDAD_TRABAJO_CHOICES, default='presencial')
    jornada_laboral = models.CharField(max_length=15, choices=JORNADA_LABORAL_CHOICES, default='completa')
    
    # Fechas importantes
    fecha_ingreso = models.DateField()
    fecha_inicio_contrato = models.DateField()
    fecha_fin_contrato = models.DateField(null=True, blank=True)
    fecha_cese = models.DateField(null=True, blank=True)
    
    # Información salarial
    sueldo_basico = models.DecimalField(max_digits=10, decimal_places=2)
    asignacion_familiar = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    bonificacion_especial = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    otras_bonificaciones = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0.00'))
    
    # Información de horario
    horario_entrada = models.TimeField(null=True, blank=True)
    horario_salida = models.TimeField(null=True, blank=True)
    horas_semanales = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal('40.00'))
    
    # Información de jefe directo
    jefe_directo = models.ForeignKey(
        'Empleado',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subordinados_laborales'
    )
    
    # Campos de control
    estado_datos = models.CharField(max_length=15, choices=ESTADO_DATOS_CHOICES, default='activo')
    observaciones = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Manager personalizado
    # objects = DatosLaboralesManager()  # Comentado temporalmente para migraciones
    
    class Meta:
        db_table = 'datos_laborales'  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['area']),
            models.Index(fields=['cargo_empleado']),
            models.Index(fields=['tipo_contrato']),
            models.Index(fields=['regimen_laboral']),
            models.Index(fields=['categoria']),
            models.Index(fields=['fecha_ingreso']),
            models.Index(fields=['fecha_inicio_contrato']),
            models.Index(fields=['fecha_fin_contrato']),
            models.Index(fields=['estado_datos']),
            models.Index(fields=['jefe_directo']),
            models.Index(fields=['modalidad_trabajo']),
            models.Index(fields=['jornada_laboral']),
        ]
        unique_together = [['empleado', 'fecha_inicio_contrato']]
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.cargo_empleado} ({self.area.nombre_area})"
    
    @property
    def sueldo_total(self):
        """Calcula el sueldo total incluyendo bonificaciones."""
        return (
            self.sueldo_basico +
            self.asignacion_familiar +
            self.bonificacion_especial +
            self.otras_bonificaciones
        )
    
    @property
    def antiguedad_anos(self):
        """Calcula la antigüedad en años."""
        if self.fecha_ingreso:
            fecha_calculo = self.fecha_cese or date.today()
            delta = fecha_calculo - self.fecha_ingreso
            return delta.days // 365
        return 0
    
    @property
    def antiguedad_meses(self):
        """Calcula la antigüedad en meses."""
        if self.fecha_ingreso:
            fecha_calculo = self.fecha_cese or date.today()
            anos = self.antiguedad_anos
            meses_restantes = ((fecha_calculo - self.fecha_ingreso).days % 365) // 30
            return (anos * 12) + meses_restantes
        return 0
    
    @property
    def antiguedad_dias(self):
        """Calcula la antigüedad en días."""
        if self.fecha_ingreso:
            fecha_calculo = self.fecha_cese or date.today()
            return (fecha_calculo - self.fecha_ingreso).days
        return 0
    
    @property
    def antiguedad_texto(self):
        """Retorna la antigüedad en formato texto legible."""
        anos = self.antiguedad_anos
        meses = self.antiguedad_meses % 12
        
        if anos > 0 and meses > 0:
            return f"{anos} año{'s' if anos != 1 else ''} y {meses} mes{'es' if meses != 1 else ''}"
        elif anos > 0:
            return f"{anos} año{'s' if anos != 1 else ''}"
        elif meses > 0:
            return f"{meses} mes{'es' if meses != 1 else ''}"
        else:
            dias = self.antiguedad_dias
            return f"{dias} día{'s' if dias != 1 else ''}"
    
    @property
    def contrato_vigente(self):
        """Verifica si el contrato está vigente."""
        if self.fecha_cese:
            return False
        if self.fecha_fin_contrato:
            return date.today() <= self.fecha_fin_contrato
        return True
    
    @property
    def dias_para_vencimiento(self):
        """Calcula los días restantes para el vencimiento del contrato."""
        if self.fecha_fin_contrato and not self.fecha_cese:
            delta = self.fecha_fin_contrato - date.today()
            return delta.days if delta.days >= 0 else 0
        return None
    
    @property
    def contrato_por_vencer(self):
        """Verifica si el contrato está por vencer (30 días)."""
        dias = self.dias_para_vencimiento
        return dias is not None and 0 <= dias <= 30
    
    @property
    def es_activo(self):
        """Verifica si los datos laborales están activos."""
        return self.estado_datos == 'activo' and not self.fecha_cese
    
    @property
    def tipo_contrato_texto(self):
        """Retorna el tipo de contrato en formato texto."""
        return dict(self.TIPO_CONTRATO_CHOICES).get(self.tipo_contrato, self.tipo_contrato)
    
    @property
    def regimen_laboral_texto(self):
        """Retorna el régimen laboral en formato texto."""
        return dict(self.REGIMEN_LABORAL_CHOICES).get(self.regimen_laboral, self.regimen_laboral)
    
    @property
    def categoria_texto(self):
        """Retorna la categoría en formato texto."""
        return dict(self.CATEGORIA_CHOICES).get(self.categoria, self.categoria)
    
    @property
    def modalidad_trabajo_texto(self):
        """Retorna la modalidad de trabajo en formato texto."""
        return dict(self.MODALIDAD_TRABAJO_CHOICES).get(self.modalidad_trabajo, self.modalidad_trabajo)
    
    @property
    def jornada_laboral_texto(self):
        """Retorna la jornada laboral en formato texto."""
        return dict(self.JORNADA_LABORAL_CHOICES).get(self.jornada_laboral, self.jornada_laboral)
    
    @property
    def horario_completo(self):
        """Retorna el horario completo en formato texto."""
        if self.horario_entrada and self.horario_salida:
            return f"{self.horario_entrada.strftime('%H:%M')} - {self.horario_salida.strftime('%H:%M')}"
        return "No definido"
    
    def calcular_vacaciones_pendientes(self):
        """Calcula los días de vacaciones pendientes."""
        # Implementar lógica de cálculo de vacaciones
        # basado en la antigüedad y días ya tomados
        dias_por_ano = 30  # Días de vacaciones por año
        anos_completos = self.antiguedad_anos
        dias_acumulados = anos_completos * dias_por_ano
        
        # Aquí se restaría los días ya tomados
        # dias_tomados = self.vacaciones_tomadas()
        # return dias_acumulados - dias_tomados
        
        return dias_acumulados
    
    def generar_codigo_empleado(self):
        """Genera un código único para el empleado."""
        area_codigo = self.area.codigo_area[:3].upper() if self.area.codigo_area else 'GEN'
        empleado_numero = str(self.empleado.empleado_id).zfill(4)
        return f"{area_codigo}-{empleado_numero}"
    
    def es_jefe_de(self, empleado):
        """Verifica si es jefe directo de otro empleado."""
        return DatosLaborales.objects.filter(
            empleado=empleado,
            jefe_directo=self.empleado,
            estado_datos='activo'
        ).exists()
    
    def subordinados_directos(self):
        """Obtiene los subordinados directos."""
        return DatosLaborales.objects.filter(
            jefe_directo=self.empleado,
            estado_datos='activo'
        )
    
    def historial_cargos(self):
        """Obtiene el historial de cargos del empleado."""
        return DatosLaborales.objects.filter(
            empleado=self.empleado
        ).order_by('-fecha_inicio_contrato')
    
    def renovar_contrato(self, nueva_fecha_fin, observaciones=None):
        """Renueva el contrato con una nueva fecha de fin."""
        self.fecha_fin_contrato = nueva_fecha_fin
        if observaciones:
            self.observaciones = f"{self.observaciones or ''}\n{observaciones}"
        self.save()
    
    def cesar_empleado(self, fecha_cese, motivo=None):
        """Registra el cese del empleado."""
        self.fecha_cese = fecha_cese
        self.estado_datos = 'inactivo'
        if motivo:
            self.observaciones = f"{self.observaciones or ''}\nCese: {motivo}"
        self.save()            self.observaciones = f"{self.observaciones or ''}\nCese: {motivo}"
        self.save()