import pytest
from rest_framework.test import APIClient

from apps.autenticacion.models import User
from apps.cultivos.models import Crop, Zone


@pytest.mark.django_db
def test_admin_puede_gestionar_zona_y_se_elimina_suavemente():
    user = User.objects.create_user(
        username="admin-zonas",
        password="ClaveSegura123!",
        role=User.Role.ADMIN,
        is_email_verified=True,
    )
    crop = Crop.objects.create(name="Maíz", owner=user)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post("/api/v1/crops/zones/", {
        "name": "Lote norte",
        "code": " z-01 ",
        "crop": crop.id,
        "latitude":  -4.001,
        "longitude": -79.201,
        "area_m2": 250,
    }, format="json")
    assert response.status_code == 201
    zone = Zone.objects.get(pk=response.data["id"])
    assert zone.code == "Z-01"

    response = client.patch(f"/api/v1/crops/zones/{zone.id}/", {
        "is_active": False,
        "description": "Zona deshabilitada",
    }, format="json")
    assert response.status_code == 200
    zone.refresh_from_db()
    assert zone.is_active is False

    response = client.delete(f"/api/v1/crops/zones/{zone.id}/")
    assert response.status_code == 204
    zone.refresh_from_db()
    assert zone.is_deleted is True


@pytest.mark.django_db
def test_zona_rechaza_coordenadas_invalidas():
    user = User.objects.create_user(
        username="admin-validacion",
        password="ClaveSegura123!",
        role=User.Role.ADMIN,
        is_email_verified=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post("/api/v1/crops/zones/", {
        "name": "Zona inválida",
        "code": "Z-99",
        "latitude": 100,
    }, format="json")
    assert response.status_code == 400
    assert "latitude" in response.data
