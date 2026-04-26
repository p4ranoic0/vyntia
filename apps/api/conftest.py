import os

import django
import pytest

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.testing")
django.setup()


@pytest.fixture
def api_client():
    """Cliente API para tests."""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def user_data():
    """Datos de usuario para tests."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def create_user(db, user_data):
    """Crear usuario para tests."""
    from django.contrib.auth import get_user_model

    user_model = get_user_model()

    def _create_user(**kwargs):
        data = user_data.copy()
        data.update(kwargs)
        return user_model.objects.create_user(**data)

    return _create_user


@pytest.fixture
def authenticated_client(api_client, create_user):
    """Cliente autenticado para tests de API."""
    user = create_user()
    api_client.force_authenticate(user=user)
    return api_client, user
    return api_client, user
