import pytest
from django.core import mail
from django.utils import timezone

from apps.autenticacion.models import User
from apps.cultivos.models import Crop, Zone
from apps.deteccion.models import DetectionEvent


@pytest.mark.django_db
def test_deteccion_crea_notificacion_in_app_y_correo_para_admin():
    admin = User.objects.create_user(
        username="admin-notificaciones",
        email="admin-notificaciones@siaac.test",
        password="ClaveSegura123!",
        role=User.Role.ADMIN,
        is_email_verified=True,
    )
    crop = Crop.objects.create(name="Cultivo notificaciones", owner=admin)
    zone = Zone.objects.create(name="Zona notificaciones", code="NOTIF-01", crop=crop)

    event = DetectionEvent.objects.create(
        zone=zone,
        object_class="horse",
        confidence=0.91,
        bbox=[1, 2, 30, 40],
        detected_at=timezone.now(),
    )

    assert event.notifications.filter(user=admin).count() == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == [admin.email]
    assert "horse" in mail.outbox[0].subject
