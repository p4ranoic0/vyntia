"""HR-domain audit tests for the contracts module (audit v1, 2026-05-23).

Replicates the empleados v1→v5 audit cycle on CONTRACTS to surface latent
Peruvian-HR bugs BEFORE sub-project D (Vyntia Pay) consumes Contract +
EmploymentData + severance_service for real payroll math.

Flows under audit:
1. Renovación de contrato — 728: 5-year accumulated cap on fixed-term.
2. Conversión modal→indefinido (desnaturalización) por exceso de plazo.
3. Período de prueba según régimen (90 / 180 / 365 días).
4. Severance / liquidación — CTS, vac truncas, grati trunca; edge: 29-feb, fracciones.
5. T-Registro — alta/baja/modificación.

The 3 severance bugs (29-feb crash, +1 inclusive overcount in vac truncas and
CTS) were originally documented as xfail(strict=True); they were FIXED in the
Bloque-H-contracts cycle and these tests now assert the correct behaviour as
regression guards. Tests that assert MISSING legal logic (tope 5 años,
desnaturalización) still PASS while documenting the gap in their docstrings.

Legal sources: D.S. 003-97-TR (LPCL), D.Leg. 728 art. 74-77 (tope 5 años),
D.S. 001-96-TR art. 77 (desnaturalización), D.S. 001-97-TR (CTS),
Ley 27735 (gratificaciones), D.S. 012-92-TR (vacaciones).
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from apps.contracts.models import Contract, ProbationPeriod, Termination
from apps.contracts.services import probation_service, severance_service
from apps.employees.models import Employee
from apps.organization.models import Department


# --------------------------------------------------------------------------- #
# Fixtures                                                                     #
# --------------------------------------------------------------------------- #

@pytest.fixture
def department(db):
    return Department.objects.create(
        nombre_unidad_organica='Operaciones', siglas_area='OPE',
        estado_area='activa',
    )


@pytest.fixture
def employee(db):
    return Employee.objects.create(
        numero_documento='71717171', tipo_documento='DNI',
        nombres_empleado='Marco', apellido_paterno='Quispe',
        apellido_materno='Rojas', fecha_nacimiento=date(1988, 3, 3),
        estado_empleado='activo',
    )


def _make_contract(employee, department, *, num, tipo, fecha_inicio,
                   fecha_fin=None, sueldo=Decimal('3000.00'), status='ACTIVO'):
    return Contract.objects.create(
        empleado=employee, area=department,
        numero_contrato=f'CON-HRAUD-{num}',
        tipo_documento=tipo,
        fecha_inicio=fecha_inicio, fecha_fin=fecha_fin,
        salario_bruto=sueldo, cargo='Operario', status=status,
    )


# ===========================================================================
# FLUJO 3 — Período de prueba según régimen (golden path, expected to PASS)
# ===========================================================================

@pytest.mark.django_db
class TestProbationPorRegimen:
    def test_comun_90_dias(self, employee, department):
        c = _make_contract(employee, department, num='pp1',
                           tipo='LEY_728_FIJO', fecha_inicio=date(2024, 1, 1),
                           fecha_fin=date(2024, 12, 31))
        pp = probation_service.create_for_contract(contract=c, regimen='728_comun')
        assert pp.plazo_dias == 90
        assert pp.end_date == date(2024, 1, 1) + timedelta(days=90)

    def test_calificado_180_dias(self, employee, department):
        c = _make_contract(employee, department, num='pp2',
                           tipo='LEY_728_FIJO', fecha_inicio=date(2024, 1, 1),
                           fecha_fin=date(2024, 12, 31))
        pp = probation_service.create_for_contract(contract=c, regimen='728_calificado')
        assert pp.plazo_dias == 180

    def test_direccion_365_dias(self, employee, department):
        c = _make_contract(employee, department, num='pp3',
                           tipo='LEY_728_INDETERMINADO', fecha_inicio=date(2024, 1, 1))
        pp = probation_service.create_for_contract(contract=c, regimen='728_direccion')
        assert pp.plazo_dias == 365


# ===========================================================================
# FLUJO 1 — Renovación de contrato: tope 5 años acumulados (728)
# Documents MISSING legal validation. Test PASSES (asserts the gap exists).
# ===========================================================================

@pytest.mark.django_db
class TestTope5AniosFijo:
    def test_contrato_fijo_excede_5_anios_sin_validacion(self, employee, department):
        """D.Leg. 728 art. 74: plazo máximo acumulado en contratos modales = 5 años.

        GAP: ni Contract.clean() ni ningún servicio valida/alerta el exceso de
        5 años. Un contrato a plazo fijo de 6 años se crea sin error.
        D (Vyntia Pay) heredará empleados mal clasificados como 'fijo' que
        legalmente ya son indeterminados.
        """
        inicio = date(2018, 1, 1)
        fin = date(2024, 1, 1)  # 6 años — excede el tope legal de 5
        c = _make_contract(employee, department, num='t5y',
                           tipo='LEY_728_FIJO', fecha_inicio=inicio, fecha_fin=fin)
        # El sistema NO valida el tope: el contrato existe pese a exceder 5 años.
        assert (c.fecha_fin - c.fecha_inicio).days > 5 * 365, (
            'GAP confirmado: contrato fijo > 5 años aceptado sin validación '
            'ni flag de desnaturalización (D.Leg. 728 art. 74).'
        )
        assert not hasattr(c, 'excede_tope_legal'), (
            'No existe propiedad/flag que advierta el exceso del tope de 5 años.'
        )


# ===========================================================================
# FLUJO 2 — Conversión modal→indefinido (desnaturalización)
# Documents MISSING logic. Test PASSES (asserts the gap exists).
# ===========================================================================

@pytest.mark.django_db
class TestDesnaturalizacion:
    def test_no_existe_logica_desnaturalizacion(self, employee, department):
        """D.S. 001-96-TR art. 77: el contrato modal se desnaturaliza (deviene
        indeterminado) si excede el plazo máximo, hay renovaciones fraudulentas,
        o el trabajador sigue laborando vencido el plazo.

        GAP: no existe servicio ni método que detecte o ejecute la conversión
        modal→indefinido. Sub-proyecto D necesitará esta lógica para clasificar
        beneficios correctamente.
        """
        c = _make_contract(employee, department, num='desnat',
                           tipo='LEY_728_FIJO', fecha_inicio=date(2017, 1, 1),
                           fecha_fin=date(2024, 1, 1))
        # No hay método de conversión en el modelo ni en services.
        assert not hasattr(c, 'desnaturalizar'), 'GAP: sin método desnaturalizar()'
        assert not hasattr(c, 'esta_desnaturalizado'), 'GAP: sin flag desnaturalización'
        # tipo_documento sigue siendo modal pese a exceder plazo.
        assert c.tipo_documento == 'LEY_728_FIJO'


# ===========================================================================
# FLUJO 4 — Severance / liquidación: edge cases RRHH-PE
# These EXPOSE BUGS. Marked xfail(strict=True) so suite stays green.
# ===========================================================================

@pytest.mark.django_db
class TestSeveranceEdgeCases:

    def test_cese_29_feb_no_crashea(self, employee, department):
        # FIXED (Bloque-H-contracts): _minus_one_year maneja 29-feb → 28-feb
        # en año no bisiesto, evitando el ValueError en _compute_vac_truncas.
        contract = _make_contract(
            employee, department, num='29feb',
            tipo='LEY_728_INDETERMINADO', fecha_inicio=date(2020, 1, 1),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia', fecha_cese=date(2024, 2, 29),
        )
        # Debe computar sin lanzar ValueError.
        settlement = severance_service.compute_settlement(term)
        assert settlement.status == 'computed'

    def test_vac_truncas_1_mes_exacto_paga_2_5_dias(self, employee, department):
        """Trabajador con exactamente 1 mes completo: 2.5 días truncas.

        sueldo 3000 → jornal 100 → 2.5 días → 250.00.
        FIXED (Bloque-H-contracts): _months_between ya no suma +1 inclusivo,
        el bug pagaba 500.00 (5 días) por 1 mes exacto.
        """
        amount, base, _ = severance_service._compute_vac_truncas(
            Decimal('3000'), date(2024, 1, 1), date(2024, 2, 1),
        )
        assert amount == Decimal('250.00'), (
            f'Esperado 250.00 (2.5 días), obtenido {amount} '
            f'(meses={base["meses_año"]})'
        )

    def test_cts_fraccion_de_mes_no_cuenta_mes_completo(self, employee, department):
        """15 días de servicio NO deben pagar 1 mes completo de CTS.

        CTS legal = (sueldo/12)×meses + (sueldo/360)×días. 15 días = ~0.5 mes,
        no 1 mes. FIXED (Bloque-H-contracts): _months_between ya no cuenta la
        fracción de mes como mes completo (antes devolvía sueldo/6).
        """
        amount, base, _ = severance_service._compute_cts(
            Decimal('3000'), date(2024, 6, 1), date(2024, 6, 15),
        )
        # 15 días ≈ 0.5 mes; un mes completo (500) es claramente excesivo.
        assert amount < Decimal('500.00'), (
            f'15 días pagaron como mes completo: {amount} '
            f'(meses_semestre={base["meses_semestre"]})'
        )

    def test_renuncia_no_genera_indemnizacion(self, employee, department):
        """Golden: renuncia voluntaria NO da indemnización (control de regresión)."""
        contract = _make_contract(
            employee, department, num='renun',
            tipo='LEY_728_INDETERMINADO', fecha_inicio=date(2022, 1, 1),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia', fecha_cese=date(2024, 6, 30),
        )
        settlement = severance_service.compute_settlement(term)
        indemn = settlement.lines.get(component='indemnizacion')
        assert indemn.amount == Decimal('0.00')


# ===========================================================================
# FLUJO 4b — Severance: fin de mes (golden, control de regresión)
# ===========================================================================

@pytest.mark.django_db
class TestSeveranceFinDeMes:
    def test_cese_fin_de_mes_31_computa(self, employee, department):
        """Cese el 31 de un mes de 31 días debe computar sin error."""
        contract = _make_contract(
            employee, department, num='fm31',
            tipo='LEY_728_INDETERMINADO', fecha_inicio=date(2022, 1, 1),
        )
        term = Termination.objects.create(
            contract=contract, employee=employee,
            regimen='728', causal='renuncia', fecha_cese=date(2024, 7, 31),
        )
        settlement = severance_service.compute_settlement(term)
        assert settlement.status == 'computed'
        assert settlement.total_amount > Decimal('0')
