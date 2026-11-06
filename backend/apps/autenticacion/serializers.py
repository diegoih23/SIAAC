from datetime import timedelta
import re
import unicodedata

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.hashers import check_password
from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils import timezone

from .models import PasswordResetCode, TwoFactorChallenge, User, UserSession
from .email_utils import send_siaac_otp_email


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            "id", "username", "email", "first_name", "last_name", "full_name",
            "role", "phone", "avatar", "is_active", "is_email_verified", "date_joined",
            "two_factor_enabled",
        )
        read_only_fields = ("id", "date_joined", "is_email_verified")

    def get_full_name(self, obj) -> str:
        return obj.get_full_name() or obj.username


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name", "phone", "password", "password_confirm")
        extra_kwargs = {
            "username": {"required": False, "allow_blank": True, "max_length": 30},
            "email": {"required": True, "max_length": 254},
            "first_name": {"required": True, "max_length": 60},
            "last_name": {"required": True, "max_length": 80},
            "phone": {"required": False, "allow_blank": True, "max_length": 20},
        }

    def validate(self, attrs):
        first_name = attrs.get("first_name", "").strip()
        last_name = attrs.get("last_name", "").strip()
        if not first_name or not last_name:
            raise serializers.ValidationError("El nombre y el apellido son obligatorios.")
        if not re.fullmatch(r"[A-Za-zÀ-ÿ' -]+", first_name, flags=re.UNICODE):
            raise serializers.ValidationError({"first_name": "El nombre contiene caracteres no válidos."})
        if not re.fullmatch(r"[A-Za-zÀ-ÿ' -]+", last_name, flags=re.UNICODE):
            raise serializers.ValidationError({"last_name": "El apellido contiene caracteres no válidos."})
        attrs["first_name"] = first_name
        attrs["last_name"] = last_name
        username = attrs.get("username", "").strip()
        if username and not re.fullmatch(r"[A-Za-z0-9._-]{3,30}", username):
            raise serializers.ValidationError({"username": "Usa 3-30 caracteres: letras, números, punto, guion o guion bajo."})
        attrs["username"] = username
        attrs["email"] = attrs["email"].strip().lower()
        if User.objects.filter(email__iexact=attrs["email"]).exists():
            raise serializers.ValidationError({"email": "Este correo ya está registrado."})
        phone = attrs.get("phone", "").strip()
        if phone and not re.fullmatch(r"\+?[0-9 ()-]{7,20}", phone):
            raise serializers.ValidationError({"phone": "Ingresa un número de celular válido."})
        attrs["phone"] = phone
        if attrs["password"] != attrs.pop("password_confirm"):
            raise serializers.ValidationError({"password_confirm": "Las contraseñas no coinciden."})
        return attrs

    def create(self, validated_data):
        username = validated_data.pop("username", "").strip()
        if not username:
            base = unicodedata.normalize("NFKD", validated_data["email"].split("@")[0])
            base = re.sub(r"[^a-zA-Z0-9._-]", "", base).lower()[:24] or "usuario"
            username = base
            suffix = 1
            while User.objects.filter(username=username).exists():
                suffix += 1
                username = f"{base[:30-len(str(suffix))-1]}_{suffix}"
        validated_data["username"] = username
        return User.objects.create_user(**validated_data)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])

    def validate_current_password(self, value):
        if not self.context["request"].user.check_password(value):
            raise serializers.ValidationError("La contraseña actual es incorrecta.")
        return value


class RequestPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class VerifyPasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.RegexField(regex=r"^\d{6}$", max_length=6, min_length=6)

    def validate(self, attrs):
        reset = PasswordResetCode.objects.filter(
            email__iexact=attrs["email"], is_used=False
        ).first()
        if not reset:
            raise serializers.ValidationError("El código no existe o ya expiró.")
        if reset.expires_at <= timezone.now():
            raise serializers.ValidationError("El código ha expirado. Solicita uno nuevo.")
        if reset.attempts >= 5:
            raise serializers.ValidationError("Se superó el límite de intentos. Solicita otro código.")
        if not check_password(attrs["code"], reset.code_hash):
            reset.attempts += 1
            reset.save(update_fields=["attempts", "updated_at"])
            raise serializers.ValidationError("El código ingresado no es válido.")
        attrs["reset"] = reset
        return attrs


class ConfirmPasswordResetSerializer(VerifyPasswordResetSerializer):
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate(self, attrs):
        attrs = super().validate(attrs)
        if attrs["new_password"] != attrs.pop("new_password_confirm"):
            raise serializers.ValidationError({"new_password_confirm": "Las contraseñas no coinciden."})
        return attrs


class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSession
        fields = (
            "id", "ip_address", "user_agent", "device_label",
            "login_at", "logout_at", "is_active",
        )
        read_only_fields = fields


class SiaacTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Incluye rol y nombre en el JWT para que el frontend autorice vistas."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["username"] = user.username
        token["full_name"] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        username = attrs.get("username", "").strip()
        user = User.objects.filter(username__iexact=username).first()
        if not user and "@" in username:
            user = User.objects.filter(email__iexact=username).first()
            if user:
                attrs["username"] = user.username
        if user and user.locked_until and user.locked_until > timezone.now():
            remaining = max(1, int((user.locked_until - timezone.now()).total_seconds() // 60) + 1)
            raise AuthenticationFailed(
                f"Cuenta bloqueada temporalmente. Intenta nuevamente en {remaining} minutos.",
                code="account_locked",
            )
        try:
            data = super().validate(attrs)
        except AuthenticationFailed:
            if user:
                user.failed_login_attempts += 1
                if user.failed_login_attempts >= 5:
                    user.locked_until = timezone.now() + timedelta(minutes=15)
                user.save(update_fields=["failed_login_attempts", "locked_until"])
            raise AuthenticationFailed(
                "Usuario o contraseña incorrectos.", code="invalid_credentials"
            )

        user = self.user
        if not user.is_superuser and not user.is_email_verified:
            raise AuthenticationFailed(
                "Debes verificar tu correo antes de iniciar sesión.",
                code="email_not_verified",
            )
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save(update_fields=["failed_login_attempts", "locked_until"])
        data["user"] = UserSerializer(self.user).data
        if self.user.two_factor_enabled:
            data.pop("access", None)
            data.pop("refresh", None)
            data.update(self._create_two_factor_challenge())
        return data

    def _create_two_factor_challenge(self):
        import secrets
        import uuid
        from datetime import timedelta

        code = f"{secrets.randbelow(1_000_000):06d}"
        TwoFactorChallenge.objects.filter(user=self.user, is_used=False).update(is_used=True)
        challenge = TwoFactorChallenge.objects.create(
            user=self.user,
            challenge_id=uuid.uuid4(),
            code_hash=make_password(code),
            expires_at=timezone.now() + timedelta(minutes=2),
        )
        send_siaac_otp_email(
            recipient=self.user.email,
            subject="Código de acceso seguro - SIAAC",
            code=code,
            title="Confirma tu identidad",
            message="Se solicitó un acceso protegido a tu cuenta. Introduce este código para completar el inicio de sesión.",
            expires="2 minutos",
        )
        return {
            "two_factor_required": True,
            "challenge_id": str(challenge.challenge_id),
            "detail": "Ingresa el código enviado a tu correo.",
            "expires_in": 120,
        }


class VerifyTwoFactorSerializer(serializers.Serializer):
    challenge_id = serializers.UUIDField()
    code = serializers.RegexField(regex=r"^\d{6}$", max_length=6, min_length=6)


class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.RegexField(regex=r"^\d{6}$", max_length=6, min_length=6)
