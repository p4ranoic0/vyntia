"""Tests para el batch import CSV de empleados (#130)."""
import io

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from api.v1.employees.batch_import import import_employees_from_csv
from apps.employees.models import Employee
from apps.identity.models import Role, User, UserRole
from apps.organization.models import Department

HEADER = (
    "numero_documento,tipo_documento,nombres_empleado,apellido_paterno,"
    "apellido_materno,fecha_nacimiento,correo_personal,regimen_laboral,"
    "fecha_ingreso,sueldo_basico,area_id"
)


@pytest.fixture
def area(db):
    return Department.objects.create(
        nombre_organo="RRHH", nombre_unidad_organica="Recursos Humanos",
        siglas_area="RRHH", estado_area="activo",
    )


@pytest.fixture
def hr_user(db):
    user = User.objects.create_user(
        username="hr_batch", email="hr_batch@test.local",
        password="Test1234!",
        nombres_usuario="HR", apellidos_usuario="Batch",
        tipo_usuario="rrhh", nivel_acceso="total",
    )
    role, _ = Role.objects.get_or_create(
        nombre_rol="Administrador RRHH",
        defaults={"estado_rol": "activo", "nivel_jerarquico": 2,
                  "es_rol_sistema": True},
    )
    UserRole.objects.get_or_create(
        usuario=user, rol=role,
        defaults={"estado_asignacion": "activo"},
    )
    return user


@pytest.fixture
def auth_client(hr_user):
    refresh = RefreshToken.for_user(hr_user)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token!s}")
    return client


def _csv_file(rows, name="empleados.csv"):
    content = HEADER + "\n" + "\n".join(rows) + "\n"
    f = io.BytesIO(content.encode("utf-8"))
    f.name = name
    return f


def _row(doc="44556677", correo="juan@example.com", regimen="728",
         nac="1990-05-10", ingreso="2024-01-15", sueldo="2500.00",
         area_id="", nombres="Juan", tipo="DNI"):
    return (
        f"{doc},{tipo},{nombres},Pérez,Gómez,{nac},{correo},{regimen},"
        f"{ingreso},{sueldo},{area_id}"
    )


class _FakeRequest:
    """Request mínima para el helper: necesita .tenant y .FILES no aplica aquí."""

    def __init__(self, tenant=None):
        self.tenant = tenant


@pytest.mark.django_db
class TestBatchImportHelper:
    def test_valid_csv_creates_all(self, area):
        f = _csv_file([
            _row(doc="44556677", correo="a@x.com", area_id=str(area.id)),
            _row(doc="44556688", correo="b@x.com", area_id=str(area.id), nombres="Ana"),
        ])
        result = import_employees_from_csv(f, _FakeRequest())
        assert result["errors"] == []
        assert result["created"] == 2
        assert Employee.objects.count() == 2

    def test_duplicate_dni_in_db_rejects_all(self, area):
        # Primera importación crea el empleado.
        import_employees_from_csv(
            _csv_file([_row(doc="44556677", correo="a@x.com", area_id=str(area.id))]),
            _FakeRequest(),
        )
        assert Employee.objects.count() == 1
        # Segunda importación con el mismo DNI debe fallar y no crear nada.
        f = _csv_file([
            _row(doc="44556677", correo="c@x.com", area_id=str(area.id)),
            _row(doc="99887766", correo="d@x.com", area_id=str(area.id), nombres="Lucia"),
        ])
        result = import_employees_from_csv(f, _FakeRequest())
        assert result["created"] == 0
        assert len(result["errors"]) == 1
        assert result["errors"][0]["row"] == 2
        assert "numero_documento" in result["errors"][0]["errors"]
        # persist-none: la fila válida tampoco se creó.
        assert Employee.objects.count() == 1

    def test_duplicate_dni_within_file(self, area):
        f = _csv_file([
            _row(doc="44556677", correo="a@x.com", area_id=str(area.id)),
            _row(doc="44556677", correo="b@x.com", area_id=str(area.id), nombres="Otro"),
        ])
        result = import_employees_from_csv(f, _FakeRequest())
        assert result["created"] == 0
        # La fila 3 (segunda data) referencia la fila 2.
        dup = [e for e in result["errors"] if e["row"] == 3]
        assert dup and "numero_documento" in dup[0]["errors"]
        assert Employee.objects.count() == 0

    def test_invalid_regimen_rejected(self, area):
        f = _csv_file([
            _row(doc="44556677", correo="a@x.com", area_id=str(area.id),
                 regimen="REGIMEN_FALSO"),
        ])
        result = import_employees_from_csv(f, _FakeRequest())
        assert result["created"] == 0
        assert len(result["errors"]) == 1
        assert "datos_laborales" in result["errors"][0]["errors"]
        assert Employee.objects.count() == 0

    def test_illegal_age_rejected(self, area):
        # Nació en 2015 → menor de 18.
        f = _csv_file([
            _row(doc="44556677", correo="a@x.com", area_id=str(area.id),
                 nac="2015-01-01"),
        ])
        result = import_employees_from_csv(f, _FakeRequest())
        assert result["created"] == 0
        assert "fecha_nacimiento" in result["errors"][0]["errors"]
        assert Employee.objects.count() == 0

    def test_collects_all_errors_without_aborting(self, area):
        # Dos filas malas: régimen inválido y edad ilegal. Deben reportarse ambas.
        f = _csv_file([
            _row(doc="44556677", correo="a@x.com", area_id=str(area.id),
                 regimen="MALO"),
            _row(doc="44556688", correo="b@x.com", area_id=str(area.id),
                 nac="2015-01-01", nombres="Mini"),
        ])
        result = import_employees_from_csv(f, _FakeRequest())
        assert result["created"] == 0
        assert len(result["errors"]) == 2

    def test_missing_required_column(self, area):
        bad_header = HEADER.replace(",area_id", "")
        content = bad_header + "\n" + "x,DNI,Juan,Pérez,Gómez,1990-01-01,a@x.com,728,2024-01-01,2500.00\n"
        f = io.BytesIO(content.encode("utf-8"))
        result = import_employees_from_csv(f, _FakeRequest())
        assert result["created"] == 0
        assert "columns" in result["errors"][0]["errors"]


@pytest.mark.django_db
class TestBatchImportEndpoint:
    def test_requires_auth(self):
        client = APIClient()
        r = client.post("/api/v1/employees/batch-import/", {}, format="multipart")
        assert r.status_code in (401, 403)

    def test_no_file_returns_400(self, auth_client):
        r = auth_client.post("/api/v1/employees/batch-import/", {}, format="multipart")
        assert r.status_code == 400

    def test_valid_upload_creates_employees(self, auth_client, area):
        f = _csv_file([
            _row(doc="44556677", correo="a@x.com", area_id=str(area.id)),
        ])
        r = auth_client.post(
            "/api/v1/employees/batch-import/", {"file": f}, format="multipart"
        )
        assert r.status_code == 201, r.content
        assert r.data["data"]["created"] == 1
        assert Employee.objects.filter(numero_documento="44556677").exists()

    def test_invalid_upload_returns_422_and_no_creation(self, auth_client, area):
        f = _csv_file([
            _row(doc="123", correo="a@x.com", area_id=str(area.id)),  # DNI inválido
        ])
        r = auth_client.post(
            "/api/v1/employees/batch-import/", {"file": f}, format="multipart"
        )
        assert r.status_code == 422, r.content
        assert r.data["errors"]["created"] == 0
        assert Employee.objects.count() == 0
