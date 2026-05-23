"""HR-domain SEAL re-audit for contracts severance (audit v2, 2026-05-23).

Confirms the Bloque-H-contracts fixes for the 3 v1 bugs hold and sweeps the
neighbouring tricky cese dates before sub-project D (Vyntia Pay) consumes
severance_service for real payroll math.

v1 bugs (now FIXED — these are pure-function regression guards here):
  - 29-feb cese crash (ValueError in _compute_vac_truncas via year-1).
  - vac truncas +1 inclusive overcount (1 mes pagaba 5 días en vez de 2.5).
  - CTS fracción de mes contada como mes completo.

NEW finding locked as xfail(strict): the fix swung the month counter to strict
day-of-month anniversary, which UNDERCOUNTS the most common scenario in RRHH-PE
— el cese a fin de mes. Un trabajador que labora del 1 al último día de un mes
trabajó un mes calendario completo (doctrina "mes calendario completo",
Ley 27735 / D.S. 005-2002-TR para grati; D.S. 001-97-TR para CTS). El conteo por
aniversario lo cuenta como mes incompleto y subpaga 1 mes en grati / CTS / vac
truncas. Ver test_*_undercount.

Legal sources: D.S. 012-92-TR (vacaciones), Ley 27735 + D.S. 005-2002-TR
(gratificaciones), D.S. 001-97-TR (CTS), LPCL Art. 38 (indemnización).
"""
from datetime import date
from decimal import Decimal

import pytest

from apps.contracts.services import severance_service as s


SUELDO = Decimal('3000')  # jornal diario = 100


# --------------------------------------------------------------------------- #
# 1. _minus_one_year — 29-feb y vecinos (no crash, traslado correcto)         #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize('fecha, esperado', [
    (date(2024, 2, 29), date(2023, 2, 28)),   # bisiesto -> no bisiesto: clamp a 28
    (date(2020, 2, 29), date(2019, 2, 28)),   # idem
    (date(2023, 2, 28), date(2022, 2, 28)),
    (date(2024, 3, 1), date(2023, 3, 1)),
    (date(2023, 12, 31), date(2022, 12, 31)),
    (date(2024, 4, 30), date(2023, 4, 30)),
])
def test_minus_one_year_maneja_29_feb(fecha, esperado):
    assert s._minus_one_year(fecha) == esperado


# --------------------------------------------------------------------------- #
# 2. _months_between — sin +1 inclusivo (fracción no es mes completo)         #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize('inicio, fin, esperado', [
    (date(2024, 1, 1), date(2024, 2, 1), 1),    # 1 mes exacto
    (date(2024, 1, 1), date(2024, 4, 1), 3),    # 3 meses
    (date(2024, 1, 1), date(2024, 7, 1), 6),    # 6 meses
    (date(2024, 1, 1), date(2025, 1, 1), 12),   # 12 meses
    (date(2024, 1, 1), date(2024, 1, 1), 0),    # mismo día
    (date(2024, 1, 1), date(2024, 1, 15), 0),   # 14 días = fracción
    (date(2024, 1, 1), date(2024, 1, 21), 0),   # 20 días = fracción
    (date(2024, 6, 1), date(2024, 6, 15), 0),   # 15 días = fracción
])
def test_months_between_no_suma_inclusivo(inicio, fin, esperado):
    assert s._months_between(inicio, fin) == esperado


# --------------------------------------------------------------------------- #
# 3. Vacaciones truncas — D.S. 012-92-TR, 2.5 días por mes                    #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize('inicio, cese, dias_esperados, monto_esperado', [
    (date(2024, 1, 1), date(2024, 2, 1), '2.5', Decimal('250.00')),   # 1 mes
    (date(2024, 1, 1), date(2024, 4, 1), '7.5', Decimal('750.00')),   # 3 meses
    (date(2024, 1, 1), date(2024, 7, 1), '15.0', Decimal('1500.00')),  # 6 meses
    (date(2024, 1, 1), date(2025, 1, 1), '30.0', Decimal('3000.00')),  # 1 año
    (date(2024, 1, 1), date(2024, 1, 21), '0.0', Decimal('0.00')),    # 20 días = fracción
])
def test_vac_truncas_proporcional(inicio, cese, dias_esperados, monto_esperado):
    amount, base, _ = s._compute_vac_truncas(SUELDO, inicio, cese)
    assert base['dias_proporcionales'] == dias_esperados
    assert amount == monto_esperado


# --------------------------------------------------------------------------- #
# 4. CTS — fracción de mes no es mes completo                                 #
# --------------------------------------------------------------------------- #

def test_cts_fraccion_15_dias_no_es_mes():
    amount, base, _ = s._compute_cts(SUELDO, date(2024, 6, 1), date(2024, 6, 15))
    assert base['meses_semestre'] == 0
    assert amount == Decimal('0.00')


def test_cts_un_mes_exacto():
    amount, base, _ = s._compute_cts(SUELDO, date(2024, 5, 1), date(2024, 6, 1))
    assert base['meses_semestre'] == 1
    assert amount == Decimal('500.00')   # sueldo/6


# --------------------------------------------------------------------------- #
# 5. Tricky cese dates — no crash, settlement sano (pure-function level)      #
# --------------------------------------------------------------------------- #

@pytest.mark.parametrize('inicio, cese', [
    (date(2020, 2, 29), date(2024, 2, 29)),  # 29-feb con inicio 29-feb bisiesto
    (date(2020, 1, 1), date(2023, 2, 28)),   # 28-feb no bisiesto
    (date(2023, 3, 1), date(2024, 3, 1)),    # 01-mar
    (date(2023, 4, 30), date(2024, 4, 30)),  # 30-abr
    (date(2022, 1, 1), date(2024, 7, 31)),   # 31 de mes de 31 días
])
def test_vac_truncas_cese_tricky_no_crashea(inicio, cese):
    amount, base, _ = s._compute_vac_truncas(SUELDO, inicio, cese)
    assert amount >= Decimal('0')
    assert Decimal(base['dias_proporcionales']) <= Decimal('30.0')


# --------------------------------------------------------------------------- #
# 6. NEW finding — cese a fin de mes subcuenta 1 mes ("mes calendario")       #
#    Locked as xfail(strict): vira a XPASS (rojo) cuando se corrija.          #
# --------------------------------------------------------------------------- #

def test_grat_trunca_fin_de_semestre_paga_completo():
    """Jul 1 → Dic 31: semestre jul-dic trabajado íntegro → 1 sueldo (3000).

    FIXED (Bloque-H-contracts v2): _months_between completa el mes cuando el
    cese cae a fin de mes ("mes calendario completo"), antes subpagaba 5/6.
    """
    amount, base, _ = s._compute_grat_trunca(SUELDO, date(2024, 7, 1), date(2024, 12, 31))
    assert amount == Decimal('3000.00'), (
        f'Trabajó el semestre completo; esperado 3000, got {amount} '
        f'(meses={base["meses_semestre"]})'
    )
