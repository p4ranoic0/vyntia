# -*- coding: utf-8 -*-
"""
Modelo FamilyMember - Gestión de información familiar de empleados

Contiene la definición del modelo FamilyMember que almacena la información
de los familiares de los empleados para efectos de beneficios y contactos de emergencia.
"""

import uuid

from django.db import models
from django.utils import timezone
from datetime import date
# from ..managers import DatosFamiliaresManager  # Comentado temporalmente para migraciones


class FamilyMember(models.Model):
    """Modelo para gestionar la información familiar de los empleados."""
    
    PARENTESCO_CHOICES = [
        ('conyuge', 'Cónyuge'),
        ('conviviente', 'Conviviente'),
        ('hijo', 'Hijo(a)'),
        ('padre', 'Padre'),
        ('madre', 'Madre'),
        ('hermano', 'Hermano(a)'),
        ('abuelo', 'Abuelo(a)'),
        ('nieto', 'Nieto(a)'),
        ('tio', 'Tío(a)'),
        ('primo', 'Primo(a)'),
        ('suegro', 'Suegro(a)'),
        ('cuñado', 'Cuñado(a)'),
        ('yerno_nuera', 'Yerno/Nuera'),
        ('otro', 'Otro'),
    ]
    
    TIPO_DOCUMENTO_CHOICES = [
        ('DNI', 'DNI'),
        ('CE', 'Carné de Extranjería'),
        ('PASAPORTE', 'Pasaporte'),
        ('PARTIDA_NACIMIENTO', 'Partida de Nacimiento'),
        ('OTROS', 'Otros'),
    ]
    
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
        ('otro', 'Otro'),
        ('no_especifica', 'No especifica'),
    ]
    
    ESTADO_CIVIL_CHOICES = [
        ('soltero', 'Soltero'),
        ('casado', 'Casado'),
        ('divorciado', 'Divorciado'),
        ('viudo', 'Viudo'),
        ('conviviente', 'Conviviente'),
    ]
    
    NIVEL_EDUCATIVO_CHOICES = [
        ('sin_estudios', 'Sin Estudios'),
        ('primaria_incompleta', 'Primaria Incompleta'),
        ('primaria_completa', 'Primaria Completa'),
        ('secundaria_incompleta', 'Secundaria Incompleta'),
        ('secundaria_completa', 'Secundaria Completa'),
        ('tecnico', 'Técnico'),
        ('universitario_incompleto', 'Universitario Incompleto'),
        ('universitario_completo', 'Universitario Completo'),
        ('postgrado', 'Postgrado'),
    ]
    
    ESTADO_FAMILIAR_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('fallecido', 'Fallecido'),
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
        'Employee',
        on_delete=models.CASCADE,
        related_name='familiares'
    )
    
    # Información personal del familiar
    nombres_familiar = models.CharField(max_length=100)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100)
    tipo_documento = models.CharField(max_length=20, choices=TIPO_DOCUMENTO_CHOICES, default='DNI')
    numero_documento = models.CharField(max_length=20)
    fecha_nacimiento = models.DateField()
    genero_familiar = models.CharField(max_length=15, choices=GENERO_CHOICES)
    
    # Relación familiar
    parentesco = models.CharField(max_length=20, choices=PARENTESCO_CHOICES)
    es_dependiente = models.BooleanField(default=False)
    es_beneficiario = models.BooleanField(default=False)
    es_contacto_emergencia = models.BooleanField(default=False)
    
    # Información adicional
    estado_civil = models.CharField(max_length=15, choices=ESTADO_CIVIL_CHOICES, null=True, blank=True)
    nivel_educativo = models.CharField(max_length=25, choices=NIVEL_EDUCATIVO_CHOICES, null=True, blank=True)
    ocupacion = models.CharField(max_length=100, null=True, blank=True)
    centro_trabajo = models.CharField(max_length=150, null=True, blank=True)
    
    # Información de contacto
    telefono_familiar = models.CharField(max_length=20, null=True, blank=True)
    correo_familiar = models.EmailField(max_length=150, null=True, blank=True)
    direccion_familiar = models.CharField(max_length=200, null=True, blank=True)
    distrito_familiar = models.CharField(max_length=100, null=True, blank=True)
    provincia_familiar = models.CharField(max_length=100, null=True, blank=True)
    departamento_familiar = models.CharField(max_length=100, null=True, blank=True)
    
    # Información de salud (para dependientes)
    tiene_seguro_salud = models.BooleanField(default=False)
    tipo_seguro_salud = models.CharField(max_length=50, null=True, blank=True)
    numero_seguro = models.CharField(max_length=30, null=True, blank=True)
    centro_salud_asignado = models.CharField(max_length=100, null=True, blank=True)
    
    # Información de discapacidad
    tiene_discapacidad = models.BooleanField(default=False)
    tipo_discapacidad = models.CharField(max_length=100, null=True, blank=True)
    grado_discapacidad = models.CharField(max_length=20, null=True, blank=True)
    certificado_discapacidad = models.CharField(max_length=50, null=True, blank=True)
    
    # Fechas importantes para beneficios
    fecha_inicio_dependencia = models.DateField(null=True, blank=True)
    fecha_fin_dependencia = models.DateField(null=True, blank=True)
    
    # Campos de control
    estado_familiar = models.CharField(max_length=15, choices=ESTADO_FAMILIAR_CHOICES, default='activo')
    observaciones = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_column='fecha_registro')
    updated_at = models.DateTimeField(auto_now=True, db_column='fecha_actualizacion')
    
    # Manager personalizado
    # objects = DatosFamiliaresManager()  # Comentado temporalmente para migraciones
    
    class Meta:
        db_table = 'datos_familiares'  # Nombre real de la tabla en MySQL
        indexes = [
            models.Index(fields=['empleado']),
            models.Index(fields=['parentesco']),
            models.Index(fields=['numero_documento']),
            models.Index(fields=['fecha_nacimiento']),
            models.Index(fields=['es_dependiente']),
            models.Index(fields=['es_beneficiario']),
            models.Index(fields=['es_contacto_emergencia']),
            models.Index(fields=['estado_familiar']),
            models.Index(fields=['genero_familiar']),
            models.Index(fields=['tipo_documento']),
        ]
        unique_together = [['tenant', 'empleado', 'numero_documento']]
    
    def __str__(self):
        return f"{self.nombre_completo} - {self.parentesco_texto} de {self.empleado.nombre_completo}"
    
    @property
    def nombre_completo(self):
        """Retorna el nombre completo del familiar."""
        return f"{self.nombres_familiar} {self.apellido_paterno} {self.apellido_materno}"
    
    @property
    def edad(self):
        """Calcula la edad del familiar."""
        if self.fecha_nacimiento:
            hoy = date.today()
            edad = hoy.year - self.fecha_nacimiento.year
            if hoy.month < self.fecha_nacimiento.month or \
               (hoy.month == self.fecha_nacimiento.month and hoy.day < self.fecha_nacimiento.day):
                edad -= 1
            return edad
        return None
    
    @property
    def es_menor_edad(self):
        """Verifica si el familiar es menor de edad."""
        return self.edad and self.edad < 18
    
    @property
    def es_mayor_edad(self):
        """Verifica si el familiar es mayor de edad."""
        return self.edad and self.edad >= 18
    
    @property
    def parentesco_texto(self):
        """Retorna el parentesco en formato texto."""
        return dict(self.PARENTESCO_CHOICES).get(self.parentesco, self.parentesco)
    
    @property
    def genero_texto(self):
        """Retorna el género en formato texto."""
        return dict(self.GENERO_CHOICES).get(self.genero_familiar, self.genero_familiar)
    
    @property
    def documento_completo(self):
        """Retorna el documento completo con tipo."""
        return f"{self.tipo_documento}: {self.numero_documento}"
    
    @property
    def direccion_completa(self):
        """Retorna la dirección completa del familiar."""
        if not self.direccion_familiar:
            return "No especificada"
        
        direccion = self.direccion_familiar
        if self.distrito_familiar:
            direccion += f", {self.distrito_familiar}"
        if self.provincia_familiar:
            direccion += f", {self.provincia_familiar}"
        if self.departamento_familiar:
            direccion += f", {self.departamento_familiar}"
        
        return direccion
    
    @property
    def contacto_completo(self):
        """Retorna la información de contacto completa."""
        contacto = []
        if self.telefono_familiar:
            contacto.append(f"Tel: {self.telefono_familiar}")
        if self.correo_familiar:
            contacto.append(f"Email: {self.correo_familiar}")
        
        return " | ".join(contacto) if contacto else "No disponible"
    
    @property
    def es_activo(self):
        """Verifica si el familiar está activo."""
        return self.estado_familiar == 'activo'
    
    @property
    def dependencia_vigente(self):
        """Verifica si la dependencia está vigente."""
        if not self.es_dependiente:
            return False
        
        if self.fecha_fin_dependencia:
            return date.today() <= self.fecha_fin_dependencia
        
        return True
    
    @property
    def edad_para_dependencia(self):
        """Verifica si cumple con la edad para ser dependiente."""
        edad = self.edad
        if not edad:
            return False
        
        # Hijos menores de 18 años o hasta 24 si estudian
        if self.parentesco == 'hijo':
            if edad < 18:
                return True
            if edad <= 24 and self.nivel_educativo in ['universitario_incompleto', 'tecnico']:
                return True
        
        # Cónyuge o conviviente
        if self.parentesco in ['conyuge', 'conviviente']:
            return True
        
        # Padres mayores de 60 años
        if self.parentesco in ['padre', 'madre'] and edad >= 60:
            return True
        
        return False
    
    @property
    def requiere_documentos_adicionales(self):
        """Verifica si requiere documentos adicionales para beneficios."""
        documentos = []
        
        if self.es_dependiente:
            if self.parentesco == 'hijo' and self.edad and self.edad > 18:
                documentos.append('Certificado de estudios')
            
            if self.parentesco in ['padre', 'madre']:
                documentos.append('Declaración jurada de dependencia económica')
        
        if self.tiene_discapacidad:
            documentos.append('Certificado de discapacidad')
        
        return documentos
    
    def activar_dependencia(self, fecha_inicio=None):
        """Activa la dependencia del familiar."""
        self.es_dependiente = True
        self.fecha_inicio_dependencia = fecha_inicio or date.today()
        self.save()
    
    def desactivar_dependencia(self, fecha_fin=None, motivo=None):
        """Desactiva la dependencia del familiar."""
        self.es_dependiente = False
        self.fecha_fin_dependencia = fecha_fin or date.today()
        if motivo:
            self.observaciones = f"{self.observaciones or ''}\nFin dependencia: {motivo}"
        self.save()
    
    def activar_beneficiario(self):
        """Activa como beneficiario."""
        self.es_beneficiario = True
        self.save()
    
    def desactivar_beneficiario(self):
        """Desactiva como beneficiario."""
        self.es_beneficiario = False
        self.save()
    
    def activar_contacto_emergencia(self):
        """Activa como contacto de emergencia."""
        self.es_contacto_emergencia = True
        self.save()
    
    def desactivar_contacto_emergencia(self):
        """Desactiva como contacto de emergencia."""
        self.es_contacto_emergencia = False
        self.save()
    
    def marcar_fallecido(self, fecha_fallecimiento=None):
        """Marca al familiar como fallecido."""
        self.estado_familiar = 'fallecido'
        self.es_dependiente = False
        self.es_beneficiario = False
        self.fecha_fin_dependencia = fecha_fallecimiento or date.today()
        self.save()
    
    def actualizar_seguro_salud(self, tiene_seguro, tipo_seguro=None, numero_seguro=None, centro_salud=None):
        """Actualiza la información del seguro de salud."""
        self.tiene_seguro_salud = tiene_seguro
        if tiene_seguro:
            self.tipo_seguro_salud = tipo_seguro
            self.numero_seguro = numero_seguro
            self.centro_salud_asignado = centro_salud
        else:
            self.tipo_seguro_salud = None
            self.numero_seguro = None
            self.centro_salud_asignado = None
        self.save()
    
    def actualizar_discapacidad(self, tiene_discapacidad, tipo_discapacidad=None, grado=None, certificado=None):
        """Actualiza la información de discapacidad."""
        self.tiene_discapacidad = tiene_discapacidad
        if tiene_discapacidad:
            self.tipo_discapacidad = tipo_discapacidad
            self.grado_discapacidad = grado
            self.certificado_discapacidad = certificado
        else:
            self.tipo_discapacidad = None
            self.grado_discapacidad = None
            self.certificado_discapacidad = None
        self.save()
    
    @classmethod
    def dependientes_activos(cls, empleado=None):
        """Obtiene los dependientes activos."""
        queryset = cls.objects.filter(
            es_dependiente=True,
            estado_familiar='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset
    
    @classmethod
    def contactos_emergencia(cls, empleado=None):
        """Obtiene los contactos de emergencia."""
        queryset = cls.objects.filter(
            es_contacto_emergencia=True,
            estado_familiar='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset
    
    @classmethod
    def beneficiarios_activos(cls, empleado=None):
        """Obtiene los beneficiarios activos."""
        queryset = cls.objects.filter(
            es_beneficiario=True,
            estado_familiar='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset
    
    @classmethod
    def hijos_menores(cls, empleado=None):
        """Obtiene los hijos menores de edad."""
        from datetime import timedelta
        fecha_limite = date.today() - timedelta(days=18*365)  # 18 años atrás
        
        queryset = cls.objects.filter(
            parentesco='hijo',
            fecha_nacimiento__gt=fecha_limite,
            estado_familiar='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset
    
    @classmethod
    def familiares_con_discapacidad(cls, empleado=None):
        """Obtiene familiares con discapacidad."""
        queryset = cls.objects.filter(
            tiene_discapacidad=True,
            estado_familiar='activo'
        )
        
        if empleado:
            queryset = queryset.filter(empleado=empleado)
        
        return queryset