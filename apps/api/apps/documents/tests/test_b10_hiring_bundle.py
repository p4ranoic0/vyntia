"""Tests for B.10 HiringDocumentBundle + bundle_service."""
from datetime import date

import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import IntegrityError

from apps.documents.models import (
    DigitalDocument,
    HiringBundleItem,
    HiringDocumentBundle,
)
from apps.documents.services import bundle_service, signature_service
from apps.employees.models import Employee
from apps.identity.models import User


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='22334455', tipo_documento='DNI',
        nombres_empleado='Carla', apellido_paterno='Ramos',
        apellido_materno='Cruz', fecha_nacimiento=date(1995, 7, 7),
        estado_empleado='activo',
    )


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_bundle', email='hr_bundle@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def document(employee):
    content = ContentFile(b'%PDF-1.4 test', name='rit.pdf')
    doc = DigitalDocument(
        empleado=employee, tipo_documento='reglamento_interno',
        categoria='normativa', nombre_documento='RIT 2026',
        estado_documento='vigente', es_version_actual=True, version='1.0',
        nombre_archivo_original='rit.pdf', formato_archivo='pdf',
        tamano_archivo=12, nivel_acceso='restringido',
    )
    doc.archivo.save('rit.pdf', content, save=False)
    doc.save()
    return doc


@pytest.mark.django_db
class TestBuildBundle:
    def test_creates_draft_with_default_six_kinds(self, employee, hr_user):
        bundle = bundle_service.build_bundle(
            employee=employee, created_by=hr_user,
        )
        assert bundle.status == 'draft'
        assert bundle.items.count() == 6
        kinds = set(bundle.items.values_list('kind', flat=True))
        assert kinds == set(bundle_service.DEFAULT_BUNDLE_ITEMS)

    def test_custom_kinds(self, employee):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato', 'codigo_etica'],
        )
        assert bundle.items.count() == 2

    def test_duplicate_kind_in_one_bundle_raises(self, employee):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato'],
        )
        with pytest.raises(IntegrityError):
            HiringBundleItem.objects.create(bundle=bundle, kind='contrato')


@pytest.mark.django_db
class TestAttachDocument:
    def test_persists_document(self, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['rit'],
        )
        item = bundle.items.first()
        out = bundle_service.attach_document(
            bundle_item_id=item.id, document=document,
        )
        assert out.document == document


@pytest.mark.django_db
class TestAttachAcuse:
    def test_links_signature_and_propagates(self, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['rit'],
        )
        item = bundle.items.first()
        bundle_service.attach_document(
            bundle_item_id=item.id, document=document,
        )
        bundle_service.mark_sent(bundle_id=bundle.id)
        # Create + capture a signature
        sig = signature_service.request_signature(
            document=document, signer_name='Carla',
            signer_doc_number='22334455', kind='typed',
        )
        signature_service.capture_signature(
            signature_id=sig.id, typed_name='Carla',
        )
        sig.refresh_from_db()
        bundle_service.attach_acuse(bundle_item_id=item.id, signature=sig)
        bundle.refresh_from_db()
        assert bundle.status == 'acknowledged'
        assert bundle.acknowledged_at is not None


@pytest.mark.django_db
class TestMarkSent:
    def test_requires_at_least_one_document(self, employee):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato'],
        )
        with pytest.raises(ValidationError):
            bundle_service.mark_sent(bundle_id=bundle.id)

    def test_succeeds_when_doc_attached(self, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato'],
        )
        item = bundle.items.first()
        bundle_service.attach_document(
            bundle_item_id=item.id, document=document,
        )
        out = bundle_service.mark_sent(bundle_id=bundle.id)
        assert out.status == 'sent'
        assert out.sent_at is not None

    def test_cannot_send_from_sent(self, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato'],
        )
        item = bundle.items.first()
        bundle_service.attach_document(
            bundle_item_id=item.id, document=document,
        )
        bundle_service.mark_sent(bundle_id=bundle.id)
        with pytest.raises(ValidationError):
            bundle_service.mark_sent(bundle_id=bundle.id)


@pytest.mark.django_db
class TestMarkAcknowledgedIfComplete:
    def test_no_op_when_required_unsigned(self, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato', 'rit'],
        )
        for item in bundle.items.all():
            bundle_service.attach_document(
                bundle_item_id=item.id, document=document,
            )
        bundle_service.mark_sent(bundle_id=bundle.id)
        # Sign only one
        item1 = bundle.items.first()
        sig = signature_service.request_signature(
            document=document, signer_name='Carla',
            signer_doc_number='X', kind='typed',
        )
        signature_service.capture_signature(
            signature_id=sig.id, typed_name='Carla',
        )
        sig.refresh_from_db()
        bundle_service.attach_acuse(
            bundle_item_id=item1.id, signature=sig,
        )
        bundle.refresh_from_db()
        assert bundle.status == 'sent'

    def test_flips_when_all_required_signed(self, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato', 'rit'],
        )
        for item in bundle.items.all():
            bundle_service.attach_document(
                bundle_item_id=item.id, document=document,
            )
        bundle_service.mark_sent(bundle_id=bundle.id)
        for item in bundle.items.all():
            sig = signature_service.request_signature(
                document=document, signer_name='Carla',
                signer_doc_number='X', kind='typed',
            )
            signature_service.capture_signature(
                signature_id=sig.id, typed_name='Carla',
            )
            sig.refresh_from_db()
            bundle_service.attach_acuse(
                bundle_item_id=item.id, signature=sig,
            )
        bundle.refresh_from_db()
        assert bundle.status == 'acknowledged'

    def test_skipped_for_optional_items(self, employee, document):
        bundle = bundle_service.build_bundle(
            employee=employee, item_kinds=['contrato', 'rit'],
        )
        rit_item = bundle.items.get(kind='rit')
        rit_item.required = False
        rit_item.save(update_fields=['required'])
        for item in bundle.items.all():
            bundle_service.attach_document(
                bundle_item_id=item.id, document=document,
            )
        bundle_service.mark_sent(bundle_id=bundle.id)
        # Only sign the required one
        item1 = bundle.items.get(kind='contrato')
        sig = signature_service.request_signature(
            document=document, signer_name='Carla',
            signer_doc_number='X', kind='typed',
        )
        signature_service.capture_signature(
            signature_id=sig.id, typed_name='Carla',
        )
        sig.refresh_from_db()
        bundle_service.attach_acuse(
            bundle_item_id=item1.id, signature=sig,
        )
        bundle.refresh_from_db()
        assert bundle.status == 'acknowledged'
