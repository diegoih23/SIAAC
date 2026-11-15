"""Cliente HTTP para enviar detecciones y lecturas al backend SIAAC."""
import logging
from datetime import datetime, timezone

import requests

from config import API_URL, DEVICE_API_KEY, DEVICE_SERIAL, ZONE_ID

logger = logging.getLogger(__name__)
HEADERS = {"X-Device-Key": DEVICE_API_KEY}


def send_detection(object_class: str, confidence: float, bbox: list, image_path: str | None) -> dict | None:
    payload = {
        "device_serial": DEVICE_SERIAL,
        "zone": ZONE_ID,
        "object_class": object_class,
        "confidence": round(confidence, 4),
        "bbox": bbox,
        "detected_at": datetime.now(timezone.utc).isoformat(),
    }
    files = None
    if image_path:
        files = {"image": open(image_path, "rb")}  # noqa: SIM115
    try:
        response = requests.post(
            f"{API_URL}/detection/events/ingest/",
            data=payload,
            files=files,
            headers=HEADERS,
            timeout=15,
        )
        response.raise_for_status()
        logger.info("Evento enviado: %s (%.2f)", object_class, confidence)
        return response.json()
    except requests.RequestException as exc:
        logger.error("Error enviando detección: %s", exc)
        return None
    finally:
        if files:
            files["image"].close()


def send_photo_for_analysis(image_path: str) -> dict | None:
    """Envía una fotografía para que el backend ejecute YOLO."""
    try:
        with open(image_path, "rb") as image:
            response = requests.post(
                f"{API_URL}/detection/events/ingest/",
                data={
                    "device_serial": DEVICE_SERIAL,
                    "zone": ZONE_ID,
                    "detected_at": datetime.now(timezone.utc).isoformat(),
                },
                files={"image": (image_path.rsplit("/", 1)[-1], image, "image/jpeg")},
                headers=HEADERS,
                timeout=30,
            )
        response.raise_for_status()
        logger.info("Fotografía enviada para análisis: %s", image_path)
        return response.json()
    except (OSError, requests.RequestException) as exc:
        logger.error("Error enviando fotografía: %s", exc)
        return None


def send_sensor(sensor_type: str, value: float, unit: str = "") -> None:
    try:
        requests.post(
            f"{API_URL}/monitoring/readings/ingest/",
            json={
                "zone": ZONE_ID,
                "sensor_type": sensor_type,
                "value": value,
                "unit": unit,
                "recorded_at": datetime.now(timezone.utc).isoformat(),
            },
            headers=HEADERS,
            timeout=10,
        ).raise_for_status()
    except requests.RequestException as exc:
        logger.warning("No se pudo enviar la lectura %s: %s", sensor_type, exc)
