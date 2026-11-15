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
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.enums import TA_LEFT
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    buffer = io.BytesIO()
    page_width, page_height = A4
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=report.title,
        author="SIAAC",
        leftMargin=36,
        rightMargin=36,
        topMargin=84,
        bottomMargin=54,
    )
    styles = getSampleStyleSheet()
    green = colors.HexColor("#173d25")
    primary = colors.HexColor("#2d9759")
    light_green = colors.HexColor("#e7f6eb")
    text = colors.HexColor("#24352b")
    muted = colors.HexColor("#6f8174")
    title_style = ParagraphStyle(
        "SiaacTitle", parent=styles["Title"], fontName="Helvetica-Bold",
        fontSize=23, leading=28, textColor=green, alignment=TA_LEFT, spaceAfter=5,
    )
    subtitle_style = ParagraphStyle(
        "SiaacSubtitle", parent=styles["Normal"], fontSize=10, leading=14,
        textColor=muted, spaceAfter=16,
    )
    cell_style = ParagraphStyle(
        "SiaacCell", parent=styles["Normal"], fontSize=8, leading=10, textColor=text,
    )
    head_style = ParagraphStyle(
        "SiaacHead", parent=cell_style, fontName="Helvetica-Bold", textColor=colors.white,
    )
    report_type = report.get_report_type_display()
    period = f"{report.period_start:%d/%m/%Y} — {report.period_end:%d/%m/%Y}"
    zone = report.zone.name if report.zone_id and report.zone else "Todas las zonas"

    def draw_page(canvas, document):
        canvas.saveState()
        canvas.setFillColor(green)
        canvas.rect(0, page_height - 58, page_width, 58, fill=1, stroke=0)
        canvas.setFillColor(colors.white)
        canvas.setFont("Helvetica-Bold", 18)
        canvas.drawString(36, page_height - 36, "SIAAC")
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(colors.HexColor("#bde9c7"))
        canvas.drawRightString(page_width - 36, page_height - 34, "VIGILANCIA INTELIGENTE")
        canvas.setStrokeColor(colors.HexColor("#dce9df"))
        canvas.line(36, 39, page_width - 36, 39)
        canvas.setFillColor(muted)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(36, 25, "Sistema Inteligente de Agricultura Asistida por Computadora")
        canvas.drawRightString(page_width - 36, 25, f"Página {document.page}")
        canvas.restoreState()

    def p(value, style=cell_style):
        return Paragraph(str(value).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"), style)

    elements = [
        Paragraph(report.title, title_style),
        Paragraph(f"Reporte de {report_type.lower()} · Generado el {datetime.now():%d/%m/%Y %H:%M}", subtitle_style),
    ]
    metadata = Table([
        [p("PERIODO", head_style), p("ZONA", head_style), p("REGISTROS", head_style)],
        [p(period), p(zone), p(f"{len(rows):,}")],
    ], colWidths=[170, 170, 120])
    metadata.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), primary),
        ("BACKGROUND", (0, 1), (-1, 1), light_green),
        ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#bfe4c8")),
        ("INNERGRID", (0, 0), (-1, -1), 0.3, colors.HexColor("#dce9df")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements += [
        metadata,
        Spacer(1, 12),
        Paragraph("Detalle del reporte", ParagraphStyle("Section", parent=styles["Heading2"], fontSize=13, textColor=green, spaceAfter=8)),
    ]
    if rows:
        table_data = [[p(header, head_style) for header in headers]]
        table_data += [[p(value) for value in row] for row in rows]
        column_widths = [((page_width - 72) / len(headers))] * len(headers)
        table = Table(table_data, repeatRows=1, colWidths=column_widths, hAlign="LEFT")
    else:
        table = Table([[p("No existen registros para el periodo seleccionado.")]], colWidths=[460])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), green),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#dce9df")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5fbf6")]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    elements.append(table)
    doc.build(elements, onFirstPage=draw_page, onLaterPages=draw_page)
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
