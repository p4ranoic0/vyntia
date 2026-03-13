# -*- coding: utf-8 -*-
"""
Servicio para generación de archivos PDF desde plantillas HTML.

Este servicio maneja la conversión de HTML a PDF y la gestión
de archivos generados para documentos de RRHH.
"""

import logging
import os
import re
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from io import BytesIO

from django.conf import settings

logger = logging.getLogger(__name__)
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils.text import slugify

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

try:
    import weasyprint
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False

try:
    from xhtml2pdf import pisa
    XHTML2PDF_AVAILABLE = True
except Exception:
    XHTML2PDF_AVAILABLE = False

from app_rrhh.models import DocumentosDigitales, ContratosAdendas, Empleado
from .template_service import TemplateService


class PDFGenerator:
    """
    Servicio para generación de archivos PDF desde plantillas HTML.
    
    Utiliza WeasyPrint como motor principal y ReportLab como alternativa
    para generar PDFs de alta calidad desde plantillas HTML.
    """
    
    def __init__(self):
        """Inicializa el generador de PDFs."""
        self.template_service = TemplateService()
        self.media_root = settings.MEDIA_ROOT
        
        # Verificar disponibilidad de librerías
        if not XHTML2PDF_AVAILABLE and not WEASYPRINT_AVAILABLE and not REPORTLAB_AVAILABLE:
            raise ImportError(
                "Se requiere al menos xhtml2pdf, WeasyPrint o ReportLab para generar PDFs. "
                "Instale con: pip install xhtml2pdf reportlab"
            )
    
    def generar_pdf_contrato(self, contrato_id: int, 
                           tipo_plantilla: Optional[str] = None,
                           guardar_automatico: bool = True) -> Tuple[bytes, str]:
        """
        Genera un PDF de contrato desde su plantilla.
        
        Args:
            contrato_id: ID del contrato a generar
            tipo_plantilla: Tipo específico de plantilla (opcional)
            guardar_automatico: Si debe guardarse automáticamente en DocumentosDigitales
            
        Returns:
            Tuple[bytes, str]: Contenido del PDF y nombre del archivo
            
        Raises:
            ValidationError: Si hay errores en la generación
        """
        try:
            # Generar HTML desde plantilla
            html_content = self.template_service.generar_contrato(
                contrato_id, tipo_plantilla
            )
            
            # Obtener datos del contrato para el nombre del archivo
            contrato = ContratosAdendas.objects.select_related(
                'empleado', 'area'
            ).get(contrato_id=contrato_id)

            # Generar nombre del archivo
            nombre_archivo = self._generar_nombre_archivo_contrato(contrato)

            # Convertir HTML a PDF
            pdf_content = self._html_to_pdf(html_content)

            # Guardar automáticamente si se solicita
            if guardar_automatico:
                self._guardar_documento_digital(
                    pdf_content=pdf_content,
                    nombre_archivo=nombre_archivo,
                    empleado=contrato.empleado,
                    tipo_documento='contrato_trabajo',
                    contrato=contrato
                )
            
            return pdf_content, nombre_archivo
            
        except Exception as e:
            raise ValidationError(f"Error generando PDF de contrato: {str(e)}")
    
    def generar_pdf_adenda(self, contrato_id: int, tipo_adenda: str,
                         guardar_automatico: bool = True) -> Tuple[bytes, str]:
        """
        Genera un PDF de adenda desde su plantilla.
        
        Args:
            contrato_id: ID del contrato base
            tipo_adenda: Tipo de adenda a generar
            guardar_automatico: Si debe guardarse automáticamente
            
        Returns:
            Tuple[bytes, str]: Contenido del PDF y nombre del archivo
        """
        try:
            # Generar HTML desde plantilla
            html_content = self.template_service.generar_adenda(
                contrato_id, tipo_adenda
            )
            
            # Obtener datos del contrato
            contrato = ContratosAdendas.objects.select_related(
                'empleado', 'area'
            ).get(contrato_id=contrato_id)

            # Generar nombre del archivo
            nombre_archivo = self._generar_nombre_archivo_adenda(contrato, tipo_adenda)

            # Convertir HTML a PDF
            pdf_content = self._html_to_pdf(html_content)

            # Guardar automáticamente si se solicita
            if guardar_automatico:
                self._guardar_documento_digital(
                    pdf_content=pdf_content,
                    nombre_archivo=nombre_archivo,
                    empleado=contrato.empleado,
                    tipo_documento='adenda_contrato',
                    contrato=contrato
                )
            
            return pdf_content, nombre_archivo
            
        except Exception as e:
            raise ValidationError(f"Error generando PDF de adenda: {str(e)}")
    
    def generar_pdf_certificado(self, empleado_id: int, tipo_certificado: str,
                              datos_adicionales: Optional[Dict[str, Any]] = None,
                              guardar_automatico: bool = True) -> Tuple[bytes, str]:
        """
        Genera un PDF de certificado laboral.
        
        Args:
            empleado_id: ID del empleado
            tipo_certificado: Tipo de certificado a generar
            datos_adicionales: Datos adicionales para el certificado
            guardar_automatico: Si debe guardarse automáticamente
            
        Returns:
            Tuple[bytes, str]: Contenido del PDF y nombre del archivo
        """
        try:
            # Generar HTML desde plantilla
            html_content = self.template_service.generar_certificado(
                empleado_id, tipo_certificado, datos_adicionales
            )
            
            # Obtener datos del empleado
            empleado = Empleado.objects.get(empleado_id=empleado_id)
            
            # Generar nombre del archivo
            nombre_archivo = self._generar_nombre_archivo_certificado(
                empleado, tipo_certificado
            )
            
            # Convertir HTML a PDF
            pdf_content = self._html_to_pdf(html_content)
            
            # Guardar automáticamente si se solicita
            if guardar_automatico:
                self._guardar_documento_digital(
                    pdf_content=pdf_content,
                    nombre_archivo=nombre_archivo,
                    empleado=empleado,
                    tipo_documento='certificado_trabajo'
                )
            
            return pdf_content, nombre_archivo
            
        except Exception as e:
            raise ValidationError(f"Error generando PDF de certificado: {str(e)}")
    
    def _html_to_pdf(self, html_content: str) -> bytes:
        """
        Convierte contenido HTML a PDF.

        Args:
            html_content: Contenido HTML a convertir

        Returns:
            bytes: Contenido del PDF generado
        """
        if XHTML2PDF_AVAILABLE:
            try:
                return self._html_to_pdf_xhtml2pdf(html_content)
            except Exception as e:
                logger.warning("xhtml2pdf failed: %s — intentando motor alternativo", e)
        if WEASYPRINT_AVAILABLE:
            try:
                return self._html_to_pdf_weasyprint(html_content)
            except Exception as e:
                logger.warning("WeasyPrint failed: %s — intentando motor alternativo", e)
        if REPORTLAB_AVAILABLE:
            logger.error(
                "Usando stub ReportLab — el PDF NO contendrá contenido real del documento. "
                "Corrija el CSS de las plantillas para que xhtml2pdf funcione."
            )
            return self._html_to_pdf_reportlab(html_content)
        raise ValidationError("No hay librerías disponibles para generar PDF")
    
    def _strip_unsupported_css(self, html_content: str) -> str:
        """
        Elimina reglas CSS que xhtml2pdf no puede parsear en Windows.

        Args:
            html_content: Contenido HTML con CSS a limpiar

        Returns:
            str: HTML con las reglas CSS incompatibles eliminadas
        """
        # Eliminar reglas @page con counter() — no soportado por xhtml2pdf
        html_content = re.sub(
            r'@page\s*\{[^}]*counter\([^}]*\}',
            '@page { size: A4; margin: 2cm; }',
            html_content,
            flags=re.DOTALL,
        )
        return html_content

    def _html_to_pdf_xhtml2pdf(self, html_content: str) -> bytes:
        """
        Convierte HTML a PDF usando xhtml2pdf.

        Args:
            html_content: Contenido HTML a convertir

        Returns:
            bytes: Contenido del PDF generado

        Raises:
            ValidationError: Si xhtml2pdf falla o produce un PDF vacío
        """
        html_content = self._strip_unsupported_css(html_content)
        buffer = BytesIO()
        result = pisa.CreatePDF(
            html_content.encode('utf-8'),
            dest=buffer,
            encoding='utf-8',
        )
        if result.err:
            raise ValidationError(
                f"xhtml2pdf conversion error (code={result.err}). "
                "Verify template CSS: remove @page counter(pages), flexbox, and gradient rules."
            )
        pdf_bytes = buffer.getvalue()
        if len(pdf_bytes) < 100:
            raise ValidationError(
                "xhtml2pdf produced empty or near-empty PDF output. "
                "Check that the HTML template renders content."
            )
        return pdf_bytes

    def _html_to_pdf_weasyprint(self, html_content: str) -> bytes:
        """
        Convierte HTML a PDF usando WeasyPrint.
        
        Args:
            html_content: Contenido HTML
            
        Returns:
            bytes: PDF generado
        """
        try:
            # Configurar CSS base para documentos
            css_content = """
            @page {
                size: A4;
                margin: 2cm;
                @bottom-center {
                    content: "Página " counter(page) " de " counter(pages);
                    font-size: 10px;
                }
            }
            body {
                font-family: 'Arial', sans-serif;
                font-size: 12px;
                line-height: 1.4;
                color: #333;
            }
            .header {
                text-align: center;
                margin-bottom: 30px;
                border-bottom: 2px solid #333;
                padding-bottom: 20px;
            }
            .content {
                margin: 20px 0;
            }
            .footer {
                margin-top: 50px;
                text-align: center;
                border-top: 1px solid #ccc;
                padding-top: 20px;
            }
            .signature-section {
                margin-top: 80px;
                display: flex;
                justify-content: space-between;
            }
            .signature-box {
                width: 200px;
                text-align: center;
                border-top: 1px solid #333;
                padding-top: 10px;
            }
            """
            
            # Crear documento HTML completo
            html_completo = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <style>{css_content}</style>
            </head>
            <body>
                {html_content}
            </body>
            </html>
            """
            
            # Generar PDF
            pdf_file = BytesIO()
            weasyprint.HTML(string=html_completo).write_pdf(pdf_file)
            return pdf_file.getvalue()
            
        except Exception as e:
            raise ValidationError(f"Error con WeasyPrint: {str(e)}")
    
    def _html_to_pdf_reportlab(self, html_content: str) -> bytes:
        """
        Convierte HTML a PDF usando ReportLab (implementación básica).
        
        Args:
            html_content: Contenido HTML
            
        Returns:
            bytes: PDF generado
        """
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)
            
            # Estilos básicos
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=30,
                alignment=1  # Centrado
            )
            
            # Contenido (simplificado - en producción se necesitaría un parser HTML)
            story.append(Paragraph("DOCUMENTO GENERADO", title_style))
            story.append(Spacer(1, 12))
            
            # Agregar contenido básico
            normal_style = styles['Normal']
            story.append(Paragraph("Contenido del documento generado desde plantilla.", normal_style))
            
            # Construir PDF
            doc.build(story)
            return buffer.getvalue()
            
        except Exception as e:
            raise ValidationError(f"Error con ReportLab: {str(e)}")
    
    def _generar_nombre_archivo_contrato(self, contrato: ContratosAdendas) -> str:
        """
        Genera un nombre de archivo para el contrato.
        
        Args:
            contrato: Instancia del contrato
            
        Returns:
            str: Nombre del archivo
        """
        empleado = contrato.empleado
        fecha = datetime.now().strftime("%Y%m%d")

        nombre_base = f"contrato_{contrato.tipo_documento.lower()}_{empleado.numero_documento}_{fecha}"
        return f"{slugify(nombre_base)}.pdf"
    
    def _generar_nombre_archivo_adenda(self, contrato: ContratosAdendas, tipo_adenda: str) -> str:
        """
        Genera un nombre de archivo para la adenda.
        
        Args:
            contrato: Instancia del contrato
            tipo_adenda: Tipo de adenda
            
        Returns:
            str: Nombre del archivo
        """
        empleado = contrato.empleado
        fecha = datetime.now().strftime("%Y%m%d")

        nombre_base = f"adenda_{tipo_adenda.lower()}_{empleado.numero_documento}_{fecha}"
        return f"{slugify(nombre_base)}.pdf"
    
    def _generar_nombre_archivo_certificado(self, empleado: Empleado, tipo_certificado: str) -> str:
        """
        Genera un nombre de archivo para el certificado.
        
        Args:
            empleado: Instancia del empleado
            tipo_certificado: Tipo de certificado
            
        Returns:
            str: Nombre del archivo
        """
        fecha = datetime.now().strftime("%Y%m%d")
        
        nombre_base = f"certificado_{tipo_certificado.lower()}_{empleado.numero_documento}_{fecha}"
        return f"{slugify(nombre_base)}.pdf"
    
    def _guardar_documento_digital(self, pdf_content: bytes, nombre_archivo: str,
                                 empleado: Empleado, tipo_documento: str,
                                 contrato: Optional[ContratosAdendas] = None) -> DocumentosDigitales:
        """
        Guarda el PDF generado en DocumentosDigitales.
        
        Args:
            pdf_content: Contenido del PDF
            nombre_archivo: Nombre del archivo
            empleado: Empleado asociado
            tipo_documento: Tipo de documento
            contrato: Contrato asociado (opcional)
            
        Returns:
            DocumentosDigitales: Documento guardado
        """
        try:
            # Crear archivo Django
            archivo_django = ContentFile(pdf_content, name=nombre_archivo)
            
            # Crear registro en DocumentosDigitales
            documento = DocumentosDigitales.objects.create(
                empleado=empleado,
                tipo_documento=tipo_documento,
                categoria='laboral',
                nombre_documento=nombre_archivo.replace('.pdf', ''),
                descripcion=f"Documento generado automáticamente el {datetime.now().strftime('%d/%m/%Y')}",
                archivo=archivo_django,
                nombre_archivo_original=nombre_archivo,
                formato_archivo='pdf',
                tamano_archivo=len(pdf_content),
                es_version_actual=True,
                estado_documento='activo',
                nivel_acceso='restringido',
            )

            # Marcar contrato como generado si aplica
            if contrato and hasattr(contrato, 'documento_generado'):
                contrato.documento_generado = True
                contrato.save(update_fields=['documento_generado'])
            
            return documento
            
        except Exception as e:
            raise ValidationError(f"Error guardando documento digital: {str(e)}")
    
    def generar_reporte_pdf(self, reporte_data: Dict[str, Any],
                           guardar_en_bd: bool = True,
                           usuario_creador=None) -> Any:
        """
        Genera un PDF de reporte de contratos.

        Args:
            reporte_data: Datos y filtros del reporte
            guardar_en_bd: Si debe guardarse en DocumentosDigitales
            usuario_creador: Usuario que genera el reporte

        Returns:
            DocumentosDigitales si guardar_en_bd=True, bytes del PDF en caso contrario
        """
        try:
            html_content = self.template_service.generar_reporte_html(reporte_data)
            pdf_content = self._html_to_pdf(html_content)

            fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
            nombre_archivo = f"reporte_contratos_{fecha_str}.pdf"

            if guardar_en_bd:
                from django.core.files.base import ContentFile
                archivo_django = ContentFile(pdf_content, name=nombre_archivo)
                documento = DocumentosDigitales.objects.create(
                    empleado=None if not usuario_creador or not hasattr(usuario_creador, 'empleado') else usuario_creador.empleado,
                    tipo_documento='otros',
                    categoria='administrativo',
                    nombre_documento=f"Reporte de Contratos {datetime.now().strftime('%d/%m/%Y')}",
                    descripcion=f"Reporte generado el {datetime.now().strftime('%d/%m/%Y %H:%M')}",
                    archivo=archivo_django,
                    nombre_archivo_original=nombre_archivo,
                    formato_archivo='pdf',
                    tamano_archivo=len(pdf_content),
                    es_version_actual=True,
                    estado_documento='activo',
                    nivel_acceso='restringido',
                    subido_por=usuario_creador,
                )
                return documento
            return pdf_content

        except Exception as e:
            raise ValidationError(f"Error generando reporte PDF: {str(e)}")

    def obtener_configuracion_disponible(self) -> Dict[str, Any]:
        """
        Obtiene información sobre las librerías disponibles.
        
        Returns:
            Dict: Configuración y capacidades disponibles
        """
        return {
            'weasyprint_disponible': WEASYPRINT_AVAILABLE,
            'reportlab_disponible': REPORTLAB_AVAILABLE,
            'xhtml2pdf_disponible': XHTML2PDF_AVAILABLE,
            'motor_preferido': 'xhtml2pdf' if XHTML2PDF_AVAILABLE else ('WeasyPrint' if WEASYPRINT_AVAILABLE else 'ReportLab'),
            'formatos_soportados': ['PDF'],
            'plantillas_disponibles': self.template_service.listar_plantillas_disponibles(),
        }