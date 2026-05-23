"""Cálculo de días hábiles peruanos (lunes-viernes, descontando feriados).

`business_days_between(start, end, region=None)` cuenta los días hábiles en el
intervalo [start, end): inclusivo del inicio, exclusivo del fin — misma
semántica que el `_business_days_between` interino que reemplaza (B.9
JobPosting / SERVIR Art. 5).

Un día hábil es lunes a viernes que NO sea feriado nacional (ni regional, si
se pasa `region`). Maneja correctamente intervalos que cruzan años (acumula
feriados de cada año tocado), años bisiestos y fines de semana.
"""
from __future__ import annotations

from datetime import date, timedelta

from .holidays import holidays_for


def is_business_day(day: date, region: str | None = None) -> bool:
    """True si `day` es lunes-viernes y no es feriado."""
    if day.weekday() >= 5:  # 5=sábado, 6=domingo
        return False
    return day not in holidays_for(day.year, region)


def business_days_between(
    start: date | None, end: date | None, region: str | None = None
) -> int:
    """Cuenta días hábiles en [start, end) — inclusivo de start, exclusivo de end.

    Devuelve 0 si algún extremo es None o si end <= start.
    """
    if start is None or end is None or end <= start:
        return 0

    # Pre-cargar feriados de cada año tocado por el intervalo (rápido y cruza años).
    holidays: set[date] = set()
    for year in range(start.year, end.year + 1):
        holidays.update(holidays_for(year, region).keys())

    count = 0
    cur = start
    while cur < end:
        if cur.weekday() < 5 and cur not in holidays:
            count += 1
        cur += timedelta(days=1)
    return count
