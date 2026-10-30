from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, UserSession


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("username", "email", "get_full_name", "role", "is_active", "date_joined")
    list_filter = ("role", "is_active", "is_staff")
    fieldsets = BaseUserAdmin.fieldsets + (
        ("SIAAC", {"fields": ("role", "phone", "avatar", "is_email_verified", "last_login_ip")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("SIAAC", {"fields": ("role", "email")}),
    )


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "device_label", "login_at", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__username", "ip_address")
