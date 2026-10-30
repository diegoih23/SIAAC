from django.apps import AppConfig


class DeteccionConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.deteccion"
    verbose_name = "Detección automática - Hardware e IA"

    def ready(self):
        from . import signals  # noqa: F401
