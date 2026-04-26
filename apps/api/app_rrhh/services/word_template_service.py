# -*- coding: utf-8 -*-
"""
Servicio para generación de documentos Word desde plantillas .docx.

Usa python-docx para abrir la plantilla y reemplazar marcadores {{VARIABLE}}
con los datos reales del empleado/contrato.
"""

import re
from datetime import datetime, date
from io import BytesIO
from typing import Dict, Any, Optional

from django.utils import timezone


class WordTemplateService:
    """
    Servicio para generar documentos Word desde plantillas .docx.

    Las plantillas deben contener marcadores del tipo {{VARIABLE}} que
    serán reemplazados con los datos reales.
    """

    def generar_desde_plantilla(
        self,
        plantilla,
        variables: Dict[str, str],
    ) -> bytes:
        """
        Genera un documento Word reemplazando variables en la plantilla.

        Args:
            plantilla: Instancia de PlantillaDocumento
            variables: Diccionario con los valores a sustituir

        Returns:
            bytes: Contenido del .docx generado
        """
        from docx import Document

        doc = Document(plantilla.archivo.path)
        self._reemplazar_en_documento(doc, variables)

        buffer = BytesIO()
        doc.save(buffer)
        return buffer.getvalue()

    def _reemplazar_en_documento(self, doc, variables: Dict[str, str]):
        """Reemplaza marcadores {{VAR}} en todos los elementos del documento."""
        # Párrafos del cuerpo
        for para in doc.paragraphs:
            self._reemplazar_en_parrafo(para, variables)

        # Tablas
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        self._reemplazar_en_parrafo(para, variables)

        # Encabezados y pies de página
        for section in doc.sections:
            for para in section.header.paragraphs:
                self._reemplazar_en_parrafo(para, variables)
            for para in section.footer.paragraphs:
                self._reemplazar_en_parrafo(para, variables)

    def _reemplazar_en_parrafo(self, para, variables: Dict[str, str]):
        """
        Reemplaza marcadores en un párrafo preservando el formato.
        Combina todos los runs para hacer el reemplazo y luego los restaura.
        """
        # Obtener texto completo del párrafo
        texto_completo = para.text
        if '{{' not in texto_completo:
            return

        # Reemplazar todos los marcadores
        texto_nuevo = texto_completo
        for clave, valor in variables.items():
            marcador = '{{' + clave + '}}'
            texto_nuevo = texto_nuevo.replace(marcador, str(valor) if valor is not None else '')

        if texto_nuevo == texto_completo:
            return

        # Aplicar el texto nuevo al primer run y limpiar el resto
        if para.runs:
            # Guardar formato del primer run
            primer_run = para.runs[0]
            primer_run.text = texto_nuevo
            # Limpiar los demás runs
            for run in para.runs[1:]:
                run.text = ''

    def construir_variables_empleado(self, empleado, datos_adicionales: Optional[Dict] = None) -> Dict[str, str]:
        """
        Construye el diccionario de variables para documentos de empleado.

        Args:
            empleado: Instancia de Empleado
            datos_adicionales: Variables adicionales (para certificados, etc.)
        """
        datos_laborales = empleado.datos_laborales_actuales()

        hoy = timezone.now().date()
        variables = {
            'NOMBRE_EMPLEADO': empleado.nombres_empleado,
            'APELLIDOS': f"{empleado.apellido_paterno} {empleado.apellido_materno}".strip(),
            'NOMBRE_COMPLETO': empleado.nombre_completo,
            'DNI': empleado.numero_documento,
            'TIPO_DOCUMENTO': empleado.get_tipo_documento_display(),
            'CARGO': datos_laborales.cargo_empleado if datos_laborales else '',
            'AREA': datos_laborales.area.nombre_completo if (datos_laborales and datos_laborales.area_id) else '',
            'FECHA_INGRESO': self._format_date(datos_laborales.fecha_ingreso if datos_laborales else None),
            'TELEFONO': empleado.telefono_celular or '',
            'EMAIL': empleado.correo_personal or '',
            'FECHA_HOY': self._format_date(hoy),
            'CIUDAD': 'Lima',
            'EMPRESA_NOMBRE': 'Institución Pública',
            'EMPRESA_RUC': '20123456789',
            'EMPRESA_DIRECCION': 'Av. Principal 123, Lima, Perú',
        }

        if datos_adicionales:
            for k, v in datos_adicionales.items():
                variables[k.upper()] = str(v) if v is not None else ''

        return variables

    def construir_variables_contrato(self, contrato) -> Dict[str, str]:
        """Construye variables para documentos de contrato/adenda."""
        empleado = contrato.empleado
        variables = self.construir_variables_empleado(empleado)

        variables.update({
            'NUMERO_CONTRATO': contrato.numero_contrato or '',
            'NUMERO_ADENDA': contrato.numero_adenda or '',
            'TIPO_CONTRATO': contrato.get_tipo_documento_display(),
            'FECHA_INICIO': self._format_date(contrato.fecha_inicio),
            'FECHA_FIN': self._format_date(contrato.fecha_fin),
            'FECHA_FIRMA': self._format_date(contrato.fecha_firma),
            'SALARIO_BRUTO': str(contrato.salario_bruto) if contrato.salario_bruto else '',
            'SALARIO_NETO': str(contrato.salario_neto) if contrato.salario_neto else '',
            'JORNADA': contrato.get_jornada_laboral_display() if contrato.jornada_laboral else '',
            'CARGO': contrato.cargo or variables.get('CARGO', ''),
            'AREA': contrato.area.nombre_completo if contrato.area_id else variables.get('AREA', ''),
            'LUGAR_TRABAJO': contrato.lugar_trabajo or '',
            'HORARIO_TRABAJO': contrato.horario_trabajo or '',
            'FUNCIONES': contrato.funciones or '',
        })
        return variables

    def construir_variables_certificado(
        self,
        empleado,
        tipo: str,
        numero_certificado: str,
        proposito: str = '',
        incluir_salario: bool = False,
    ) -> Dict[str, str]:
        """Construye variables para certificados y constancias."""
        from django.utils import timezone
        hoy = timezone.now().date()

        variables = self.construir_variables_empleado(empleado)

        datos_laborales = empleado.datos_laborales_actuales()
        salario = ''
        if incluir_salario and datos_laborales:
            # Buscar salario del último contrato activo
            from apps.contracts.models import ContratosAdendas
            contrato = ContratosAdendas.objects.filter(
                empleado=empleado, estado='ACTIVO'
            ).order_by('-fecha_inicio').first()
            if contrato:
                salario = str(contrato.salario_bruto)

        variables.update({
            'NUMERO_CERTIFICADO': numero_certificado,
            'TIPO_CERTIFICADO': tipo,
            'FECHA_EXPEDICION': self._format_date(hoy),
            'PROPOSITO': proposito or '',
            'SALARIO_BRUTO': salario,
        })
        return variables

    def _format_date(self, value) -> str:
        """Formatea una fecha como 'DD de Mes de AAAA' en español."""
        if not value:
            return ''
        MESES = {
            1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril',
            5: 'mayo', 6: 'junio', 7: 'julio', 8: 'agosto',
            9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre',
        }
        try:
            if isinstance(value, datetime):
                value = value.date()
            return f"{value.day:02d} de {MESES[value.month]} de {value.year}"
        except Exception:
            return str(value)

    def pdf_desde_docx(self, docx_bytes: bytes, nombre_archivo: str = 'documento.docx') -> Optional[bytes]:
        """
        Convierte bytes .docx a PDF usando docx2pdf (requiere Word instalado en Windows).
        Retorna None si la conversión falla.
        """
        import tempfile
        import os
        try:
            from docx2pdf import convert
            with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as tmp_docx:
                tmp_docx.write(docx_bytes)
                tmp_docx_path = tmp_docx.name

            tmp_pdf_path = tmp_docx_path.replace('.docx', '.pdf')
            convert(tmp_docx_path, tmp_pdf_path)

            with open(tmp_pdf_path, 'rb') as f:
                pdf_bytes = f.read()

            os.unlink(tmp_docx_path)
            os.unlink(tmp_pdf_path)
            return pdf_bytes
        except Exception:
            return None
