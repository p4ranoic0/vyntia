"""Servicio para gestionar el proceso de onboarding de nuevos empleados."""

import logging
import unicodedata

from ..models import OnboardingProcess
from apps.documents.models import DigitalDocument
from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from app_rrhh.tasks import send_email_html_task
from django.conf import settings
from django.db import transaction
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.crypto import get_random_string

logger = logging.getLogger(__name__)

# Documentos requeridos para el onboarding, organizados por checklist flag
DOCUMENTOS_REQUERIDOS = {
    "dni_subido": [
        {"tipo_documento": "dni", "categoria": "personal", "label": "Copia de DNI"},
    ],
    "declaraciones_juradas_subidas": [
        {
            "tipo_documento": "declaracion_jurada",
            "categoria": "legal",
            "label": "Declaracion Jurada",
        },
    ],
    "certificados_academicos_subidos": [
        {
            "tipo_documento": "certificado_estudios",
            "categoria": "academico",
            "label": "Certificado de Estudios",
        },
        {
            "tipo_documento": "titulo_profesional",
            "categoria": "academico",
            "label": "Titulo Profesional",
        },
    ],
    "certificados_trabajo_subidos": [
        {
            "tipo_documento": "certificado_trabajo",
            "categoria": "laboral",
            "label": "Certificado de Trabajo",
        },
    ],
    "documentos_familiares_subidos": [
        {
            "tipo_documento": "dni_familiar",
            "categoria": "familiar",
            "label": "DNI de Familiares",
        },
        {
            "tipo_documento": "acta_matrimonio",
            "categoria": "familiar",
            "label": "Acta de Matrimonio (si aplica)",
        },
    ],
}


