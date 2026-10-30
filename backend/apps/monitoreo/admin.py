from django.contrib import admin

from .models import Camera, SensorReading


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = ("name", "zone", "status", "has_night_vision", "last_frame_at")
    list_filter = ("status", "has_night_vision")


@admin.register(SensorReading)
class SensorReadingAdmin(admin.ModelAdmin):
    list_display = ("zone", "sensor_type", "value", "unit", "recorded_at")
    list_filter = ("sensor_type",)
    date_hierarchy = "recorded_at"
