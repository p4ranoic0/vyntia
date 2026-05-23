"""Tests para el catálogo de feriados peruanos y el helper de días hábiles."""
from datetime import date

import pytest

from apps.core.business_days import business_days_between, is_business_day
from apps.core.holidays import (
    CATALOG_YEARS,
    HOLIDAYS_PERU,
    _easter_sunday,
    holidays_for,
    peru_national_holidays,
)


class TestEaster:
    """Domingo de Pascua — valores conocidos (algoritmo gregoriano)."""

    @pytest.mark.parametrize(
        "year,expected",
        [
            (2024, date(2024, 3, 31)),
            (2025, date(2025, 4, 20)),
            (2026, date(2026, 4, 5)),
            (2027, date(2027, 3, 28)),
            (2028, date(2028, 4, 16)),
        ],
    )
    def test_easter_known_dates(self, year, expected):
        assert _easter_sunday(year) == expected

    def test_jueves_y_viernes_santo_2026(self):
        holidays = peru_national_holidays(2026)
        # Pascua 2026 = 5 abril → Jueves Santo 2 abr, Viernes Santo 3 abr.
        assert holidays[date(2026, 4, 2)] == "Jueves Santo"
        assert holidays[date(2026, 4, 3)] == "Viernes Santo"


class TestHolidayCatalog:
    """Catálogo materializado HOLIDAYS_PERU 2024-2028."""

    def test_catalog_covers_required_years(self):
        for year in range(2024, 2029):
            assert year in HOLIDAYS_PERU
        assert set(CATALOG_YEARS) == set(HOLIDAYS_PERU.keys())

    def test_fixed_holidays_present_every_year(self):
        fixed = [
            (1, 1),
            (5, 1),
            (6, 29),
            (7, 28),
            (7, 29),
            (8, 30),
            (10, 8),
            (11, 1),
            (12, 8),
            (12, 9),
            (12, 25),
        ]
        for year, holidays in HOLIDAYS_PERU.items():
            for month, day in fixed:
                assert date(year, month, day) in holidays, (
                    f"falta feriado {month:02d}-{day:02d} en {year}"
                )

    def test_each_year_has_two_movable_holidays(self):
        # 11 fijos + Jueves Santo + Viernes Santo = 13.
        for year, holidays in HOLIDAYS_PERU.items():
            assert len(holidays) == 13, f"{year} tiene {len(holidays)} feriados"

    def test_holidays_for_arbitrary_year_beyond_catalog(self):
        # Funciona más allá de 2028 (los feriados fijos no cambian).
        holidays = holidays_for(2030)
        assert date(2030, 7, 28) in holidays
        assert date(2030, 12, 25) in holidays


class TestIsBusinessDay:
    def test_weekend_is_not_business_day(self):
        assert is_business_day(date(2026, 5, 23)) is False  # sábado
        assert is_business_day(date(2026, 5, 24)) is False  # domingo

    def test_regular_weekday_is_business_day(self):
        assert is_business_day(date(2026, 5, 22)) is True  # viernes normal

    def test_national_holiday_is_not_business_day(self):
        assert is_business_day(date(2026, 7, 28)) is False  # Fiestas Patrias


class TestBusinessDaysBetween:
    def test_none_or_inverted_returns_zero(self):
        assert business_days_between(None, date(2026, 1, 10)) == 0
        assert business_days_between(date(2026, 1, 10), None) == 0
        assert business_days_between(date(2026, 1, 10), date(2026, 1, 1)) == 0
        assert business_days_between(date(2026, 1, 10), date(2026, 1, 10)) == 0

    def test_inclusive_start_exclusive_end(self):
        # Lun 4 may → vie 8 may 2026, [start, end): cuenta 4,5,6,7 = 4.
        assert business_days_between(date(2026, 5, 4), date(2026, 5, 8)) == 4

    def test_skips_weekends(self):
        # Vie 1 may 2026 → lun 4 may: 1 may es Día del Trabajo (feriado),
        # 2-3 fin de semana → 0 hábiles en [1, 4).
        assert business_days_between(date(2026, 5, 1), date(2026, 5, 4)) == 0
        # Vie 8 may → mié 13 may: 8(vie),11(lun),12(mar) = 3 (9-10 finde).
        assert business_days_between(date(2026, 5, 8), date(2026, 5, 13)) == 3

    def test_subtracts_holiday_in_range(self):
        # Lun 27 jul → vie 31 jul 2026: 27,28,29,30,31 son lun-vie,
        # pero 28 y 29 son Fiestas Patrias → 5 - 2 = 3 hábiles.
        assert business_days_between(date(2026, 7, 27), date(2026, 8, 1)) == 3

    def test_crossing_holy_week_2026(self):
        # Lun 30 mar → lun 6 abr 2026. Jueves Santo 2 abr + Viernes Santo 3 abr.
        # Días lun-vie en [30 mar, 6 abr): 30,31 mar, 1,2,3 abr = 5 weekdays.
        # menos 2 feriados (2,3 abr) = 3.
        assert business_days_between(date(2026, 3, 30), date(2026, 4, 6)) == 3

    def test_crossing_year_end(self):
        # Lun 28 dic 2026 → vie 8 ene 2027.
        # Weekdays en [28 dic, 8 ene): 28,29,30,31 dic; 1,4,5,6,7 ene.
        #   = 4 + 5 = 9 weekdays.
        # Feriados en rango: 25 dic (fuera), 1 ene 2027 (Año Nuevo, dentro).
        #   28-31 dic: ningún feriado (Navidad 25 ya pasó). 1 ene es feriado.
        # 9 weekdays - 1 (1 ene) = 8.
        assert business_days_between(date(2026, 12, 28), date(2027, 1, 8)) == 8

    def test_leap_year_feb29_counted_as_business_day(self):
        # 2028 bisiesto: Feb 29 = martes, no feriado → cuenta como hábil.
        # Lun 28 feb → mié 1 mar 2028: [28 feb, 1 mar) = 28(lun),29(mar) = 2.
        assert business_days_between(date(2028, 2, 28), date(2028, 3, 1)) == 2

    def test_full_week_with_no_holidays(self):
        # Lun 11 may → lun 18 may 2026: 11-15 = 5 hábiles (16-17 finde).
        assert business_days_between(date(2026, 5, 11), date(2026, 5, 18)) == 5

    def test_servir_minimum_threshold(self):
        # Caso B.9: 1 jun → 15 jun 2026 debe dar ≥ 7 (SERVIR Art. 5).
        assert business_days_between(date(2026, 6, 1), date(2026, 6, 15)) >= 7
