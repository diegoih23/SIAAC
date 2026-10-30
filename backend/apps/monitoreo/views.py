"""Módulo 3: consulta de lecturas, cámaras e ingesta desde hardware."""
from django.conf import settings
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.nucleo.permissions import IsAdminOrReadOnly

from .models import Camera, SensorReading
from .serializers import CameraSerializer, SensorReadingSerializer
from .services import broadcast_to_zone


class CameraViewSet(viewsets.ModelViewSet):
    queryset = Camera.objects.select_related("zone")
    serializer_class = CameraSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["zone", "status", "has_night_vision"]

    @action(detail=True, methods=["post"])
    def snapshot(self, request, pk=None):
        camera = self.get_object()
        # La captura real la realiza el servicio de la Raspberry Pi.
        return Response({"detail": f"Captura solicitada a {camera.name}."}, status=202)


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = SensorReading.objects.select_related("zone", "device")
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["zone", "device", "sensor_type"]
    ordering_fields = ["recorded_at", "value"]

    @action(detail=False, methods=["get"])
    def latest(self, request):
        zone_id = request.query_params.get("zone")
        qs = self.get_queryset()
        if zone_id:
            qs = qs.filter(zone_id=zone_id)
        seen, result = set(), []
        for reading in qs.order_by("zone_id", "sensor_type", "-recorded_at"):
            key = (reading.zone_id, reading.sensor_type)
            if key not in seen:
                seen.add(key)
                result.append(SensorReadingSerializer(reading).data)
        return Response(result)


class SensorIngestView(APIView):
    """Endpoint para que ESP32 / Raspberry Pi envíen lecturas."""

    permission_classes = [AllowAny]

    def post(self, request):
        api_key = request.headers.get("X-Device-Key", "")
        if api_key != settings.DEVICE_API_KEY:
            return Response({"detail": "Dispositivo no autorizado."}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = SensorReadingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reading = serializer.save(recorded_at=serializer.validated_data.get("recorded_at") or timezone.now())
        broadcast_to_zone(reading.zone_id, "sensor.reading", SensorReadingSerializer(reading).data)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
