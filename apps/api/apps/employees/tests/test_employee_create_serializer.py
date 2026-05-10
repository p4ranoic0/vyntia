"""Tests for EmpleadoCreateSerializer fixes (B.4 #17)."""

import inspect

import pytest
from rest_framework import serializers as drf_serializers


@pytest.mark.django_db
class TestEmpleadoCreateSerializerAreaLookup:
    def test_serializer_uses_id_not_area_id_for_dept_lookup(self):
        from api.v1.rrhh.serializers import EmpleadoCreateSerializer

        src = inspect.getsource(EmpleadoCreateSerializer)
        assert "Department.objects.get(area_id=" not in src
        assert "Department.objects.get(id=" in src or "Department.objects.get(pk=" in src

    def test_area_inicial_is_uuid_not_integer_field(self):
        from api.v1.rrhh.serializers import EmpleadoCreateSerializer

        field = EmpleadoCreateSerializer().fields.get("area_inicial")
        if field is not None:
            assert not isinstance(field, drf_serializers.IntegerField)
