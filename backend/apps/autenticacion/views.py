"""Módulo 1: registro, perfil, sesiones y recuperación OTP."""
import secrets
import uuid
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
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

from .models import AccessAttempt, EmailVerificationCode, TwoFactorChallenge, User, UserSession
from .serializers import (
    ConfirmPasswordResetSerializer,
    ChangePasswordSerializer,
    RegisterSerializer,
    RequestPasswordResetSerializer,
    VerifyPasswordResetSerializer,
    VerifyTwoFactorSerializer,
    VerifyEmailSerializer,
    SessionSerializer,
    SiaacTokenObtainPairSerializer,
    UserSerializer,
)
from .models import PasswordResetCode


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        send_email_verification_code(user)


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


class RequestPasswordResetView(APIView):
    """Genera y envía un código OTP sin revelar si el correo existe."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RequestPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"].lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first()

        if user:
            PasswordResetCode.objects.filter(email__iexact=email, is_used=False).update(is_used=True)
            code = f"{secrets.randbelow(1_000_000):06d}"
            reset = PasswordResetCode.objects.create(
                email=email,
                code_hash=make_password(code),
                reset_token=uuid.uuid4(),
                expires_at=timezone.now() + timedelta(minutes=10),
            )
            send_mail(
                subject="Código de recuperación SIAAC",
                message=(
                    f"Hola {user.get_full_name() or user.username},\n\n"
                    f"Tu código de recuperación es: {code}\n"
                    "Tiene una vigencia de 10 minutos. Si no solicitaste este código, ignora este mensaje."
                ),
                from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "seguridad@siaac.local"),
                recipient_list=[user.email],
                fail_silently=True,
            )

        return Response({
            "detail": "Si el correo está registrado, recibirás un código de recuperación.",
            "expires_in": 600,
        })


class VerifyPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"detail": "Código verificado.", "reset_token": str(serializer.validated_data["reset"].reset_token)})


class ConfirmPasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ConfirmPasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reset = serializer.validated_data["reset"]
        user = User.objects.filter(email__iexact=reset.email, is_active=True).first()
        if not user:
            return Response({"detail": "No se pudo actualizar la contraseña."}, status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password"])
        reset.is_verified = True
        reset.is_used = True
        reset.used_at = timezone.now()
        reset.save(update_fields=["is_verified", "is_used", "used_at", "updated_at"])
        UserSession.objects.filter(user=user, is_active=True).update(
            is_active=False, logout_at=timezone.now()
        )
        return Response({"detail": "Contraseña actualizada. Ya puedes iniciar sesión."})


class VerifyTwoFactorView(APIView):
    """Valida el segundo factor y entrega el JWT definitivo."""

    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth.hashers import check_password
        from rest_framework.exceptions import ValidationError

        serializer = VerifyTwoFactorSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        challenge = TwoFactorChallenge.objects.select_related("user").filter(
            challenge_id=serializer.validated_data["challenge_id"], is_used=False
        ).first()
        if not challenge or challenge.expires_at <= timezone.now():
            raise ValidationError({"detail": "El desafío ha expirado. Inicia sesión nuevamente."})
        if challenge.attempts >= 5:
            raise ValidationError({"detail": "Se superó el límite de intentos. Inicia sesión nuevamente."})
        if not check_password(serializer.validated_data["code"], challenge.code_hash):
            challenge.attempts += 1
            challenge.save(update_fields=["attempts", "updated_at"])
            raise ValidationError({"detail": "El código de verificación no es válido."})

        challenge.is_used = True
        challenge.used_at = timezone.now()
        challenge.save(update_fields=["is_used", "used_at", "updated_at"])
        token = SiaacTokenObtainPairSerializer.get_token(challenge.user)
        return Response({
            "refresh": str(token),
            "access": str(token.access_token),
            "user": UserSerializer(challenge.user).data,
            "detail": "Acceso verificado correctamente.",
        })


class ToggleTwoFactorView(APIView):
    """Activa o desactiva 2FA para el usuario autenticado."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        enabled = bool(request.data.get("enabled", not request.user.two_factor_enabled))
        if enabled and not request.user.email:
            return Response(
                {"detail": "Debes tener un correo registrado para activar 2FA."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.user.two_factor_enabled = enabled
        request.user.save(update_fields=["two_factor_enabled"])
        return Response({
            "two_factor_enabled": request.user.two_factor_enabled,
            "detail": "Doble factor actualizado.",
        })


def send_email_verification_code(user):
    """Genera y envía el OTP requerido para activar el correo."""
    code = f"{secrets.randbelow(1_000_000):06d}"
    EmailVerificationCode.objects.filter(user=user, is_used=False).update(is_used=True)
    verification = EmailVerificationCode.objects.create(
        user=user,
        code_hash=make_password(code),
        expires_at=timezone.now() + timedelta(minutes=2),
    )
    send_mail(
        subject="Verifica tu correo electrónico - SIAAC",
        message=(
            f"Hola {user.get_full_name() or user.username},\n\n"
            f"Tu usuario SIAAC es: {user.username}\n"
            f"Tu código de verificación SIAAC es: {code}\n"
            "Tiene una vigencia de 2 minutos. Si no creaste esta cuenta, ignora este mensaje."
        ),
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "seguridad@siaac.local"),
        recipient_list=[user.email],
        fail_silently=True,
    )
    return verification


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        from django.contrib.auth.hashers import check_password
        from rest_framework.exceptions import ValidationError

        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        verification = EmailVerificationCode.objects.select_related("user").filter(
            user__email__iexact=serializer.validated_data["email"], is_used=False
        ).first()
        if not verification or verification.expires_at <= timezone.now():
            raise ValidationError({"detail": "El código ha expirado. Solicita uno nuevo."})
        if verification.attempts >= 5:
            raise ValidationError({"detail": "Se superó el límite de intentos. Solicita otro código."})
        if not check_password(serializer.validated_data["code"], verification.code_hash):
            verification.attempts += 1
            verification.save(update_fields=["attempts", "updated_at"])
            raise ValidationError({"detail": "El código de verificación no es válido."})

        user = verification.user
        user.is_email_verified = True
        user.save(update_fields=["is_email_verified"])
        verification.is_used = True
        verification.used_at = timezone.now()
        verification.save(update_fields=["is_used", "used_at", "updated_at"])
        return Response({"detail": "Correo verificado correctamente. Ya puedes iniciar sesión."})


class ResendEmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = str(request.data.get("email", "")).strip().lower()
        user = User.objects.filter(email__iexact=email, is_active=True).first()
        if user and not user.is_email_verified:
            latest = EmailVerificationCode.objects.filter(user=user).first()
            if latest:
                elapsed = (timezone.now() - latest.created_at).total_seconds()
                if elapsed < 60:
                    retry_after = max(1, 60 - int(elapsed))
                    return Response(
                        {
                            "detail": f"Espera {retry_after} segundos antes de solicitar otro código.",
                            "retry_after": retry_after,
                        },
                        status=status.HTTP_429_TOO_MANY_REQUESTS,
                    )
            send_email_verification_code(user)
        return Response({"detail": "Si la cuenta existe, enviamos un nuevo código.", "expires_in": 120})


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
        forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
        ip = forwarded.split(",")[0].strip() or request.META.get("REMOTE_ADDR")
        username = request.data.get("username", "")
        user = User.objects.filter(username__iexact=username).first()
        AccessAttempt.objects.create(
            username=username,
            user=user,
            ip_address=ip or None,
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
            successful=response.status_code == status.HTTP_200_OK and not response.data.get("two_factor_required"),
            reason=(
                "segundo_factor_requerido" if response.status_code == status.HTTP_200_OK and response.data.get("two_factor_required")
                else "login_exitoso" if response.status_code == status.HTTP_200_OK
                else "credenciales_invalidas"
            ),
        )
        if response.status_code == 200 and not response.data.get("two_factor_required"):
            if user:
                UserSession.objects.create(
                    user=user,
                    ip_address=ip or None,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
                )
                user.last_login_ip = ip or None
                user.save(update_fields=["last_login_ip"])
        return response
