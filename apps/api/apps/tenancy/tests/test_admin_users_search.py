"""Tests for /api/admin/users/?q=<term> search endpoint."""

import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def staff_user(django_user_model):
    user = django_user_model.objects.create_user(
        username="zviera", email="zviera@vyntia.pe", password="x"
    )
    user.is_vyntia_staff = True
    user.save()
    return user


@pytest.fixture
def alice(django_user_model):
    return django_user_model.objects.create_user(
        username="alice", email="alice@example.com", password="x"
    )


@pytest.fixture
def bob(django_user_model):
    return django_user_model.objects.create_user(
        username="bob", email="bob@example.com", password="x"
    )


@pytest.fixture
def client(staff_user):
    c = APIClient()
    c.credentials(HTTP_AUTHORIZATION=f"Bearer {RefreshToken.for_user(staff_user).access_token}")
    return c


@pytest.mark.django_db
class TestUsersSearch:
    def test_returns_all_when_q_empty(self, client, alice, bob):
        response = client.get("/api/admin/users/")
        assert response.status_code == 200
        data = response.json()["data"]
        # alice + bob + staff_user (3)
        assert data["pagination"]["total_items"] == 3

    def test_filters_by_username(self, client, alice, bob):
        response = client.get("/api/admin/users/?q=alice")
        data = response.json()["data"]
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["username"] == "alice"

    def test_filters_by_email(self, client, alice, bob):
        response = client.get("/api/admin/users/?q=bob@")
        data = response.json()["data"]
        assert data["pagination"]["total_items"] == 1
        assert data["results"][0]["email"] == "bob@example.com"

    def test_pagination(self, client, alice, bob):
        response = client.get("/api/admin/users/?page_size=1&page=1")
        data = response.json()["data"]
        assert len(data["results"]) == 1
        assert data["pagination"]["total_pages"] >= 1

    def test_unauthenticated_denied(self):
        c = APIClient()
        response = c.get("/api/admin/users/")
        assert response.status_code == 401
