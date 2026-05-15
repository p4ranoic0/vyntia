"""Tests for B.12 dossier_service."""
from datetime import date

import pytest
from django.core.files.base import ContentFile

from apps.documents.models import (
    DigitalDocument,
    DigitalDossier,
    DossierSection,
)
from apps.documents.services import dossier_service
from apps.employees.models import Employee


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='50505050', tipo_documento='DNI',
        nombres_empleado='Sofía', apellido_paterno='Mendez',
        apellido_materno='Ruiz', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


def _make_doc(employee, tipo_documento, nombre):
    content = ContentFile(b'%PDF-1.4 test', name=f'{tipo_documento}.pdf')
    doc = DigitalDocument(
        empleado=employee, tipo_documento=tipo_documento,
        categoria='personal', nombre_documento=nombre,
        estado_documento='vigente', es_version_actual=True, version='1.0',
        nombre_archivo_original=f'{tipo_documento}.pdf', formato_archivo='pdf',
        tamano_archivo=12, nivel_acceso='restringido',
    )
    doc.archivo.save(f'{tipo_documento}.pdf', content, save=False)
    doc.save()
    return doc


@pytest.mark.django_db
class TestBuildDossier:
    def test_creates_15_sections(self, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        assert dossier.sections.count() == 15

    def test_idempotent(self, employee):
        dossier_service.build_dossier_for_employee(employee=employee)
        dossier_service.build_dossier_for_employee(employee=employee)
        assert DigitalDossier.objects.filter(employee=employee).count() == 1
        assert DossierSection.objects.filter(dossier__employee=employee).count() == 15

    def test_medical_section_has_pl9(self, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        med = dossier.sections.get(kind='medicos')
        assert med.permission_level == 9


@pytest.mark.django_db
class TestAttachDocumentToSection:
    def test_dni_routes_to_identidad_cuspp(self, employee):
        doc = _make_doc(employee, 'dni', 'DNI')
        section = dossier_service.attach_document_to_section(document=doc)
        assert section.kind == 'identidad_cuspp'

    def test_examen_medico_routes_to_medicos(self, employee):
        doc = _make_doc(employee, 'examen_medico', 'Examen')
        section = dossier_service.attach_document_to_section(document=doc)
        assert section.kind == 'medicos'

    def test_unknown_type_falls_back(self, employee):
        doc = _make_doc(employee, 'otro_documento_extraño', 'X')
        section = dossier_service.attach_document_to_section(document=doc)
        assert section.kind == 'datos_personales'

    def test_creates_dossier_if_missing(self, employee):
        assert not DigitalDossier.objects.filter(employee=employee).exists()
        doc = _make_doc(employee, 'dni', 'DNI')
        dossier_service.attach_document_to_section(document=doc)
        assert DigitalDossier.objects.filter(employee=employee).exists()


@pytest.mark.django_db
class TestRenderConsolidatedIndexHtml:
    def test_includes_employee_name(self, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        html = dossier_service.render_consolidated_index_html(dossier.id)
        assert employee.nombres_empleado in html
        assert employee.apellido_paterno in html

    def test_lists_all_15_sections(self, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        html = dossier_service.render_consolidated_index_html(dossier.id)
        # Each section label should appear once
        for kind, label, _ in __import__(
            'apps.documents.models.digital_dossier', fromlist=['SECTION_DEFAULTS']
        ).SECTION_DEFAULTS:
            assert label in html

    def test_includes_document_names_when_present(self, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        _make_doc(employee, 'dni', 'Mi DNI 123')
        html = dossier_service.render_consolidated_index_html(dossier.id)
        assert 'Mi DNI 123' in html

    def test_references_ley_29733(self, employee):
        dossier = dossier_service.build_dossier_for_employee(employee=employee)
        html = dossier_service.render_consolidated_index_html(dossier.id)
        assert '29733' in html
