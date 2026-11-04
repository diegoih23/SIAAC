"""Módulo 1: usuarios, roles y trazabilidad de sesiones."""
from django.contrib.auth.models import AbstractUser
from django.conf import settings
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
    failed_login_attempts = models.PositiveSmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    two_factor_enabled = models.BooleanField(default=False)

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


class PasswordResetCode(TimeStampedModel):
    """Código OTP de recuperación de contraseña con expiración y límite de intentos."""

    email = models.EmailField(db_index=True)
    code_hash = models.CharField(max_length=128)
    reset_token = models.UUIDField(unique=True)
    expires_at = models.DateTimeField(db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    is_verified = models.BooleanField(default=False)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "codigos_recuperacion"
        verbose_name = "Código de recuperación"
        verbose_name_plural = "Códigos de recuperación"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"OTP {self.email} ({self.expires_at:%H:%M})"


class AccessAttempt(TimeStampedModel):
    """Auditoría de accesos exitosos y fallidos."""

    username = models.CharField(max_length=150, db_index=True)
    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="access_attempts"
    )
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True)
    successful = models.BooleanField(default=False, db_index=True)
    reason = models.CharField(max_length=80, blank=True)

    class Meta:
        db_table = "intentos_acceso"
        verbose_name = "Intento de acceso"
        verbose_name_plural = "Intentos de acceso"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        state = "exitoso" if self.successful else "fallido"
        return f"{self.username} - {state}"


class TwoFactorChallenge(TimeStampedModel):
    """Desafío OTP temporal generado después de validar la contraseña."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="two_factor_challenges")
    challenge_id = models.UUIDField(unique=True)
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField(db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "desafios_doble_factor"
        verbose_name = "Desafío de doble factor"
        verbose_name_plural = "Desafíos de doble factor"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"2FA {self.user.username} ({self.expires_at:%H:%M})"


class EmailVerificationCode(TimeStampedModel):
    """Código OTP para validar el correo durante el registro."""

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="email_verifications")
    code_hash = models.CharField(max_length=128)
    expires_at = models.DateTimeField(db_index=True)
    attempts = models.PositiveSmallIntegerField(default=0)
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "codigos_verificacion_correo"
        verbose_name = "Código de verificación de correo"
        verbose_name_plural = "Códigos de verificación de correo"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Verificación {self.user.email} ({self.expires_at:%H:%M})"
