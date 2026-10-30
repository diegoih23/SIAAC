"""Módulo 3: lecturas de sensores y cámaras en tiempo real."""
from django.db import models

from apps.nucleo.models import TimeStampedModel


class Camera(TimeStampedModel):
    class Status(models.TextChoices):
        ONLINE = "ONLINE", "En línea"
        OFFLINE = "OFFLINE", "Fuera de línea"
        MAINTENANCE = "MAINTENANCE", "Mantenimiento"

    zone = models.ForeignKey(
        "cultivos.Zone", on_delete=models.CASCADE, related_name="cameras"
    )
    name = models.CharField(max_length=120)
    stream_url = models.CharField(max_length=500, help_text="URL RTSP / HTTP del stream")
    has_night_vision = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE)
    last_frame_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "camaras"
        verbose_name = "Cámara"
        verbose_name_plural = "Cámaras"
        ordering = ["zone", "name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.zone.code})"


class SensorReading(TimeStampedModel):
    class SensorType(models.TextChoices):
        PIR = "PIR", "Movimiento PIR"
        TEMPERATURE = "TEMP", "Temperatura"
        HUMIDITY = "HUM", "Humedad"
        SOIL_MOISTURE = "SOIL", "Humedad del suelo"
        LIGHT = "LIGHT", "Luminosidad"

    zone = models.ForeignKey(
        "cultivos.Zone", on_delete=models.CASCADE, related_name="sensor_readings"
    )
    device = models.ForeignKey(
        "deteccion.Device", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="readings",
    )
    sensor_type = models.CharField(max_length=10, choices=SensorType.choices, db_index=True)
    value = models.FloatField()
    unit = models.CharField(max_length=20, blank=True)
    recorded_at = models.DateTimeField(db_index=True)
    raw_payload = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "lecturas_sensor"
        verbose_name = "Lectura de sensor"
        verbose_name_plural = "Lecturas de sensores"
        ordering = ["-recorded_at"]
        indexes = [
            models.Index(fields=["zone", "sensor_type", "-recorded_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_sensor_type_display()}: {self.value}{self.unit}"
