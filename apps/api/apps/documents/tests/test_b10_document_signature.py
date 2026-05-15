"""Tests for B.10 DocumentSignature model + signature_service."""
from datetime import date, timedelta
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.utils import timezone

from apps.documents.models import DigitalDocument, DocumentSignature
from apps.documents.services import signature_service
from apps.employees.models import Employee
from apps.identity.models import User


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='44556677', tipo_documento='DNI',
        nombres_empleado='Luis', apellido_paterno='Sánchez',
        apellido_materno='Mejía', fecha_nacimiento=date(1992, 4, 4),
        estado_empleado='activo',
    )


@pytest.fixture
def signer(db):
    return User.objects.create(
        username='signer_b10', email='signer_b10@test.local',
        tipo_usuario='colaborador', estado_usuario='activo',
    )


@pytest.fixture
def document(employee):
    content = ContentFile(b'%PDF-1.4 fake content', name='ctr.pdf')
    doc = DigitalDocument(
        empleado=employee, tipo_documento='contrato_inicial',
        categoria='contractual', nombre_documento='Contrato 728',
        estado_documento='vigente', es_version_actual=True, version='1.0',
        nombre_archivo_original='ctr.pdf', formato_archivo='pdf',
        tamano_archivo=22, nivel_acceso='restringido',
    )
    doc.archivo.save('ctr.pdf', content, save=False)
    doc.save()
    return doc


@pytest.mark.django_db
class TestRequestSignature:
    def test_creates_in_requested_state(self, document, signer):
        sig = signature_service.request_signature(
            document=document, signer_user=signer,
            signer_name='Luis Sánchez Mejía', signer_doc_number='44556677',
            signer_email='luis@example.com', kind='canvas',
        )
        assert sig.status == 'requested'
        assert sig.expires_at is not None
        assert sig.expires_at > timezone.now() + timedelta(days=29)
        assert sig.document_id == document.id

    def test_no_expiry_when_zero_days(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='checkbox', expires_in_days=0,
        )
        assert sig.expires_at is None


@pytest.mark.django_db
class TestCaptureSignature:
    def test_canvas_capture_persists_payload(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='canvas',
        )
        out = signature_service.capture_signature(
            signature_id=sig.id, canvas_base64='base64payload',
            signer_ip='10.0.0.1', signer_user_agent='Mozilla',
        )
        assert out.status == 'signed'
        assert out.canvas_base64 == 'base64payload'
        assert out.signer_ip == '10.0.0.1'
        assert out.signed_at is not None

    def test_canvas_requires_base64(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='canvas',
        )
        with pytest.raises(ValidationError):
            signature_service.capture_signature(signature_id=sig.id)

    def test_typed_requires_typed_name(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='typed',
        )
        with pytest.raises(ValidationError):
            signature_service.capture_signature(signature_id=sig.id)

    def test_checkbox_requires_text(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='checkbox',
        )
        with pytest.raises(ValidationError):
            signature_service.capture_signature(signature_id=sig.id)

    def test_cannot_capture_already_signed(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='typed',
        )
        signature_service.capture_signature(
            signature_id=sig.id, typed_name='Pedro',
        )
        with pytest.raises(ValidationError):
            signature_service.capture_signature(
                signature_id=sig.id, typed_name='Pedro 2',
            )


@pytest.mark.django_db
class TestRejectSignature:
    def test_persists_reason(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='canvas',
        )
        out = signature_service.reject_signature(
            signature_id=sig.id, reason='No conforme',
        )
        assert out.status == 'rejected'
        assert out.rejection_reason == 'No conforme'

    def test_requires_reason(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='canvas',
        )
        with pytest.raises(ValidationError):
            signature_service.reject_signature(signature_id=sig.id, reason='')

    def test_cannot_reject_signed(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='typed',
        )
        signature_service.capture_signature(
            signature_id=sig.id, typed_name='Mario',
        )
        with pytest.raises(ValidationError):
            signature_service.reject_signature(signature_id=sig.id, reason='x')


@pytest.mark.django_db
class TestExpireOverdueSignatures:
    def test_flips_overdue_requested(self, document):
        past = timezone.now() - timedelta(days=1)
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='canvas',
        )
        # Backdate expires_at
        DocumentSignature.objects.filter(pk=sig.id).update(expires_at=past)
        count = signature_service.expire_overdue_signatures()
        assert count == 1
        sig.refresh_from_db()
        assert sig.status == 'expired'

    def test_does_not_flip_signed(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='typed',
        )
        signature_service.capture_signature(
            signature_id=sig.id, typed_name='X',
        )
        past = timezone.now() - timedelta(days=1)
        DocumentSignature.objects.filter(pk=sig.id).update(expires_at=past)
        count = signature_service.expire_overdue_signatures()
        assert count == 0


@pytest.mark.django_db
class TestVerifySignature:
    def test_signed_canvas_returns_true(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='canvas',
        )
        signature_service.capture_signature(
            signature_id=sig.id, canvas_base64='b64',
        )
        sig.refresh_from_db()
        assert signature_service.verify_signature(sig) is True

    def test_requested_returns_false(self, document):
        sig = signature_service.request_signature(
            document=document, signer_name='X', signer_doc_number='12345678',
            kind='canvas',
        )
        assert signature_service.verify_signature(sig) is False
