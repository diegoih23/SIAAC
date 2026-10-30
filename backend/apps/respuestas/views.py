"""Módulo 5: CRUD de reglas y activación manual de la respuesta disuasiva."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.nucleo.permissions import IsAdminOrReadOnly, IsOperatorOrAdmin
from rest_framework.permissions import IsAuthenticated

from .models import DisuasionActivation, DisuasiveRule
from .serializers import DisuasionActivationSerializer, DisuasiveRuleSerializer
from .services import dispatch_activation


class DisuasiveRuleViewSet(viewsets.ModelViewSet):
    queryset = DisuasiveRule.objects.select_related("zone", "created_by")
    serializer_class = DisuasiveRuleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["zone", "action", "is_active"]
    search_fields = ["name"]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"], permission_classes=[IsOperatorOrAdmin])
    def activate(self, request, pk=None):
        rule = self.get_object()
        activation = dispatch_activation(rule, user=request.user)
        return Response(DisuasionActivationSerializer(activation).data, status=201)


class DisuasionActivationViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = DisuasionActivation.objects.select_related("rule", "event", "device")
    serializer_class = DisuasionActivationSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "rule", "device"]
    ordering_fields = ["started_at"]
