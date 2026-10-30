from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    channel_display = serializers.CharField(source="get_channel_display", read_only=True)
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    priority_display = serializers.CharField(source="get_priority_display", read_only=True)

    class Meta:
        model = Notification
        fields = (
            "id", "title", "message", "channel", "channel_display", "category",
            "category_display", "priority", "priority_display", "is_read", "read_at",
            "sent_at", "payload", "related_event", "created_at",
        )
        read_only_fields = ("read_at", "sent_at", "created_at")


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = (
            "id", "category", "channel", "enabled",
            "quiet_hours_start", "quiet_hours_end", "updated_at",
        )
        read_only_fields = ("updated_at",)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)
