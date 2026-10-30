from django.contrib import admin

from .models import DisuasionActivation, DisuasiveRule


@admin.register(DisuasiveRule)
class DisuasiveRuleAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "action", "min_confidence", "duration_seconds", "is_active")
    list_filter = ("action", "is_active")


@admin.register(DisuasionActivation)
class DisuasionActivationAdmin(admin.ModelAdmin):
    list_display = ("rule", "event", "status", "started_at", "ended_at")
    list_filter = ("status",)
