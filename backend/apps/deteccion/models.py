"""Detección automática: dispositivos de hardware, modelos YOLO y eventos."""
from django.conf import settings
from django.db import models

from apps.nucleo.models import TimeStampedModel
from apps.nucleo.utils import generate_device_token


class Device(TimeStampedModel):
    class Type(models.TextChoices):
        ESP32 = "ESP32", "ESP32"
        RASPBERRY_PI = "RPI", "Raspberry Pi"
        CAMERA = "CAMERA", "Cámara IP"

    class Status(models.TextChoices):
        ONLINE = "ONLINE", "En línea"
        OFFLINE = "OFFLINE", "Fuera de línea"
        ERROR = "ERROR", "Con fallas"

    name = models.CharField(max_length=120)
    device_type = models.CharField(max_length=10, choices=Type.choices)
    serial_number = models.CharField(max_length=80, unique=True)
    zone = models.ForeignKey(
        "cultivos.Zone", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="devices",
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    api_key = models.CharField(max_length=64, unique=True, default=generate_device_token)
    firmware_version = models.CharField(max_length=40, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OFFLINE)
    last_seen = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        db_table = "dispositivos"
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} [{self.get_device_type_display()}]"


class AIModel(TimeStampedModel):
    name = models.CharField(max_length=120)
    version = models.CharField(max_length=40)
    architecture = models.CharField(max_length=40, default="YOLO11")
    weights_path = models.CharField(max_length=500)
    confidence_threshold = models.FloatField(default=0.45)
    iou_threshold = models.FloatField(default=0.50)
    classes = models.JSONField(default=list, blank=True, help_text="Clases entrenadas")
    is_active = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = "modelos_ia"
        verbose_name = "Modelo de IA"
        verbose_name_plural = "Modelos de IA"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["name", "version"], name="uniq_model_version"),
        ]

    def __str__(self) -> str:
        return f"{self.name} v{self.version}"


class DetectionEvent(TimeStampedModel):
    class Status(models.TextChoices):
        NEW = "NEW", "Nuevo"
        VERIFIED = "VERIFIED", "Verificado"
        FALSE_POSITIVE = "FALSE_POSITIVE", "Falso positivo"
        ATTENDED = "ATTENDED", "Atendido"

    zone = models.ForeignKey(
        "cultivos.Zone", on_delete=models.CASCADE, related_name="detection_events"
    )
    device = models.ForeignKey(
        Device, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="events",
    )
    camera = models.ForeignKey(
        "monitoreo.Camera", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="events",
    )
    ai_model = models.ForeignKey(
        AIModel, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="events",
    )
    object_class = models.CharField(max_length=80, db_index=True)
    confidence = models.FloatField()
    bbox = models.JSONField(default=list, help_text="[x1, y1, x2, y2]")
    image = models.ImageField(upload_to="detections/%Y/%m/%d/", null=True, blank=True)
    detected_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW)
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reviewed_events",
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    disuasion_triggered = models.BooleanField(default=False)

    class Meta:
        db_table = "eventos_deteccion"
        verbose_name = "Evento de detección"
        verbose_name_plural = "Eventos de detección"
        ordering = ["-detected_at"]
        indexes = [
            models.Index(fields=["zone", "-detected_at"]),
            models.Index(fields=["object_class", "-detected_at"]),
        ]

    def __str__(self) -> str:
        return f"{self.object_class} ({self.confidence:.0%}) - {self.zone.code}"
