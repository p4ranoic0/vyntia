# -*- coding: utf-8 -*-
"""
Servicio para gestión de plantillas y generación de documentos.

Este servicio maneja la lógica de generación de documentos desde plantillas
para contratos, adendas, certificados y reportes.
"""

import os
from datetime import datetime
from typing import Dict, Any, Optional
from django.template.loader import get_template
from django.template import Context, Template
from django.conf import settings
from django.core.exceptions import ValidationError
from apps.documents.models import DigitalDocument
from apps.contracts.models import Contract
from apps.employees.models import Employee
from apps.organization.models import Department


class TemplateService:
    """
    Servicio para gestión de plantillas y generación de documentos.
    
    Proporciona métodos para generar diferentes tipos de documentos
    desde plantillas HTML utilizando datos del sistema.
    """
    
    # Mapeo de tipos de contrato a plantillas (keys = Contract.TIPO_DOCUMENTO_CHOICES)
    PLANTILLAS_CONTRATO = {
        'CAS_INDETERMINADO': 'contratos/contrato_cas.html',
        'CAS_DETERMINADO': 'contratos/contrato_cas.html',
        'CAS_SUPLENCIA': 'contratos/contrato_cas.html',
        'LEY_728_FIJO': 'contratos/contrato_728.html',
        'LEY_728_FIJO_SUPLENCIA': 'contratos/contrato_728.html',
        'LEY_728_INDETERMINADO': 'contratos/contrato_728.html',
        'LEY_276_INDETERMINADO': 'contratos/contrato_276.html',
    }
    PLANTILLAS_ADENDA = {
        'ADENDA_SALARIAL': 'adendas/adenda_base.html',
        'ADENDA_CARGO': 'adendas/adenda_base.html',
        'ADENDA_HORARIO': 'adendas/adenda_base.html',
        'ADENDA_EXTENSION': 'adendas/adenda_base.html',
    }
    PLANTILLAS_CERTIFICADO = {
        'CONSTANCIA': 'certificados/constancia_laboral.html',
        'CERTIFICADO': 'certificados/certificado_trabajo.html',
    }
    
    def __init__(self):
        """Inicializa el servicio de plantillas."""
        self.templates_dir = os.path.join(settings.BASE_DIR, 'templates')
    
    def generar_contrato(self, contrato_id: int, tipo_plantilla: Optional[str] = None) -> str:
        """
        Genera el HTML de un contrato desde su plantilla.
        
        Args:
            contrato_id: ID del contrato a generar
            tipo_plantilla: Tipo específico de plantilla (opcional)
            
        Returns:
            str: HTML generado del contrato
            
        Raises:
            ValidationError: Si el contrato no existe o faltan datos
        """
        try:
            contrato = Contract.objects.select_related(
                'empleado',
                'area',
                'creado_por'
            ).get(contrato_id=contrato_id)

            # Determinar la plantilla a usar
            if tipo_plantilla:
                plantilla = self.PLANTILLAS_CONTRATO.get(tipo_plantilla)
            else:
                plantilla = self.PLANTILLAS_CONTRATO.get(
                    contrato.tipo_documento,
                    'contratos/contrato_base.html'
                )

            # Fallback to base template if specific one not found
            if not plantilla:
                plantilla = 'contratos/contrato_base.html'
            
            # Preparar contexto de datos
            contexto = self._preparar_contexto_contrato(contrato)
            
            # Renderizar plantilla
            template = get_template(plantilla)
            html_generado = template.render(contexto)
            
            return html_generado
            
        except Contract.DoesNotExist:
            raise ValidationError(f"No se encontró el contrato con ID: {contrato_id}")
        except Exception as e:
            raise ValidationError(f"Error generando contrato: {str(e)}")
    
    def generar_adenda(self, contrato_id: int, tipo_adenda: str) -> str:
        """
        Genera el HTML de una adenda desde su plantilla.
        
        Args:
            contrato_id: ID del contrato base
            tipo_adenda: Tipo de adenda a generar
            
        Returns:
            str: HTML generado de la adenda
        """
        try:
            contrato = Contract.objects.select_related(
                'empleado',
                'area',
                'creado_por'
            ).get(contrato_id=contrato_id)

            plantilla = self.PLANTILLAS_ADENDA.get(tipo_adenda, 'adendas/adenda_base.html')
            
            contexto = self._preparar_contexto_contrato(contrato)
            contexto['tipo_adenda'] = tipo_adenda
            contexto['es_adenda'] = True
            
            template = get_template(plantilla)
            html_generado = template.render(contexto)
            
            return html_generado
            
        except Contract.DoesNotExist:
            raise ValidationError(f"No se encontró el contrato con ID: {contrato_id}")
        except Exception as e:
            raise ValidationError(f"Error generando adenda: {str(e)}")
    
    def generar_certificado(self, empleado_id: int, tipo_certificado: str, 
                          datos_adicionales: Optional[Dict[str, Any]] = None) -> str:
        """
        Genera el HTML de un certificado laboral.
        
        Args:
            empleado_id: ID del empleado
            tipo_certificado: Tipo de certificado a generar
            datos_adicionales: Datos adicionales para el certificado
            
        Returns:
            str: HTML generado del certificado
        """
        try:
            empleado = Employee.objects.get(empleado_id=empleado_id)

            # Auto-detect: active employee → CONSTANCIA, cesado → CERTIFICADO
            if tipo_certificado in ('LABORAL', None, ''):
                estado = getattr(empleado, 'estado_empleado', 'activo')
                tipo_certificado = 'CONSTANCIA' if estado == 'activo' else 'CERTIFICADO'

            plantilla = self.PLANTILLAS_CERTIFICADO.get(tipo_certificado, 'certificados/constancia_laboral.html')
            
            contexto = self._preparar_contexto_empleado(empleado)
            if datos_adicionales:
                contexto['certificado'] = datos_adicionales
            
            template = get_template(plantilla)
            html_generado = template.render(contexto)
            
            return html_generado
            
        except Employee.DoesNotExist:
            raise ValidationError(f"No se encontró el empleado con ID: {empleado_id}")
        except Exception as e:
            raise ValidationError(f"Error generando certificado: {str(e)}")
    
    def _preparar_contexto_contrato(self, contrato: Contract) -> Dict[str, Any]:
        """
        Prepara el contexto de datos para plantillas de contrato.
        
        Args:
            contrato: Instancia del contrato
            
        Returns:
            Dict: Contexto con todos los datos necesarios
        """
        empleado = contrato.empleado
        institucion = self._obtener_datos_institucion()

        contexto = {
            # Datos del contrato
            'contrato': {
                'numero': contrato.numero_contrato,
                'numero_adenda': contrato.numero_adenda,
                'tipo': contrato.get_tipo_documento_display(),
                'tipo_contrato': contrato.tipo_documento,
                'jornada': contrato.get_jornada_laboral_display(),
                'fecha_inicio': contrato.fecha_inicio,
                'fecha_fin': contrato.fecha_fin,
                'fecha_firma': contrato.fecha_firma,
                'salario_base': contrato.salario_bruto,
                'salario_neto': contrato.salario_neto,
                'cargo': contrato.cargo,
                'funciones': contrato.funciones,
                'lugar_trabajo': contrato.lugar_trabajo,
                'horario_trabajo': contrato.horario_trabajo,
                'observaciones': contrato.observaciones,
                'estado': contrato.get_estado_display(),
                'area': contrato.area.nombre_completo if contrato.area_id else '',
                'tipo_modalidad': contrato.get_tipo_documento_display(),
                'regimen_laboral': 'CAS (D.L. 1057)' if contrato.tipo_documento.startswith('CAS') else ('Ley 728 (D.Leg. 728)' if contrato.tipo_documento.startswith('LEY_728') else 'Ley 276 (D.Leg. 276)'),
                'es_determinado': contrato.fecha_fin is not None,
                'es_suplencia': 'SUPLENCIA' in contrato.tipo_documento,
            },

            # Datos del empleado
            'empleado': self._obtener_datos_empleado(empleado),

            # Datos del área
            'area': {
                'nombre': contrato.area.nombre_completo if contrato.area_id else '',
                'siglas': contrato.area.siglas_area if contrato.area_id else '',
            },

            # Datos institucionales (ambas claves para compatibilidad con plantillas)
            'institucion': institucion,
            'empresa': institucion,

            # Datos de generación
            'generacion': {
                'fecha': datetime.now(),
                'usuario': contrato.creado_por.nombre_completo if contrato.creado_por_id else 'Sistema',
            },
            'fecha_generacion': datetime.now(),
        }

        return contexto
    
    def _preparar_contexto_empleado(self, empleado: Employee) -> Dict[str, Any]:
        """
        Prepara el contexto de datos para plantillas de empleado.
        
        Args:
            empleado: Instancia del empleado
            
        Returns:
            Dict: Contexto con datos del empleado
        """
        institucion = self._obtener_datos_institucion()
        datos_laborales = empleado.datos_laborales_actuales()
        contexto = {
            'empleado': self._obtener_datos_empleado(empleado),
            'datos_laborales': datos_laborales,
            'institucion': institucion,
            'empresa': institucion,
            'generacion': {
                'fecha': datetime.now(),
            },
            'fecha_generacion': datetime.now(),
        }

        return contexto
    
    def _obtener_datos_empleado(self, empleado: Employee) -> Dict[str, Any]:
        """
        Obtiene todos los datos relevantes del empleado.
        
        Args:
            empleado: Instancia del empleado
            
        Returns:
            Dict: Datos completos del empleado
        """
        datos_laborales = empleado.datos_laborales_actuales()
        return {
            'nombres': empleado.nombres_empleado,
            'apellidos': f"{empleado.apellido_paterno} {empleado.apellido_materno}",
            'nombre_completo': empleado.nombre_completo,
            'tipo_documento': empleado.get_tipo_documento_display(),
            'numero_documento': empleado.numero_documento,
            'fecha_nacimiento': empleado.fecha_nacimiento,
            'genero': empleado.genero_texto,
            'estado_civil': empleado.get_estado_civil_display(),
            'telefono': empleado.telefono_celular,
            'email': empleado.correo_personal,
            'direccion': empleado.direccion_domicilio,
            'distrito': empleado.distrito_domicilio,
            'provincia': empleado.provincia_domicilio,
            'departamento': empleado.departamento_domicilio,
            'fecha_ingreso': datos_laborales.fecha_ingreso if datos_laborales else None,
            'cargo': datos_laborales.cargo_empleado if datos_laborales else None,
        }
    
    def _obtener_datos_institucion(self) -> Dict[str, Any]:
        """
        Obtiene los datos institucionales para los documentos.

        Returns:
            Dict: Datos de la institución
        """
        from apps.organization.models import Company
        cfg = Company.get_config()
        return {
            'nombre': cfg.nombre,
            'ruc': cfg.ruc,
            'nit': cfg.ruc,  # alias for templates that use empresa.nit
            'direccion': cfg.direccion,
            'distrito': cfg.distrito,
            'provincia': cfg.provincia,
            'departamento': cfg.departamento,
            'ciudad': f"{cfg.distrito or cfg.provincia}",
            'telefono': cfg.telefono,
            'email': cfg.email,
            'web': cfg.web,
            'logo': cfg.logo.url if cfg.logo else '',
            'logo_url': cfg.logo.url if cfg.logo else '',
            'representante_legal': cfg.representante_legal,
            'cargo_representante': cfg.cargo_representante,
            'cedula_representante': cfg.dni_representante,  # alias
            'dni_representante': cfg.dni_representante,
            'resolucion_creacion': cfg.resolucion_creacion,
        }
    
    def validar_plantilla(self, ruta_plantilla: str) -> bool:
        """
        Valida que una plantilla existe y es accesible.
        
        Args:
            ruta_plantilla: Ruta de la plantilla a validar
            
        Returns:
            bool: True si la plantilla es válida
        """
        try:
            get_template(ruta_plantilla)
            return True
        except Exception:
            return False
    
    def listar_plantillas_disponibles(self) -> Dict[str, list]:
        """
        Lista todas las plantillas disponibles por categoría.

        Returns:
            Dict: Plantillas organizadas por categoría
        """
        return {
            'contratos': list(self.PLANTILLAS_CONTRATO.keys()),
            'adendas': list(self.PLANTILLAS_ADENDA.keys()),
            'certificados': list(self.PLANTILLAS_CERTIFICADO.keys()),
        }

    def obtener_plantillas_disponibles(self) -> Dict[str, list]:
        """Alias de listar_plantillas_disponibles() para compatibilidad con views."""
        return self.listar_plantillas_disponibles()

    def generar_reporte_html(self, reporte_data: Dict[str, Any]) -> str:
        """
        Genera el HTML de un reporte de contratos.

        Args:
            reporte_data: Diccionario con filtros y parametros del reporte

        Returns:
            str: HTML generado del reporte
        """
        from django.db.models import Q

        # Construir queryset de contratos segun filtros
        queryset = Contract.objects.select_related('empleado', 'area')

        filtros = Q()
        if reporte_data.get('fecha_inicio'):
            filtros &= Q(fecha_inicio__gte=reporte_data['fecha_inicio'])
        if reporte_data.get('fecha_fin'):
            filtros &= Q(fecha_fin__lte=reporte_data['fecha_fin'])
        if reporte_data.get('tipo_contrato'):
            filtros &= Q(tipo_documento=reporte_data['tipo_contrato'])
        if reporte_data.get('estado'):
            filtros &= Q(estado=reporte_data['estado'])
        if reporte_data.get('area'):
            filtros &= Q(area_id=reporte_data['area'])

        contratos = queryset.filter(filtros).order_by('-fecha_inicio')

        contexto = {
            'contratos': contratos,
            'filtros': reporte_data,
            'total_contratos': contratos.count(),
            'fecha_generacion': datetime.now(),
            'usuario_generador': reporte_data.get('usuario_generador', 'Sistema'),
            'institucion': self._obtener_datos_institucion(),
        }

        try:
            template = get_template('reportes/reporte_contratos.html')
            return template.render(contexto)
        except Exception:
            # Fallback: generar HTML basico si no existe la plantilla
            return self._generar_reporte_html_fallback(contexto)

    def _generar_reporte_html_fallback(self, contexto: Dict[str, Any]) -> str:
        """Genera HTML basico para el reporte cuando no existe la plantilla."""
        contratos = contexto['contratos']
        filas = ""
        for c in contratos:
            empleado_nombre = c.empleado.nombre_completo if c.empleado else "N/A"
            area_nombre = c.area.nombre_completo if c.area_id else "N/A"
            filas += f"""
            <tr>
                <td>{c.numero_contrato or c.contrato_id}</td>
                <td>{empleado_nombre}</td>
                <td>{c.tipo_documento}</td>
                <td>{area_nombre}</td>
                <td>{c.fecha_inicio or ''}</td>
                <td>{c.fecha_fin or ''}</td>
                <td>{c.get_estado_display()}</td>
            </tr>"""

        return f"""
        <html>
        <head><meta charset="utf-8"><title>Reporte de Contratos</title></head>
        <body>
            <h1>Reporte de Contratos</h1>
            <p>Fecha: {contexto['fecha_generacion'].strftime('%d/%m/%Y %H:%M')}</p>
            <p>Generado por: {contexto['usuario_generador']}</p>
            <p>Total: {contexto['total_contratos']} contratos</p>
            <table border="1" cellpadding="5" cellspacing="0">
                <thead>
                    <tr>
                        <th>N° Contrato</th><th>Employee</th><th>Tipo</th>
                        <th>Department</th><th>Inicio</th><th>Fin</th><th>Estado</th>
                    </tr>
                </thead>
                <tbody>{filas}</tbody>
            </table>
        </body>
        </html>
        """