# -*- coding: utf-8 -*-
"""
Modelo Certification - Gestión de cursos y certificaciones de empleados

Almacena los cursos, capacitaciones y certificaciones completados por los empleados,
con referencia opcional al documento digital que los certifica.
"""

from django.db import models


class Certification(models.Model):
    """Modelo para gestionar cursos y certificaciones de los empleados."""

    curso_id = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(
        'Employee', on_delete=models.CASCADE, related_name='cursos_certificaciones'
    )
    nombre_curso = models.CharField(max_length=200)
    institucion = models.CharField(max_length=200)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    horas = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    documento = models.ForeignKey(
        'documents.DigitalDocument',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='curso_certificacion',
    )
    estado_registro = models.CharField(max_length=20, default='activo')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cursos_certificaciones'
        unique_together = [['empleado', 'nombre_curso', 'institucion', 'fecha_inicio']]

    def __str__(self):
        return f"{self.nombre_curso} — {self.institucion}"
