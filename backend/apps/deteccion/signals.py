"""Difusión en vivo de eventos y generación de notificaciones."""
from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.monitoreo.services import broadcast_global, broadcast_to_zone
from apps.notificaciones.services import notify_detection

from .models import DetectionEvent, Device


@receiver(post_save, sender=DetectionEvent)
def on_detection_event(sender, instance: DetectionEvent, created: bool, **kwargs):
    if not created:
        return
    payload = {
        "id": instance.id,
        "zone": instance.zone_id,
        "zone_name": instance.zone.name,
        "object_class": instance.object_class,
        "confidence": instance.confidence,
        "detected_at": instance.detected_at.isoformat(),
        "status": instance.status,
    }
    broadcast_to_zone(instance.zone_id, "detection.event", payload)
    broadcast_global("detection.event", payload)
    notify_detection(instance)

    # Respuesta disuasiva automática según las reglas activas de la zona.
    try:
        from apps.respuestas.services import evaluate_rules

        activations = evaluate_rules(instance)
        if activations:
            DetectionEvent.objects.filter(pk=instance.pk).update(disuasion_triggered=True)
    except Exception:  # el fallo de MQTT no debe perder el evento
        import logging

        logging.getLogger(__name__).exception("Error evaluando reglas disuasivas")


@receiver(post_save, sender=Device)
def on_device_saved(sender, instance: Device, created: bool, **kwargs):
    if created:
        broadcast_global("device.registered", {"id": instance.id, "name": instance.name})
