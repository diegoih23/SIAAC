from rest_framework import serializers

from .models import Crop, Zone


class CropSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    zones_count = serializers.IntegerField(source="zones.count", read_only=True)
    assigned_user_names = serializers.SerializerMethodField()

    class Meta:
        model = Crop
        fields = (
            "id", "name", "scientific_name", "variety", "description",
            "planting_date", "harvest_date", "status", "owner", "owner_name",
            "assigned_users", "assigned_user_names", "zones_count", "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "owner_name", "assigned_user_names", "zones_count")

    def get_assigned_user_names(self, obj):
        return [user.get_full_name() or user.username for user in obj.assigned_users.all()]


class ZoneSerializer(serializers.ModelSerializer):
    crop_name = serializers.CharField(source="crop.name", read_only=True)
    responsible_name = serializers.CharField(source="responsible.get_full_name", read_only=True)
    devices_count = serializers.IntegerField(source="devices.count", read_only=True)

    class Meta:
        model = Zone
        fields = (
            "id", "name", "code", "crop", "crop_name", "description",
            "latitude", "longitude", "area_m2", "responsible", "responsible_name",
            "is_active", "devices_count", "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "crop_name", "devices_count")

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        latitude = attrs.get("latitude")
        longitude = attrs.get("longitude")
        area = attrs.get("area_m2")
        if latitude is not None and not -90 <= latitude <= 90:
            raise serializers.ValidationError({"latitude": "La latitud debe estar entre -90 y 90."})
        if longitude is not None and not -180 <= longitude <= 180:
            raise serializers.ValidationError({"longitude": "La longitud debe estar entre -180 y 180."})
        if area is not None and area <= 0:
            raise serializers.ValidationError({"area_m2": "El área debe ser mayor que cero."})
        return attrs
