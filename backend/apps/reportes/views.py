"""Módulo 4: generación de reportes y tablero de supervisión."""
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.cultivos.models import Crop, Zone
from apps.deteccion.models import DetectionEvent, Device
from apps.respuestas.models import DisuasionActivation
from apps.notificaciones.models import Notification

from .models import Report
from .serializers import ReportSerializer
from .services import generate_report


class ReportViewSet(viewsets.ModelViewSet):
    queryset = Report.objects.select_related("zone", "generated_by")
    serializer_class = ReportSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["report_type", "format", "status", "zone"]
    ordering_fields = ["created_at"]

    def perform_create(self, serializer):
        report = serializer.save(generated_by=self.request.user)
        generate_report(report)

    @action(detail=True, methods=["post"])
    def regenerate(self, request, pk=None):
        report = self.get_object()
        report.status = Report.Status.PENDING
        report.save(update_fields=["status", "updated_at"])
        generate_report(report)
        return Response(self.get_serializer(report).data)


class DashboardSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        now = timezone.now()
        day_ago = now - timedelta(hours=24)
        events_today = DetectionEvent.objects.filter(detected_at__gte=day_ago)
        not_read = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response(
            {
                "zones": {
                    "total": Zone.objects.filter(is_deleted=False).count(),
                    "active": Zone.objects.filter(is_deleted=False, is_active=True).count(),
                },
                "crops": Crop.objects.count(),
                "devices": {
                    "total": Device.objects.count(),
                    "online": Device.objects.filter(status=Device.Status.ONLINE).count(),
                },
                "detections_24h": events_today.count(),
                "disuasions_24h": DisuasionActivation.objects.filter(started_at__gte=day_ago).count(),
                "unread_notifications": not_read,
                "top_classes_24h": list(
                    events_today.values("object_class")
                    .annotate(total=Count("id"))
                    .order_by("-total")[:5]
                ),
                "recent_events": list(
                    events_today.select_related("zone")
                    .values("id", "object_class", "confidence", "detected_at", "zone__name")[:10]
                ),
            }
        )