class OnboardingService:
    """Servicio principal para el flujo de onboarding."""

    @staticmethod
    def _enviar_email_sincrono(
        subject, from_email, recipient, text_content, html_content
    ):
        """Envio sincrono de email (SMTP/console segun EMAIL_BACKEND)."""
        from django.core.mail import EmailMultiAlternatives

        msg = EmailMultiAlternatives(subject, text_content, from_email, [recipient])
        msg.attach_alternative(html_content, "text/html")
        msg.send()

    @staticmethod
    def _normalizar_texto(texto):
        """Remueve acentos y caracteres especiales para generar usernames."""
        nfkd = unicodedata.normalize("NFKD", texto)
        return "".join(c for c in nfkd if not unicodedata.combining(c))

    @staticmethod
    def generar_username(nombres, apellido_paterno):
        """
        Genera un username a partir del nombre y apellido.
        Formato: primera letra del nombre + apellido paterno (todo en minusculas).
        Maneja colisiones agregando un numero secuencial.
        """
        nombres_clean = OnboardingService._normalizar_texto(nombres.strip().lower())
        apellido_clean = OnboardingService._normalizar_texto(
            apellido_paterno.strip().lower()
        )

        # Primera letra del primer nombre + apellido
        primera_letra = nombres_clean[0] if nombres_clean else ""
        base_username = f"{primera_letra}{apellido_clean}".replace(" ", "")

        # Verificar colisiones
        username = base_username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1

        return username

    @staticmethod
    def generar_password_temporal():
        """Genera una contrasena temporal segura."""
        return get_random_string(
            length=12,
            allowed_chars="abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789!@#$",
        )

    @staticmethod
    def enviar_email_bienvenida(usuario, password_temporal):
        """
        Envia el email de bienvenida con las credenciales temporales.
        En desarrollo se muestra en consola, en produccion se envia por SMTP.
        """
        empleado = usuario.empleado
        nombre_empleado = (
            empleado.nombre_completo if empleado else usuario.nombres_usuario
        )
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")

        context = {
            "nombre_empleado": nombre_empleado,
            "username": usuario.username,
            "password_temporal": password_temporal,
            "frontend_url": frontend_url,
        }

        # Renderizar templates
        html_content = render_to_string("emails/bienvenida.html", context)
        text_content = render_to_string("emails/bienvenida.txt", context)

        subject = "Bienvenido - Intranet RRHH"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@intranet.gob.pe")
        recipient = empleado.correo_personal if empleado else usuario.email

        # En backends de desarrollo no tiene sentido encolar en Celery.
        # El correo se imprime en consola/memoria/archivo de forma sincrona.
        email_backend = getattr(settings, "EMAIL_BACKEND", "")
        backends_sincronos = {
            "django.core.mail.backends.console.EmailBackend",
            "django.core.mail.backends.locmem.EmailBackend",
            "django.core.mail.backends.filebased.EmailBackend",
        }

        if email_backend in backends_sincronos:
            try:
                OnboardingService._enviar_email_sincrono(
                    subject,
                    from_email,
                    recipient,
                    text_content,
                    html_content,
                )
                logger.info(
                    "Email de bienvenida enviado sincronicamente a %s (backend=%s)",
                    recipient,
                    email_backend,
                )
                return True
            except Exception as sync_error:
                logger.error(
                    "Error al enviar email sincrono a %s (backend=%s): %s",
                    recipient,
                    email_backend,
                    sync_error,
                )
                return False

        try:
            send_email_html_task.apply_async(
                subject=subject,
                from_email=from_email,
                recipients=[recipient],
                text_content=text_content,
                html_content=html_content,
                ignore_result=True,
            )
            logger.info(
                "Email de bienvenida encolado para %s (usuario %s)",
                recipient,
                usuario.username,
            )
            return True
        except Exception as e:
            logger.warning("Celery no disponible, enviando email sincronamente: %s", e)
            try:
                OnboardingService._enviar_email_sincrono(
                    subject,
                    from_email,
                    recipient,
                    text_content,
                    html_content,
                )
                logger.info("Email de bienvenida enviado sincronamente a %s", recipient)
                return True
            except Exception as sync_error:
                logger.error("Error al enviar email sincronamente a %s: %s", recipient, sync_error)
                return False

    @staticmethod
    @transaction.atomic
    def crear_onboarding_completo(empleado_data, creado_por):
        """
        Crea el flujo completo de onboarding:
        1. Crea el registro de Employee
        2. Genera username y password temporal
        3. Crea el User vinculado al Employee
        4. Crea el registro de OnboardingProcess
        5. Envia email de bienvenida

        Args:
            empleado_data: dict con datos del empleado (nombres, apellidos, DNI, email, etc.)
            creado_por: User que inicia el onboarding (RRHH)

        Returns:
            dict con onboarding, empleado, usuario y password_temporal
        """
        # 1. Crear Employee
        empleado = Employee.objects.create(
            nombres_empleado=empleado_data["nombres_empleado"],
            apellido_paterno=empleado_data["apellido_paterno"],
            apellido_materno=empleado_data.get("apellido_materno", ""),
            numero_documento=empleado_data["numero_documento"],
            correo_personal=empleado_data["correo_personal"],
            genero_empleado=empleado_data.get("genero_empleado", "masculino"),
            fecha_nacimiento=empleado_data.get("fecha_nacimiento"),
            estado_empleado="activo",
        )

        # 2. Generar credenciales
        username = OnboardingService.generar_username(
            empleado.nombres_empleado,
            empleado.apellido_paterno,
        )
        password_temporal = OnboardingService.generar_password_temporal()

        # 3. Crear User
        usuario = User.objects.create_user(
            username=username,
            email=empleado.correo_personal,
            password=password_temporal,
            nombres_usuario=empleado.nombres_empleado,
            apellidos_usuario=f"{empleado.apellido_paterno} {empleado.apellido_materno}".strip(),
            tipo_usuario="empleado",
            nivel_acceso="personal",
            empleado=empleado,
            estado_usuario="pendiente",
            requiere_cambio_password=True,
        )

        # Asignar rol de empleado
        try:
            rol_empleado = Role.objects.filter(
                nombre_rol__in=["Employee", "empleado"], estado_rol="activo"
            ).first()
            if rol_empleado:
                UserRole.objects.create(
                    usuario=usuario,
                    rol=rol_empleado,
                    estado_asignacion="activo",
                )
        except Exception as e:
            logger.warning(f"No se pudo asignar rol de empleado: {e}")

        # 4. Crear OnboardingProcess
        onboarding = OnboardingProcess.objects.create(
            empleado=empleado,
            usuario=usuario,
            estado_onboarding="pendiente_datos",
        )

        # 5. Enviar email de bienvenida
        email_enviado = OnboardingService.enviar_email_bienvenida(
            usuario, password_temporal
        )
        if email_enviado:
            onboarding.email_bienvenida_enviado = True
            onboarding.fecha_email_bienvenida = timezone.now()
            onboarding.save()

        logger.info(
            f"Onboarding creado para {empleado.nombre_completo} "
            f"(usuario: {username}) por {creado_por.username}"
        )

        return {
            "onboarding": onboarding,
            "empleado": empleado,
            "usuario": usuario,
            "password_temporal": password_temporal,
            "email_enviado": email_enviado,
        }

    @staticmethod
    def actualizar_estado_onboarding(empleado_id):
        """
        Recalcula el estado del onboarding basado en los documentos subidos.
        Verifica cada categoria de documentos requeridos.

        Acepta empleado_id (FK a Employee) o onboarding_id (PK de OnboardingProcess).
        Retorna un dict con claves:
          - onboarding: instancia actualizada de OnboardingProcess
          - historial_cambio: dict con estado_anterior y estado_nuevo
          - notificacion_enviada: bool
          - estado_protegido: bool (True si el estado no retrocedió)
          - progreso_porcentaje: int (0-100)
        Retorna None si no se encuentra el onboarding.
        """
        # Intentar lookup por empleado_id primero, luego por onboarding_id (PK)
        onboarding = None
        try:
            onboarding = OnboardingProcess.objects.get(empleado_id=empleado_id)
        except OnboardingProcess.DoesNotExist:
            try:
                onboarding = OnboardingProcess.objects.get(onboarding_id=empleado_id)
            except OnboardingProcess.DoesNotExist:
                return None

        estado_anterior = onboarding.estado_onboarding

        if onboarding.estado_onboarding == "completado":
            return {
                "onboarding": onboarding,
                "historial_cambio": {"estado_anterior": estado_anterior, "estado_nuevo": estado_anterior},
                "notificacion_enviada": False,
                "estado_protegido": True,
                "progreso_porcentaje": onboarding.progreso_porcentaje,
            }

        # Obtener documentos del empleado
        documentos = DigitalDocument.objects.filter(
            empleado_id=onboarding.empleado_id,
            es_version_actual=True,
        )

        # Verificar DNI
        onboarding.dni_subido = documentos.filter(
            tipo_documento="dni",
            estado_documento__in=["activo", "pendiente_revision", "aprobado"],
        ).exists()

        # Verificar declaraciones juradas
        onboarding.declaraciones_juradas_subidas = documentos.filter(
            tipo_documento="declaracion_jurada",
            estado_documento__in=["activo", "pendiente_revision", "aprobado"],
        ).exists()

        # Verificar certificados academicos
        onboarding.certificados_academicos_subidos = documentos.filter(
            tipo_documento__in=[
                "certificado_estudios",
                "titulo_profesional",
                "diploma",
            ],
            estado_documento__in=["activo", "pendiente_revision", "aprobado"],
        ).exists()

        # Verificar certificados de trabajo
        onboarding.certificados_trabajo_subidos = documentos.filter(
            tipo_documento="certificado_trabajo",
            estado_documento__in=["activo", "pendiente_revision", "aprobado"],
        ).exists()

        # Verificar documentos familiares (al menos un DNI familiar)
        onboarding.documentos_familiares_subidos = documentos.filter(
            tipo_documento__in=["dni_familiar", "acta_matrimonio", "certificado_union_hecho"],
            categoria="familiar",
            estado_documento__in=["activo", "pendiente_revision", "aprobado"],
        ).exists()

        # Verificar datos personales (empleado tiene campos basicos completos)
        empleado = onboarding.empleado
        onboarding.datos_personales_completos = all(
            [
                empleado.nombres_empleado,
                empleado.apellido_paterno,
                empleado.numero_documento,
                empleado.fecha_nacimiento,
                empleado.telefono_celular,
                empleado.correo_personal,
                empleado.direccion_domicilio,
            ]
        )

        # Verificar datos laborales
        onboarding.datos_laborales_completos = empleado.datos_laborales.filter(
            estado_datos="activo"
        ).exists()

        # Proteger estado: no retroceder si ya está en pendiente_validacion o superior
        ESTADOS_AVANZADOS = {"pendiente_validacion", "en_revision", "observado"}
        estado_protegido = estado_anterior in ESTADOS_AVANZADOS

        # Actualizar estado
        onboarding.actualizar_estado()

        # Si el estado estaba protegido y retrocedió, restaurar
        if estado_protegido and onboarding.estado_onboarding == "pendiente_documentos":
            onboarding.estado_onboarding = estado_anterior
            onboarding.save(update_fields=["estado_onboarding"])

        estado_nuevo = onboarding.estado_onboarding
        notificacion_enviada = False

        return {
            "onboarding": onboarding,
            "historial_cambio": {"estado_anterior": estado_anterior, "estado_nuevo": estado_nuevo},
            "notificacion_enviada": notificacion_enviada,
            "estado_protegido": estado_protegido,
            "progreso_porcentaje": onboarding.progreso_porcentaje,
        }

    @staticmethod
    def obtener_documentos_pendientes(empleado_id):
        """
        Retorna lista de tipos de documento que faltan por subir.
        """
        try:
            onboarding = OnboardingProcess.objects.get(empleado_id=empleado_id)
        except OnboardingProcess.DoesNotExist:
            return []

        pendientes = []

        documentos = DigitalDocument.objects.filter(
            empleado_id=empleado_id,
            es_version_actual=True,
            estado_documento__in=["activo", "pendiente_revision", "aprobado"],
        )

        for flag, requeridos in DOCUMENTOS_REQUERIDOS.items():
            flag_value = getattr(onboarding, flag, False)
            if not flag_value:
                for req in requeridos:
                    exists = documentos.filter(
                        tipo_documento=req["tipo_documento"],
                    ).exists()
                    if not exists:
                        pendientes.append(
                            {
                                "tipo_documento": req["tipo_documento"],
                                "categoria": req["categoria"],
                                "label": req["label"],
                            }
                        )

        return pendientes

    @staticmethod
    def corregir_correo_personal(onboarding_id, nuevo_correo):
        """
        Actualiza el correo personal del empleado y el email del usuario asociado.

        Acepta onboarding_id (PK de OnboardingProcess).
        Retorna el onboarding actualizado, o None si no se encuentra.
        """
        try:
            onboarding = OnboardingProcess.objects.select_related(
                "empleado", "usuario"
            ).get(onboarding_id=onboarding_id)
        except OnboardingProcess.DoesNotExist:
            return None

        onboarding.empleado.correo_personal = nuevo_correo
        onboarding.empleado.save(update_fields=["correo_personal"])
        onboarding.usuario.email = nuevo_correo
        onboarding.usuario.save(update_fields=["email"])

        return onboarding

    @staticmethod
    def reenviar_email_bienvenida(onboarding_id, nuevo_password=True):
        """
        Reenvia el email de bienvenida, opcionalmente con nueva contrasena.
        """
        try:
            onboarding = OnboardingProcess.objects.select_related(
                "usuario", "empleado"
            ).get(onboarding_id=onboarding_id)
        except OnboardingProcess.DoesNotExist:
            return None

        password_temporal = None
        if nuevo_password:
            password_temporal = OnboardingService.generar_password_temporal()
            onboarding.usuario.set_password(password_temporal)
            onboarding.usuario.requiere_cambio_password = True
            onboarding.usuario.save()
        else:
            password_temporal = "(use su contrasena actual)"

        email_enviado = OnboardingService.enviar_email_bienvenida(
            onboarding.usuario, password_temporal
        )

        if email_enviado:
            onboarding.email_bienvenida_enviado = True
            onboarding.fecha_email_bienvenida = timezone.now()
            onboarding.save()

        return {
            "email_enviado": email_enviado,
            "nuevo_password": nuevo_password,
        }

    @staticmethod
    def _enviar_notificacion(subject, from_email, recipient, text_content, html_content):
        """Intenta enviar via Celery, cae a sincrono si falla."""
        try:
            send_email_html_task.apply_async(
                args=[subject, from_email, recipient, text_content, html_content]
            )
        except Exception:
            OnboardingService._enviar_email_sincrono(subject, from_email, recipient, text_content, html_content)

    @staticmethod
    def validar_onboarding(onboarding_id, validado_por, observaciones=""):
        """
        RRHH valida todos los documentos y marca el onboarding como completado.
        """
        try:
            onboarding = OnboardingProcess.objects.select_related(
                "empleado", "usuario"
            ).get(onboarding_id=onboarding_id)
        except OnboardingProcess.DoesNotExist:
            return None

        # Validar todos los documentos pendientes de revision
        documentos = DigitalDocument.objects.filter(
            empleado=onboarding.empleado,
            estado_documento="pendiente_revision",
            es_version_actual=True,
        )
        for doc in documentos:
            doc.validar_documento(validado_por, observaciones)

        # Activar el usuario si estaba pendiente
        if onboarding.usuario.estado_usuario == "pendiente":
            onboarding.usuario.estado_usuario = "activo"
            onboarding.usuario.save()

        # Marcar onboarding como completado
        onboarding.marcar_completado(validado_por)
        onboarding.observaciones = observaciones
        onboarding.save()

        logger.info(f"Onboarding completado para {onboarding.empleado.nombre_completo}")
        return onboarding


