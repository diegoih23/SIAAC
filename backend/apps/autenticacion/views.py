"""Módulo 1: registro, perfil, cambio de contraseña y sesiones."""
from django.utils import timezone
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.nucleo.permissions import IsAdministrator

from .models import User, UserSession
from .serializers import (
    ChangePasswordSerializer,
    RegisterSerializer,
    SessionSerializer,
    SiaacTokenObtainPairSerializer,
    UserSerializer,
)


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data["new_password"])
        request.user.save(update_fields=["password"])
        UserSession.objects.filter(user=request.user, is_active=True).update(
            is_active=False, logout_at=timezone.now()
        )
        return Response({"detail": "Contraseña actualizada. Inicia sesión de nuevo."})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh = request.data.get("refresh")
        if refresh:
            try:
                RefreshToken(refresh).blacklist()
            except TokenError:
                pass
        UserSession.objects.filter(user=request.user, is_active=True).update(
            is_active=False, logout_at=timezone.now()
        )
        return Response({"detail": "Sesión cerrada."}, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    """Administración de usuarios (solo rol ADMIN)."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdministrator]
    filterset_fields = ["role", "is_active"]
    search_fields = ["username", "email", "first_name", "last_name"]

    @action(detail=True, methods=["post"])
    def toggle_active(self, request, pk=None):
        user = self.get_object()
        user.is_active = not user.is_active
        user.save(update_fields=["is_active"])
        return Response(UserSerializer(user).data)


class SessionViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = SessionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = UserSession.objects.select_related("user")
        if self.request.user.is_admin_role:
            return qs
        return qs.filter(user=self.request.user)

    @action(detail=True, methods=["post"])
    def revoke(self, request, pk=None):
        session = self.get_object()
        session.is_active = False
        session.logout_at = timezone.now()
        session.save(update_fields=["is_active", "logout_at"])
        return Response({"detail": "Sesión revocada."})


class SiaacTokenObtainPairView(TokenObtainPairView):
    serializer_class = SiaacTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            user = User.objects.filter(username=request.data.get("username")).first()
            if user:
                forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
                ip = forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR")
                UserSession.objects.create(
                    user=user,
                    ip_address=ip or None,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
                )
                user.last_login_ip = ip or None
                user.save(update_fields=["last_login_ip"])
        return response
