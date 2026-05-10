"""OnboardingViewSet — bounded-context module per B.5b #82.

Migrated from `api/v1/rrhh/views.py` (lines 1640-2158 pre-migration). The
ViewSet uses the existing `TenantAwareViewSetMixin` (from B.1) and the
`OnboardingService` business-logic layer in `apps/onboarding/services/`.
"""

import logging
import os

from django.utils import timezone
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.core.decorators import require_authenticated, require_hr
from apps.core.pagination import StandardResultsSetPagination
from apps.core.responses import APIResponse
from apps.core.viewsets import TenantAwareViewSetMixin
from apps.documents.models import DigitalDocument
from apps.onboarding.models import OnboardingProcess

from api.v1.rrhh.permissions import RRHHPermission
from api.v1.rrhh.serializers import (
    OnboardingEmpleadoSerializer,
    OnboardingIniciarSerializer,
    OnboardingValidacionSerializer,
)

logger = logging.getLogger(__name__)


class OnboardingViewSet(TenantAwareViewSetMixin, viewsets.ModelViewSet):
    """ViewSet para gestionar el proceso de onboarding de nuevos empleados."""

    queryset = OnboardingProcess.objects.select_related(
        "empleado", "usuario", "validado_por"
    )
    serializer_class = OnboardingEmpleadoSerializer
    permission_classes = [RRHHPermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = [
        "empleado__nombres_empleado",
        "empleado__apellido_paterno",
        "empleado__numero_documento",
    ]
    ordering_fields = ["fecha_inicio", "estado_onboarding", "fecha_completado"]
    ordering = ["-fecha_inicio"]

    def get_permissions(self):
        """Allow authenticated employees to use upload actions."""
        if self.action in (
            "subir_foto",
            "subir_documento",
            "mi_onboarding",
            "retrieve",
        ):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == "create":
            return OnboardingIniciarSerializer
        if self.action in ["validar", "rechazar"]:
            return OnboardingValidacionSerializer
        return OnboardingEmpleadoSerializer

    def get_queryset(self):
        # B.1 (#15): tenant filter applied via _filter_by_tenant so OnboardingProcess
        # rows are scoped to request.tenant. TenantAwareViewSetMixin.get_queryset()
        # is NOT called here (we override fully) — apply the helper manually.
        queryset = OnboardingProcess.objects.select_related(
            "empleado", "usuario", "validado_por"
        )
        estado = self.request.query_params.get("estado")
        if estado:
            queryset = queryset.filter(estado_onboarding=estado)
        return self._filter_by_tenant(queryset)

    @require_hr()
    def list(self, request, *args, **kwargs):
        """Listar onboardings - requiere rol RRHH."""
        return super().list(request, *args, **kwargs)

    @require_hr()
    def create(self, request, *args, **kwargs):
        """Iniciar onboarding - requiere rol RRHH."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        onboarding = result["onboarding"]
        response_serializer = OnboardingEmpleadoSerializer(onboarding)

        return APIResponse.success(
            data={
                **response_serializer.data,
                "username": result["usuario"].username,
                "email_enviado": result["email_enviado"],
            },
            message=f"Onboarding iniciado para {result['empleado'].nombre_completo}",
            status_code=status.HTTP_201_CREATED,
        )

    @require_authenticated()
    def retrieve(self, request, *args, **kwargs):
        """Ver detalle de onboarding - empleado solo ve el suyo."""
        from apps.onboarding.services import OnboardingService

        onboarding = self.get_object()
        user = request.user
        # Non-HR users can only see their own onboarding
        if not (user.es_administrador or user.es_rrhh or user.es_admin_rrhh):
            if onboarding.usuario_id != user.pk:
                return APIResponse.error(
                    message="No tiene permisos para ver este onboarding",
                    status_code=status.HTTP_403_FORBIDDEN,
                )
        # Recalcular estado si no está completado
        if onboarding.estado_onboarding != "completado":
            resultado = OnboardingService.actualizar_estado_onboarding(
                onboarding.empleado_id
            )
            onboarding = (
                resultado["onboarding"] if isinstance(resultado, dict) else resultado
            ) or onboarding
        serializer = self.get_serializer(onboarding)
        return APIResponse.success(data=serializer.data)

    @action(detail=False, methods=["get"])
    @require_authenticated()
    def mi_onboarding(self, request):
        """Obtener el onboarding del usuario actual, recalculando el estado al momento."""
        from apps.onboarding.services import OnboardingService

        try:
            onboarding = OnboardingProcess.objects.select_related(
                "empleado", "usuario", "validado_por"
            ).get(usuario=request.user)
            # Recalcular estado en cada consulta para reflejar datos actualizados
            if onboarding.estado_onboarding != "completado":
                resultado = OnboardingService.actualizar_estado_onboarding(
                    onboarding.empleado_id
                )
                onboarding = (
                    resultado["onboarding"]
                    if isinstance(resultado, dict)
                    else resultado
                ) or onboarding
            serializer = self.get_serializer(onboarding)
            return APIResponse.success(data=serializer.data)
        except OnboardingProcess.DoesNotExist:
            return APIResponse.error(
                message="No tiene un proceso de onboarding activo",
                status_code=status.HTTP_404_NOT_FOUND,
            )

    @action(detail=True, methods=["post"])
    @require_hr()
    def validar(self, request, pk=None):
        """Validar el onboarding y aprobar todos los documentos."""
        from apps.onboarding.services import (
            OnboardingNotificationService,
            OnboardingService,
        )

        serializer = OnboardingValidacionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        accion = serializer.validated_data["accion"]
        observaciones = serializer.validated_data.get("observaciones", "")

        onboarding = self.get_object()

        if accion == "aprobar":
            result = OnboardingService.validar_onboarding(
                onboarding.pk, request.user, observaciones
            )
            if not result:
                return APIResponse.error(
                    message="Onboarding no encontrado", status_code=404
                )
            try:
                OnboardingNotificationService.notificar_onboarding_aprobado(result)
            except Exception:
                pass
            response_serializer = OnboardingEmpleadoSerializer(result)
            return APIResponse.success(
                data=response_serializer.data,
                message="Onboarding validado y completado exitosamente",
            )
        else:
            onboarding.marcar_observado(observaciones)
            try:
                OnboardingNotificationService.notificar_onboarding_observado(
                    onboarding, observaciones
                )
            except Exception:
                pass
            response_serializer = OnboardingEmpleadoSerializer(onboarding)
            return APIResponse.success(
                data=response_serializer.data,
                message="Onboarding observado - se requieren correcciones",
            )

    @action(
        detail=True, methods=["post"], url_path=r"documentos/(?P<doc_id>[^/.]+)/aprobar"
    )
    @require_hr()
    def aprobar_documento(self, request, pk=None, doc_id=None):
        """RRHH approves a specific document from the onboarding legajo."""
        from apps.onboarding.services import OnboardingService

        onboarding = self.get_object()
        try:
            doc = DigitalDocument.objects.get(
                documento_id=doc_id,
                empleado=onboarding.empleado,
                es_version_actual=True,
            )
        except DigitalDocument.DoesNotExist:
            return APIResponse.error(
                message="Documento no encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        doc.validar_documento(request.user)
        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        return APIResponse.success(
            message=f"Documento '{doc.nombre_documento}' aprobado",
            data={
                "id": doc.documento_id,
                "estado_documento": doc.estado_documento,
            },
        )

    @action(
        detail=True,
        methods=["post"],
        url_path=r"documentos/(?P<doc_id>[^/.]+)/rechazar",
    )
    @require_hr()
    def rechazar_documento(self, request, pk=None, doc_id=None):
        """RRHH rejects a specific document with a mandatory motivo."""
        from apps.onboarding.services import (
            OnboardingNotificationService,
            OnboardingService,
        )

        motivo = request.data.get("motivo", "").strip()
        if not motivo:
            return APIResponse.error(
                message="El campo motivo es requerido para rechazar un documento"
            )
        onboarding = self.get_object()
        try:
            doc = DigitalDocument.objects.get(
                documento_id=doc_id,
                empleado=onboarding.empleado,
                es_version_actual=True,
            )
        except DigitalDocument.DoesNotExist:
            return APIResponse.error(
                message="Documento no encontrado", status_code=status.HTTP_404_NOT_FOUND
            )
        doc.rechazar_documento(request.user, motivo)
        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        try:
            OnboardingNotificationService.notificar_documento_rechazado(
                onboarding, doc, motivo
            )
        except Exception:
            pass
        return APIResponse.success(
            message=f"Documento '{doc.nombre_documento}' rechazado",
            data={
                "id": doc.documento_id,
                "estado_documento": doc.estado_documento,
            },
        )

    @action(detail=True, methods=["post"])
    @require_hr()
    def reenviar_email(self, request, pk=None):
        """Reenviar email de bienvenida."""
        from apps.onboarding.services import OnboardingService

        onboarding = self.get_object()
        result = OnboardingService.reenviar_email_bienvenida(onboarding.pk)

        if not result:
            return APIResponse.error(
                message="Onboarding no encontrado", status_code=404
            )

        if result["email_enviado"]:
            return APIResponse.success(
                message="Email de bienvenida reenviado exitosamente"
            )
        else:
            return APIResponse.error(
                message="Error al reenviar el email", status_code=500
            )

    @action(detail=True, methods=["post"], url_path="corregir-correo")
    @require_hr()
    def corregir_correo(self, request, pk=None):
        """Actualiza el correo del empleado y reenvía el email de bienvenida."""
        from apps.onboarding.services import OnboardingService

        nuevo_correo = request.data.get("correo_personal", "").strip()
        if not nuevo_correo:
            return APIResponse.error(message="correo_personal es requerido")
        try:
            onboarding = self.get_object()
            onboarding.empleado.correo_personal = nuevo_correo
            onboarding.empleado.save(update_fields=["correo_personal"])
            onboarding.usuario.email = nuevo_correo
            onboarding.usuario.save(update_fields=["email"])
            result = OnboardingService.reenviar_email_bienvenida(
                onboarding.pk
            )
            if result and result.get("email_enviado"):
                return APIResponse.success(
                    message="Correo actualizado y email de bienvenida reenviado",
                    data={"email_enviado": True, "correo_personal": nuevo_correo},
                )
            return APIResponse.error(
                message="Correo actualizado pero el email no pudo enviarse. Revise la configuración SMTP.",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
        except Exception as e:
            return APIResponse.error(message=str(e))

    @action(detail=True, methods=["post"], url_path="actualizar-estado")
    @require_hr()
    def actualizar_estado(self, request, pk=None):
        """Recalcula el estado del checklist de onboarding basado en documentos y datos actuales."""
        from apps.onboarding.services import OnboardingService

        onboarding = self.get_object()
        resultado = OnboardingService.actualizar_estado_onboarding(
            onboarding.empleado_id
        )
        if not resultado:
            return APIResponse.error(
                message="No se encontró el onboarding", status_code=404
            )
        updated = resultado["onboarding"] if isinstance(resultado, dict) else resultado
        serializer = OnboardingEmpleadoSerializer(updated)
        return APIResponse.success(
            data=serializer.data,
            message="Estado de onboarding actualizado",
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="subir-foto",
        parser_classes=[MultiPartParser],
    )
    @require_authenticated()
    def subir_foto(self, request):
        """El empleado en onboarding sube su foto de perfil (JPG o PNG)."""
        from apps.onboarding.services import OnboardingService

        archivo = request.FILES.get("archivo")
        if not archivo:
            return APIResponse.error(message="Se requiere el archivo de foto")
        if archivo.content_type not in ("image/jpeg", "image/png"):
            return APIResponse.error(message="Solo se permiten imágenes JPG o PNG")
        try:
            onboarding = OnboardingProcess.objects.get(usuario=request.user)
        except OnboardingProcess.DoesNotExist:
            return APIResponse.error(message="No tiene un proceso de onboarding activo")
        empleado = onboarding.empleado
        # Usar crear_nueva_version si ya existe una foto, o crear nueva
        doc_existente = DigitalDocument.objects.filter(
            empleado=empleado,
            tipo_documento="foto",
            es_version_actual=True,
        ).first()
        if doc_existente:
            doc = doc_existente.crear_nueva_version(
                archivo=archivo, usuario=request.user
            )
        else:
            doc = DigitalDocument.objects.create(
                empleado=empleado,
                tipo_documento="foto",
                categoria="personal",
                nombre_documento="Foto de perfil",
                archivo=archivo,
                nombre_archivo_original=archivo.name,
                formato_archivo=(
                    archivo.name.rsplit(".", 1)[-1].lower()
                    if "." in archivo.name
                    else ""
                ),
                tamano_archivo=archivo.size,
                estado_documento="pendiente_revision",
                nivel_acceso="restringido",
                subido_por=request.user,
            )
        empleado.ruta_fotografia = doc.archivo.name
        empleado.save(update_fields=["ruta_fotografia"])
        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        return APIResponse.success(
            message="Foto subida exitosamente",
            data={
                "id": doc.pk,
                "archivo_url": (
                    request.build_absolute_uri(doc.archivo.url) if doc.archivo else None
                ),
                "estado_documento": doc.estado_documento,
                "fecha_subida": (
                    doc.fecha_subida.isoformat() if doc.fecha_subida else None
                ),
            },
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="subir-documento",
        parser_classes=[MultiPartParser],
    )
    @require_authenticated()
    def subir_documento(self, request):
        """El empleado en onboarding sube un documento PDF a su legajo."""
        from apps.onboarding.services import OnboardingService

        _TIPO_CATEGORIA_MAP = {
            "dni": "personal",
            "carnet_extranjeria": "personal",
            "dni_familiar": "familiar",
            "certificado_nacimiento": "familiar",
            "acta_matrimonio": "familiar",
            "certificado_union_hecho": "familiar",
            "partida_nacimiento": "familiar",
            "certificado_estudios": "academico",
            "titulo_profesional": "academico",
            "diploma": "academico",
            "certificado_capacitacion": "academico",
            "declaracion_jurada": "laboral",
            "cv": "laboral",
            "certificado_trabajo": "laboral",
            "constancia_trabajo": "laboral",
            "carta_recomendacion": "laboral",
        }

        archivo = request.FILES.get("archivo")
        tipo_documento = request.data.get("tipo_documento", "").strip()
        if not archivo:
            return APIResponse.error(message="Se requiere el archivo")
        if archivo.content_type != "application/pdf":
            return APIResponse.error(message="Solo se permiten archivos PDF")
        if tipo_documento not in _TIPO_CATEGORIA_MAP:
            return APIResponse.error(
                message=f"Tipo de documento no válido. Opciones: {', '.join(_TIPO_CATEGORIA_MAP.keys())}"
            )
        try:
            onboarding = OnboardingProcess.objects.get(usuario=request.user)
        except OnboardingProcess.DoesNotExist:
            return APIResponse.error(message="No tiene un proceso de onboarding activo")
        empleado = onboarding.empleado
        categoria = _TIPO_CATEGORIA_MAP[tipo_documento]
        nombre_documento = request.data.get(
            "nombre_documento", tipo_documento.replace("_", " ").title()
        )
        # Usar crear_nueva_version si ya existe el mismo tipo_documento
        doc_existente = DigitalDocument.objects.filter(
            empleado=empleado,
            tipo_documento=tipo_documento,
            es_version_actual=True,
        ).first()
        if doc_existente:
            doc = doc_existente.crear_nueva_version(
                archivo=archivo, usuario=request.user
            )
        else:
            doc = DigitalDocument.objects.create(
                empleado=empleado,
                tipo_documento=tipo_documento,
                categoria=categoria,
                nombre_documento=nombre_documento,
                archivo=archivo,
                nombre_archivo_original=archivo.name,
                formato_archivo=(
                    archivo.name.rsplit(".", 1)[-1].lower()
                    if "." in archivo.name
                    else ""
                ),
                tamano_archivo=archivo.size,
                estado_documento="pendiente_revision",
                nivel_acceso="restringido",
                subido_por=request.user,
            )
        # Optional FK linking: attach document to academico/curso record
        # Note: FamilyMember does not have a documento FK — familiar_id param is accepted
        # but only used to tag the doc's category context (no DB link on familiar itself)
        familiar_id = request.data.get(
            "id"
        )  # accepted, reserved for future use

        academico_id = request.data.get("id")
        if academico_id:
            try:
                from apps.employees.models import AcademicRecord

                academico = AcademicRecord.objects.get(
                    academico_id=int(academico_id), empleado=onboarding.empleado
                )
                academico.documento = doc
                academico.save(update_fields=["documento"])
            except (AcademicRecord.DoesNotExist, ValueError, AttributeError):
                pass

        curso_id = request.data.get("id")
        if curso_id:
            try:
                from apps.employees.models import Certification

                curso = Certification.objects.get(
                    curso_id=int(curso_id), empleado=onboarding.empleado
                )
                curso.documento = doc
                curso.save(update_fields=["documento"])
            except (Certification.DoesNotExist, ValueError):
                pass

        OnboardingService.actualizar_estado_onboarding(onboarding.empleado_id)
        return APIResponse.success(
            message="Documento subido exitosamente",
            data={
                "id": doc.pk,
                "tipo_documento": doc.tipo_documento,
                "estado_documento": doc.estado_documento,
                "fecha_subida": (
                    doc.fecha_subida.isoformat() if doc.fecha_subida else None
                ),
                "nombre_documento": doc.nombre_documento,
                "archivo_url": (
                    request.build_absolute_uri(doc.archivo.url) if doc.archivo else None
                ),
            },
        )