class OnboardingNotificationService:
    """Email notifications for onboarding document and status events."""

    @staticmethod
    def notificar_documento_rechazado(onboarding, documento, motivo):
        """Send email to employee when a document is rejected by RRHH."""
        empleado = onboarding.empleado
        recipient = empleado.correo_personal
        if not recipient:
            return
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        context = {
            "nombre_empleado": empleado.nombre_completo,
            "nombre_documento": documento.nombre_documento,
            "motivo": motivo,
            "frontend_url": frontend_url,
        }
        html_content = render_to_string("emails/documento_rechazado.html", context)
        text_content = render_to_string("emails/documento_rechazado.txt", context)
        subject = f"Documento rechazado: {documento.nombre_documento}"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@intranet.pe")
        OnboardingService._enviar_notificacion(subject, from_email, recipient, text_content, html_content)

    @staticmethod
    def notificar_onboarding_aprobado(onboarding):
        """Send congratulations email when full onboarding is approved."""
        empleado = onboarding.empleado
        recipient = empleado.correo_personal
        if not recipient:
            return
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        context = {
            "nombre_empleado": empleado.nombre_completo,
            "frontend_url": frontend_url,
        }
        html_content = render_to_string("emails/onboarding_aprobado.html", context)
        text_content = render_to_string("emails/onboarding_aprobado.txt", context)
        subject = "¡Tu onboarding ha sido aprobado!"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@intranet.pe")
        OnboardingService._enviar_notificacion(subject, from_email, recipient, text_content, html_content)

    @staticmethod
    def notificar_onboarding_observado(onboarding, observaciones):
        """Send email when onboarding is marked as observed/rejected by RRHH."""
        empleado = onboarding.empleado
        recipient = empleado.correo_personal
        if not recipient:
            return
        frontend_url = getattr(settings, "FRONTEND_URL", "http://localhost:5173")
        context = {
            "nombre_empleado": empleado.nombre_completo,
            "observaciones": observaciones,
            "frontend_url": frontend_url,
        }
        html_content = render_to_string("emails/onboarding_observado.html", context)
        text_content = render_to_string("emails/onboarding_observado.txt", context)
        subject = "Tu onboarding requiere correcciones"
        from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@intranet.pe")
        OnboardingService._enviar_notificacion(subject, from_email, recipient, text_content, html_content)
