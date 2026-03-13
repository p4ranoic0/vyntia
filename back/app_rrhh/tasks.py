# -*- coding: utf-8 -*-
"""
Tareas asincronas de Celery para app_rrhh.

Incluye envio de emails y otras tareas que pueden ejecutarse en background.
"""

import logging

from celery import shared_task
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def send_email_html_task(self, subject, from_email, recipients, text_content, html_content):
    """
    Envia un email con contenido HTML de forma asincrona.

    Args:
        subject: Asunto del email
        from_email: Email del remitente
        recipients: Lista de destinatarios
        text_content: Contenido en texto plano (fallback)
        html_content: Contenido HTML del email
    """
    try:
        msg = EmailMultiAlternatives(subject, text_content, from_email, recipients)
        msg.attach_alternative(html_content, "text/html")
        msg.send()
        logger.info("Email enviado exitosamente a %s", recipients)
    except Exception as exc:
        logger.error("Error enviando email a %s: %s", recipients, exc)
        raise self.retry(exc=exc, countdown=60)
