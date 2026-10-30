from rest_framework import serializers

from .models import Camera, SensorReading


class CameraSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)

    class Meta:
        model = Camera
        fields = (
            "id", "zone", "zone_name", "name", "stream_url", "has_night_vision",
            "status", "last_frame_at", "created_at", "updated_at",
        )
        read_only_fields = ("last_frame_at", "created_at", "updated_at")


class SensorReadingSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    sensor_type_display = serializers.CharField(source="get_sensor_type_display", read_only=True)

    class Meta:
        model = SensorReading
        fields = (
            "id", "zone", "zone_name", "device", "sensor_type", "sensor_type_display",
            "value", "unit", "recorded_at", "raw_payload", "created_at",
        )
        read_only_fields = ("created_at",)
        extra_kwargs = {"recorded_at": {"required": False}}
