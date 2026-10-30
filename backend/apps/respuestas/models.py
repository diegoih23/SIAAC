"""Módulo 5: reglas de activación de sirena, luces y respuestas del prototipo."""
from django.conf import settings
from django.db import models

from apps.nucleo.models import TimeStampedModel


class DisuasiveRule(TimeStampedModel):
    class Action(models.TextChoices):
        SIREN = "SIREN", "Bocina / sirena"
        LIGHT = "LIGHT", "Iluminación disuasiva"
        BOTH = "BOTH", "Sirena + luces"

    name = models.CharField(max_length=120)
    zone = models.ForeignKey(
        "cultivos.Zone", on_delete=models.CASCADE, related_name="disuasive_rules"
    )
    trigger_classes = models.JSONField(
        default=list, help_text="Clases YOLO que activan la respuesta, ej. ['person','dog']"
    )
    min_confidence = models.FloatField(default=0.60)
    start_time = models.TimeField(null=True, blank=True, help_text="Inicio de la ventana horaria")
    end_time = models.TimeField(null=True, blank=True, help_text="Fin de la ventana horaria")
    action = models.CharField(max_length=10, choices=Action.choices, default=Action.BOTH)
    duration_seconds = models.PositiveIntegerField(default=15)
    is_active = models.BooleanField(default=True, db_index=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="disuasive_rules",
    )

    class Meta:
        db_table = "reglas_disuasion"
        verbose_name = "Regla disuasiva"
        verbose_name_plural = "Reglas disuasivas"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} - {self.get_action_display()}"


class DisuasionActivation(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        SENT = "SENT", "Enviada"
        EXECUTED = "EXECUTED", "Ejecutada"
        FAILED = "FAILED", "Fallida"

    rule = models.ForeignKey(
        DisuasiveRule, on_delete=models.SET_NULL, null=True, related_name="activations"
    )
    event = models.ForeignKey(
        "deteccion.DetectionEvent", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="disuasion_activations",
    )
    device = models.ForeignKey(
        "deteccion.Device", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="disuasion_activations",
    )
    command = models.JSONField(default=dict)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    response = models.TextField(blank=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="disuasion_activations",
    )

    class Meta:
        db_table = "activaciones_disuasion"
        verbose_name = "Activación disuasiva"
        verbose_name_plural = "Activaciones disuasivas"
        ordering = ["-started_at"]

    def __str__(self) -> str:
        return f"{self.rule} @ {self.started_at:%Y-%m-%d %H:%M:%S}"
