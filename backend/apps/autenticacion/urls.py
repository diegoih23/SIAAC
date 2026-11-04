from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    ChangePasswordView,
    LogoutView,
    MeView,
    RegisterView,
    RequestPasswordResetView,
    VerifyPasswordResetView,
    ConfirmPasswordResetView,
    ToggleTwoFactorView,
    VerifyTwoFactorView,
    VerifyEmailView,
    ResendEmailVerificationView,
    SessionViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")
router.register("sessions", SessionViewSet, basename="session")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("me/", MeView.as_view(), name="me"),
    path("change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password-reset/request/", RequestPasswordResetView.as_view(), name="password-reset-request"),
    path("password-reset/verify/", VerifyPasswordResetView.as_view(), name="password-reset-verify"),
    path("password-reset/confirm/", ConfirmPasswordResetView.as_view(), name="password-reset-confirm"),
    path("two-factor/verify/", VerifyTwoFactorView.as_view(), name="two-factor-verify"),
    path("two-factor/toggle/", ToggleTwoFactorView.as_view(), name="two-factor-toggle"),
    path("email-verification/verify/", VerifyEmailView.as_view(), name="email-verification-verify"),
    path("email-verification/resend/", ResendEmailVerificationView.as_view(), name="email-verification-resend"),
    path("", include(router.urls)),
]
