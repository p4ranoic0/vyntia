"""Catálogo de feriados peruanos (días no laborables a nivel nacional).

Base legal: feriados nacionales del régimen laboral peruano (DL 713 y normas
complementarias; consolidados en la práctica bajo el calendario que cita la
Ley 29408). Cubre los feriados nacionales fijos + los dos movibles ligados a
Semana Santa (Jueves y Viernes Santo, calculados a partir de la Pascua).

Diseño:
  - `peru_national_holidays(year)` calcula el calendario para CUALQUIER año
    (los feriados fijos no cambian; los movibles se derivan de la Pascua).
  - `HOLIDAYS_PERU` es el catálogo materializado para 2024-2028 (rango mínimo
    pedido por D-Pay) construido sobre esa función — útil para inspección y
    para tests deterministas.
  - `REGIONAL_HOLIDAYS` es el punto de extensión para feriados regionales
    (p.ej. fundación de ciudad). Vacío por defecto; D-Pay lo poblará por
    `region` cuando exista la configuración por tenant/sede.

Todas las fechas son `datetime.date`. Los lookups devuelven un dict
`{date: nombre}` para que el consumidor pueda mostrar el motivo del feriado.
"""
from __future__ import annotations

from datetime import date
from functools import lru_cache

# Años con catálogo materializado explícitamente (mínimo pedido por D-Pay).
CATALOG_YEARS = range(2024, 2029)  # 2024, 2025, 2026, 2027, 2028

# Feriados nacionales con fecha fija (mes, día) -> nombre.
_FIXED_HOLIDAYS: list[tuple[int, int, str]] = [
    (1, 1, "Año Nuevo"),
    (5, 1, "Día del Trabajo"),
    (6, 29, "San Pedro y San Pablo"),
    (7, 28, "Fiestas Patrias"),
    (7, 29, "Fiestas Patrias"),
    (8, 30, "Santa Rosa de Lima"),
    (10, 8, "Combate de Angamos"),
    (11, 1, "Día de Todos los Santos"),
    (12, 8, "Inmaculada Concepción"),
    (12, 9, "Batalla de Ayacucho"),
    (12, 25, "Navidad"),
]

# Feriados regionales: {region_code: [(mes, dia, nombre), ...]}.
# Punto de extensión para D-Pay (configuración por tenant/sede). Vacío hoy.
REGIONAL_HOLIDAYS: dict[str, list[tuple[int, int, str]]] = {}


def _easter_sunday(year: int) -> date:
    """Domingo de Pascua (algoritmo de Gauss/Meeus para el calendario gregoriano)."""
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    month = (h + el - 7 * m + 114) // 31
    day = ((h + el - 7 * m + 114) % 31) + 1
    return date(year, month, day)


@lru_cache(maxsize=None)
def peru_national_holidays(year: int) -> dict[date, str]:
    """Devuelve {fecha: nombre} de los feriados nacionales del año dado.

    Incluye los feriados fijos y los movibles (Jueves y Viernes Santo,
    derivados del Domingo de Pascua). Funciona para cualquier año, no solo
    los del catálogo materializado.
    """
    holidays: dict[date, str] = {
        date(year, month, day): name for month, day, name in _FIXED_HOLIDAYS
    }
    easter = _easter_sunday(year)
    from datetime import timedelta

    holidays[easter - timedelta(days=3)] = "Jueves Santo"
    holidays[easter - timedelta(days=2)] = "Viernes Santo"
    return holidays


def holidays_for(year: int, region: str | None = None) -> dict[date, str]:
    """Feriados nacionales del año + regionales de `region` si aplica."""
    holidays = dict(peru_national_holidays(year))
    if region and region in REGIONAL_HOLIDAYS:
        for month, day, name in REGIONAL_HOLIDAYS[region]:
            holidays[date(year, month, day)] = name
    return holidays


# Catálogo materializado para inspección / tests (2024-2028).
HOLIDAYS_PERU: dict[int, dict[date, str]] = {
    year: peru_national_holidays(year) for year in CATALOG_YEARS
}
