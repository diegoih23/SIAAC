import io
from unittest.mock import patch

import pytest
from PIL import Image
from rest_framework.test import APIClient

from apps.autenticacion.models import User


def image_file():
    image = Image.new("RGB", (40, 40), color="white")
    stream = io.BytesIO()
    image.save(stream, format="JPEG")
    stream.seek(0)
    stream.name = "captura.jpg"
    return stream


@pytest.mark.django_db
def test_analizar_imagen_con_yolo_y_opencv():
    user = User.objects.create_user(
        username="analista",
        password="ClaveSegura123!",
        role=User.Role.ADMIN,
        is_email_verified=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    fake_detections = [{
        "class_id": 19,
        "object_class": "horse",
        "confidence": 0.94,
        "bbox": [1.0, 2.0, 30.0, 35.0],
    }]

    with patch("apps.deteccion.views.get_detector") as detector_factory:
        detector_factory.return_value.predict.return_value = fake_detections
        response = client.post(
            "/api/v1/detection/events/analyze/",
            {"image": image_file()},
            format="multipart",
        )

    assert response.status_code == 200
    assert response.data["count"] == 1
    assert response.data["detections"][0]["object_class"] == "horse"


@pytest.mark.django_db
def test_analizar_rechaza_archivo_que_no_es_imagen():
    user = User.objects.create_user(
        username="analista-invalido",
        password="ClaveSegura123!",
        role=User.Role.ADMIN,
        is_email_verified=True,
    )
    client = APIClient()
    client.force_authenticate(user=user)
    response = client.post(
        "/api/v1/detection/events/analyze/",
        {"image": io.BytesIO(b"no es una imagen")},
        format="multipart",
    )
    assert response.status_code == 400
    assert "image" in response.data
