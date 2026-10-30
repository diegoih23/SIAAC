"""WebSockets del Módulo 3: lecturas y estado de una zona."""
import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ZoneConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.zone_id = self.scope["url_route"]["kwargs"]["zone_id"]
        self.group_name = f"zone_{self.zone_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()
        await self.send(json.dumps({"event": "connected", "zone": self.zone_id}))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        if text_data == "ping":
            await self.send(json.dumps({"event": "pong"}))

    async def zone_event(self, event):
        await self.send(json.dumps({
            "event": event["event"],
            "payload": event["payload"],
        }))


class GlobalMonitoringConsumer(AsyncWebsocketConsumer):
    """Canal global para el tablero de monitoreo (todas las zonas)."""

    async def connect(self):
        if not self.scope["user"].is_authenticated:
            await self.close()
            return
        await self.channel_layer.group_add("monitoring", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("monitoring", self.channel_name)

    async def zone_event(self, event):
        await self.send(json.dumps({"event": event["event"], "payload": event["payload"]}))
