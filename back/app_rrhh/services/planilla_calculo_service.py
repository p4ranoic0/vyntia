"""
Servicio para cálculo de planillas mensuales.
Implementa la lógica completa del proceso de remuneraciones según normativa peruana.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from app_rrhh.models import (
    ConfiguracionAfp,
    ConfiguracionUit,
    DetallePlanilla,
    Empleado,
    PlanillaMensual,
)
from django.db import transaction
from django.db.models import Sum
from django.utils import timezone


class PlanillaCalculoService:
    """Servicio para el cálculo de planillas mensuales."""

    @transaction.atomic
    def calcular_planilla(self, planilla_id: int) -> Dict[str, Any]:
        """
        Calcula todos los detalles de una planilla mensual.

        Proceso:
        1. Verificar estado laboral de empleados
        2. Calcular haberes (proporcional a días laborados)
        3. Calcular descuentos por sistema de pensiones (AFP/ONP)
        4. Calcular ESSALUD (según modalidad: CAS o estándar)
        5. Calcular renta de 4ta categoría (con validación de suspensión)
        6. Calcular neto a pagar
        7. Actualizar totales de planilla
        """
        try:
            planilla = PlanillaMensual.objects.get(planilla_id=planilla_id)

            if planilla.estado not in ["borrador", "generada", "procesando"]:
                raise ValueError(
                    "Solo se pueden calcular planillas en borrador o generadas"
                )

            # Cambiar estado a procesando
            planilla.estado = "procesando"
            planilla.save()

            # Obtener configuración UIT del año
            anio_planilla = int(planilla.periodo[:4])
            try:
                config_uit = ConfiguracionUit.objects.get(
                    anio=anio_planilla, estado="activo"
                )
            except ConfiguracionUit.DoesNotExist:
                config_uit = None

            detalles = DetallePlanilla.objects.filter(planilla=planilla)

            for detalle in detalles:
                self._calcular_detalle_planilla(detalle, planilla, config_uit)

            # Actualizar totales de planilla
            self._actualizar_totales_planilla(planilla)

            # Cambiar estado a generada
            planilla.estado = "generada"
            planilla.fecha_generacion = timezone.now()
            planilla.save()

            return {
                "success": True,
                "message": "Planilla calculada exitosamente",
                "planilla_id": planilla_id,
                "total_trabajadores": planilla.total_trabajadores,
                "total_neto_pagar": float(planilla.total_neto_pagar),
            }

        except PlanillaMensual.DoesNotExist as exc:
            raise ValueError(f"Planilla {planilla_id} no encontrada") from exc
        except Exception as exc:
            # Revertir estado si hay error
            if "planilla" in locals():
                planilla.estado = "borrador"
                planilla.save()
            raise RuntimeError(f"Error al calcular planilla: {exc}") from exc

    def _calcular_detalle_planilla(
        self,
        detalle: DetallePlanilla,
        planilla: PlanillaMensual,
        config_uit: Optional[ConfiguracionUit] = None,
    ):
        """Calcula un detalle individual de planilla."""

        # 1. Verificar datos del empleado
        empleado = detalle.empleado
        datos_laborales = detalle.datos_laborales

        # Verificar estado laboral
        if empleado.estado_empleado not in ["activo"]:
            detalle.estado_laboral = "suspendido"

        # 2. Calcular haberes (proporcional a días laborados si <30)
        dias_mes = 30  # Se considera 30 días para cálculos mensuales
        factor_proporcional = Decimal(str(detalle.dias_laborados)) / Decimal(
            str(dias_mes)
        )

        # Aplicar proporcionalidad si hay días no laborados
        if detalle.dias_laborados < dias_mes:
            detalle.remuneracion_basica = (
                datos_laborales.sueldo_basico * factor_proporcional
                if datos_laborales
                else detalle.remuneracion_basica * factor_proporcional
            )

        # Total haberes
        detalle.total_haberes = (
            detalle.remuneracion_basica
            + detalle.asignacion_familiar
            + detalle.bonificacion_especial
            + detalle.otras_bonificaciones
        )

        # 3. Calcular descuentos sistema pensiones
        self._calcular_sistema_pensiones(detalle, planilla.periodo)

        # 4. Calcular ESSALUD según modalidad
        self._calcular_essalud(detalle, planilla.modalidad, config_uit)

        # 5. Calcular renta de 4ta categoría
        self._calcular_renta_cuarta(detalle, empleado, config_uit)

        # 6. Calcular total descuentos
        detalle.total_descuentos = (
            detalle.total_afp
            + detalle.aporte_onp
            + detalle.renta_quinta_categoria
            + detalle.descuentos_judiciales
            + detalle.prestamos
            + detalle.otros_descuentos
        )

        # 7. Calcular neto a pagar
        detalle.neto_pagar = detalle.total_haberes - detalle.total_descuentos

        detalle.save()

    def _calcular_sistema_pensiones(self, detalle: DetallePlanilla, periodo: str):
        """Calcula descuentos del sistema de pensiones (AFP/ONP)."""

        if (
            "AFP" in detalle.sistema_pensiones
            and not detalle.sistema_pensiones.startswith("PENSIONISTA")
        ):
            # Extraer nombre AFP
            afp_nombre = detalle.sistema_pensiones.replace("AFP ", "").strip()

            try:
                config_afp = ConfiguracionAfp.objects.get(
                    afp_nombre__icontains=afp_nombre,
                    vigencia_mes=periodo,
                    estado="activo",
                )

                # Aplicar tope de remuneración asegurable
                base_calculo = min(
                    detalle.total_haberes,
                    config_afp.remuneracion_max_asegurable,
                )

                # Aporte obligatorio (10%)
                detalle.aporte_afp_obligatorio = (
                    base_calculo * config_afp.aporte_obligatorio_pct / Decimal("100")
                )

                # Comisión según tipo
                if detalle.tipo_comision_afp == "FLUJO":
                    detalle.comision_afp = (
                        base_calculo * config_afp.comision_flujo_pct / Decimal("100")
                    )
                else:  # MIXTA
                    detalle.comision_afp = (
                        base_calculo * config_afp.comision_mixta_pct / Decimal("100")
                    )

                # Prima de seguro
                detalle.prima_seguro_afp = (
                    base_calculo * config_afp.prima_seguro_pct / Decimal("100")
                )

                # Total AFP
                detalle.total_afp = (
                    detalle.aporte_afp_obligatorio
                    + detalle.comision_afp
                    + detalle.prima_seguro_afp
                )

                # ONP en cero
                detalle.aporte_onp = Decimal("0.00")

            except ConfiguracionAfp.DoesNotExist:
                # Usar tasas por defecto si no hay configuración
                detalle.aporte_afp_obligatorio = (
                    detalle.total_haberes * Decimal("10.00") / Decimal("100")
                )
                detalle.comision_afp = (
                    detalle.total_haberes * Decimal("1.47") / Decimal("100")
                )
                detalle.prima_seguro_afp = (
                    detalle.total_haberes * Decimal("1.37") / Decimal("100")
                )
                detalle.total_afp = (
                    detalle.aporte_afp_obligatorio
                    + detalle.comision_afp
                    + detalle.prima_seguro_afp
                )
                detalle.aporte_onp = Decimal("0.00")

        elif "ONP" in detalle.sistema_pensiones:
            # ONP: 13% de la remuneración
            detalle.aporte_onp = (
                detalle.total_haberes * Decimal("13.00") / Decimal("100")
            )
            detalle.total_afp = Decimal("0.00")
            detalle.aporte_afp_obligatorio = Decimal("0.00")
            detalle.comision_afp = Decimal("0.00")
            detalle.prima_seguro_afp = Decimal("0.00")

        else:
            # Sin sistema de pensiones o pensionista
            detalle.aporte_onp = Decimal("0.00")
            detalle.total_afp = Decimal("0.00")
            detalle.aporte_afp_obligatorio = Decimal("0.00")
            detalle.comision_afp = Decimal("0.00")
            detalle.prima_seguro_afp = Decimal("0.00")

    def _calcular_essalud(
        self,
        detalle: DetallePlanilla,
        modalidad: str,
        config_uit: Optional[ConfiguracionUit] = None,
    ):
        """
        Calcula ESSALUD según modalidad de contrato.
        - CAS: 9% del 45% de la UIT vigente (monto fijo mensual)
        - Otros: 9% de la remuneración total
        """

        if modalidad in ["plazo_determinado", "subsidio", "locacion", "consultoria"]:  # CAS y similares
            if config_uit:
                # 9% del 45% de UIT dividido entre 12 meses
                detalle.essalud = config_uit.essalud_cas_mensual
            else:
                # Usar UIT por defecto (5350 para 2026)
                uit_default = Decimal("5350.00")
                detalle.essalud = (
                    uit_default * Decimal("0.45") * Decimal("0.09")
                ) / Decimal("12")
        else:  # Planilla regular
            # 9% del total de haberes
            detalle.essalud = detalle.total_haberes * Decimal("9.00") / Decimal("100")

    def _calcular_renta_cuarta(
        self,
        detalle: DetallePlanilla,
        empleado: Empleado,
        config_uit: Optional[ConfiguracionUit] = None,
    ):
        """
        Calcula retención de renta de 4ta categoría.
        - 8% de la remuneración si NO tiene suspensión vigente
        - 0% si tiene suspensión vigente y no ha superado el tope anual
        """

        # Verificar si tiene suspensión vigente
        if empleado.tiene_suspension_renta_cuarta_vigente:
            # Verificar tope anual
            if config_uit:
                tope_anual = config_uit.tope_renta_cuarta_soles
            else:
                # Tope por defecto: 45 UITs
                tope_anual = Decimal("5350.00") * Decimal("45.00")

            # Si no ha superado el tope, NO retener
            if detalle.tope_suspension_anual < tope_anual:
                detalle.tiene_suspension_renta_cuarta = True
                detalle.renta_quinta_categoria = Decimal("0.00")
                # Actualizar acumulado
                detalle.tope_suspension_anual += detalle.total_haberes
            else:
                # Superó el tope, retener
                detalle.tiene_suspension_renta_cuarta = False
                if config_uit:
                    porcentaje = config_uit.porcentaje_renta_cuarta
                else:
                    porcentaje = Decimal("8.00")
                detalle.renta_quinta_categoria = (
                    detalle.total_haberes * porcentaje / Decimal("100")
                )
        else:
            # No tiene suspensión, retener 8%
            detalle.tiene_suspension_renta_cuarta = False
            if config_uit:
                porcentaje = config_uit.porcentaje_renta_cuarta
            else:
                porcentaje = Decimal("8.00")
            detalle.renta_quinta_categoria = (
                detalle.total_haberes * porcentaje / Decimal("100")
            )

    def _actualizar_totales_planilla(self, planilla: PlanillaMensual):
        """Actualiza los totales consolidados de la planilla."""

        detalles = DetallePlanilla.objects.filter(planilla=planilla)

        totales = detalles.aggregate(
            total_remuneracion_bruta=Sum("total_haberes"),
            total_descuentos=Sum("total_descuentos"),
            total_neto_pagar=Sum("neto_pagar"),
            total_essalud=Sum("essalud"),
            total_aporte_afp=Sum("total_afp"),
            total_onp=Sum("aporte_onp"),
        )

        planilla.total_trabajadores = detalles.count()
        planilla.total_remuneracion_bruta = totales[
            "total_remuneracion_bruta"
        ] or Decimal("0.00")
        planilla.total_descuentos = totales["total_descuentos"] or Decimal("0.00")
        planilla.total_neto_pagar = totales["total_neto_pagar"] or Decimal("0.00")
        planilla.total_essalud = totales["total_essalud"] or Decimal("0.00")
        planilla.total_aporte_afp = totales["total_aporte_afp"] or Decimal("0.00")
        planilla.total_onp = totales["total_onp"] or Decimal("0.00")
        planilla.save()
