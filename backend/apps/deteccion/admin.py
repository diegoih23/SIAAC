from django.contrib import admin

from .models import AIModel, DetectionEvent, Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("name", "device_type", "zone", "status", "last_seen")
    list_filter = ("device_type", "status")
    search_fields = ("name", "serial_number")


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ("name", "version", "architecture", "confidence_threshold", "is_active")


@admin.register(DetectionEvent)
class DetectionEventAdmin(admin.ModelAdmin):
    list_display = ("object_class", "zone", "confidence", "detected_at", "status")
    list_filter = ("status", "object_class")
    date_hierarchy = "detected_at"
