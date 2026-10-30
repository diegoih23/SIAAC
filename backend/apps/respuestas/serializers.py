from rest_framework import serializers

from .models import DisuasionActivation, DisuasiveRule


class DisuasiveRuleSerializer(serializers.ModelSerializer):
    zone_name = serializers.CharField(source="zone.name", read_only=True)
    action_display = serializers.CharField(source="get_action_display", read_only=True)

    class Meta:
        model = DisuasiveRule
        fields = (
            "id", "name", "zone", "zone_name", "trigger_classes", "min_confidence",
            "start_time", "end_time", "action", "action_display", "duration_seconds",
            "is_active", "created_by", "created_at", "updated_at",
        )
        read_only_fields = ("created_by", "created_at", "updated_at")

    def validate_trigger_classes(self, value):
        if not isinstance(value, list) or not value:
            raise serializers.ValidationError("Indica al menos una clase de objeto.")
        return value


class DisuasionActivationSerializer(serializers.ModelSerializer):
    rule_name = serializers.CharField(source="rule.name", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = DisuasionActivation
        fields = (
            "id", "rule", "rule_name", "event", "device", "command", "status",
            "status_display", "response", "started_at", "ended_at", "triggered_by",
        )
        read_only_fields = ("started_at", "ended_at", "triggered_by")
