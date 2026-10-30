"""Detección automática: dispositivos, modelos y eventos YOLO."""
from django.db.models import Count
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.nucleo.permissions import IsAdminOrReadOnly, IsOperatorOrAdminOrReadOnly

from .models import AIModel, DetectionEvent, Device
from .serializers import (
    AIModelSerializer,
    DetectionEventSerializer,
    DetectionIngestSerializer,
    DeviceSerializer,
)


class DeviceViewSet(viewsets.ModelViewSet):
    queryset = Device.objects.select_related("zone")
    serializer_class = DeviceSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["device_type", "status", "zone"]
    search_fields = ["name", "serial_number", "ip_address"]

    @action(detail=True, methods=["post"])
    def heartbeat(self, request, pk=None):
        device = self.get_object()
        device.status = Device.Status.ONLINE
        device.last_seen = timezone.now()
        device.ip_address = request.data.get("ip_address", device.ip_address)
        device.firmware_version = request.data.get("firmware_version", device.firmware_version)
        device.save(update_fields=["status", "last_seen", "ip_address", "firmware_version", "updated_at"])
        return Response(DeviceSerializer(device).data)


class AIModelViewSet(viewsets.ModelViewSet):
    queryset = AIModel.objects.all()
    serializer_class = AIModelSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["architecture", "is_active"]


class DetectionEventViewSet(viewsets.ModelViewSet):
    queryset = DetectionEvent.objects.select_related("zone", "device", "camera", "ai_model")
    serializer_class = DetectionEventSerializer
    permission_classes = [IsOperatorOrAdminOrReadOnly]
    filterset_fields = ["zone", "device", "object_class", "status"]
    search_fields = ["object_class", "notes"]
    ordering_fields = ["detected_at", "confidence"]

    @action(detail=True, methods=["post"])
    def review(self, request, pk=None):
        event = self.get_object()
        new_status = request.data.get("status", DetectionEvent.Status.VERIFIED)
        if new_status not in DetectionEvent.Status.values:
            return Response({"status": "Estado inválido."}, status=status.HTTP_400_BAD_REQUEST)
        event.status = new_status
        event.notes = request.data.get("notes", event.notes)
        event.reviewed_by = request.user
        event.reviewed_at = timezone.now()
        event.save(update_fields=["status", "notes", "reviewed_by", "reviewed_at", "updated_at"])
        return Response(DetectionEventSerializer(event, context={"request": request}).data)

    @action(detail=False, methods=["get"])
    def statistics(self, request):
        qs = self.get_queryset()
        total = qs.count()
        by_class = list(qs.values("object_class").annotate(total=Count("id")).order_by("-total"))
        return Response({"total": total, "by_class": by_class})


class DetectionIngestView(APIView):
    """Recibe un evento ya inferido por la Raspberry Pi (YOLO)."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = DetectionIngestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        event = serializer.save(detected_at=serializer.validated_data.get("detected_at") or timezone.now())
        return Response(
            DetectionEventSerializer(event, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )
