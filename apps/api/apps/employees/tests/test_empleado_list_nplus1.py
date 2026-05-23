"""Fix N+1 de EmpleadoListSerializer (audit: 66 queries para 15 empleados → ~10).

El serializer disparaba ubicacion_actual() + datos_laborales_actuales() (×2)
por cada empleado. Ahora EmpleadoViewSet.get_queryset() prefetchea las filas
activas vía to_attr y el serializer las lee de cache.
"""
from datetime import date
from decimal import Decimal

import pytest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from api.v1.rrhh.serializers import EmpleadoListSerializer
from api.v1.rrhh.views import EmpleadoViewSet
from apps.contracts.models import EmploymentData
from apps.employees.models import Employee
from apps.organization.models import Department, LocationHistory


def _seed_employees(n, area):
    for i in range(n):
        emp = Employee.objects.create(
            numero_documento=f"{40000000 + i}",
            nombres_empleado=f"Emp{i}",
            apellido_paterno="Pérez",
            apellido_materno="Gómez",
            estado_empleado="activo",
        )
        EmploymentData.objects.create(
            empleado=emp, area=area,
            cargo_empleado="Analista", categoria="profesional",
            tipo_contrato="indefinido", regimen_laboral="728",
            fecha_ingreso=date(2024, 1, 1), fecha_inicio_contrato=date(2024, 1, 1),
            sueldo_basico=Decimal("2500.00"), estado_datos="activo",
        )
        LocationHistory.objects.create(
            empleado=emp, area_destino=area,
            tipo_movimiento="ingreso", fecha_inicio=date(2024, 1, 1),
            estado_ubicacion="activo",
        )


def _list_queryset():
    """Reproduce el queryset real del viewset para action='list'."""
    factory = APIRequestFactory()
    drf_request = Request(factory.get("/api/v1/employees/?page_size=50"))
    view = EmpleadoViewSet()
    view.action = "list"
    view.request = drf_request
    view.kwargs = {}
    return view.get_queryset()


@pytest.mark.django_db
class TestEmpleadoListNPlusOne:
    def test_list_serialization_is_constant_query_count(
        self, django_assert_max_num_queries
    ):
        area = Department.objects.create(
            nombre_organo="T", nombre_unidad_organica="Tecnología",
            siglas_area="TEC", estado_area="activo",
        )
        _seed_employees(50, area)

        qs = _list_queryset()
        # Sin fix: ~3 queries por empleado → >150 con 50 empleados.
        # Con fix: empleados (1) + 2 prefetches activos = constante.
        with django_assert_max_num_queries(12):
            data = EmpleadoListSerializer(qs, many=True).data

        assert len(data) == 50
        # El resumen y la ubicación se poblaron desde el prefetch (no None).
        assert data[0]["datos_laborales_resumen"]["regimen_laboral"] == "728"
        assert data[0]["ubicacion_actual"]["area_siglas"] == "TEC"

    def test_query_count_does_not_grow_with_rows(
        self, django_assert_max_num_queries
    ):
        area = Department.objects.create(
            nombre_organo="A", nombre_unidad_organica="Área", siglas_area="A",
            estado_area="activo",
        )
        # 5 empleados deben usar el MISMO número de queries que 50 (constante).
        _seed_employees(5, area)
        with django_assert_max_num_queries(12):
            EmpleadoListSerializer(_list_queryset(), many=True).data

    def test_serializer_without_prefetch_still_correct(self):
        # Fallback: instanciado directo (sin to_attr) usa los métodos del modelo.
        area = Department.objects.create(
            nombre_organo="T2", nombre_unidad_organica="Tec2", siglas_area="TC2",
            estado_area="activo",
        )
        _seed_employees(1, area)
        emp = Employee.objects.get()
        data = EmpleadoListSerializer(emp).data
        assert data["datos_laborales_resumen"]["regimen_laboral"] == "728"
        assert data["ubicacion_actual"]["area_siglas"] == "TC2"
