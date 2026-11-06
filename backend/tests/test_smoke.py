"""Pruebas mínimas de humo para validar la configuración del proyecto."""
import pytest
import re
from datetime import timedelta
from django.core import mail
from django.utils import timezone
from apps.autenticacion.models import EmailVerificationCode, User
from django.urls import reverse


@pytest.mark.django_db
def test_api_root_schema_disponible(client):
    response = client.get(reverse("schema"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_login_requiere_credenciales(client):
    response = client.post("/api/v1/auth/token/", {"username": "nadie", "password": "x"})
    assert response.status_code == 401


@pytest.mark.django_db
def test_recuperacion_otp_actualiza_contrasena(client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = User.objects.create_user(
        username="cultivador",
        email="cultivador@siaac.test",
        password="ClaveAnterior123!",
    )

    request = client.post("/api/v1/auth/password-reset/request/", {"email": user.email})
    assert request.status_code == 200
    assert len(mail.outbox) == 1
    code = re.search(r"\b(\d{6})\b", mail.outbox[0].body).group(1)

    verify = client.post(
        "/api/v1/auth/password-reset/verify/",
        {"email": user.email, "code": code},
    )
    assert verify.status_code == 200

    confirm = client.post(
        "/api/v1/auth/password-reset/confirm/",
        {
            "email": user.email,
            "code": code,
            "new_password": "NuevaClave123!",
            "new_password_confirm": "NuevaClave123!",
        },
    )
    assert confirm.status_code == 200
    user.refresh_from_db()
    assert user.check_password("NuevaClave123!")


@pytest.mark.django_db
def test_bloqueo_temporal_despues_de_cinco_intentos(client):
    user = User.objects.create_user(username="seguro", password="ClaveSegura123!")

    for _ in range(5):
        response = client.post(
            "/api/v1/auth/token/",
            {"username": user.username, "password": "incorrecta"},
        )
        assert response.status_code == 401

    user.refresh_from_db()
    assert user.failed_login_attempts == 5
    assert user.locked_until is not None

    response = client.post(
        "/api/v1/auth/token/",
        {"username": user.username, "password": "ClaveSegura123!"},
    )
    assert response.status_code == 401
    assert "bloqueada" in str(response.data).lower()


@pytest.mark.django_db
def test_login_con_doble_factor_requiere_codigo(client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    user = User.objects.create_user(
        username="doble.factor",
        email="doble@siaac.test",
        password="ClaveSegura123!",
        two_factor_enabled=True,
        is_email_verified=True,
    )

    login = client.post(
        "/api/v1/auth/token/",
        {"username": user.username, "password": "ClaveSegura123!"},
    )
    assert login.status_code == 200
    assert login.data["two_factor_required"] is True
    assert "access" not in login.data
    code = re.search(r"\b(\d{6})\b", mail.outbox[-1].body).group(1)

    verified = client.post(
        "/api/v1/auth/two-factor/verify/",
        {"challenge_id": login.data["challenge_id"], "code": code},
    )
    assert verified.status_code == 200
    assert "access" in verified.data


@pytest.mark.django_db
def test_registro_genera_usuario_y_valida_datos(client):
    response = client.post(
        "/api/v1/auth/register/",
        {
            "first_name": "María",
            "last_name": "Gómez",
            "email": "maria@siaac.test",
            "phone": "+57 300 123 4567",
            "password": "ClaveNueva123!",
            "password_confirm": "ClaveNueva123!",
        },
    )
    assert response.status_code == 201
    assert response.data["username"] == "maria"

    invalid = client.post(
        "/api/v1/auth/register/",
        {
            "first_name": "1234567890",
            "last_name": "Usuario",
            "email": "correo-no-valido",
            "username": "usuario.invalido",
            "password": "ClaveNueva123!",
            "password_confirm": "ClaveNueva123!",
        },
    )
    assert invalid.status_code == 400

@pytest.mark.django_db
def test_registro_envia_y_verifica_correo(client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    response = client.post(
        "/api/v1/auth/register/",
        {
            "first_name": "Ana",
            "last_name": "López",
            "email": "ana@siaac.test",
            "username": "ana.lopez",
            "password": "ClaveNueva123!",
            "password_confirm": "ClaveNueva123!",
        },
    )
    assert response.status_code == 201
    assert len(mail.outbox) == 1
    code = re.search(r"\b(\d{6})\b", mail.outbox[0].body).group(1)

    blocked = client.post(
        "/api/v1/auth/token/",
        {"username": response.data["username"], "password": "ClaveNueva123!"},
    )
    assert blocked.status_code == 401
    assert "verificar tu correo" in str(blocked.data).lower()

    verified = client.post(
        "/api/v1/auth/email-verification/verify/",
        {"email": "ana@siaac.test", "code": code},
    )
    assert verified.status_code == 200
    assert User.objects.get(email="ana@siaac.test").is_email_verified is True


@pytest.mark.django_db
def test_reenvio_de_codigo_y_limite_temporal(client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    response = client.post(
        "/api/v1/auth/register/",
        {
            "first_name": "Laura",
            "last_name": "Pérez",
            "email": "laura@siaac.test",
            "username": "laura.perez",
            "password": "ClaveNueva123!",
            "password_confirm": "ClaveNueva123!",
        },
    )
    assert response.status_code == 201
    assert len(mail.outbox) == 1

    blocked = client.post(
        "/api/v1/auth/email-verification/resend/",
        {"email": "laura@siaac.test"},
    )
    assert blocked.status_code == 429
    assert blocked.data["retry_after"] > 0

    EmailVerificationCode.objects.filter(user__email="laura@siaac.test").update(
        created_at=timezone.now() - timedelta(minutes=2)
    )
    resent = client.post(
        "/api/v1/auth/email-verification/resend/",
        {"email": "laura@siaac.test"},
    )
    assert resent.status_code == 200
    assert len(mail.outbox) == 2


@pytest.mark.django_db
def test_codigo_de_correo_expirado_se_rechaza(client, settings):
    settings.EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
    response = client.post(
        "/api/v1/auth/register/",
        {
            "first_name": "Carlos",
            "last_name": "Mora",
            "email": "carlos@siaac.test",
            "username": "carlos.mora",
            "password": "ClaveNueva123!",
            "password_confirm": "ClaveNueva123!",
        },
    )
    assert response.status_code == 201
    verification = EmailVerificationCode.objects.get(user__email="carlos@siaac.test")
    verification.expires_at = timezone.now() - timedelta(minutes=1)
    verification.save(update_fields=["expires_at", "updated_at"])

    expired = client.post(
        "/api/v1/auth/email-verification/verify/",
        {"email": "carlos@siaac.test", "code": "123456"},
    )
    assert expired.status_code == 400
    assert "expirado" in str(expired.data).lower()
    assert User.objects.get(email="carlos@siaac.test").is_email_verified is False
