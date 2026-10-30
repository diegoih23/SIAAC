"""Envío de comandos disuasivos al ESP32 (MQTT o HTTP local)."""
import json
import logging

from django.conf import settings
from django.utils import timezone

from .models import DisuasionActivation

logger = logging.getLogger(__name__)


def build_command(rule) -> dict:
    return {
        "action": rule.action,
        "duration_seconds": rule.duration_seconds,
        "zone_id": rule.zone_id,
        "timestamp": timezone.now().isoformat(),
    }


def dispatch_activation(rule, event=None, user=None) -> DisuasionActivation:
    activation = DisuasionActivation.objects.create(
        rule=rule,
        event=event,
        device=event.device if event else None,
        command=build_command(rule),
        triggered_by=user,
    )
    topic = f"siaac/zones/{rule.zone_id}/commands"
    try:
        import paho.mqtt.publish as mqtt_publish

        mqtt_publish.single(
            topic,
            payload=json.dumps(activation.command),
            hostname=settings.MQTT_BROKER_HOST,
            port=settings.MQTT_BROKER_PORT,
            qos=1,
        )
        activation.status = DisuasionActivation.Status.SENT
    except Exception as exc:  # broker no disponible en desarrollo
        logger.warning("No se pudo publicar el comando MQTT: %s", exc)
        activation.status = DisuasionActivation.Status.FAILED
        activation.response = str(exc)
    activation.save(update_fields=["status", "response", "updated_at"])
    return activation


def evaluate_rules(event) -> list[DisuasionActivation]:
    """Evalúa las reglas activas de la zona contra un evento de detección."""
    activations = []
    rules = event.zone.disuasive_rules.filter(is_active=True)
    for rule in rules:
        if rule.trigger_classes and event.object_class not in rule.trigger_classes:
            continue
        if event.confidence < rule.min_confidence:
            continue
        activations.append(dispatch_activation(rule, event))
    return activations
