"""Módulo 2: CRUD de cultivos y zonas."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.nucleo.permissions import IsAdminOrReadOnly, IsOperatorOrAdmin

from .models import Crop, Zone
from .serializers import CropSerializer, ZoneSerializer


class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.select_related("owner").prefetch_related("zones")
    serializer_class = CropSerializer
    permission_classes = [IsOperatorOrAdmin]
    filterset_fields = ["status", "owner"]
    search_fields = ["name", "scientific_name", "variety"]
    ordering_fields = ["name", "planting_date", "created_at"]

    @action(detail=True, methods=["get"])
    def zones(self, request, pk=None):
        crop = self.get_object()
        return Response(ZoneSerializer(crop.zones.all(), many=True).data)


class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.select_related("crop", "responsible").filter(is_deleted=False)
    serializer_class = ZoneSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["crop", "is_active", "responsible"]
    search_fields = ["name", "code", "description"]
    ordering_fields = ["name", "code", "created_at"]

    def perform_destroy(self, instance):
        instance.soft_delete()
