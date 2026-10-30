"""Módulo 4: reportes históricos y supervisión."""
from django.conf import settings
from django.db import models

from apps.nucleo.models import TimeStampedModel


class Report(TimeStampedModel):
    class Type(models.TextChoices):
        DETECTIONS = "DETECTIONS", "Eventos de detección"
        SENSORS = "SENSORS", "Lecturas de sensores"
        DISUASION = "DISUASION", "Activaciones disuasivas"
        GENERAL = "GENERAL", "Resumen general"

    class Format(models.TextChoices):
        PDF = "PDF", "PDF"
        CSV = "CSV", "CSV"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        READY = "READY", "Listo"
        FAILED = "FAILED", "Fallido"

    title = models.CharField(max_length=160)
    report_type = models.CharField(max_length=20, choices=Type.choices, default=Type.GENERAL)
    format = models.CharField(max_length=5, choices=Format.choices, default=Format.PDF)
    zone = models.ForeignKey(
        "cultivos.Zone", on_delete=models.SET_NULL, null=True, blank=True, related_name="reports"
    )
    period_start = models.DateTimeField()
    period_end = models.DateTimeField()
    parameters = models.JSONField(default=dict, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    file = models.FileField(upload_to="reports/%Y/%m/", null=True, blank=True)
    error_message = models.TextField(blank=True)
    generated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="reports",
    )

    class Meta:
        db_table = "reportes"
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.title} ({self.format})"
