"""Pruebas mínimas de humo para validar la configuración del proyecto."""
import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_api_root_schema_disponible(client):
    response = client.get(reverse("schema"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_requiere_credenciales(client):
    response = client.post("/api/v1/auth/token/", {"username": "nadie", "password": "x"})
    assert response.status_code == 401
