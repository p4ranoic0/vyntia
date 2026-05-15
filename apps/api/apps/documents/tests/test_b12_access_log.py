"""Tests for B.12 DocumentAccessLog + access_service."""
from datetime import date

import pytest
from django.core.files.base import ContentFile

from apps.documents.models import DigitalDocument, DocumentAccessLog
from apps.documents.services import access_service
from apps.employees.models import Employee
from apps.identity.models import User


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='40404040', tipo_documento='DNI',
        nombres_empleado='Olga', apellido_paterno='Soto',
        apellido_materno='Lara', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.fixture
def document(employee):
    content = ContentFile(b'%PDF-1.4 test', name='med.pdf')
    doc = DigitalDocument(
        empleado=employee, tipo_documento='examen_medico',
        categoria='medico', nombre_documento='Examen 2026',
        estado_documento='vigente', es_version_actual=True, version='1.0',
        nombre_archivo_original='med.pdf', formato_archivo='pdf',
        tamano_archivo=12, nivel_acceso='confidencial',
        permission_level=9,
    )
    doc.archivo.save('med.pdf', content, save=False)
    doc.save()
    return doc


@pytest.fixture
def standard_doc(employee):
    content = ContentFile(b'%PDF-1.4 test', name='dni.pdf')
    doc = DigitalDocument(
        empleado=employee, tipo_documento='dni',
        categoria='personal', nombre_documento='DNI',
        estado_documento='vigente', es_version_actual=True, version='1.0',
        nombre_archivo_original='dni.pdf', formato_archivo='pdf',
        tamano_archivo=12, nivel_acceso='restringido',
        permission_level=3,
    )
    doc.archivo.save('dni.pdf', content, save=False)
    doc.save()
    return doc


@pytest.fixture
def hr_user(db):
    return User.objects.create(
        username='hr_b12', email='hr_b12@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
        nivel_acceso='alto',
    )


@pytest.fixture
def admin_user(db):
    return User.objects.create(
        username='admin_b12', email='admin_b12@test.local',
        tipo_usuario='administrador', estado_usuario='activo',
        nivel_acceso='total',
    )


@pytest.fixture
def basic_user(db):
    return User.objects.create(
        username='basic_b12', email='basic_b12@test.local',
        tipo_usuario='colaborador', estado_usuario='activo',
        nivel_acceso='bajo',
    )


@pytest.mark.django_db
class TestUserPermissionLevel:
    def test_bajo_to_1(self, basic_user):
        assert access_service.user_permission_level(basic_user) == 1

    def test_alto_to_5(self, hr_user):
        assert access_service.user_permission_level(hr_user) == 5

    def test_total_to_9(self, admin_user):
        assert access_service.user_permission_level(admin_user) == 9

    def test_none_user_is_zero(self):
        assert access_service.user_permission_level(None) == 0


@pytest.mark.django_db
class TestCanAccess:
    def test_admin_can_access_pl9(self, admin_user, document):
        assert access_service.can_access(admin_user, document) is True

    def test_hr_cannot_access_pl9(self, hr_user, document):
        assert access_service.can_access(hr_user, document) is False

    def test_basic_cannot_access_pl3(self, basic_user, standard_doc):
        assert access_service.can_access(basic_user, standard_doc) is False

    def test_hr_can_access_pl3(self, hr_user, standard_doc):
        assert access_service.can_access(hr_user, standard_doc) is True


@pytest.mark.django_db
class TestLogAccess:
    def test_persists_entry(self, hr_user, standard_doc):
        log = access_service.log_access(
            document=standard_doc, user=hr_user, action='view',
            ip='10.0.0.1', user_agent='Mozilla',
        )
        assert log.id is not None
        assert log.document == standard_doc
        assert log.action == 'view'
        assert log.user == hr_user

    def test_none_user_persists_null(self, standard_doc):
        log = access_service.log_access(
            document=standard_doc, user=None, action='preview',
        )
        assert log.user is None


@pytest.mark.django_db
class TestCheckAndLog:
    def test_denied_when_insufficient(self, hr_user, document):
        allowed = access_service.check_and_log(
            document=document, user=hr_user, action='download',
        )
        assert allowed is False
        log = DocumentAccessLog.objects.filter(document=document).last()
        assert log.action == 'denied'

    def test_allowed_logs_action(self, admin_user, document):
        allowed = access_service.check_and_log(
            document=document, user=admin_user, action='download',
        )
        assert allowed is True
        log = DocumentAccessLog.objects.filter(document=document).last()
        assert log.action == 'download'


@pytest.mark.django_db
class TestDocumentExtensions:
    def test_permission_level_default_3(self, employee):
        content = ContentFile(b'test', name='x.pdf')
        doc = DigitalDocument(
            empleado=employee, tipo_documento='dni',
            categoria='personal', nombre_documento='X',
            estado_documento='vigente', es_version_actual=True, version='1.0',
            nombre_archivo_original='x.pdf', formato_archivo='pdf',
            tamano_archivo=4, nivel_acceso='restringido',
        )
        doc.archivo.save('x.pdf', content, save=False)
        doc.save()
        assert doc.permission_level == 3

    def test_contract_fk_nullable(self, employee):
        content = ContentFile(b'test', name='x.pdf')
        doc = DigitalDocument(
            empleado=employee, tipo_documento='dni',
            categoria='personal', nombre_documento='X',
            estado_documento='vigente', es_version_actual=True, version='1.0',
            nombre_archivo_original='x.pdf', formato_archivo='pdf',
            tamano_archivo=4, nivel_acceso='restringido',
        )
        doc.archivo.save('x.pdf', content, save=False)
        doc.save()
        assert doc.contract is None
