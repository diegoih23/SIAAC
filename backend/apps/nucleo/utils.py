"""Funciones auxiliares compartidas."""
import math
import uuid


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia aproximada en metros entre dos coordenadas GPS."""
    radius = 6_371_000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)
    a = math.sin(d_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def generate_device_token() -> str:
    """Token único para emparejar un ESP32 / Raspberry Pi con la plataforma."""
    return uuid.uuid4().hex
