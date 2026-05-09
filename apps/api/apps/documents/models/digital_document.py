# -*- coding: utf-8 -*-
"""
Modelo DigitalDocument - Gestión de documentos digitales de empleados

Contiene la definición del modelo DigitalDocument que almacena la información
de documentos digitalizados y archivos asociados a los empleados.
"""

import uuid

from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from datetime import date
import os
# from ..managers import DocumentosDigitalesManager  # Comentado temporalmente para migraciones


def documento_upload_path(instance, filename):
    """Mantiene compatibilidad con migraciones históricas que referencian esta función."""
    empleado_id = getattr(instance, 'empleado_id', None) or 'sin-empleado'
    return f"documentos_empleados/{empleado_id}/{filename}"


class DigitalDocument(models.Model):
    """Modelo para gestionar documentos digitales de los empleados."""
    
    TIPO_DOCUMENTO_CHOICES = [
        ('dni', 'DNI'),
        ('pasaporte', 'Pasaporte'),
        ('carnet_extranjeria', 'Carnet de Extranjería'),
        ('licencia_conducir', 'Licencia de Conducir'),
        ('certificado_nacimiento', 'Certificado de Nacimiento'),
        ('certificado_estudios', 'Certificado de Estudios'),
        ('titulo_profesional', 'Título Profesional'),
        ('diploma', 'Diploma'),
        ('certificado_trabajo', 'Certificado de Trabajo'),
        ('carta_recomendacion', 'Carta de Recomendación'),
        ('cv', 'Curriculum Vitae'),
        ('foto', 'Fotografía'),
        ('certificado_medico', 'Certificado Médico'),
        ('certificado_antecedentes', 'Certificado de Antecedentes'),
        ('declaracion_jurada', 'Declaración Jurada'),
        ('contrato_trabajo', 'Contrato de Trabajo'),
        ('adenda_contrato', 'Adenda de Contrato'),
        ('memorandum', 'Memorándum'),
        ('carta_amonestacion', 'Carta de Amonestación'),
        ('solicitud_vacaciones', 'Solicitud de Vacaciones'),
        ('certificado_capacitacion', 'Certificado de Capacitación'),
        ('evaluacion_desempeno', 'Evaluación de Desempeño'),
        # Documentos institucionales
        ('boleta_pago', 'Boleta de Pago'),
        ('constancia_trabajo', 'Constancia de Trabajo'),
        ('constancia_participacion', 'Constancia de Participación'),
        ('constancia_haberes', 'Constancia de Haberes'),
        ('resolucion_encargatura', 'Resolución de Encargatura'),
        ('resolucion_licencia', 'Resolución de Licencia'),
        ('resolucion_sancion', 'Resolución de Sanción'),
        ('carta_cese', 'Carta de Cese'),
        ('otros', 'Otros'),
    ]
    
    CATEGORIA_CHOICES = [
        ('personal', 'Personal'),
        ('academico', 'Académico'),
        ('laboral', 'Laboral'),
        ('medico', 'Médico'),
        ('legal', 'Legal'),
        ('administrativo', 'Administrativo'),
        ('capacitacion', 'Capacitación'),
        ('evaluacion', 'Evaluación'),
        ('remuneraciones', 'Remuneraciones'),
        ('ubicacion', 'Ubicacion'),
        ('otros', 'Otros'),
    ]
    
    ESTADO_DOCUMENTO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('vencido', 'Vencido'),
        ('pendiente_revision', 'Pendiente de Revisión'),
        ('aprobado', 'Aprobado'),
        ('rechazado', 'Rechazado'),
        ('archivado', 'Archivado'),
    ]
    
    NIVEL_ACCESO_CHOICES = [
        ('publico', 'Público'),
        ('restringido', 'Restringido'),
        ('confidencial', 'Confidencial'),
        ('muy_confidencial', 'Muy Confidencial'),
    ]
    
    FORMATO_ARCHIVO_CHOICES = [
        ('pdf', 'PDF'),
        ('jpg', 'JPG'),
        ('jpeg', 'JPEG'),
        ('png', 'PNG'),
        ('doc', 'DOC'),
        ('docx', 'DOCX'),
        ('xls', 'XLS'),
        ('xlsx', 'XLSX'),
        ('txt', 'TXT'),
        ('zip', 'ZIP'),
        ('rar', 'RAR'),
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
    empleado = models.ForeignKey(
        'employees.Employee',
        on_delete=models.CASCADE,
        related_name='documentos_digitales'
    )
    
    # Información del documento
    tipo_documento = models.CharField(max_length=30, choices=TIPO_DOCUMENTO_CHOICES)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    nombre_documento = models.CharField(max_length=200)
    descripcion = models.TextField(null=True, blank=True)
    
    # Archivo
    archivo = models.FileField(
        upload_to='documentos_empleados/%Y/%m/',
        validators=[FileExtensionValidator(
            allowed_extensions=['pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx', 'xls', 'xlsx', 'txt', 'zip', 'rar']
        )]
    )
    nombre_archivo_original = models.CharField(max_length=255)
    formato_archivo = models.CharField(max_length=10, choices=FORMATO_ARCHIVO_CHOICES)
    tamano_archivo = models.BigIntegerField(help_text="Tamaño en bytes")
    
    # Metadatos del documento
    numero_documento = models.CharField(max_length=100, null=True, blank=True)
    fecha_emision = models.DateField(null=True, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    entidad_emisora = models.CharField(max_length=200, null=True, blank=True)
    
    # Control de acceso y seguridad
    nivel_acceso = models.CharField(max_length=20, choices=NIVEL_ACCESO_CHOICES, default='restringido')
    requiere_autorizacion = models.BooleanField(default=False)
    es_documento_oficial = models.BooleanField(default=False)
    es_copia_certificada = models.BooleanField(default=False)
    
    # Versioning
    version = models.CharField(max_length=10, default='1.0')
    documento_padre = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='versiones'
    )
    familiar = models.ForeignKey(
        'employees.FamilyMember',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='documentos',
    )
    es_version_actual = models.BooleanField(default=True)
    
    # Estado y validación
    estado_documento = models.CharField(max_length=20, choices=ESTADO_DOCUMENTO_CHOICES, default='activo')
    validado_por = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_validados'
    )
    fecha_validacion = models.DateTimeField(null=True, blank=True)
    observaciones_validacion = models.TextField(null=True, blank=True)
    
    # Información de digitalización
    digitalizado_por = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_digitalizados'
    )
    fecha_digitalizacion = models.DateTimeField(auto_now_add=True)
    calidad_digitalizacion = models.CharField(
        max_length=10,
        choices=[('alta', 'Alta'), ('media', 'Media'), ('baja', 'Baja')],
        default='media'
    )
    
    # Campos de auditoría
    fecha_subida = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')
    subido_por = models.ForeignKey(
        'identity.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documentos_subidos'
    )
    
    # Información adicional
    palabras_clave = models.CharField(max_length=500, null=True, blank=True)
    notas_internas = models.TextField(null=True, blank=True)
    es_confidencial = models.BooleanField(default=False)
    requiere_firma_digital = models.BooleanField(default=False)
    
    # Manager personalizado
    # objects = DocumentosDigitalesManager()
    
    class Meta:
        db_table = 'documentos_digitales'  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['tipo_documento']),
            models.Index(fields=['categoria']),
            models.Index(fields=['estado_documento']),
            models.Index(fields=['fecha_vencimiento']),
            models.Index(fields=['nivel_acceso']),
            models.Index(fields=['es_version_actual']),
            models.Index(fields=['fecha_subida']),
            models.Index(fields=['formato_archivo']),
            models.Index(fields=['es_documento_oficial']),
            models.Index(fields=['validado_por']),
            models.Index(fields=['digitalizado_por']),
        ]
        unique_together = [['empleado', 'tipo_documento', 'numero_documento', 'version']]
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.nombre_documento}"
    
    @property
    def tipo_documento_texto(self):
        """Retorna el tipo de documento en formato texto."""
        return dict(self.TIPO_DOCUMENTO_CHOICES).get(self.tipo_documento, self.tipo_documento)
    
    @property
    def categoria_texto(self):
        """Retorna la categoría en formato texto."""
        return dict(self.CATEGORIA_CHOICES).get(self.categoria, self.categoria)
    
    @property
    def estado_texto(self):
        """Retorna el estado en formato texto."""
        return dict(self.ESTADO_DOCUMENTO_CHOICES).get(self.estado_documento, self.estado_documento)
    
    @property
    def nivel_acceso_texto(self):
        """Retorna el nivel de acceso en formato texto."""
        return dict(self.NIVEL_ACCESO_CHOICES).get(self.nivel_acceso, self.nivel_acceso)
    
    @property
    def tamano_archivo_legible(self):
        """Retorna el tamaño del archivo en formato legible (solo lectura)."""
        if not self.tamano_archivo:
            return "0 B"

        size = float(self.tamano_archivo)
        for unidad in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unidad}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def extension_archivo(self):
        """Retorna la extensión del archivo."""
        if self.archivo:
            return os.path.splitext(self.archivo.name)[1].lower().replace('.', '')
        return self.formato_archivo
    
    @property
    def esta_vencido(self):
        """Verifica si el documento está vencido."""
        if self.fecha_vencimiento:
            return date.today() > self.fecha_vencimiento
        return False
    
    @property
    def dias_para_vencimiento(self):
        """Calcula los días restantes para el vencimiento."""
        if self.fecha_vencimiento:
            delta = self.fecha_vencimiento - date.today()
            return delta.days
        return None
    
    @property
    def proximo_a_vencer(self):
        """Verifica si está próximo a vencer (30 días)."""
        dias = self.dias_para_vencimiento
        return dias is not None and 0 <= dias <= 30
    
    @property
    def es_imagen(self):
        """Verifica si es un archivo de imagen."""
        extensiones_imagen = ['jpg', 'jpeg', 'png', 'gif', 'bmp']
        return self.formato_archivo.lower() in extensiones_imagen
    
    @property
    def es_pdf(self):
        """Verifica si es un archivo PDF."""
        return self.formato_archivo.lower() == 'pdf'
    
    @property
    def es_documento_office(self):
        """Verifica si es un documento de Office."""
        extensiones_office = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
        return self.formato_archivo.lower() in extensiones_office
    
    @property
    def url_descarga(self):
        """Retorna la URL de descarga del archivo."""
        if self.archivo:
            return self.archivo.url
        return None
    
    @property
    def informacion_validacion(self):
        """Retorna información de validación."""
        if self.validado_por and self.fecha_validacion:
            return f"Validado por {self.validado_por.nombre_completo} el {self.fecha_validacion.strftime('%d/%m/%Y')}"
        return "Sin validar"
    
    @property
    def informacion_version(self):
        """Retorna información de versión."""
        info = f"v{self.version}"
        if not self.es_version_actual:
            info += " (Versión anterior)"
        if self.documento_padre:
            info += f" - Basado en documento #{self.documento_padre.id}"
        return info
    
    @property
    def requiere_atencion(self):
        """Verifica si requiere atención inmediata."""
        return (
            self.esta_vencido or
            self.proximo_a_vencer or
            self.estado_documento == 'pendiente_revision' or
            (self.requiere_autorizacion and not self.validado_por)
        )
    
    @property
    def nivel_seguridad(self):
        """Retorna el nivel de seguridad del documento."""
        if self.es_confidencial or self.nivel_acceso in ['confidencial', 'muy_confidencial']:
            return 'Alto'
        elif self.nivel_acceso == 'restringido':
            return 'Medio'
        else:
            return 'Bajo'
    
    def validar_documento(self, usuario, observaciones=None):
        """Valida el documento."""
        self.validado_por = usuario
        self.fecha_validacion = timezone.now()
        self.estado_documento = 'aprobado'
        if observaciones:
            self.observaciones_validacion = observaciones
        self.save()
    
    def rechazar_documento(self, usuario, motivo):
        """Rechaza el documento."""
        self.validado_por = usuario
        self.fecha_validacion = timezone.now()
        self.estado_documento = 'rechazado'
        self.observaciones_validacion = motivo
        self.save()
    
    def crear_nueva_version(self, archivo, usuario, descripcion_cambios=None):
        """Crea una nueva versión del documento."""
        # Marcar versión actual como no actual
        self.es_version_actual = False
        self.save()
        
        # Crear nueva versión
        nueva_version = DigitalDocument.objects.create(
            empleado=self.empleado,
            tipo_documento=self.tipo_documento,
            categoria=self.categoria,
            nombre_documento=self.nombre_documento,
            descripcion=descripcion_cambios or self.descripcion,
            archivo=archivo,
            nombre_archivo_original=archivo.name,
            formato_archivo=os.path.splitext(archivo.name)[1].lower().replace('.', ''),
            tamano_archivo=archivo.size,
            numero_documento=self.numero_documento,
            fecha_emision=self.fecha_emision,
            fecha_vencimiento=self.fecha_vencimiento,
            entidad_emisora=self.entidad_emisora,
            nivel_acceso=self.nivel_acceso,
            requiere_autorizacion=self.requiere_autorizacion,
            es_documento_oficial=self.es_documento_oficial,
            version=self._generar_nueva_version(),
            documento_padre=self,
            es_version_actual=True,
            digitalizado_por=usuario,
            subido_por=usuario
        )
        
        return nueva_version
    
    def _generar_nueva_version(self):
        """Genera el número de la nueva versión."""
        try:
            version_actual = float(self.version)
            nueva_version = version_actual + 0.1
            return f"{nueva_version:.1f}"
        except ValueError:
            return "1.1"
    
    def marcar_como_vencido(self):
        """Marca el documento como vencido."""
        self.estado_documento = 'vencido'
        self.save()
    
    def renovar_documento(self, nueva_fecha_vencimiento, archivo=None):
        """Renueva el documento con nueva fecha de vencimiento."""
        self.fecha_vencimiento = nueva_fecha_vencimiento
        self.estado_documento = 'activo'
        
        if archivo:
            self.archivo = archivo
            self.nombre_archivo_original = archivo.name
            self.tamano_archivo = archivo.size
            self.updated_at = timezone.now()
        
        self.save()
    
    def archivar_documento(self, motivo=None):
        """Archiva el documento."""
        self.estado_documento = 'archivado'
        self.es_version_actual = False
        if motivo:
            self.notas_internas = f"{self.notas_internas or ''}\nArchivado: {motivo}"
        self.save()
    
    def cambiar_nivel_acceso(self, nuevo_nivel, usuario, justificacion=None):
        """Cambia el nivel de acceso del documento."""
        nivel_anterior = self.nivel_acceso
        self.nivel_acceso = nuevo_nivel
        
        nota = f"Nivel de acceso cambiado de '{nivel_anterior}' a '{nuevo_nivel}' por {usuario.nombre_completo}"
        if justificacion:
            nota += f". Justificación: {justificacion}"
        
        self.notas_internas = f"{self.notas_internas or ''}\n{nota}"
        self.save()
    
    def agregar_palabras_clave(self, palabras):
        """Agrega palabras clave para búsqueda."""
        if isinstance(palabras, list):
            palabras = ', '.join(palabras)
        
        if self.palabras_clave:
            self.palabras_clave += f", {palabras}"
        else:
            self.palabras_clave = palabras
        
        self.save()
    
    @classmethod
    def por_tipo_documento(cls, tipo_documento, empleado=None):
        """Obtiene documentos por tipo."""
        queryset = cls.objects.filter(
            tipo_documento=tipo_documento,
            es_version_actual=True,
            estado_documento='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset
    
    @classmethod
    def documentos_vencidos(cls):
        """Obtiene documentos vencidos."""
        return cls.objects.filter(
            fecha_vencimiento__lt=date.today(),
            es_version_actual=True,
            estado_documento='activo'
        )
    
    @classmethod
    def proximos_a_vencer(cls, dias=30):
        """Obtiene documentos próximos a vencer."""
        from datetime import timedelta
        fecha_limite = date.today() + timedelta(days=dias)
        
        return cls.objects.filter(
            fecha_vencimiento__lte=fecha_limite,
            fecha_vencimiento__gte=date.today(),
            es_version_actual=True,
            estado_documento='activo'
        )
    
    @classmethod
    def pendientes_validacion(cls):
        """Obtiene documentos pendientes de validación."""
        return cls.objects.filter(
            estado_documento='pendiente_revision',
            es_version_actual=True
        )
    
    @classmethod
    def por_categoria(cls, categoria, empleado=None):
        """Obtiene documentos por categoría."""
        queryset = cls.objects.filter(
            categoria=categoria,
            es_version_actual=True,
            estado_documento='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset
    
    @classmethod
    def buscar_por_palabras_clave(cls, palabras):
        """Busca documentos por palabras clave."""
        return cls.objects.filter(
            palabras_clave__icontains=palabras,
            es_version_actual=True,
            estado_documento='activo'
        )
    
    @classmethod
    def documentos_confidenciales(cls):
        """Obtiene documentos confidenciales."""
        return cls.objects.filter(
            models.Q(es_confidencial=True) |
            models.Q(nivel_acceso__in=['confidencial', 'muy_confidencial']),
            es_version_actual=True
        )
    
    @classmethod
    def estadisticas_por_tipo(cls):
        """Obtiene estadísticas por tipo de documento."""
        from django.db.models import Count
        
        return cls.objects.filter(
            es_version_actual=True,
            estado_documento='activo'
        ).values(
            'tipo_documento'
        ).annotate(
            total=Count('id')
        ).order_by('tipo_documento')
    
    @classmethod
    def documentos_por_empleado(cls, empleado):
        """Obtiene todos los documentos de un empleado."""
        return cls.objects.filter(
            empleado=empleado,
            es_version_actual=True
        ).order_by('categoria', 'tipo_documento', 'fecha_subida')
    
    def save(self, *args, **kwargs):
        """Override del método save para procesar el archivo."""
        if self.archivo and not self.tamano_archivo:
            self.tamano_archivo = self.archivo.size
        
        if self.archivo and not self.nombre_archivo_original:
            self.nombre_archivo_original = self.archivo.name
        
        if self.archivo and not self.formato_archivo:
            self.formato_archivo = os.path.splitext(self.archivo.name)[1].lower().replace('.', '')
        
        super().save(*args, **kwargs)