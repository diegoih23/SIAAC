from rest_framework import serializers

from .models import Crop, Zone


class CropSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source="owner.get_full_name", read_only=True)
    zones_count = serializers.IntegerField(source="zones.count", read_only=True)

    class Meta:
        model = Crop
        fields = (
            "id", "name", "scientific_name", "variety", "description",
            "planting_date", "harvest_date", "status", "owner", "owner_name",
            "zones_count", "created_at", "updated_at",
        )
        read_only_fields = ("created_at", "updated_at", "owner_name", "zones_count")


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
