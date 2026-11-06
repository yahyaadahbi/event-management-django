"""
Utility functions for QR code and PDF ticket generation.
"""

import os
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


def generate_qr_code(registration):
    """Generate a QR code image for a registration and save it to media."""
    qr_data = (
        f"EVENTHUB-TICKET\n"
        f"Code: {registration.ticket_code}\n"
        f"Event: {registration.event.title}\n"
        f"Participant: {registration.participant.get_full_name() or registration.participant.username}\n"
        f"Date: {registration.event.event_date.strftime('%Y-%m-%d %H:%M')}"
    )

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#1e1b4b", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)

    filename = f"qr_{registration.ticket_code}.png"
    registration.qr_code.save(filename, ContentFile(buffer.read()), save=False)
    return registration


def ensure_qr_code(registration):
    """
    If the registration is a valid active ticket but has no stored QR image,
    generate it (e.g. after manual admin change or missing file).
    """
    if registration.status != 'confirmed':
        return registration
    if registration.payment_status not in ('paid', 'not_required'):
        return registration
    if not registration.qr_code:
        registration = generate_qr_code(registration)
        registration.save()
    return registration


def generate_ticket_pdf(registration):
    """
    Generate a beautiful PDF ticket using ReportLab.
    Returns BytesIO buffer with the PDF content.
    """
    buffer = BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    styles = getSampleStyleSheet()
    elements = []

    # ── Color Palette ──────────────────────────────────────────────────────
    brand_purple = colors.HexColor('#6366f1')
    brand_dark   = colors.HexColor('#1e1b4b')
    brand_light  = colors.HexColor('#f8fafc')
    brand_gray   = colors.HexColor('#64748b')
    brand_green  = colors.HexColor('#10b981')
    white        = colors.white

    # ── Custom Styles ──────────────────────────────────────────────────────
    title_style = ParagraphStyle(
        'TicketTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=white,
        alignment=TA_CENTER,
        spaceAfter=4,
        fontName='Helvetica-Bold',
    )
    subtitle_style = ParagraphStyle(
        'TicketSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#c7d2fe'),
        alignment=TA_CENTER,
        fontName='Helvetica',
    )
    section_title_style = ParagraphStyle(
        'SectionTitle',
        parent=styles['Normal'],
        fontSize=9,
        textColor=brand_gray,
        fontName='Helvetica-Bold',
        spaceBefore=8,
        spaceAfter=2,
        leftIndent=0,
    )
    field_value_style = ParagraphStyle(
        'FieldValue',
        parent=styles['Normal'],
        fontSize=13,
        textColor=brand_dark,
        fontName='Helvetica-Bold',
        spaceAfter=6,
    )
    code_style = ParagraphStyle(
        'TicketCode',
        parent=styles['Normal'],
        fontSize=10,
        textColor=brand_gray,
        alignment=TA_CENTER,
        fontName='Helvetica',
        spaceAfter=4,
    )
    bold_code_style = ParagraphStyle(
        'BoldCode',
        parent=styles['Normal'],
        fontSize=14,
        textColor=brand_dark,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )

    # ── Header Banner ─────────────────────────────────────────────────────
    header_data = [[
        Paragraph("🎟 EventHub", title_style),
    ]]
    header_table = Table(header_data, colWidths=[17 * cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), brand_dark),
        ('ROUNDEDCORNERS', [12, 12, 0, 0]),
        ('TOPPADDING', (0, 0), (-1, -1), 20),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 20),
        ('RIGHTPADDING', (0, 0), (-1, -1), 20),
    ]))
    elements.append(header_table)

    # ── Subheader ─────────────────────────────────────────────────────────
    sub_data = [[Paragraph("OFFICIAL EVENT TICKET", subtitle_style)]]
    sub_table = Table(sub_data, colWidths=[17 * cm])
    sub_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), brand_purple),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    elements.append(sub_table)
    elements.append(Spacer(1, 0.5 * cm))

    # ── Event Title ───────────────────────────────────────────────────────
    event_title_style = ParagraphStyle(
        'EventTitle',
        parent=styles['Normal'],
        fontSize=20,
        textColor=brand_dark,
        fontName='Helvetica-Bold',
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    elements.append(Paragraph(registration.event.title, event_title_style))

    # ── Category Badge ────────────────────────────────────────────────────
    if registration.event.category:
        cat_style = ParagraphStyle(
            'CatBadge', parent=styles['Normal'],
            fontSize=9, textColor=white,
            alignment=TA_CENTER, fontName='Helvetica-Bold',
        )
        cat_data = [[Paragraph(registration.event.category.name.upper(), cat_style)]]
        cat_table = Table(cat_data, colWidths=[4 * cm])
        cat_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), brand_purple),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        wrapper = Table([[cat_table]], colWidths=[17 * cm])
        wrapper.setStyle(TableStyle([('ALIGN', (0, 0), (-1, -1), 'CENTER')]))
        elements.append(wrapper)

    elements.append(Spacer(1, 0.4 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#e2e8f0')))
    elements.append(Spacer(1, 0.4 * cm))

    # ── Details Grid ──────────────────────────────────────────────────────
    event = registration.event
    participant = registration.participant

    left_col = [
        [Paragraph("ATTENDEE", section_title_style)],
        [Paragraph(participant.get_full_name() or participant.username, field_value_style)],
        [Paragraph("EMAIL", section_title_style)],
        [Paragraph(participant.email, field_value_style)],
        [Paragraph("DATE & TIME", section_title_style)],
        [Paragraph(event.event_date.strftime("%A, %B %d, %Y — %H:%M"), field_value_style)],
        [Paragraph("LOCATION", section_title_style)],
        [Paragraph(event.location, field_value_style)],
    ]

    ticket_type_name = registration.ticket_type.name if registration.ticket_type else "General"
    price = registration.get_ticket_price()
    right_col = [
        [Paragraph("TICKET TYPE", section_title_style)],
        [Paragraph(ticket_type_name, field_value_style)],
        [Paragraph("PRICE", section_title_style)],
        [Paragraph(f"${price:.2f}" if price > 0 else "FREE", field_value_style)],
        [Paragraph("STATUS", section_title_style)],
        [Paragraph("✅ CONFIRMED", ParagraphStyle(
            'Confirmed', parent=styles['Normal'],
            fontSize=13, textColor=brand_green, fontName='Helvetica-Bold'
        ))],
        [Paragraph("REGISTERED ON", section_title_style)],
        [Paragraph(registration.created_at.strftime("%B %d, %Y"), field_value_style)],
    ]

    details_left = Table(left_col, colWidths=[8 * cm])
    details_left.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
    ]))

    details_right = Table(right_col, colWidths=[7 * cm])
    details_right.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
    ]))

    # QR Code
    qr_elements = [
        [Paragraph("SCAN TO VERIFY", section_title_style)],
    ]
    if registration.qr_code and os.path.exists(registration.qr_code.path):
        qr_img = Image(registration.qr_code.path, width=4.5 * cm, height=4.5 * cm)
        qr_elements.append([qr_img])
    else:
        qr_elements.append([Paragraph("[QR CODE]", styles['Normal'])])

    qr_table = Table(qr_elements, colWidths=[5.5 * cm])
    qr_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))

    grid_data = [[details_left, details_right, qr_table]]
    grid = Table(grid_data, colWidths=[8 * cm, 4.5 * cm, 5 * cm])
    grid.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    elements.append(grid)

    elements.append(Spacer(1, 0.5 * cm))
    elements.append(HRFlowable(width="100%", thickness=1, lineCap='round',
                                color=colors.HexColor('#e2e8f0'), dash=(4, 3)))
    elements.append(Spacer(1, 0.3 * cm))

    # ── Ticket Code Footer ────────────────────────────────────────────────
    elements.append(Paragraph("TICKET CODE", code_style))
    elements.append(Paragraph(str(registration.ticket_code).upper(), bold_code_style))
    elements.append(Spacer(1, 0.3 * cm))

    # ── Footer Banner ─────────────────────────────────────────────────────
    footer_text = ParagraphStyle(
        'Footer', parent=styles['Normal'],
        fontSize=8, textColor=white, alignment=TA_CENTER, fontName='Helvetica',
    )
    footer_data = [[
        Paragraph(
            "This ticket is non-transferable. Please present this ticket (printed or digital) at entry. "
            "EventHub — Connecting people through experiences.",
            footer_text
        )
    ]]
    footer_table = Table(footer_data, colWidths=[17 * cm])
    footer_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), brand_dark),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 16),
        ('RIGHTPADDING', (0, 0), (-1, -1), 16),
    ]))
    elements.append(footer_table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
