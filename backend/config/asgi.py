"""Punto de entrada ASGI: HTTP + WebSocket para monitoreo en tiempo real."""
import os

from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django_asgi_app = get_asgi_application()

from channels.auth import AuthMiddlewareStack  # noqa: E402
from channels.routing import ProtocolTypeRouter, URLRouter  # noqa: E402
from channels.security.websocket import AllowedHostsOriginValidator  # noqa: E402

from apps.nucleo.ws_auth import JWTAuthMiddleware  # noqa: E402
from apps.monitoreo.routing import websocket_urlpatterns as monitoreo_ws  # noqa: E402
from apps.notificaciones.routing import websocket_urlpatterns as notificaciones_ws  # noqa: E402

jwt_stack = AuthMiddlewareStack(
    JWTAuthMiddleware(URLRouter(monitoreo_ws + notificaciones_ws))
)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(jwt_stack),
    }
)
