"""Módulo 1: usuarios, roles y trazabilidad de sesiones."""
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.nucleo.models import TimeStampedModel


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Administrador"
        OPERATOR = "OPERATOR", "Operador"
        VIEWER = "VIEWER", "Consulta"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    is_email_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-date_joined"]

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.username} ({self.role})"

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser


class UserSession(TimeStampedModel):
    """Sesión activa/inactiva para auditoría y cierre remoto."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sessions")
    refresh_jti = models.CharField(max_length=64, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    device_label = models.CharField(max_length=120, blank=True)
    login_at = models.DateTimeField(auto_now_add=True)
    logout_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        db_table = "sesiones_usuario"
        verbose_name = "Sesión de usuario"
        verbose_name_plural = "Sesiones de usuario"
        ordering = ["-login_at"]

    def __str__(self) -> str:
        return f"{self.user.username} @ {self.login_at:%Y-%m-%d %H:%M}"
