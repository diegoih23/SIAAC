"""Módulo 2: CRUD de cultivos y zonas."""
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.nucleo.permissions import IsAdminOrReadOnly

from .models import Crop, Zone
from .serializers import CropSerializer, ZoneSerializer


class CropViewSet(viewsets.ModelViewSet):
    queryset = Crop.objects.select_related("owner").prefetch_related("zones")
    serializer_class = CropSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["status", "owner"]
    search_fields = ["name", "scientific_name", "variety"]
    ordering_fields = ["name", "planting_date", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_admin_role:
            return queryset
        return queryset.filter(
            Q(owner=self.request.user) | Q(assigned_users=self.request.user)
        ).distinct()

    def perform_create(self, serializer):
        # El administrador puede seleccionar un responsable; si no lo indica,
        # el cultivo queda asociado al administrador que lo creó.
        if serializer.validated_data.get("owner") is None:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

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

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.is_admin_role:
            return queryset
        return queryset.filter(
            Q(crop__owner=self.request.user) | Q(crop__assigned_users=self.request.user)
        ).distinct()

    def perform_destroy(self, instance):
        instance.soft_delete()
