# -*- coding: utf-8 -*-
"""
Fixtures compartidas para los tests de la Phase 1: Onboarding Self-Service.

Provee:
- onboarding_factory: crea Empleado + Usuario + OnboardingEmpleado en test DB.
- hr_client: APIClient autenticado como usuario RRHH.
- onboarding_client: APIClient autenticado como el empleado de onboarding.
"""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from app_rrhh.models import Empleado, OnboardingEmpleado, Usuario
from app_rrhh.models.roles import Rol
from app_rrhh.models.sistema import UsuarioRoles


def _make_empleado(**kwargs):
    """Crea un Empleado con valores por defecto, acepta overrides."""
    defaults = dict(
        nombres_empleado="Nuevo",
        apellido_paterno="Empleado",
        apellido_materno="Test",
        numero_documento="99887766",
        tipo_documento="DNI",
        correo_personal="nuevo.empleado@test.com",
        telefono_celular="999888777",
        fecha_nacimiento="1995-06-15",
        estado_civil="soltero",
        genero_empleado="masculino",
        direccion_domicilio="Av. Test 456",
        distrito_domicilio="Lima",
        provincia_domicilio="Lima",
        departamento_domicilio="Lima",
        estado_empleado="activo",
    )
    defaults.update(kwargs)
    return Empleado.objects.create(**defaults)


def _make_usuario(empleado=None, tipo="empleado", suffix="onb", **kwargs):
    """Crea un Usuario con valores por defecto."""
    defaults = dict(
        username=f"usuario_{suffix}",
        email=f"{suffix}@test.com",
        nombres_usuario="Nuevo",
        apellidos_usuario="Test",
        password="testpass123",
        tipo_usuario=tipo,
        nivel_acceso="personal",
        empleado=empleado,
    )
    defaults.update(kwargs)
    return Usuario.objects.create_user(**defaults)


def _get_jwt_client(usuario):
    """Devuelve APIClient autenticado via JWT Bearer para el usuario dado."""
    refresh = RefreshToken.for_user(usuario)
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return client


@pytest.fixture
def onboarding_factory(db):
    """
    Factoría de onboardings de prueba.

    Uso:
        onboarding = onboarding_factory()
        onboarding = onboarding_factory(estado_onboarding='completado')

    Devuelve: OnboardingEmpleado instance.
    """
    created = []

    def factory(**kwargs):
        onboarding_kwargs = {}
        empleado_kwargs = {}
        usuario_kwargs = {}

        # Separar kwargs por destino
        onboarding_fields = {
            "estado_onboarding",
            "datos_personales_completos",
            "datos_laborales_completos",
            "dni_subido",
            "declaraciones_juradas_subidas",
            "certificados_academicos_subidos",
            "certificados_trabajo_subidos",
            "documentos_familiares_subidos",
            "email_bienvenida_enviado",
            "observaciones",
        }
        for k, v in kwargs.items():
            if k in onboarding_fields:
                onboarding_kwargs[k] = v
            else:
                empleado_kwargs[k] = k

        # Crear Empleado
        empleado = _make_empleado()

        # Crear Usuario empleado vinculado al Empleado
        usuario = _make_usuario(empleado=empleado, tipo="empleado", suffix=f"empl_{empleado.empleado_id}")

        # Crear OnboardingEmpleado
        onboarding = OnboardingEmpleado.objects.create(
            empleado=empleado,
            usuario=usuario,
            **onboarding_kwargs,
        )
        created.append(onboarding)
        return onboarding

    yield factory


def _assign_rrhh_role(usuario):
    """Asigna el rol 'Administrador RRHH' al usuario dado (crea el rol si no existe)."""
    rol, _ = Rol.objects.get_or_create(
        nombre_rol="Administrador RRHH",
        defaults={"estado_rol": "activo", "nivel_jerarquico": 2, "es_rol_sistema": True},
    )
    UsuarioRoles.objects.get_or_create(
        usuario=usuario,
        rol=rol,
        defaults={"estado_asignacion": "activo"},
    )
    return usuario


@pytest.fixture
def hr_usuario(db):
    """Usuario de tipo RRHH para tests de API."""
    usuario = _make_usuario(
        tipo="rrhh",
        suffix="rrhh",
        nivel_acceso="total",
    )
    return _assign_rrhh_role(usuario)


@pytest.fixture
def hr_client(hr_usuario):
    """APIClient autenticado como usuario RRHH."""
    return _get_jwt_client(hr_usuario)


@pytest.fixture
def onboarding_client(onboarding_factory):
    """APIClient autenticado como el empleado de onboarding."""
    onboarding = onboarding_factory()
    client = _get_jwt_client(onboarding.usuario)
    client._onboarding = onboarding
    return client
