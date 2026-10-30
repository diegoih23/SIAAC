from django.contrib import admin

from .models import Crop, Zone


@admin.register(Crop)
class CropAdmin(admin.ModelAdmin):
    list_display = ("name", "variety", "status", "planting_date", "harvest_date", "owner")
    list_filter = ("status",)
    search_fields = ("name", "scientific_name", "variety")


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "crop", "responsible", "is_active")
    list_filter = ("is_active",)
    search_fields = ("code", "name")
