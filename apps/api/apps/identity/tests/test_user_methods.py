"""Tests for User model bug fixes (B.2 #44, #45)."""

from datetime import timedelta

import pytest
from django.utils import timezone


@pytest.mark.django_db
class TestTiempoDesdeUltimoLogin:
    def _user(self):
        from apps.identity.models import User
        u = User(username="t", email="t@t.local")
        u.set_password("x")
        return u

    def test_returns_days_when_more_than_a_day_old(self):
        u = self._user()
        u.last_login = timezone.now() - timedelta(days=3)
        assert u.tiempo_desde_ultimo_login.startswith("3 día")

    def test_returns_hours_when_between_1_hour_and_1_day(self):
        u = self._user()
        u.last_login = timezone.now() - timedelta(hours=2, minutes=10)
        assert u.tiempo_desde_ultimo_login.startswith("2 hora")

    def test_returns_minutes_when_between_1_minute_and_1_hour(self):
        """Bug #44: elif delta.seconds > 60 branch was missing a return — now fixed."""
        u = self._user()
        u.last_login = timezone.now() - timedelta(minutes=15)
        result = u.tiempo_desde_ultimo_login
        assert result is not None
        assert result.startswith("15 minuto")

    def test_returns_seconds_fallback_when_less_than_a_minute(self):
        """Edge case: brand-new login — returns a non-None string."""
        u = self._user()
        u.last_login = timezone.now() - timedelta(seconds=30)
        result = u.tiempo_desde_ultimo_login
        assert result is not None
        assert isinstance(result, str)

    def test_returns_none_when_no_last_login(self):
        u = self._user()
        u.last_login = None
        assert u.tiempo_desde_ultimo_login is None
