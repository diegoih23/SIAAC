"""Autenticación JWT para conexiones WebSocket.

El frontend envía el access token como query string:
    ws://host/ws/notifications/?token=<access>
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import AccessToken

User = get_user_model()


@database_sync_to_async
def _get_user(token: str):
    try:
        access = AccessToken(token)
        return User.objects.get(id=access["user_id"], is_active=True)
    except (TokenError, KeyError, User.DoesNotExist):
        return AnonymousUser()


class JWTAuthMiddleware:
    """Sobrescribe el usuario de la sesión si hay un token válido en la URL."""

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query = parse_qs(scope.get("query_string", b"").decode())
        token = query.get("token", [None])[0]
        if token:
            scope["user"] = await _get_user(token)
        return await self.inner(scope, receive, send)
