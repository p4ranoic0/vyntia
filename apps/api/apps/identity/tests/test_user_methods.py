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


@pytest.mark.django_db
class TestUsuarioManagerActivos:
    def test_activos_returns_only_users_with_is_active_true_and_estado_activo(self):
        from apps.identity.models import User

        u_active = User(username="active_um", email="a@a.local", is_active=True, estado_usuario="activo")
        u_active.set_password("x")
        u_active.save()

        u_blocked = User(username="blocked_um", email="b@b.local", is_active=True, estado_usuario="bloqueado")
        u_blocked.set_password("x")
        u_blocked.save()

        u_disabled = User(username="off_um", email="o@o.local", is_active=False, estado_usuario="inactivo")
        u_disabled.set_password("x")
        u_disabled.save()

        active_set = set(User.objects.activos().values_list("username", flat=True))
        assert "active_um" in active_set
        assert "blocked_um" not in active_set
        assert "off_um" not in active_set

    def test_inactivos_excludes_active_users(self):
        from apps.identity.models import User

        u_active = User(username="ux_um", email="ux@ux.local", is_active=True, estado_usuario="activo")
        u_active.set_password("x")
        u_active.save()

        u_off = User(username="ox_um", email="ox@ox.local", is_active=False, estado_usuario="inactivo")
        u_off.set_password("x")
        u_off.save()

        inactive_set = set(User.objects.inactivos().values_list("username", flat=True))
        assert "ux_um" not in inactive_set
        assert "ox_um" in inactive_set


@pytest.mark.django_db
class TestUsuarioManagerPorRol:
    def test_por_rol_returns_users_with_active_role_assignment(self):
        """por_rol must traverse the UserRole pivot, not a non-existent direct rel."""
        from apps.identity.models import User, Role
        from apps.identity.models.rbac import UserRole

        rol = Role.objects.create(nombre_rol="TestRole_PR", estado_rol="activo")

        u_with = User(username="with_role_pr", email="wr@local", is_active=True, estado_usuario="activo")
        u_with.set_password("x")
        u_with.save()
        UserRole.objects.create(usuario=u_with, rol=rol, estado_asignacion="activo")

        u_without = User(username="without_role_pr", email="wo@local", is_active=True, estado_usuario="activo")
        u_without.set_password("x")
        u_without.save()

        usernames = set(User.objects.por_rol("TestRole_PR").values_list("username", flat=True))
        assert "with_role_pr" in usernames
        assert "without_role_pr" not in usernames
