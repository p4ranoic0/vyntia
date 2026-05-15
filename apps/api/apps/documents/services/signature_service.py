"""signature_service — DocumentSignature lifecycle helpers (B.10).

Thin functional API over DocumentSignature. Keeps validation + state transitions
out of the model so the model stays a data record and so the service is the
authoritative seam for future enhancements (real PKI, audit-log integration).

See Module 03.2 § 3.2 and ROADMAP-B.md backlog #112.
"""

from __future__ import annotations

from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.documents.models import DocumentSignature


def request_signature(
    *,
    document,
    signer_name: str,
    signer_doc_number: str,
    signer_user=None,
    signer_email: str = '',
    kind: str = 'canvas',
    checkbox_text: str = '',
    expires_in_days: int = 30,
    tenant=None,
) -> DocumentSignature:
    """Create a new DocumentSignature in 'requested' state.

    If `tenant` is not provided, falls back to the document's tenant.
    """
    if tenant is None:
        tenant = getattr(document, 'tenant', None)
    expires_at = None
    if expires_in_days:
        expires_at = timezone.now() + timedelta(days=expires_in_days)
    return DocumentSignature.objects.create(
        tenant=tenant,
        document=document,
        signer_user=signer_user,
        signer_name=signer_name,
        signer_doc_number=signer_doc_number,
        signer_email=signer_email,
        kind=kind,
        checkbox_text=checkbox_text,
        expires_at=expires_at,
    )


def capture_signature(
    *,
    signature_id,
    signer_ip: str = '',
    signer_user_agent: str = '',
    canvas_base64: str = '',
    typed_name: str = '',
    checkbox_text: str = '',
) -> DocumentSignature:
    """Capture the signature payload and flip status to 'signed'.

    Validates the payload matches the declared `kind`.
    """
    signature = DocumentSignature.objects.get(pk=signature_id)
    if signature.status != 'requested':
        raise ValidationError(
            f'Cannot capture signature in status={signature.status}'
        )

    if signature.kind == 'canvas':
        if not canvas_base64:
            raise ValidationError('canvas_base64 required for kind=canvas')
        signature.canvas_base64 = canvas_base64
    elif signature.kind == 'typed':
        if not typed_name:
            raise ValidationError('typed_name required for kind=typed')
        signature.typed_name = typed_name
    elif signature.kind == 'checkbox':
        if not checkbox_text:
            raise ValidationError(
                'checkbox_text required for kind=checkbox'
            )
        signature.checkbox_text = checkbox_text

    signature.signer_ip = signer_ip or None
    signature.signer_user_agent = signer_user_agent
    signature.status = 'signed'
    signature.signed_at = timezone.now()
    signature.save()
    return signature


def reject_signature(*, signature_id, reason: str) -> DocumentSignature:
    """Flip a requested signature to 'rejected' with a reason."""
    if not reason:
        raise ValidationError('rejection reason is required')
    signature = DocumentSignature.objects.get(pk=signature_id)
    if signature.status != 'requested':
        raise ValidationError(
            f'Cannot reject signature in status={signature.status}'
        )
    signature.status = 'rejected'
    signature.rejection_reason = reason
    signature.save(update_fields=['status', 'rejection_reason', 'updated_at'])
    return signature


def expire_overdue_signatures(now=None) -> int:
    """Flip requested signatures whose expires_at < now → 'expired'.

    Returns the number of signatures expired.
    """
    if now is None:
        now = timezone.now()
    qs = DocumentSignature.objects.filter(
        status='requested',
        expires_at__isnull=False,
        expires_at__lt=now,
    )
    return qs.update(status='expired', updated_at=now)


def verify_signature(signature: DocumentSignature) -> bool:
    """Return True if the signature is in a verified-signed state.

    Currently a shape-of-payload check: signed + has the required payload
    matching its kind. Future PKI verification slots in here.
    """
    if signature.status != 'signed':
        return False
    if signature.kind == 'canvas':
        return bool(signature.canvas_base64)
    if signature.kind == 'typed':
        return bool(signature.typed_name)
    if signature.kind == 'checkbox':
        return bool(signature.checkbox_text)
    return False
