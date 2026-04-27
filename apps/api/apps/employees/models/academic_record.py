# -*- coding: utf-8 -*-
"""
Modelo AcademicRecord - Gestión de formación académica de empleados

Contiene la definición del modelo AcademicRecord que almacena la información
educativa y de formación profesional de los empleados.
"""

from django.db import models
from django.utils import timezone
from datetime import date
# from ..managers import DatosAcademicosManager  # Comentado temporalmente para migraciones


class AcademicRecord(models.Model):
    """Modelo para gestionar la formación académica de los empleados."""
    
    NIVEL_EDUCATIVO_CHOICES = [
        ('primaria', 'Primaria'),
        ('secundaria', 'Secundaria'),
        ('tecnico_basico', 'Técnico Básico'),
        ('tecnico_superior', 'Técnico Superior'),
        ('universitario', 'Universitario'),
        ('bachiller', 'Bachiller'),
        ('titulo_profesional', 'Título Profesional'),
        ('especializacion', 'Especialización'),
        ('maestria', 'Maestría'),
        ('doctorado', 'Doctorado'),
        ('diplomado', 'Diplomado'),
        ('curso_especializado', 'Curso Especializado'),
    ]
    
    ESTADO_ESTUDIOS_CHOICES = [
        ('completo', 'Completo'),
        ('incompleto', 'Incompleto'),
        ('en_curso', 'En Curso'),
        ('trunco', 'Trunco'),
        ('convalidado', 'Convalidado'),
    ]
    
    TIPO_INSTITUCION_CHOICES = [
        ('publica', 'Pública'),
        ('privada', 'Privada'),
        ('internacional', 'Internacional'),
        ('virtual', 'Virtual'),
        ('presencial', 'Presencial'),
        ('semipresencial', 'Semipresencial'),
    ]
    
    MODALIDAD_CHOICES = [
        ('presencial', 'Presencial'),
        ('virtual', 'Virtual'),
        ('semipresencial', 'Semipresencial'),
        ('a_distancia', 'A Distancia'),
    ]
    
    ESTADO_REGISTRO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('verificado', 'Verificado'),
        ('pendiente_verificacion', 'Pendiente de Verificación'),
    ]
    
    # Campos principales
    academico_id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(
        'Employee',
        on_delete=models.CASCADE,
        related_name='formacion_academica'
    )
    
    # Información del estudio
    nivel_educativo = models.CharField(max_length=25, choices=NIVEL_EDUCATIVO_CHOICES)
    nombre_institucion = models.CharField(max_length=200)
    tipo_institucion = models.CharField(max_length=20, choices=TIPO_INSTITUCION_CHOICES)
    modalidad_estudio = models.CharField(max_length=20, choices=MODALIDAD_CHOICES, default='presencial')
    
    # Información del programa
    nombre_carrera = models.CharField(max_length=200)
    codigo_carrera = models.CharField(max_length=50, null=True, blank=True)
    area_conocimiento = models.CharField(max_length=100, null=True, blank=True)
    duracion_anos = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    duracion_semestres = models.IntegerField(null=True, blank=True)
    
    # Fechas importantes
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    fecha_graduacion = models.DateField(null=True, blank=True)
    
    # Estado y resultados
    estado_estudios = models.CharField(max_length=20, choices=ESTADO_ESTUDIOS_CHOICES)
    promedio_ponderado = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    creditos_aprobados = models.IntegerField(null=True, blank=True)
    creditos_totales = models.IntegerField(null=True, blank=True)
    
    # Información de titulación
    numero_titulo = models.CharField(max_length=100, null=True, blank=True)
    numero_diploma = models.CharField(max_length=100, null=True, blank=True)
    numero_colegiatura = models.CharField(max_length=50, null=True, blank=True)
    colegio_profesional = models.CharField(max_length=150, null=True, blank=True)
    
    # Ubicación de la institución
    pais_institucion = models.CharField(max_length=100, default='Perú')
    departamento_institucion = models.CharField(max_length=100, null=True, blank=True)
    provincia_institucion = models.CharField(max_length=100, null=True, blank=True)
    distrito_institucion = models.CharField(max_length=100, null=True, blank=True)
    
    # Información adicional
    mencion_especialidad = models.CharField(max_length=200, null=True, blank=True)
    tesis_titulo = models.CharField(max_length=300, null=True, blank=True)
    reconocimientos = models.TextField(null=True, blank=True)
    
    # Documentos
    ruta_certificado = models.CharField(max_length=255, null=True, blank=True)
    ruta_titulo = models.CharField(max_length=255, null=True, blank=True)
    ruta_diploma = models.CharField(max_length=255, null=True, blank=True)
    documento = models.ForeignKey(
        'documents.DigitalDocument',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='dato_academico',
    )

    # Verificación
    verificado_sunedu = models.BooleanField(default=False)
    fecha_verificacion_sunedu = models.DateField(null=True, blank=True)
    codigo_verificacion_sunedu = models.CharField(max_length=100, null=True, blank=True)
    
    # Campos de control
    estado_registro = models.CharField(max_length=25, choices=ESTADO_REGISTRO_CHOICES, default='activo')
    observaciones = models.TextField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Manager personalizado
    # objects = DatosAcademicosManager()  # Comentado temporalmente para migraciones
    
    class Meta:
        db_table = 'datos_academicos'  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['nivel_educativo']),
            models.Index(fields=['nombre_institucion']),
            models.Index(fields=['nombre_carrera']),
            models.Index(fields=['estado_estudios']),
            models.Index(fields=['fecha_graduacion']),
            models.Index(fields=['area_conocimiento']),
            models.Index(fields=['tipo_institucion']),
            models.Index(fields=['modalidad_estudio']),
            models.Index(fields=['verificado_sunedu']),
            models.Index(fields=['estado_registro']),
        ]
        unique_together = [['empleado', 'nivel_educativo', 'nombre_carrera', 'nombre_institucion']]
    
    def __str__(self):
        return f"{self.empleado.nombre_completo} - {self.nivel_educativo_texto}: {self.nombre_carrera}"
    
    @property
    def nivel_educativo_texto(self):
        """Retorna el nivel educativo en formato texto."""
        return dict(self.NIVEL_EDUCATIVO_CHOICES).get(self.nivel_educativo, self.nivel_educativo)
    
    @property
    def estado_estudios_texto(self):
        """Retorna el estado de estudios en formato texto."""
        return dict(self.ESTADO_ESTUDIOS_CHOICES).get(self.estado_estudios, self.estado_estudios)
    
    @property
    def tipo_institucion_texto(self):
        """Retorna el tipo de institución en formato texto."""
        return dict(self.TIPO_INSTITUCION_CHOICES).get(self.tipo_institucion, self.tipo_institucion)
    
    @property
    def modalidad_texto(self):
        """Retorna la modalidad en formato texto."""
        return dict(self.MODALIDAD_CHOICES).get(self.modalidad_estudio, self.modalidad_estudio)
    
    @property
    def duracion_completa(self):
        """Retorna la duración completa del programa."""
        duracion = []
        if self.duracion_anos:
            duracion.append(f"{self.duracion_anos} año{'s' if self.duracion_anos != 1 else ''}")
        if self.duracion_semestres:
            duracion.append(f"{self.duracion_semestres} semestre{'s' if self.duracion_semestres != 1 else ''}")
        
        return " / ".join(duracion) if duracion else "No especificada"
    
    @property
    def periodo_estudios(self):
        """Retorna el período de estudios."""
        if self.fecha_inicio:
            inicio = self.fecha_inicio.strftime('%Y')
            if self.fecha_fin:
                fin = self.fecha_fin.strftime('%Y')
                return f"{inicio} - {fin}"
            elif self.estado_estudios == 'en_curso':
                return f"{inicio} - Actualidad"
            else:
                return f"Desde {inicio}"
        return "No especificado"
    
    @property
    def es_graduado(self):
        """Verifica si está graduado."""
        return self.estado_estudios == 'completo' and self.fecha_graduacion is not None
    
    @property
    def es_estudiante_activo(self):
        """Verifica si es estudiante activo."""
        return self.estado_estudios == 'en_curso'
    
    @property
    def porcentaje_avance(self):
        """Calcula el porcentaje de avance en los estudios."""
        if self.creditos_totales and self.creditos_aprobados:
            return round((self.creditos_aprobados / self.creditos_totales) * 100, 2)
        return None
    
    @property
    def anos_desde_graduacion(self):
        """Calcula los años transcurridos desde la graduación."""
        if self.fecha_graduacion:
            delta = date.today() - self.fecha_graduacion
            return delta.days // 365
        return None
    
    @property
    def ubicacion_institucion(self):
        """Retorna la ubicación completa de la institución."""
        ubicacion = []
        if self.distrito_institucion:
            ubicacion.append(self.distrito_institucion)
        if self.provincia_institucion:
            ubicacion.append(self.provincia_institucion)
        if self.departamento_institucion:
            ubicacion.append(self.departamento_institucion)
        if self.pais_institucion and self.pais_institucion != 'Perú':
            ubicacion.append(self.pais_institucion)
        
        return ", ".join(ubicacion) if ubicacion else "No especificada"
    
    @property
    def informacion_colegiatura(self):
        """Retorna la información de colegiatura."""
        if self.numero_colegiatura and self.colegio_profesional:
            return f"{self.colegio_profesional} - N° {self.numero_colegiatura}"
        elif self.colegio_profesional:
            return self.colegio_profesional
        return "No colegiado"
    
    @property
    def documentos_disponibles(self):
        """Lista los documentos disponibles."""
        documentos = []
        if self.ruta_certificado:
            documentos.append('Certificado')
        if self.ruta_titulo:
            documentos.append('Título')
        if self.ruta_diploma:
            documentos.append('Diploma')
        
        return documentos
    
    @property
    def requiere_verificacion(self):
        """Verifica si requiere verificación SUNEDU."""
        niveles_universitarios = ['universitario', 'bachiller', 'titulo_profesional', 'maestria', 'doctorado']
        return (
            self.nivel_educativo in niveles_universitarios and
            not self.verificado_sunedu and
            self.pais_institucion == 'Perú'
        )
    
    @property
    def es_nivel_superior(self):
        """Verifica si es educación superior."""
        niveles_superiores = [
            'tecnico_superior', 'universitario', 'bachiller', 'titulo_profesional',
            'especializacion', 'maestria', 'doctorado'
        ]
        return self.nivel_educativo in niveles_superiores
    
    @property
    def es_postgrado(self):
        """Verifica si es estudios de postgrado."""
        return self.nivel_educativo in ['especializacion', 'maestria', 'doctorado']
    
    def marcar_graduado(self, fecha_graduacion=None, numero_titulo=None):
        """Marca como graduado."""
        self.estado_estudios = 'completo'
        self.fecha_graduacion = fecha_graduacion or date.today()
        if numero_titulo:
            self.numero_titulo = numero_titulo
        if not self.fecha_fin:
            self.fecha_fin = self.fecha_graduacion
        self.save()
    
    def marcar_en_curso(self):
        """Marca como en curso."""
        self.estado_estudios = 'en_curso'
        self.fecha_fin = None
        self.fecha_graduacion = None
        self.save()
    
    def marcar_incompleto(self, fecha_fin=None, motivo=None):
        """Marca como incompleto."""
        self.estado_estudios = 'incompleto'
        self.fecha_fin = fecha_fin or date.today()
        if motivo:
            self.observaciones = f"{self.observaciones or ''}\nIncompleto: {motivo}"
        self.save()
    
    def verificar_sunedu(self, codigo_verificacion=None):
        """Marca como verificado por SUNEDU."""
        self.verificado_sunedu = True
        self.fecha_verificacion_sunedu = date.today()
        if codigo_verificacion:
            self.codigo_verificacion_sunedu = codigo_verificacion
        self.save()
    
    def actualizar_promedio(self, nuevo_promedio):
        """Actualiza el promedio ponderado."""
        self.promedio_ponderado = nuevo_promedio
        self.save()
    
    def actualizar_creditos(self, creditos_aprobados, creditos_totales=None):
        """Actualiza los créditos aprobados."""
        self.creditos_aprobados = creditos_aprobados
        if creditos_totales:
            self.creditos_totales = creditos_totales
        self.save()
    
    def agregar_colegiatura(self, numero_colegiatura, colegio_profesional):
        """Agrega información de colegiatura."""
        self.numero_colegiatura = numero_colegiatura
        self.colegio_profesional = colegio_profesional
        self.save()
    
    def agregar_documento(self, tipo_documento, ruta_archivo):
        """Agrega un documento."""
        if tipo_documento == 'certificado':
            self.ruta_certificado = ruta_archivo
        elif tipo_documento == 'titulo':
            self.ruta_titulo = ruta_archivo
        elif tipo_documento == 'diploma':
            self.ruta_diploma = ruta_archivo
        self.save()
    
    @classmethod
    def por_nivel_educativo(cls, nivel_educativo, empleado=None):
        """Obtiene registros por nivel educativo."""
        queryset = cls.objects.filter(
            nivel_educativo=nivel_educativo,
            estado_registro='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset
    
    @classmethod
    def graduados_recientes(cls, anos=5):
        """Obtiene graduados recientes."""
        from datetime import timedelta
        fecha_limite = date.today() - timedelta(days=anos * 365)
        
        return cls.objects.filter(
            estado_estudios='completo',
            fecha_graduacion__gte=fecha_limite,
            estado_registro='activo'
        )
    
    @classmethod
    def estudiantes_activos(cls):
        """Obtiene estudiantes activos."""
        return cls.objects.filter(
            estado_estudios='en_curso',
            estado_registro='activo'
        )
    
    @classmethod
    def pendientes_verificacion_sunedu(cls):
        """Obtiene registros pendientes de verificación SUNEDU."""
        niveles_universitarios = ['universitario', 'bachiller', 'titulo_profesional', 'maestria', 'doctorado']
        
        return cls.objects.filter(
            nivel_educativo__in=niveles_universitarios,
            verificado_sunedu=False,
            pais_institucion='Perú',
            estado_registro='activo'
        )
    
    @classmethod
    def por_area_conocimiento(cls, area_conocimiento):
        """Obtiene registros por área de conocimiento."""
        return cls.objects.filter(
            area_conocimiento__icontains=area_conocimiento,
            estado_registro='activo'
        )
    
    @classmethod
    def profesionales_colegiados(cls):
        """Obtiene profesionales colegiados."""
        return cls.objects.filter(
            numero_colegiatura__isnull=False,
            colegio_profesional__isnull=False,
            estado_registro='activo'
        ).exclude(
            numero_colegiatura='',
            colegio_profesional=''
        )
    
    @classmethod
    def estadisticas_por_nivel(cls):
        """Obtiene estadísticas por nivel educativo."""
        from django.db.models import Count
        
        return cls.objects.filter(
            estado_registro='activo'
        ).values(
            'nivel_educativo'
        ).annotate(
            total=Count('academico_id')
        ).order_by('nivel_educativo')