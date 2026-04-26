"""Servicio para generar reportes PDF de empleados."""

import logging

from app_rrhh.models import DocumentosDigitales
from apps.employees.models import Empleado
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone

logger = logging.getLogger(__name__)


class EmpleadoReportService:
    """Servicio para generar reportes integrales de empleados en PDF."""

    def __init__(self):
        self._pdf_generator = None

    @property
    def pdf_generator(self):
        """Lazy-load PDFGenerator para evitar crash si WeasyPrint no esta disponible."""
        if self._pdf_generator is None:
            from .pdf_generator import PDFGenerator

            self._pdf_generator = PDFGenerator()
        return self._pdf_generator

    def generar_reporte_integral(self, empleado_id):
        """
        Genera un reporte PDF integral del empleado con todos sus datos.

        Args:
            empleado_id: ID del empleado

        Returns:
            tuple: (pdf_bytes, nombre_archivo)
        """
        empleado = Empleado.objects.get(empleado_id=empleado_id)
        context = self._obtener_contexto_completo(empleado)
        html_content = render_to_string("reportes/reporte_empleado.html", context)
        pdf_content = self.pdf_generator._html_to_pdf(html_content)
        nombre_archivo = f"reporte_integral_{empleado.numero_documento}.pdf"
        return pdf_content, nombre_archivo

    def generar_reporte_seccion(self, empleado_id, seccion):
        """
        Genera un reporte PDF de una seccion especifica del empleado.

        Args:
            empleado_id: ID del empleado
            seccion: 'personal', 'laboral', 'academico', 'familiar'

        Returns:
            tuple: (pdf_bytes, nombre_archivo)
        """
        empleado = Empleado.objects.get(empleado_id=empleado_id)
        context = self._obtener_contexto_completo(empleado)
        context["seccion"] = seccion

        html_content = render_to_string("reportes/reporte_empleado.html", context)
        pdf_content = self.pdf_generator._html_to_pdf(html_content)
        nombre_archivo = f"reporte_{seccion}_{empleado.numero_documento}.pdf"
        return pdf_content, nombre_archivo

    def _obtener_contexto_completo(self, empleado):
        """Obtiene todo el contexto necesario para el reporte."""
        # Datos laborales activos
        datos_laborales = (
            empleado.datos_laborales.filter(estado_datos="activo")
            .select_related("area")
            .first()
        )

        # Formacion academica
        formacion = empleado.formacion_academica.filter(
            estado_registro="activo"
        ).order_by("-nivel_educativo")

        # Familiares
        familiares = empleado.familiares.filter(estado_familiar="activo").order_by(
            "parentesco"
        )

        # Documentos del legajo
        documentos = DocumentosDigitales.objects.filter(
            empleado=empleado,
            es_version_actual=True,
        ).order_by("categoria", "tipo_documento")

        return {
            "empleado": empleado,
            "datos_laborales": datos_laborales,
            "formacion": formacion,
            "familiares": familiares,
            "documentos": documentos,
            "fecha_generacion": timezone.now(),
            "seccion": "todos",
        }

    def crear_http_response(self, pdf_content, nombre_archivo, inline=True):
        """Crea un HttpResponse con el PDF para descarga o visualizacion inline."""
        response = HttpResponse(pdf_content, content_type="application/pdf")
        disposition = "inline" if inline else "attachment"
        response["Content-Disposition"] = f'{disposition}; filename="{nombre_archivo}"'
        return response
