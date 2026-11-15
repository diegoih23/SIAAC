"""Detección automática: dispositivos, modelos y eventos YOLO."""
import time

import cv2
import numpy as np
from django.core.files.base import ContentFile
from django.db import transaction
from django.db.models import Count
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.nucleo.permissions import IsAdminOrReadOnly, IsOperatorOrAdminOrReadOnly
from apps.cultivos.models import Zone
from ml.yolo.detector import get_detector

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
    """Recibe una detección inferida o una fotografía para inferirla con YOLO."""

    permission_classes = [AllowAny]
    parser_classes = [JSONParser, MultiPartParser, FormParser]

    def post(self, request):
        if request.FILES.get("image") and not request.data.get("object_class"):
            return self._infer_photo(request)
        serializer = DetectionIngestSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        event = serializer.save(detected_at=serializer.validated_data.get("detected_at") or timezone.now())
        return Response(
            DetectionEventSerializer(event, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    def _infer_photo(self, request):
        uploaded = request.FILES["image"]
        raw = uploaded.read()
        frame = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return Response({"image": "El archivo no es una imagen válida."}, status=400)

        serial = str(request.data.get("device_serial", "")).strip()
        key = request.headers.get("X-Device-Key")
        device = Device.objects.filter(serial_number=serial, api_key=key).first()
        if not device:
            return Response({"device_serial": "Dispositivo o API key inválidos."}, status=401)
        zone_id = request.data.get("zone") or device.zone_id
        if not zone_id:
            return Response({"zone": "El dispositivo debe estar asociado a una zona."}, status=400)
        if not Zone.objects.filter(pk=zone_id, is_deleted=False).exists():
            return Response({"zone": "La zona no existe o está eliminada."}, status=400)
        if device.zone_id and str(device.zone_id) != str(zone_id):
            return Response({"zone": "La zona no coincide con la zona del dispositivo."}, status=400)

        try:
            detections = get_detector().predict(frame)
        except (FileNotFoundError, ModuleNotFoundError, ImportError):
            return Response(
                {"detail": "El modelo YOLO no está disponible."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        created = []
        detected_at = parse_datetime(str(request.data.get("detected_at", ""))) or timezone.now()
        with transaction.atomic():
            for index, detection in enumerate(detections):
                event = DetectionEvent.objects.create(
                    zone_id=zone_id,
                    device=device,
                    object_class=detection["object_class"],
                    confidence=detection["confidence"],
                    bbox=detection["bbox"],
                    image=ContentFile(raw, name=f"{uploaded.name or 'captura'}-{index}.jpg"),
                    detected_at=detected_at,
                )
                created.append(event)

        return Response({
            "created": len(created),
            "detections": DetectionEventSerializer(
                created, many=True, context={"request": request}
            ).data,
        }, status=status.HTTP_201_CREATED)


class DetectionAnalyzeView(APIView):
    """Analiza una imagen con YOLO + OpenCV sin crear todavía un evento."""

    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        uploaded = request.FILES.get("image")
        if not uploaded:
            return Response(
                {"image": "Debes adjuntar una imagen."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if uploaded.size > 10 * 1024 * 1024:
            return Response(
                {"image": "La imagen no puede superar 10 MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        raw = uploaded.read()
        frame = cv2.imdecode(np.frombuffer(raw, dtype=np.uint8), cv2.IMREAD_COLOR)
        if frame is None:
            return Response(
                {"image": "El archivo no es una imagen válida."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        started = time.perf_counter()
        try:
            detections = get_detector().predict(frame)
        except (FileNotFoundError, ModuleNotFoundError, ImportError) as exc:
            return Response(
                {"detail": "El modelo YOLO no está disponible. Configura sus pesos en ml/yolo/weights/."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )
        elapsed_ms = round((time.perf_counter() - started) * 1000, 2)
        return Response({
            "detections": detections,
            "count": len(detections),
            "processing_time_ms": elapsed_ms,
            "image_width": int(frame.shape[1]),
            "image_height": int(frame.shape[0]),
        })
