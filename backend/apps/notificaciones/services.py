"""Creación y entrega de notificaciones (in-app, correo y WebSocket)."""
import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification

logger = logging.getLogger(__name__)
User = get_user_model()


def _push_ws(notification: Notification) -> None:
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(
        f"notifications_{notification.user_id}",
        {
            "type": "notification.message",
            "payload": {
                "id": notification.id,
                "title": notification.title,
                "message": notification.message,
                "priority": notification.priority,
                "category": notification.category,
                "created_at": notification.created_at.isoformat(),
            },
        },
    )


def send_notification(user, title, message, *, category=Notification.Category.SYSTEM,
                      priority=Notification.Priority.NORMAL, payload=None,
                      related_event=None) -> Notification:
    notification = Notification.objects.create(
        user=user,
        title=title,
        message=message,
        category=category,
        priority=priority,
        payload=payload or {},
        related_event=related_event,
        sent_at=timezone.now(),
    )
    _push_ws(notification)
    return notification


def notify_detection(event) -> list[Notification]:
    """Notifica a administradores y operadores cuando YOLO detecta un objeto."""
    recipients = User.objects.filter(is_active=True, role__in=["ADMIN", "OPERATOR"])
    priority = (
        Notification.Priority.CRITICAL
        if event.confidence >= 0.85
        else Notification.Priority.HIGH
    )
    notifications = []
    for user in recipients:
        notifications.append(
            send_notification(
                user,
                title=f"Detección: {event.object_class}",
                message=(
                    f"Se detectó {event.object_class} en la zona {event.zone.name} "
                    f"con {event.confidence:.0%} de confianza."
                ),
                category=Notification.Category.DETECTION,
                priority=priority,
                payload={"event_id": event.id, "zone_id": event.zone_id},
                related_event=event,
            )
        )
    return notifications
