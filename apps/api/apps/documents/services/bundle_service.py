"""bundle_service — HiringDocumentBundle assembly + workflow (B.10).

Builds a hiring document bundle for an employee with one HiringBundleItem per
declared kind. Items start without a document; HR attaches the DigitalDocument
file later (generated via existing template_service / pdf_generator). When the
employee signs, attach the DocumentSignature to the item; when ALL required
items are signed, the bundle is automatically marked 'acknowledged'.

See Module 03.2 § 3.2 and ROADMAP-B.md backlog #113.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from apps.documents.models import (
    HiringBundleItem,
    HiringDocumentBundle,
)

DEFAULT_BUNDLE_ITEMS = [
    'contrato',
    'rit',
    'reglamento_sst',
    'codigo_etica',
    'politica_datos',
    'manual_funciones',
]


@transaction.atomic
def build_bundle(
    *,
    employee,
    contract=None,
    tenant=None,
    item_kinds: list[str] | None = None,
    created_by=None,
    title: str = '',
) -> HiringDocumentBundle:
    """Create a bundle (draft) with one HiringBundleItem per item_kind."""
    if tenant is None:
        tenant = getattr(employee, 'tenant', None)
    kinds = item_kinds or DEFAULT_BUNDLE_ITEMS
    bundle = HiringDocumentBundle.objects.create(
        tenant=tenant,
        employee=employee,
        contract=contract,
        created_by=created_by,
        title=title or 'Documentos de vinculación',
    )
    for order, kind in enumerate(kinds):
        HiringBundleItem.objects.create(
            bundle=bundle, kind=kind, order=order,
        )
    return bundle


def attach_document(*, bundle_item_id, document) -> HiringBundleItem:
    """Link a DigitalDocument to a bundle item."""
    item = HiringBundleItem.objects.get(pk=bundle_item_id)
    item.document = document
    item.save(update_fields=['document'])
    return item


def attach_acuse(*, bundle_item_id, signature) -> HiringBundleItem:
    """Link a DocumentSignature (acuse) to a bundle item, then propagate."""
    item = HiringBundleItem.objects.get(pk=bundle_item_id)
    item.signature = signature
    item.save(update_fields=['signature'])
    # Best-effort propagation; not raising if bundle is in draft.
    mark_acknowledged_if_complete(bundle_id=item.bundle_id)
    return item


def mark_sent(*, bundle_id) -> HiringDocumentBundle:
    """draft → sent. Requires at least one item to have a document attached."""
    bundle = HiringDocumentBundle.objects.get(pk=bundle_id)
    if bundle.status != 'draft':
        raise ValidationError(
            f'Cannot send bundle in status={bundle.status}'
        )
    if not bundle.items.filter(document__isnull=False).exists():
        raise ValidationError(
            'Cannot send bundle with no documents attached to any item'
        )
    bundle.status = 'sent'
    bundle.sent_at = timezone.now()
    bundle.save(update_fields=['status', 'sent_at', 'updated_at'])
    return bundle


def mark_acknowledged_if_complete(*, bundle_id) -> HiringDocumentBundle:
    """Flip sent → acknowledged when all required items have signed signatures."""
    bundle = HiringDocumentBundle.objects.get(pk=bundle_id)
    if bundle.status != 'sent':
        return bundle
    required_items = bundle.items.filter(required=True)
    if not required_items.exists():
        return bundle
    for item in required_items:
        sig = item.signature
        if sig is None or sig.status != 'signed':
            return bundle
    bundle.status = 'acknowledged'
    bundle.acknowledged_at = timezone.now()
    bundle.save(update_fields=[
        'status', 'acknowledged_at', 'updated_at',
    ])
    return bundle
