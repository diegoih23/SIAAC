import pytest
from rest_framework.test import APIClient

from apps.autenticacion.models import User
from apps.cultivos.models import Crop


@pytest.mark.django_db
def test_admin_puede_crear_editar_y_eliminar_cultivo():
    user = User.objects.create_user(
        username="admin-cultivos",
        password="ClaveSegura123!",
        role=User.Role.ADMIN,
        is_email_verified=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post("/api/v1/crops/crops/", {
        "name": "Maíz",
        "variety": "Híbrido",
        "status": "GROWING",
    }, format="json")
    assert response.status_code == 201
    crop = Crop.objects.get(pk=response.data["id"])
    assert crop.owner_id == user.id

    response = client.patch(f"/api/v1/crops/crops/{crop.id}/", {
        "description": "Lote norte",
        "status": "HARVEST",
    }, format="json")
    assert response.status_code == 200
    crop.refresh_from_db()
    assert crop.status == "HARVEST"

    response = client.delete(f"/api/v1/crops/crops/{crop.id}/")
    assert response.status_code == 204


@pytest.mark.django_db
def test_operador_no_puede_modificar_cultivos():
    user = User.objects.create_user(
        username="operador-cultivos",
        password="ClaveSegura123!",
        role=User.Role.OPERATOR,
        is_email_verified=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.post("/api/v1/crops/crops/", {
        "name": "Café",
        "status": "GROWING",
    }, format="json")
    assert response.status_code == 403
