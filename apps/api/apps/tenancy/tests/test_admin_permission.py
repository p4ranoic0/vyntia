"""Tests for the IsVyntiaStaff permission class."""

import pytest
from django.test import RequestFactory
from rest_framework.test import APIClient

from api.admin.permissions import IsVyntiaStaff


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def regular_user(django_user_model):
    return django_user_model.objects.create_user(
        username="maria", email="maria@a.com", password="x"
    )


@pytest.mark.django_db
class TestIsVyntiaStaffPermission:
    def test_anonymous_denied(self):
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        from django.contrib.auth.models import AnonymousUser
        request.user = AnonymousUser()
        assert permission.has_permission(request, None) is False

    def test_regular_user_denied(self, regular_user):
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        request.user = regular_user
        assert permission.has_permission(request, None) is False

    def test_vyntia_staff_allowed(self, staff_user):
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        request.user = staff_user
        assert permission.has_permission(request, None) is True

    def test_user_with_is_staff_but_not_vyntia_staff_denied(self, regular_user):
        """Django's `is_staff` is unrelated — only `is_vyntia_staff` counts."""
        regular_user.is_staff = True
        regular_user.save()
        permission = IsVyntiaStaff()
        request = RequestFactory().get("/")
        request.user = regular_user
        assert permission.has_permission(request, None) is False
