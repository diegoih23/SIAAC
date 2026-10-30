"""Módulo 2: cultivos, zonas geográficas y responsables."""
from django.conf import settings
from django.db import models

from apps.nucleo.models import SoftDeleteModel, TimeStampedModel


class Crop(TimeStampedModel):
    class Status(models.TextChoices):
        PLANNED = "PLANNED", "Planificado"
        GROWING = "GROWING", "En crecimiento"
        HARVEST = "HARVEST", "En cosecha"
        HARVESTED = "HARVESTED", "Cosechado"

    name = models.CharField(max_length=120, db_index=True)
    scientific_name = models.CharField(max_length=160, blank=True)
    variety = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    planting_date = models.DateField(null=True, blank=True)
    harvest_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.GROWING)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="crops",
    )

    class Meta:
        db_table = "cultivos"
        verbose_name = "Cultivo"
        verbose_name_plural = "Cultivos"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Zone(SoftDeleteModel):
    """Zona o lote monitoreado; concentra dispositivos, eventos y reportes."""

    name = models.CharField(max_length=120, db_index=True)
    code = models.CharField(max_length=40, unique=True)
    crop = models.ForeignKey(
        Crop, on_delete=models.SET_NULL, null=True, blank=True, related_name="zones"
    )
    description = models.TextField(blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    area_m2 = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    responsible = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="zones_in_charge",
    )
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "zonas"
        verbose_name = "Zona"
        verbose_name_plural = "Zonas"
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"
