# -*- coding: utf-8 -*-
"""
Tests para OnboardingService — Wave 0 RED scaffold.

Estos tests deben FALLAR (RED) hasta que Wave 1 implemente la lógica.
Cubre: ONBD-01 (corregir correo), ONBD-04 (notificar progreso),
       ONBD-05 (estado tras DNI subido via API), ONBD-06 (familiar),
       ONBD-07 (academico/laboral).
"""

import pytest

from apps.onboarding.models import OnboardingEmpleado
from apps.onboarding.services import OnboardingService


@pytest.mark.django_db
class TestActualizarEstado:
    """Tests para comportamientos de OnboardingService no implementados aún (ONBD-04 a ONBD-07).

    El servicio actualizar_estado_onboarding existe pero NO emite notificaciones
    ni registra historial de cambios — esas características son de Wave 1.
    """

    def test_dni_subido_retorna_historial_de_cambio(self, onboarding_factory):
        """ONBD-05: actualizar_estado_onboarding debe retornar dict con 'historial_cambio'.

        El servicio actualmente devuelve solo el OnboardingEmpleado.
        Wave 1 debe enriquecer el retorno con historial.
        DEBE FALLAR en RED hasta que se implemente el historial.
        """
        onboarding = onboarding_factory()

        resultado = OnboardingService.actualizar_estado_onboarding(onboarding.onboarding_id)

        # Wave 1 debe cambiar la firma para devolver dict con historial
        # Actualmente devuelve OnboardingEmpleado directamente — esto falla RED
        assert isinstance(resultado, dict), (
            f"Se esperaba dict con 'historial_cambio', pero se obtuvo {type(resultado).__name__}. "
            "Wave 1 debe cambiar la firma de actualizar_estado_onboarding."
        )
        assert "historial_cambio" in resultado, (
            "El resultado debe incluir clave 'historial_cambio' con el estado anterior."
        )

    def test_familiar_subido_notifica_empleado(self, onboarding_factory):
        """ONBD-06: Al completar documentos_familiares, se debe notificar al empleado.

        El servicio actualmente NO envía notificación al completar sección familiar.
        DEBE FALLAR en RED — Wave 1 agrega notificación.
        """
        onboarding = onboarding_factory()

        # Simular que documentos familiares ya fueron subidos
        onboarding.documentos_familiares_subidos = True
        onboarding.datos_personales_completos = True
        onboarding.save()

        resultado = OnboardingService.actualizar_estado_onboarding(onboarding.onboarding_id)

        # Wave 1 debe agregar clave 'notificacion_enviada' al resultado
        assert isinstance(resultado, dict), (
            "Se esperaba dict con 'notificacion_enviada', pero se obtuvo "
            f"{type(resultado).__name__}."
        )
        assert "notificacion_enviada" in resultado

    def test_academico_subido_no_retrocede_estado(self, onboarding_factory):
        """ONBD-07: El estado no debe retroceder si ya estaba en pendiente_validacion.

        Si el onboarding está en 'pendiente_validacion' y se llama actualizar_estado,
        no debe regresar a 'pendiente_documentos'.
        DEBE FALLAR en RED — Wave 1 debe implementar protección de estado.
        """
        onboarding = onboarding_factory(estado_onboarding="pendiente_validacion")

        resultado = OnboardingService.actualizar_estado_onboarding(onboarding.onboarding_id)

        # Actualmente el servicio puede regresar el estado — esto falla RED
        # ya que el resultado es un model, no dict con 'estado_protegido'
        assert isinstance(resultado, dict), (
            "Se esperaba dict con 'estado_protegido', pero el servicio devolvió "
            f"{type(resultado).__name__}."
        )
        assert resultado.get("estado_protegido") is True, (
            "Wave 1 debe evitar retroceso de estado en onboardings pendientes de validación."
        )

    def test_laboral_subido_progreso_porcentaje_actualizado(self, onboarding_factory):
        """ONBD-07: Tras subir docs laborales, progreso_porcentaje debe estar en el resultado.

        El servicio actualmente devuelve el modelo, no un dict con el progreso.
        DEBE FALLAR en RED.
        """
        onboarding = onboarding_factory()
        onboarding.declaraciones_juradas_subidas = True
        onboarding.certificados_trabajo_subidos = True
        onboarding.datos_personales_completos = True
        onboarding.save()

        resultado = OnboardingService.actualizar_estado_onboarding(onboarding.onboarding_id)

        # Wave 1 debe devolver dict con 'progreso_porcentaje'
        assert isinstance(resultado, dict), (
            f"Se esperaba dict, pero se obtuvo {type(resultado).__name__}."
        )
        assert "progreso_porcentaje" in resultado, (
            "El resultado debe incluir 'progreso_porcentaje' calculado tras actualización."
        )


@pytest.mark.django_db
class TestCorregirCorreoService:
    """Tests para la lógica de corrección de correo en el servicio (ONBD-01)."""

    def test_corregir_correo_cambia_email_en_empleado(self, onboarding_factory):
        """ONBD-01: corregir_correo_personal actualiza Empleado.correo_personal.

        Este test DEBE FALLAR en RED porque el método corregir_correo_personal
        no existe todavía en OnboardingService.
        """
        onboarding = onboarding_factory()
        nuevo_correo = "correo.nuevo@example.com"

        # Este método no existe aún — falla RED con AttributeError
        resultado = OnboardingService.corregir_correo_personal(
            onboarding.onboarding_id,
            nuevo_correo,
        )

        onboarding.empleado.refresh_from_db()
        assert onboarding.empleado.correo_personal == nuevo_correo, (
            f"Se esperaba correo '{nuevo_correo}' pero se obtuvo "
            f"'{onboarding.empleado.correo_personal}'"
        )
        assert resultado is not None


# --- Wave 5 stubs: CursosCertificaciones model ---

@pytest.mark.django_db
class TestCursosCertificacionesModel:
    """Stubs for CursosCertificaciones model — implemented in Wave 5."""

    def test_cursos_certificaciones_model_stub(self):
        """Placeholder — full tests added when ViewSet is wired (plan 01-09)."""
        from apps.employees.models import CursosCertificaciones
        assert hasattr(CursosCertificaciones, 'nombre_curso')
        assert hasattr(CursosCertificaciones, 'empleado_id')
        assert hasattr(CursosCertificaciones, 'documento_id')

    def test_progreso_aprobado_property_exists(self, onboarding_factory):
        """progreso_aprobado property is accessible without error."""
        onboarding = onboarding_factory()
        assert hasattr(onboarding, 'progreso_aprobado')
        assert isinstance(onboarding.progreso_aprobado, int)
