# -*- coding: utf-8 -*-
"""
Modelo PlantillaDocumento - Plantillas Word para generación de documentos.
"""

from django.db import models


class PlantillaDocumento(models.Model):
    """
    Modelo para almacenar plantillas Word (.docx) que se usan para generar
    contratos, certificados, constancias y adendas.

    Las plantillas deben usar marcadores de posición como {{NOMBRE_EMPLEADO}}
    que serán reemplazados con los datos reales al momento de generar.
    """

    TIPO_CHOICES = [
        ('certificado_trabajo', 'Certificado de Trabajo'),
        ('constancia_laboral', 'Constancia Laboral'),
        ('contrato', 'Contrato'),
        ('adenda', 'Adenda'),
    ]

    plantilla_id = models.AutoField(primary_key=True)
    tipo = models.CharField(
        max_length=30,
        choices=TIPO_CHOICES,
        help_text='Tipo de documento que genera esta plantilla',
    )
    nombre = models.CharField(max_length=200, help_text='Nombre descriptivo de la plantilla')
    descripcion = models.TextField(blank=True, default='', help_text='Descripcion de la plantilla')
    archivo = models.FileField(
        upload_to='plantillas_word/%Y/',
        help_text='Archivo .docx de la plantilla',
    )
    activa = models.BooleanField(default=True, help_text='Si esta plantilla esta disponible para uso')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creada_por = models.ForeignKey(
        'identity.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='plantillas_creadas',
    )

    class Meta:
        db_table = 'app_rrhh_plantilla_documento'
        ordering = ['-fecha_creacion']
        verbose_name = 'Plantilla de Documento'
        verbose_name_plural = 'Plantillas de Documentos'

    def __str__(self):
        return f"{self.get_tipo_display()} - {self.nombre}"

    @property
    def variables_disponibles(self):
        """Retorna las variables disponibles segun el tipo de plantilla."""
        base = [
            '{{NOMBRE_EMPLEADO}}', '{{APELLIDOS}}', '{{NOMBRE_COMPLETO}}',
            '{{DNI}}', '{{CARGO}}', '{{AREA}}', '{{FECHA_INGRESO}}',
            '{{EMPRESA_NOMBRE}}', '{{EMPRESA_RUC}}', '{{EMPRESA_DIRECCION}}',
            '{{FECHA_HOY}}', '{{CIUDAD}}',
        ]
        if self.tipo in ('certificado_trabajo', 'constancia_laboral'):
            base += [
                '{{NUMERO_CERTIFICADO}}', '{{FECHA_EXPEDICION}}',
                '{{PROPOSITO}}', '{{SALARIO_BRUTO}}',
            ]
        elif self.tipo == 'contrato':
            base += [
                '{{NUMERO_CONTRATO}}', '{{TIPO_CONTRATO}}',
                '{{FECHA_INICIO}}', '{{FECHA_FIN}}',
                '{{SALARIO_BRUTO}}', '{{SALARIO_NETO}}', '{{JORNADA}}',
            ]
        elif self.tipo == 'adenda':
            base += [
                '{{NUMERO_CONTRATO}}', '{{NUMERO_ADENDA}}',
                '{{FECHA_INICIO}}', '{{FECHA_FIN}}',
                '{{SALARIO_BRUTO}}', '{{SALARIO_NETO}}',
            ]
        return base
