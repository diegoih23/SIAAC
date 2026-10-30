"""Publicación de datos en tiempo real a los WebSocket del frontend."""
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def broadcast_to_zone(zone_id: int, event_type: str, payload: dict) -> None:
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(
        f"zone_{zone_id}",
        {"type": "zone.event", "event": event_type, "payload": payload},
    )


def broadcast_global(event_type: str, payload: dict) -> None:
    layer = get_channel_layer()
    if layer is None:
        return
    async_to_sync(layer.group_send)(
        "monitoring",
        {"type": "zone.event", "event": event_type, "payload": payload},
    )
