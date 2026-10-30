from rest_framework import serializers

from .models import AIModel, DetectionEvent, Device


class DeviceSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    device_type_display = serializers.CharField(source="get_device_type_display", read_only=True)

    class Meta:
        model = Device
        fields = (
            "id", "name", "device_type", "device_type_display", "serial_number",
            "zone", "zone_name", "ip_address", "api_key", "firmware_version",
            "status", "last_seen", "metadata", "created_at", "updated_at",
        )
        read_only_fields = ("api_key", "last_seen", "created_at", "updated_at")
        extra_kwargs = {"api_key": {"read_only": True}}


class AIModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIModel
        fields = "__all__"
        read_only_fields = ("created_at", "updated_at")


class DetectionEventSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    device_name = serializers.CharField(source="device.name", read_only=True)
    object_class_display = serializers.CharField(source="get_status_display", read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = DetectionEvent
        fields = (
            "id", "zone", "zone_name", "device", "device_name", "camera", "ai_model",
            "object_class", "object_class_display", "confidence", "bbox", "image",
            "image_url", "detected_at", "status", "reviewed_by", "reviewed_at",
            "notes", "disuasion_triggered", "created_at",
        )
        read_only_fields = ("reviewed_by", "reviewed_at", "created_at", "disuasion_triggered")

    def get_image_url(self, obj) -> str | None:
        request = self.context.get("request")
        if not obj.image:
            return None
        return request.build_absolute_uri(obj.image.url) if request else obj.image.url


class DetectionIngestSerializer(serializers.ModelSerializer):
    """Payload enviado por la Raspberry Pi tras ejecutar YOLO."""

    device_serial = serializers.CharField(write_only=True)

    class Meta:
        model = DetectionEvent
        fields = (
            "device_serial", "zone", "camera", "object_class", "confidence",
            "bbox", "image", "detected_at",
        )
        extra_kwargs = {
            "zone": {"required": False},
            "camera": {"required": False},
            "image": {"required": False},
            "detected_at": {"required": False},
        }

    def validate(self, attrs):
        request = self.context.get("request")
        key = request.headers.get("X-Device-Key") if request else None
        serial = attrs.pop("device_serial")
        try:
            device = Device.objects.get(serial_number=serial)
        except Device.DoesNotExist:
            raise serializers.ValidationError({"device_serial": "Dispositivo no registrado."})
        if key != device.api_key:
            raise serializers.ValidationError({"device_serial": "API key del dispositivo inválida."})
        attrs["device"] = device
        attrs.setdefault("zone", device.zone)
        if attrs["zone"] is None:
            raise serializers.ValidationError({"zone": "La zona es obligatoria."})
        return attrs
