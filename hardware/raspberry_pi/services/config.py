"""Configuración del servicio de detección de la Raspberry Pi."""
import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / "config" / ".env")

API_URL = os.getenv("SIAAC_API_URL", "http://127.0.0.1:8000/api/v1")
DEVICE_SERIAL = os.getenv("DEVICE_SERIAL", "RPI-SIAAC-001")
DEVICE_API_KEY = os.getenv("DEVICE_API_KEY", "")
ZONE_ID = int(os.getenv("ZONE_ID", "1"))

CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "1280"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "720"))
FPS = int(os.getenv("FPS", "5"))

YOLO_WEIGHTS = str(BASE_DIR / os.getenv("YOLO_WEIGHTS", "models/siaac_intrusos.pt"))
YOLO_CONFIDENCE = float(os.getenv("YOLO_CONFIDENCE", "0.45"))
YOLO_DEVICE = os.getenv("YOLO_DEVICE", "cpu")
YOLO_CLASSES = [c.strip() for c in os.getenv("YOLO_CLASSES", "person").split(",") if c.strip()]
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "10"))
SAVE_EVIDENCE = os.getenv("SAVE_EVIDENCE", "true").lower() == "true"
EVIDENCE_DIR = BASE_DIR / os.getenv("EVIDENCE_DIR", "evidence")

MQTT_HOST = os.getenv("MQTT_HOST", "127.0.0.1")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC_COMMANDS = os.getenv("MQTT_TOPIC_COMMANDS", f"siaac/zones/{ZONE_ID}/commands")
