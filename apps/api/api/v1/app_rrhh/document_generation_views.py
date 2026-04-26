# -*- coding: utf-8 -*-
"""
Vistas para la generación de documentos desde plantillas.

Este módulo contiene las vistas API para generar contratos, adendas,
certificados y reportes desde plantillas HTML y convertirlos a PDF.
"""

from apps.contracts.models import (
    ContratosAdendas,
    DatosLaborales,
)
from apps.documents.models import (
    DocumentosDigitales,
    PlantillaDocumento,
)
from apps.employees.models import Empleado
from apps.documents.services import TemplateService, WordTemplateService
from apps.core.decorators import (
    require_admin,
    require_authenticated,
    require_hr,
    require_manager,
    require_permissions,
)
from apps.core.permissions import IsHRUser
from apps.core.responses import APIResponse
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet


def _get_pdf_generator():
    """Lazy import de PDFGenerator para evitar crash si WeasyPrint no esta disponible."""
    from apps.documents.services import PDFGenerator

    return PDFGenerator()


@extend_schema(exclude=True)
class DocumentGenerationViewSet(ViewSet):
    """
    ViewScript para la generación de documentos desde plantillas.

    Proporciona endpoints para generar contratos, adendas, certificados
    y reportes en formato HTML y PDF.

    NOTA: Excluido del schema OpenAPI porque es un ViewSet personalizado
    que no usa serializers estándar (genera PDFs).
    """

    permission_classes = [IsAuthenticated, IsHRUser]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.template_service = TemplateService()
        self.word_service = WordTemplateService()
        self._pdf_generator = None

    @property
    def pdf_generator(self):
        """Lazy-load PDFGenerator solo cuando se necesite."""
        if self._pdf_generator is None:
            self._pdf_generator = _get_pdf_generator()
        return self._pdf_generator

    # @extend_schema(
    #     description="Generar contrato en formato PDF",
    #     request={
    #         'contrato_id': int,
    #         'formato': str,
    #         'guardar_documento': bool,
    #         'plantilla': str
    #     }
    # )
    @require_hr()
    @action(detail=False, methods=["post"], url_path="generar-contrato")
    def generar_contrato(self, request):
        """
        Generar un contrato desde plantilla.

        Args:
            request: Objeto de solicitud HTTP con datos del contrato

        Returns:
            Response: Respuesta con el documento generado o error
        """
        try:
            contrato_id = request.data.get("contrato_id")
            formato = request.data.get("formato", "pdf")
            guardar_documento = request.data.get("guardar_documento", True)
            plantilla = request.data.get("plantilla")

            if not contrato_id:
                return APIResponse.error(
                    message="El ID del contrato es requerido",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Obtener el contrato
            contrato = get_object_or_404(ContratosAdendas, contrato_id=contrato_id)

            if formato == "html":
                html_content = self.template_service.generar_contrato(
                    contrato.contrato_id, tipo_plantilla=plantilla
                )
                return HttpResponse(
                    html_content, content_type="text/html; charset=utf-8"
                )

            elif formato == "pdf":
                html_content = self.template_service.generar_contrato(
                    contrato.contrato_id, tipo_plantilla=plantilla
                )
                pdf_bytes = self.pdf_generator._html_to_pdf(html_content)

                if guardar_documento:
                    nombre_doc = (
                        f"Contrato {contrato.numero_contrato or contrato.contrato_id}"
                    )
                    nombre_archivo = f"contrato_{contrato.contrato_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
                    documento = DocumentosDigitales.objects.create(
                        empleado=contrato.empleado,
                        tipo_documento="contrato_trabajo",
                        categoria="laboral",
                        nombre_documento=nombre_doc,
                        archivo=ContentFile(pdf_bytes, name=nombre_archivo),
                        nombre_archivo_original=nombre_archivo,
                        formato_archivo="pdf",
                        tamano_archivo=len(pdf_bytes),
                        nivel_acceso="restringido",
                        es_version_actual=True,
                        estado_documento="activo",
                    )
                    contrato.documento_generado = True
                    contrato.save(update_fields=["documento_generado"])
                    return APIResponse.success(
                        data={
                            "documento_id": documento.documento_id,
                            "archivo_url": (
                                documento.archivo.url if documento.archivo else None
                            ),
                            "nombre_archivo": documento.nombre_documento,
                        },
                        message="Contrato generado y guardado exitosamente",
                    )
                else:
                    response = HttpResponse(pdf_bytes, content_type="application/pdf")
                    response["Content-Disposition"] = (
                        f'attachment; filename="contrato_{contrato.contrato_id}.pdf"'
                    )
                    return response

            else:
                return APIResponse.error(
                    message="Formato no válido. Use 'html' o 'pdf'",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except ContratosAdendas.DoesNotExist:
            return APIResponse.error(
                message="Contrato no encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return APIResponse.error(
                message=f"Error al generar contrato: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @extend_schema(
    #     description="Generar adenda en formato PDF",
    #     request={
    #         'adenda_id': int,
    #         'formato': str,
    #         'guardar_documento': bool
    #     }
    # )
    @require_hr()
    @action(detail=False, methods=["post"], url_path="generar-adenda")
    def generar_adenda(self, request):
        """
        Generar una adenda desde plantilla.

        Args:
            request: Objeto de solicitud HTTP con datos de la adenda

        Returns:
            Response: Respuesta con el documento generado o error
        """
        try:
            adenda_id = request.data.get("adenda_id")
            formato = request.data.get("formato", "pdf")
            guardar_documento = request.data.get("guardar_documento", True)

            if not adenda_id:
                return APIResponse.error(
                    message="El ID de la adenda es requerido",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Obtener la adenda
            adenda = get_object_or_404(ContratosAdendas, contrato_id=adenda_id)

            if formato == "html":
                html_content = self.template_service.generar_adenda(
                    adenda.contrato_id, tipo_adenda=adenda.tipo_documento
                )
                return HttpResponse(
                    html_content, content_type="text/html; charset=utf-8"
                )

            elif formato == "pdf":
                html_content = self.template_service.generar_adenda(
                    adenda.contrato_id, tipo_adenda=adenda.tipo_documento
                )
                pdf_bytes = self.pdf_generator._html_to_pdf(html_content)

                if guardar_documento:
                    nombre_doc = f"Adenda {adenda.numero_adenda or adenda.contrato_id}"
                    nombre_archivo = f"adenda_{adenda.contrato_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
                    documento = DocumentosDigitales.objects.create(
                        empleado=adenda.empleado,
                        tipo_documento="adenda_contrato",
                        categoria="laboral",
                        nombre_documento=nombre_doc,
                        archivo=ContentFile(pdf_bytes, name=nombre_archivo),
                        nombre_archivo_original=nombre_archivo,
                        formato_archivo="pdf",
                        tamano_archivo=len(pdf_bytes),
                        nivel_acceso="restringido",
                        es_version_actual=True,
                        estado_documento="activo",
                    )
                    return APIResponse.success(
                        data={
                            "documento_id": documento.documento_id,
                            "archivo_url": (
                                documento.archivo.url if documento.archivo else None
                            ),
                            "nombre_archivo": documento.nombre_documento,
                        },
                        message="Adenda generada y guardada exitosamente",
                    )
                else:
                    response = HttpResponse(pdf_bytes, content_type="application/pdf")
                    response["Content-Disposition"] = (
                        f'attachment; filename="adenda_{adenda.contrato_id}.pdf"'
                    )
                    return response

            else:
                return APIResponse.error(
                    message="Formato no válido. Use 'html' o 'pdf'",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except ContratosAdendas.DoesNotExist:
            return APIResponse.error(
                message="Adenda no encontrada", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return APIResponse.error(
                message=f"Error al generar adenda: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @extend_schema(
    #     description="Generar certificado laboral en formato PDF",
    #     request={
    #         'empleado_id': int,
    #         'tipo_certificado': str,
    #         'proposito': str,
    #         'incluir_salario': bool,
    #         'incluir_prestaciones': bool,
    #         'observaciones': str,
    #         'formato': str,
    #         'guardar_documento': bool
    #     }
    # )
    @require_hr()
    @action(detail=False, methods=["post"], url_path="generar-certificado")
    def generar_certificado(self, request):
        """
        Generar un certificado laboral desde plantilla.

        Args:
            request: Objeto de solicitud HTTP con datos del certificado

        Returns:
            Response: Respuesta con el documento generado o error
        """
        try:
            empleado_id = request.data.get("empleado_id")
            tipo_certificado = request.data.get("tipo_certificado", "LABORAL")
            proposito = request.data.get("proposito", "")
            incluir_salario = request.data.get("incluir_salario", False)
            incluir_prestaciones = request.data.get("incluir_prestaciones", False)
            observaciones = request.data.get("observaciones", "")
            formato = request.data.get("formato", "pdf")
            guardar_documento = request.data.get("guardar_documento", True)

            if not empleado_id:
                return APIResponse.error(
                    message="El ID del empleado es requerido",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            # Obtener el empleado
            empleado = get_object_or_404(Empleado, empleado_id=empleado_id)

            # Crear datos del certificado
            certificado_data = {
                "tipo": tipo_certificado,
                "proposito": proposito,
                "incluir_salario": incluir_salario,
                "incluir_prestaciones": incluir_prestaciones,
                "observaciones_adicionales": observaciones,
                "fecha_expedicion": timezone.now().date(),
                "numero_certificado": f"CERT-{empleado.empleado_id}-{timezone.now().strftime('%Y%m%d%H%M%S')}",
            }

            if formato == "html":
                html_content = self.template_service.generar_certificado(
                    empleado.empleado_id,
                    tipo_certificado=tipo_certificado,
                    datos_adicionales=certificado_data,
                )
                return HttpResponse(
                    html_content, content_type="text/html; charset=utf-8"
                )

            elif formato == "pdf":
                html_content = self.template_service.generar_certificado(
                    empleado.empleado_id,
                    tipo_certificado=tipo_certificado,
                    datos_adicionales=certificado_data,
                )
                pdf_bytes = self.pdf_generator._html_to_pdf(html_content)

                if guardar_documento:
                    num_cert = certificado_data["numero_certificado"]
                    nombre_archivo = f"certificado_{empleado.empleado_id}_{timezone.now().strftime('%Y%m%d%H%M%S')}.pdf"
                    documento = DocumentosDigitales.objects.create(
                        empleado=empleado,
                        tipo_documento="certificado_trabajo",
                        categoria="laboral",
                        nombre_documento=f"Certificado Laboral {num_cert}",
                        archivo=ContentFile(pdf_bytes, name=nombre_archivo),
                        nombre_archivo_original=nombre_archivo,
                        formato_archivo="pdf",
                        tamano_archivo=len(pdf_bytes),
                        nivel_acceso="restringido",
                        es_version_actual=True,
                        estado_documento="activo",
                    )
                    return APIResponse.success(
                        data={
                            "documento_id": documento.documento_id,
                            "archivo_url": (
                                documento.archivo.url if documento.archivo else None
                            ),
                            "nombre_archivo": documento.nombre_documento,
                            "numero_certificado": num_cert,
                        },
                        message="Certificado generado y guardado exitosamente",
                    )
                else:
                    response = HttpResponse(pdf_bytes, content_type="application/pdf")
                    response["Content-Disposition"] = (
                        f'attachment; filename="certificado_{empleado.empleado_id}.pdf"'
                    )
                    return response

            else:
                return APIResponse.error(
                    message="Formato no válido. Use 'html' o 'pdf'",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except Empleado.DoesNotExist:
            return APIResponse.error(
                message="Empleado no encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return APIResponse.error(
                message=f"Error al generar certificado: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @extend_schema(
    #     description="Generar reporte de contratos en formato PDF",
    #     request={
    #         'fecha_inicio': str,
    #         'fecha_fin': str,
    #         'area': str,
    #         'tipo_contrato': str,
    #         'estado': str,
    #         'agrupar_por_area': bool,
    #         'incluir_vencimientos': bool,
    #         'incluir_graficos': bool,
    #         'incluir_observaciones': bool,
    #         'formato': str,
    #         'guardar_documento': bool
    #     }
    # )
    @require_hr()
    @action(detail=False, methods=["post"], url_path="generar-reporte")
    def generar_reporte(self, request):
        """
        Generar un reporte de contratos desde plantilla.

        Args:
            request: Objeto de solicitud HTTP con parámetros del reporte

        Returns:
            Response: Respuesta con el documento generado o error
        """
        try:
            # Obtener parámetros del reporte
            fecha_inicio = request.data.get("fecha_inicio")
            fecha_fin = request.data.get("fecha_fin")
            area = request.data.get("area")
            tipo_contrato = request.data.get("tipo_contrato")
            estado = request.data.get("estado")
            agrupar_por_area = request.data.get("agrupar_por_area", False)
            incluir_vencimientos = request.data.get("incluir_vencimientos", True)
            incluir_graficos = request.data.get("incluir_graficos", False)
            incluir_observaciones = request.data.get("incluir_observaciones", True)
            formato = request.data.get("formato", "pdf")
            guardar_documento = request.data.get("guardar_documento", True)

            # Crear datos del reporte
            reporte_data = {
                "fecha_inicio": fecha_inicio,
                "fecha_fin": fecha_fin,
                "area": area,
                "tipo_contrato": tipo_contrato,
                "estado": estado,
                "agrupar_por_area": agrupar_por_area,
                "incluir_vencimientos": incluir_vencimientos,
                "incluir_graficos": incluir_graficos,
                "incluir_observaciones": incluir_observaciones,
                "usuario_generador": getattr(request.user, 'nombre_completo', '')
                or request.user.username,
                "fecha_generacion": timezone.now(),
            }

            if formato == "html":
                html_content = self.template_service.generar_reporte_html(reporte_data)
                return HttpResponse(
                    html_content, content_type="text/html; charset=utf-8"
                )

            elif formato == "pdf":
                with transaction.atomic():
                    documento = self.pdf_generator.generar_reporte_pdf(
                        reporte_data=reporte_data,
                        guardar_en_bd=guardar_documento,
                        usuario_creador=request.user,
                    )

                if guardar_documento:
                    return APIResponse.success(
                        data={
                            "documento_id": documento.documento_id,
                            "archivo_url": (
                                documento.archivo.url if documento.archivo else None
                            ),
                            "nombre_archivo": documento.nombre_documento,
                        },
                        message="Reporte generado y guardado exitosamente",
                    )
                else:
                    response = HttpResponse(documento, content_type="application/pdf")
                    response["Content-Disposition"] = (
                        f'attachment; filename="reporte_contratos_{timezone.now().strftime("%Y%m%d")}.pdf"'
                    )
                    return response

            else:
                return APIResponse.error(
                    message="Formato no válido. Use 'html' o 'pdf'",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

        except Exception as e:
            return APIResponse.error(
                message=f"Error al generar reporte: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # @extend_schema(
    #     description="Listar plantillas disponibles"
    # )
    @require_authenticated()
    @action(detail=False, methods=["get"], url_path="plantillas-disponibles")
    def plantillas_disponibles(self, request):
        """
        Listar todas las plantillas disponibles para generación de documentos.

        Returns:
            Response: Lista de plantillas organizadas por tipo
        """
        try:
            plantillas = self.template_service.obtener_plantillas_disponibles()

            return APIResponse.success(
                data=plantillas, message="Plantillas obtenidas exitosamente"
            )

        except Exception as e:
            return APIResponse.error(
                message=f"Error al obtener plantillas: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    # ─────────────────────────────────────────────────────────────
    # GESTIÓN DE PLANTILLAS WORD
    # ─────────────────────────────────────────────────────────────

    @require_authenticated()
    @action(detail=False, methods=["get"], url_path="plantillas-word")
    def listar_plantillas_word(self, request):
        """Listar todas las plantillas Word disponibles."""
        try:
            tipo = request.query_params.get("tipo")
            qs = PlantillaDocumento.objects.filter(activa=True)
            if tipo:
                qs = qs.filter(tipo=tipo)
            qs = qs.order_by("-fecha_creacion")

            data = [
                {
                    "plantilla_id": p.plantilla_id,
                    "tipo": p.tipo,
                    "tipo_texto": p.get_tipo_display(),
                    "nombre": p.nombre,
                    "descripcion": p.descripcion,
                    "activa": p.activa,
                    "fecha_creacion": p.fecha_creacion.isoformat(),
                    "variables_disponibles": p.variables_disponibles,
                    "archivo_nombre": p.archivo.name.split("/")[-1] if p.archivo else None,
                }
                for p in qs
            ]
            return APIResponse.success(data=data, message="Plantillas obtenidas exitosamente")
        except Exception as e:
            return APIResponse.error(
                message=f"Error al listar plantillas: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @require_hr()
    @action(detail=False, methods=["post"], url_path="plantillas-word/subir")
    def subir_plantilla_word(self, request):
        """Subir una nueva plantilla Word (.docx)."""
        try:
            archivo = request.FILES.get("archivo")
            nombre = request.data.get("nombre", "").strip()
            tipo = request.data.get("tipo", "").strip()
            descripcion = request.data.get("descripcion", "")

            if not archivo:
                return APIResponse.error(message="Se requiere el archivo .docx", status_code=status.HTTP_400_BAD_REQUEST)
            if not nombre:
                return APIResponse.error(message="El nombre es requerido", status_code=status.HTTP_400_BAD_REQUEST)
            if not tipo:
                return APIResponse.error(message="El tipo es requerido", status_code=status.HTTP_400_BAD_REQUEST)

            tipos_validos = [c[0] for c in PlantillaDocumento.TIPO_CHOICES]
            if tipo not in tipos_validos:
                return APIResponse.error(
                    message=f"Tipo inválido. Valores permitidos: {', '.join(tipos_validos)}",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            if not archivo.name.lower().endswith('.docx'):
                return APIResponse.error(message="Solo se permiten archivos .docx", status_code=status.HTTP_400_BAD_REQUEST)

            plantilla = PlantillaDocumento.objects.create(
                tipo=tipo,
                nombre=nombre,
                descripcion=descripcion,
                archivo=archivo,
                activa=True,
                creada_por=request.user,
            )

            return APIResponse.success(
                data={
                    "plantilla_id": plantilla.plantilla_id,
                    "tipo": plantilla.tipo,
                    "tipo_texto": plantilla.get_tipo_display(),
                    "nombre": plantilla.nombre,
                    "variables_disponibles": plantilla.variables_disponibles,
                },
                message="Plantilla subida exitosamente",
                status_code=status.HTTP_201_CREATED,
            )
        except Exception as e:
            return APIResponse.error(
                message=f"Error al subir plantilla: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @require_hr()
    @action(detail=False, methods=["delete"], url_path="plantillas-word/(?P<plantilla_id>[0-9]+)/eliminar")
    def eliminar_plantilla_word(self, request, plantilla_id=None):
        """Eliminar (desactivar) una plantilla Word."""
        try:
            plantilla = get_object_or_404(PlantillaDocumento, plantilla_id=plantilla_id)
            plantilla.activa = False
            plantilla.save(update_fields=["activa"])
            return APIResponse.success(message="Plantilla eliminada exitosamente")
        except Exception as e:
            return APIResponse.error(
                message=f"Error al eliminar plantilla: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @require_authenticated()
    @action(detail=False, methods=["get"], url_path="plantillas-word/(?P<plantilla_id>[0-9]+)/descargar")
    def descargar_plantilla_word(self, request, plantilla_id=None):
        """Descargar el archivo .docx de una plantilla."""
        try:
            plantilla = get_object_or_404(PlantillaDocumento, plantilla_id=plantilla_id, activa=True)
            with open(plantilla.archivo.path, 'rb') as f:
                docx_bytes = f.read()
            response = HttpResponse(docx_bytes, content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
            nombre_archivo = f"plantilla_{plantilla.tipo}_{plantilla.plantilla_id}.docx"
            response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
            return response
        except Exception as e:
            return APIResponse.error(
                message=f"Error al descargar plantilla: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @require_hr()
    @action(detail=False, methods=["post"], url_path="generar-desde-plantilla-word")
    def generar_desde_plantilla_word(self, request):
        """
        Genera un documento usando una plantilla Word (.docx).

        Parámetros:
            plantilla_id: ID de la plantilla
            empleado_id: ID del empleado (para cert/constancia)
            contrato_id: ID del contrato (para contratos/adendas)
            formato: 'docx' (default) o 'pdf'
            # Para certificados:
            proposito: Propósito del certificado
            incluir_salario: bool
            numero_certificado: (auto-generado si no se provee)
            guardar_documento: bool (default True)
        """
        try:
            plantilla_id = request.data.get("plantilla_id")
            empleado_id = request.data.get("empleado_id")
            contrato_id = request.data.get("contrato_id")
            formato = request.data.get("formato", "docx")
            guardar = request.data.get("guardar_documento", True)

            if not plantilla_id:
                return APIResponse.error(message="plantilla_id es requerido", status_code=status.HTTP_400_BAD_REQUEST)

            plantilla = get_object_or_404(PlantillaDocumento, plantilla_id=plantilla_id, activa=True)

            # Construir variables según el tipo de plantilla
            if plantilla.tipo in ('certificado_trabajo', 'constancia_laboral'):
                if not empleado_id:
                    return APIResponse.error(message="empleado_id es requerido para este tipo de plantilla", status_code=status.HTTP_400_BAD_REQUEST)
                empleado = get_object_or_404(Empleado, empleado_id=empleado_id)
                numero_cert = request.data.get("numero_certificado") or f"CERT-{empleado.empleado_id}-{timezone.now().strftime('%Y%m%d%H%M%S')}"
                variables = self.word_service.construir_variables_certificado(
                    empleado=empleado,
                    tipo=plantilla.get_tipo_display(),
                    numero_certificado=numero_cert,
                    proposito=request.data.get("proposito", ""),
                    incluir_salario=request.data.get("incluir_salario", False),
                )
                nombre_base = f"{plantilla.tipo}_{empleado.empleado_id}"
                asociado_empleado = empleado
            elif plantilla.tipo in ('contrato', 'adenda'):
                if not contrato_id:
                    return APIResponse.error(message="contrato_id es requerido para este tipo de plantilla", status_code=status.HTTP_400_BAD_REQUEST)
                contrato = get_object_or_404(ContratosAdendas, contrato_id=contrato_id)
                variables = self.word_service.construir_variables_contrato(contrato)
                nombre_base = f"{plantilla.tipo}_{contrato.contrato_id}"
                asociado_empleado = contrato.empleado
            else:
                return APIResponse.error(message="Tipo de plantilla no soportado", status_code=status.HTTP_400_BAD_REQUEST)

            # Generar el documento
            docx_bytes = self.word_service.generar_desde_plantilla(plantilla, variables)

            # Convertir a PDF si se solicita
            if formato == "pdf":
                pdf_bytes = self.word_service.pdf_desde_docx(docx_bytes)
                if pdf_bytes:
                    content_bytes = pdf_bytes
                    ext = "pdf"
                    content_type = "application/pdf"
                else:
                    # Fallback a docx si la conversión falla
                    content_bytes = docx_bytes
                    ext = "docx"
                    content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            else:
                content_bytes = docx_bytes
                ext = "docx"
                content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

            if guardar:
                nombre_archivo = f"{nombre_base}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                tipo_doc = plantilla.tipo if plantilla.tipo in ['certificado_trabajo', 'constancia_laboral', 'contrato', 'adenda'] else 'otros'
                documento = DocumentosDigitales.objects.create(
                    empleado=asociado_empleado,
                    tipo_documento=tipo_doc,
                    categoria='laboral',
                    nombre_documento=f"{plantilla.nombre} - {asociado_empleado.nombre_completo}",
                    archivo=ContentFile(content_bytes, name=nombre_archivo),
                    nombre_archivo_original=nombre_archivo,
                    formato_archivo=ext,
                    tamano_archivo=len(content_bytes),
                    nivel_acceso='restringido',
                    es_version_actual=True,
                    estado_documento='activo',
                )
                return APIResponse.success(
                    data={
                        "documento_id": documento.documento_id,
                        "archivo_url": documento.archivo.url if documento.archivo else None,
                        "nombre_archivo": documento.nombre_documento,
                        "formato": ext,
                    },
                    message="Documento generado y guardado exitosamente",
                )
            else:
                nombre_archivo = f"{nombre_base}_{timezone.now().strftime('%Y%m%d%H%M%S')}.{ext}"
                response = HttpResponse(content_bytes, content_type=content_type)
                response["Content-Disposition"] = f'attachment; filename="{nombre_archivo}"'
                return response

        except Exception as e:
            return APIResponse.error(
                message=f"Error al generar documento: {str(e)}",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
