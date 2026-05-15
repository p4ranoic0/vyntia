"""Tests for B.12 DigitalDossier + DossierSection."""
from datetime import date

import pytest
from django.db import IntegrityError

from apps.documents.models import DigitalDossier, DossierSection
from apps.documents.models.digital_dossier import SECTION_DEFAULTS
from apps.employees.models import Employee


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='30303030', tipo_documento='DNI',
        nombres_empleado='Pedro', apellido_paterno='Quispe',
        apellido_materno='Cruz', fecha_nacimiento=date(1990, 1, 1),
        estado_empleado='activo',
    )


@pytest.mark.django_db
class TestDigitalDossier:
    def test_create_one_per_employee(self, employee):
        d = DigitalDossier.objects.create(employee=employee)
        assert d.id is not None
        assert d.is_closed is False
        # Try creating a duplicate
        with pytest.raises(IntegrityError):
            DigitalDossier.objects.create(employee=employee)

    def test_string_repr(self, employee):
        d = DigitalDossier.objects.create(employee=employee)
        assert str(employee.id) in str(d)

    def test_indexes_declared(self):
        index_fields = {tuple(i.fields) for i in DigitalDossier._meta.indexes}
        assert ('tenant', 'is_closed') in index_fields


@pytest.mark.django_db
class TestDossierSection:
    def test_section_defaults_count(self):
        assert len(SECTION_DEFAULTS) == 15

    def test_section_defaults_keys_unique(self):
        keys = [k for k, _, _ in SECTION_DEFAULTS]
        assert len(set(keys)) == 15

    def test_medical_and_accidents_have_pl9(self):
        d = dict((k, pl) for k, _, pl in SECTION_DEFAULTS)
        assert d['medicos'] == 9
        assert d['accidentes'] == 9

    def test_standard_sections_have_pl3(self):
        d = dict((k, pl) for k, _, pl in SECTION_DEFAULTS)
        assert d['datos_personales'] == 3
        assert d['datos_academicos'] == 3
        assert d['contratos'] == 3

    def test_create_section(self, employee):
        dossier = DigitalDossier.objects.create(employee=employee)
        s = DossierSection.objects.create(
            dossier=dossier, kind='datos_personales',
            label='Datos personales', permission_level=3, order=0,
        )
        assert s.kind == 'datos_personales'

    def test_unique_kind_per_dossier(self, employee):
        dossier = DigitalDossier.objects.create(employee=employee)
        DossierSection.objects.create(
            dossier=dossier, kind='medicos', label='Médicos',
            permission_level=9,
        )
        with pytest.raises(IntegrityError):
            DossierSection.objects.create(
                dossier=dossier, kind='medicos', label='Médicos dup',
                permission_level=9,
            )

    def test_string_repr(self, employee):
        dossier = DigitalDossier.objects.create(employee=employee)
        s = DossierSection.objects.create(
            dossier=dossier, kind='cese', label='Cese', permission_level=5,
        )
        assert 'cese' in str(s)
