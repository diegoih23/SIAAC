"""Generación de reportes PDF/CSV a partir de eventos y lecturas."""
import csv
import io
from datetime import datetime

from django.core.files.base import ContentFile
from django.db.models import Count

from apps.deteccion.models import DetectionEvent
from apps.respuestas.models import DisuasionActivation
from apps.monitoreo.models import SensorReading

from .models import Report


def _detection_rows(report: Report) -> list[list]:
    qs = DetectionEvent.objects.filter(
        detected_at__range=(report.period_start, report.period_end)
    ).select_related("zone", "device")
    if report.zone_id:
        qs = qs.filter(zone_id=report.zone_id)
    return [
        [
            e.detected_at.strftime("%Y-%m-%d %H:%M:%S"),
            e.zone.code,
            e.object_class,
            f"{e.confidence:.2f}",
            e.get_status_display(),
        ]
        for e in qs[:5000]
    ]


def _sensor_rows(report: Report) -> list[list]:
    qs = SensorReading.objects.filter(
        recorded_at__range=(report.period_start, report.period_end)
    ).select_related("zone")
    if report.zone_id:
        qs = qs.filter(zone_id=report.zone_id)
    return [
        [r.recorded_at.strftime("%Y-%m-%d %H:%M:%S"), r.zone.code, r.get_sensor_type_display(),
         f"{r.value:.2f}", r.unit]
        for r in qs[:5000]
    ]


def _header_and_rows(report: Report) -> tuple[list[str], list[list]]:
    if report.report_type == Report.Type.SENSORS:
        return ["Fecha", "Zona", "Sensor", "Valor", "Unidad"], _sensor_rows(report)
    if report.report_type == Report.Type.DISUASION:
        qs = DisuasionActivation.objects.filter(
            started_at__range=(report.period_start, report.period_end)
        ).select_related("rule", "event")
        rows = [
            [a.started_at.strftime("%Y-%m-%d %H:%M:%S"), a.rule.name if a.rule else "-",
             a.status, a.event.object_class if a.event else "-"]
            for a in qs[:5000]
        ]
        return ["Fecha", "Regla", "Estado", "Evento"], rows
    return ["Fecha", "Zona", "Clase", "Confianza", "Estado"], _detection_rows(report)


def _build_csv(headers, rows) -> ContentFile:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(headers)
    writer.writerows(rows)
    return ContentFile(buffer.getvalue().encode("utf-8"))


def _build_pdf(report: Report, headers, rows) -> ContentFile:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title=report.title)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(report.title, styles["Title"]),
        Paragraph(
            f"Periodo: {report.period_start:%Y-%m-%d} a {report.period_end:%Y-%m-%d}", styles["Normal"]
        ),
        Spacer(1, 12),
    ]
    table = Table([headers] + rows, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E7D32")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F8E9")]),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    return ContentFile(buffer.getvalue())


def generate_report(report: Report) -> Report:
    try:
        headers, rows = _header_and_rows(report)
        if report.format == Report.Format.CSV:
            content = _build_csv(headers, rows)
            ext = "csv"
        else:
            content = _build_pdf(report, headers, rows)
            ext = "pdf"
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report.file.save(f"reporte_{report.id}_{stamp}.{ext}", content, save=False)
        report.status = Report.Status.READY
        report.error_message = ""
    except Exception as exc:  # se guarda el error para mostrarlo en la UI
        report.status = Report.Status.FAILED
        report.error_message = str(exc)
    report.save()
    return report
