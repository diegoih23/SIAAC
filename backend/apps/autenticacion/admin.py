from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import AccessAttempt, EmailVerificationCode, TwoFactorChallenge, User, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "get_full_name", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("SIAAC", {"fields": ("role", "phone", "avatar", "is_email_verified", "last_login_ip", "two_factor_enabled", "failed_login_attempts", "locked_until")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("SIAAC", {"fields": ("role", "email")}),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "device_label", "login_at", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__username", "ip_address")


@admin.register(AccessAttempt)
class AccessAttemptAdmin(admin.ModelAdmin):
    list_display = ("username", "successful", "ip_address", "reason", "created_at")
    list_filter = ("successful", "reason")
    search_fields = ("username", "ip_address")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TwoFactorChallenge)
class TwoFactorChallengeAdmin(admin.ModelAdmin):
    list_display = ("user", "challenge_id", "expires_at", "attempts", "is_used")
    list_filter = ("is_used",)
    search_fields = ("user__username", "user__email", "challenge_id")


@admin.register(EmailVerificationCode)
class EmailVerificationCodeAdmin(admin.ModelAdmin):
    list_display = ("user", "expires_at", "attempts", "is_used")
    list_filter = ("is_used",)
    search_fields = ("user__username", "user__email")
