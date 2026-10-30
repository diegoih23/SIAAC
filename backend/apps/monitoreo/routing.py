from django.urls import path

from .consumers import GlobalMonitoringConsumer, ZoneConsumer

websocket_urlpatterns = [
    path("ws/monitoring/", GlobalMonitoringConsumer.as_asgi()),
    path("ws/monitoring/zones/<int:zone_id>/", ZoneConsumer.as_asgi()),
]
