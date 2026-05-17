"""Tests for B.15a policy_acknowledgment_service."""
from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.employees.models import Employee
from apps.identity.models import User
from apps.policies.models import (
    Policy,
    PolicyAcknowledgment,
    PolicyPublication,
    PolicyVersion,
)
from apps.policies.services import policy_acknowledgment_service


@pytest.fixture
def owner(db):
    return User.objects.create(
        username='owner_ack', email='owner_ack@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
    )


@pytest.fixture
def employees(db):
    return [
        Employee.objects.create(
            numero_documento=f'4040404{i}', tipo_documento='DNI',
            nombres_empleado=f'Emp{i}', apellido_paterno='Test',
            apellido_materno='Demo', fecha_nacimiento=date(1990, 1, 1),
            estado_empleado='activo',
        )
        for i in range(3)
    ]


@pytest.fixture
def publication(owner, employees):
    p = Policy.objects.create(
        kind='codigo_etica', title='Ética Ack', owner_user=owner, status='approved',
    )
    v = PolicyVersion.objects.create(policy=p, version_number=1, status='approved')
    pub = PolicyPublication.objects.create(
        policy_version=v, published_at=timezone.now(),
        published_by=owner, target_audience='all',
        acknowledgment_deadline=date.today() + timedelta(days=5),
    )
    return pub


@pytest.mark.django_db
class TestSeed:
    def test_seed_creates_one_ack_per_employee(self, publication, employees):
        created = policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        assert created == len(employees)
        assert PolicyAcknowledgment.objects.filter(publication=publication).count() == len(employees)

    def test_seed_is_idempotent(self, publication, employees):
        policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        again = policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        assert again == 0

    def test_seed_skipped_when_no_acknowledgment_required(self, owner, employees):
        p = Policy.objects.create(kind='rit', title='Sin Ack', owner_user=owner, status='approved')
        v = PolicyVersion.objects.create(policy=p, version_number=1, status='approved')
        pub = PolicyPublication.objects.create(
            policy_version=v, published_at=timezone.now(),
            published_by=owner, target_audience='all',
            requires_acknowledgment=False,
        )
        created = policy_acknowledgment_service.seed_acknowledgments_for_publication(pub)
        assert created == 0


@pytest.mark.django_db
class TestCaptureAndDecline:
    def test_capture_marks_acknowledged(self, publication, employees):
        policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        ack = PolicyAcknowledgment.objects.first()
        policy_acknowledgment_service.capture(
            acknowledgment=ack, signature_kind='checkbox', signature_payload='true',
            ip='192.168.0.10', user_agent='UA',
        )
        ack.refresh_from_db()
        assert ack.status == 'acknowledged'
        assert ack.ip == '192.168.0.10'

    def test_capture_canvas_requires_payload(self, publication, employees):
        policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        ack = PolicyAcknowledgment.objects.first()
        with pytest.raises(ValidationError):
            policy_acknowledgment_service.capture(
                acknowledgment=ack, signature_kind='canvas', signature_payload='',
            )

    def test_decline_marks_declined(self, publication, employees):
        policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        ack = PolicyAcknowledgment.objects.first()
        policy_acknowledgment_service.decline(
            acknowledgment=ack, reason='No de acuerdo con cláusula 5',
            ip='10.0.0.1',
        )
        ack.refresh_from_db()
        assert ack.status == 'declined'
        assert 'cláusula' in ack.declined_reason


@pytest.mark.django_db
class TestExpireOverdue:
    def test_expire_overdue_flips_only_past_deadline(self, owner, employees):
        # Publication 1: deadline in the past
        p1 = Policy.objects.create(kind='rit', title='Expired', owner_user=owner, status='approved')
        v1 = PolicyVersion.objects.create(policy=p1, version_number=1, status='approved')
        pub1 = PolicyPublication.objects.create(
            policy_version=v1, published_at=timezone.now(),
            published_by=owner, target_audience='all',
            acknowledgment_deadline=date.today() - timedelta(days=1),
        )
        # Publication 2: deadline still alive
        p2 = Policy.objects.create(kind='codigo_etica', title='Alive', owner_user=owner, status='approved')
        v2 = PolicyVersion.objects.create(policy=p2, version_number=1, status='approved')
        pub2 = PolicyPublication.objects.create(
            policy_version=v2, published_at=timezone.now(),
            published_by=owner, target_audience='all',
            acknowledgment_deadline=date.today() + timedelta(days=5),
        )
        ack_expired = PolicyAcknowledgment.objects.create(publication=pub1, employee=employees[0])
        ack_alive = PolicyAcknowledgment.objects.create(publication=pub2, employee=employees[1])

        count = policy_acknowledgment_service.expire_overdue()
        assert count == 1
        ack_expired.refresh_from_db()
        ack_alive.refresh_from_db()
        assert ack_expired.status == 'expired'
        assert ack_alive.status == 'pending'


@pytest.mark.django_db
class TestListForEmployee:
    def test_list_pending_for_employee_returns_only_pending(self, publication, employees):
        policy_acknowledgment_service.seed_acknowledgments_for_publication(publication)
        emp = employees[0]
        # Mark one acknowledged
        ack = PolicyAcknowledgment.objects.get(publication=publication, employee=emp)
        ack.mark_acknowledged(signature_kind='checkbox', signature_payload='true')
        pending = list(policy_acknowledgment_service.list_pending_for_employee(emp))
        assert all(a.status == 'pending' for a in pending)
        assert all(a.employee_id == emp.pk for a in pending)
        assert ack not in pending
