"""Módulo 6: notificaciones multicanal y preferencias por usuario."""
from django.conf import settings
from django.db import models

from apps.nucleo.models import TimeStampedModel


class Notification(TimeStampedModel):
    class Channel(models.TextChoices):
        IN_APP = "IN_APP", "En la aplicación"
        EMAIL = "EMAIL", "Correo electrónico"
        PUSH = "PUSH", "Notificación push"
        SMS = "SMS", "SMS"

    class Category(models.TextChoices):
        DETECTION = "DETECTION", "Detección"
        DISUASION = "DISUASION", "Respuesta disuasiva"
        DEVICE = "DEVICE", "Dispositivo"
        REPORT = "REPORT", "Reporte"
        SYSTEM = "SYSTEM", "Sistema"

    class Priority(models.TextChoices):
        LOW = "LOW", "Baja"
        NORMAL = "NORMAL", "Normal"
        HIGH = "HIGH", "Alta"
        CRITICAL = "CRITICAL", "Crítica"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=160)
    message = models.TextField()
    channel = models.CharField(max_length=10, choices=Channel.choices, default=Channel.IN_APP)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.SYSTEM)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.NORMAL)
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    payload = models.JSONField(default=dict, blank=True)
    related_event = models.ForeignKey(
        "deteccion.DetectionEvent", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="notifications",
    )

    class Meta:
        db_table = "notificaciones"
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "is_read", "-created_at"])]

    def __str__(self) -> str:
        return f"{self.title} -> {self.user.username}"


class NotificationPreference(TimeStampedModel):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_preferences"
    )
    category = models.CharField(max_length=20, choices=Notification.Category.choices)
    channel = models.CharField(max_length=10, choices=Notification.Channel.choices)
    enabled = models.BooleanField(default=True)
    quiet_hours_start = models.TimeField(null=True, blank=True)
    quiet_hours_end = models.TimeField(null=True, blank=True)

    class Meta:
        db_table = "preferencias_notificacion"
        verbose_name = "Preferencia de notificación"
        verbose_name_plural = "Preferencias de notificación"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "category", "channel"], name="uniq_user_category_channel"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.user.username}: {self.category}/{self.channel}"
