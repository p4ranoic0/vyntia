# -*- coding: utf-8 -*-
"""
Modelos de Ubicación - Gestión de historial de ubicaciones de empleados

Contiene la definición del modelo HistorialUbicaciones que registra
el historial de movimientos y desplazamientos de los empleados en la institución.
Basado en la tabla historial_ubicaciones de la base de datos.
"""

from django.db import models
from django.utils import timezone
from datetime import date


class HistorialUbicaciones(models.Model):
    """Modelo para gestionar el historial de ubicaciones y desplazamientos de empleados."""
    
    TIPO_MOVIMIENTO_CHOICES = [
        ('ingreso', 'Ingreso'),
        ('traslado', 'Traslado'),
        ('rotacion', 'Rotación'),
        ('comision', 'Comisión'),
        ('destacamento', 'Destacamento'),
        ('retorno', 'Retorno'),
    ]
    
    ESTADO_UBICACION_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('temporal', 'Temporal'),
    ]
    
    # Campos principales
    ubicacion_id = models.AutoField(
        primary_key=True,
        help_text='ID único del registro de ubicación'
    )
    empleado = models.ForeignKey(
        'Empleado',
        on_delete=models.CASCADE,
        related_name='historial_ubicaciones',
        help_text='ID del empleado'
    )
    area_origen = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        related_name='ubicaciones_origen',
        null=True,
        blank=True,
        help_text='ID del área de origen'
    )
    area_destino = models.ForeignKey(
        'Area',
        on_delete=models.PROTECT,
        related_name='ubicaciones_destino',
        help_text='ID del área de destino'
    )
    
    # Información del movimiento
    tipo_movimiento = models.CharField(
        max_length=20,
        choices=TIPO_MOVIMIENTO_CHOICES,
        help_text='Tipo de movimiento'
    )
    fecha_inicio = models.DateField(
        help_text='Fecha de inicio del movimiento'
    )
    fecha_termino = models.DateField(
        null=True,
        blank=True,
        help_text='Fecha de término del movimiento'
    )
    motivo_movimiento = models.TextField(
        null=True,
        blank=True,
        help_text='Motivo del movimiento'
    )
    
    # Documentación del movimiento
    documento = models.ForeignKey(
        'DocumentosDigitales',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ubicaciones_documento',
        help_text='ID del documento adjunto'
    )
    documento_sustento = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Documento que sustenta el movimiento'
    )
    numero_documento_sustento = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        help_text='Número del documento de sustento'
    )
    
    # Campos de control
    observaciones = models.TextField(
        null=True,
        blank=True,
        help_text='Observaciones adicionales'
    )
    estado_ubicacion = models.CharField(
        max_length=15,
        choices=ESTADO_UBICACION_CHOICES,
        default='activo',
        help_text='Estado de la ubicación'
    )
    registrado_por_usuario = models.ForeignKey(
        'identity.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ubicaciones_registradas',
        help_text='Usuario que registró el movimiento'
    )
    fecha_registro = models.DateTimeField(
        auto_now_add=True,
        help_text='Fecha de registro'
    )
    
    # Manager personalizado
    objects = models.Manager()
    
    class Meta:
        db_table = 'historial_ubicaciones'  # Nombre real de la tabla en MySQL
        verbose_name = 'Historial de Ubicación'
        verbose_name_plural = 'Historial de Ubicaciones'
        indexes = [
            models.Index(fields=['empleado'], name='idx_empleado_id'),
            models.Index(fields=['area_origen'], name='idx_area_origen'),
            models.Index(fields=['area_destino'], name='idx_area_destino'),
            models.Index(fields=['fecha_inicio'], name='idx_fecha_inicio'),
            models.Index(fields=['tipo_movimiento'], name='idx_tipo_movimiento'),
            models.Index(fields=['estado_ubicacion']),
            models.Index(fields=['registrado_por_usuario']),
        ]
        ordering = ['-fecha_inicio', '-fecha_registro']
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.get_tipo_movimiento_display()} ({self.fecha_inicio})"
    
    @property
    def movimiento_completo(self):
        """Retorna la descripción completa del movimiento."""
        origen = self.area_origen.nombre_area if self.area_origen else "Sin área origen"
        destino = self.area_destino.nombre_area if self.area_destino else "Sin área destino"
        
        return f"{self.get_tipo_movimiento_display()}: {origen} → {destino}"
    
    @property
    def duracion_movimiento(self):
        """Calcula la duración del movimiento en días."""
        if self.fecha_termino:
            return (self.fecha_termino - self.fecha_inicio).days
        else:
            return (date.today() - self.fecha_inicio).days
    
    @property
    def es_activa(self):
        """Verifica si la ubicación está activa."""
        return (
            self.estado_ubicacion == 'activo' and
            (self.fecha_termino is None or self.fecha_termino >= date.today())
        )
    
    @property
    def es_movimiento_temporal(self):
        """Verifica si es un movimiento temporal."""
        return self.estado_ubicacion == 'temporal'
    
    @property
    def tipo_movimiento_texto(self):
        """Retorna el tipo de movimiento en formato texto."""
        return dict(self.TIPO_MOVIMIENTO_CHOICES).get(self.tipo_movimiento, self.tipo_movimiento)
    
    @property
    def estado_texto(self):
        """Retorna el estado en formato texto."""
        return dict(self.ESTADO_UBICACION_CHOICES).get(self.estado_ubicacion, self.estado_ubicacion)
    
    @property
    def tiene_documentacion(self):
        """Verifica si el movimiento tiene documentación asociada."""
        return bool(self.documento or self.documento_sustento or self.numero_documento_sustento)
    
    @property
    def documentacion_completa(self):
        """Retorna la información completa de documentación."""
        docs = []
        if self.documento_sustento:
            doc_info = self.documento_sustento
            if self.numero_documento_sustento:
                doc_info += f" N° {self.numero_documento_sustento}"
            docs.append(doc_info)
        
        if self.documento:
            docs.append(f"Documento digital: {self.documento.nombre_archivo}")
        
        return " | ".join(docs) if docs else "Sin documentación"
    
    @property
    def codigo_movimiento(self):
        """Genera un código único para el movimiento."""
        # Generar código automático basado en el movimiento
        tipo_codigo = self.tipo_movimiento[:3].upper()
        area_destino_codigo = self.area_destino.codigo_area[:3].upper() if self.area_destino.codigo_area else 'GEN'
        movimiento_id = str(self.ubicacion_id).zfill(4)
        fecha_codigo = self.fecha_inicio.strftime('%y%m')
        
        return f"{tipo_codigo}-{area_destino_codigo}-{fecha_codigo}-{movimiento_id}"
    
    def finalizar_movimiento(self, fecha_termino=None, observaciones=None):
        """Finaliza el movimiento de ubicación."""
        self.fecha_termino = fecha_termino or date.today()
        self.estado_ubicacion = 'inactivo'
        if observaciones:
            self.observaciones = f"{self.observaciones or ''}\n{observaciones}"
        self.save()
    
    def extender_movimiento(self, nueva_fecha_termino, observaciones=None):
        """Extiende la fecha de término del movimiento."""
        self.fecha_termino = nueva_fecha_termino
        if observaciones:
            self.observaciones = f"{self.observaciones or ''}\n{observaciones}"
        self.save()
    
    def cambiar_estado(self, nuevo_estado, observaciones=None):
        """Cambia el estado del movimiento."""
        self.estado_ubicacion = nuevo_estado
        if observaciones:
            self.observaciones = f"{self.observaciones or ''}\n{observaciones}"
        self.save()
    
    def agregar_documentacion(self, documento_sustento=None, numero_documento=None, documento_digital=None):
        """Agrega documentación al movimiento."""
        if documento_sustento:
            self.documento_sustento = documento_sustento
        if numero_documento:
            self.numero_documento_sustento = numero_documento
        if documento_digital:
            self.documento = documento_digital
        self.save()
    
    def empleados_en_area_destino(self):
        """Obtiene otros empleados activos en la misma área destino."""
        return HistorialUbicaciones.objects.filter(
            area_destino=self.area_destino,
            estado_ubicacion='activo'
        ).exclude(empleado=self.empleado)
    
    def historial_empleado_movimientos(self):
        """Obtiene el historial completo de movimientos del empleado."""
        return HistorialUbicaciones.objects.filter(
            empleado=self.empleado
        ).order_by('-fecha_inicio')
    
    def movimientos_similares(self):
        """Obtiene movimientos similares (mismo tipo y área destino)."""
        return HistorialUbicaciones.objects.filter(
            tipo_movimiento=self.tipo_movimiento,
            area_destino=self.area_destino,
            estado_ubicacion='activo'
        ).exclude(ubicacion_id=self.ubicacion_id)
    
    @classmethod
    def movimientos_activos(cls, tipo_movimiento=None, area_destino=None):
        """Obtiene movimientos activos con filtros opcionales."""
        queryset = cls.objects.filter(estado_ubicacion='activo')
        
        if tipo_movimiento:
            queryset = queryset.filter(tipo_movimiento=tipo_movimiento)
        if area_destino:
            queryset = queryset.filter(area_destino=area_destino)
        
        return queryset
    
    @classmethod
    def empleados_sin_movimiento_activo(cls):
        """Obtiene empleados que no tienen movimiento activo."""
        from .empleado import Empleado
        empleados_con_movimiento = cls.objects.filter(
            estado_ubicacion='activo'
        ).values_list('empleado_id', flat=True)
        
        return Empleado.objects.filter(
            estado_empleado='activo'
        ).exclude(empleado_id__in=empleados_con_movimiento)
    
    @classmethod
    def movimientos_por_periodo(cls, fecha_inicio, fecha_fin):
        """Obtiene movimientos en un período específico."""
        return cls.objects.filter(
            fecha_inicio__range=[fecha_inicio, fecha_fin]
        ).order_by('-fecha_inicio')
    
    @classmethod
    def estadisticas_movimientos(cls):
        """Obtiene estadísticas de movimientos por tipo."""
        from django.db.models import Count
        return cls.objects.values('tipo_movimiento').annotate(
            total=Count('ubicacion_id')
        ).order_by('-total')