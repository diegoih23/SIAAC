from rest_framework import serializers

from .models import Report


class ReportSerializer(serializers.ModelSerializer):
    report_type_display = serializers.CharField(source="get_report_type_display", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    generated_by_name = serializers.CharField(source="generated_by.get_full_name", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Report
        fields = (
            "id", "title", "report_type", "report_type_display", "format", "zone",
            "period_start", "period_end", "parameters", "status", "status_display",
            "file", "file_url", "error_message", "generated_by", "generated_by_name",
            "created_at", "updated_at",
        )
        read_only_fields = (
            "status", "file", "error_message", "generated_by", "created_at", "updated_at",
        )

    def get_file_url(self, obj) -> str | None:
        request = self.context.get("request")
        if not obj.file:
            return None
        return request.build_absolute_uri(obj.file.url) if request else obj.file.url

    def validate(self, attrs):
        start = attrs.get("period_start", getattr(self.instance, "period_start", None))
        end = attrs.get("period_end", getattr(self.instance, "period_end", None))
        if start and end and end <= start:
            raise serializers.ValidationError({"period_end": "Debe ser posterior al inicio."})
        return attrs
