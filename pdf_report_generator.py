import os
from datetime import datetime

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from utils import format_money


# ============================================================
# COLORS
# ============================================================

DARK_BLUE = colors.HexColor("#1F4E78")
BLUE = colors.HexColor("#2F75B5")
LIGHT_BLUE = colors.HexColor("#D9EAF7")

GREEN = colors.HexColor("#548235")
LIGHT_GREEN = colors.HexColor("#E2F0D9")

DARK_GRAY = colors.HexColor("#404040")
LIGHT_GRAY = colors.HexColor("#F2F2F2")

WHITE = colors.white


# ============================================================
# DATE FORMATTER
# ============================================================

def format_report_date(date_value):
    """
    Convert AWS date format:

        YYYY-MM-DD

    to report format:

        DD-MM-YYYY

    Example:
        2026-08-01 -> 01-08-2026
    """

    date_obj = datetime.strptime(
        date_value,
        "%Y-%m-%d"
    )

    return date_obj.strftime("%d-%m-%Y")


# ============================================================
# CREATE PDF
# ============================================================

def create_pdf_report(
    start,
    end,
    billing_data,
    filename,
    include_credits=True
):
    """
    Create the AWS billing PDF report.
    """

    # Create reports folder if it does not exist
    os.makedirs(
        os.path.dirname(filename),
        exist_ok=True
    )

    # --------------------------------------------------------
    # PDF document
    # --------------------------------------------------------

    document = SimpleDocTemplate(
        filename,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=18 * mm,
        bottomMargin=18 * mm
    )

    # --------------------------------------------------------
    # Styles
    # --------------------------------------------------------

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Title"],
        fontSize=22,
        leading=26,
        alignment=TA_CENTER,
        textColor=DARK_BLUE,
        spaceAfter=10
    )

    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        textColor=DARK_BLUE,
        spaceBefore=8,
        spaceAfter=8
    )

    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=DARK_GRAY
    )

    small_style = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=DARK_GRAY
    )

    service_name_style = ParagraphStyle(
        "ServiceName",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=10,
        textColor=DARK_GRAY
    )

    header_style = ParagraphStyle(
        "HeaderStyle",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=WHITE
    )

    value_style = ParagraphStyle(
        "ValueStyle",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=DARK_GRAY
    )

    date_style = ParagraphStyle(
        "DateStyle",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=10,
        alignment=TA_CENTER,
        textColor=DARK_GRAY
    )

    content = []

    # --------------------------------------------------------
    # Get billing data
    # --------------------------------------------------------

    currency = billing_data["currency"]

    total_usage = billing_data["total_usage"]
    total_credit = billing_data["total_credit"]
    net_cost = billing_data["net_cost"]
    total_cost = billing_data["total_cost"]
    total_other = billing_data["total_other"]
    other_record_types = billing_data["other_record_types"]

    service_usage = billing_data["service_usage"]
    service_credit = billing_data["service_credit"]
    service_total = billing_data["service_total"]

    daily_usage = billing_data["daily_usage"]
    daily_credit = billing_data["daily_credit"]
    daily_total = billing_data["daily_total"]


    # ========================================================
    # TITLE
    # ========================================================

    content.append(
        Paragraph(
            "AWS Billing Report",
            title_style
        )
    )

    content.append(
        Paragraph(
            f"<b>Billing Period:</b> {start} to {end}",
            normal_style
        )
    )

    content.append(
        Paragraph(
            f"<b>Currency:</b> {currency}",
            normal_style
        )
    )

    content.append(
        Spacer(1, 15)
    )


    # ========================================================
    # COST SUMMARY
    # ========================================================

    content.append(
        Paragraph(
            "Cost Summary",
            heading_style
        )
    )

    summary_table = [
        [
            "Description",
            f"Amount ({currency})"
        ]
    ]

    if include_credits:
        summary_table.extend([
            ["Total AWS Cost", format_money(total_cost)],
            ["Usage Cost", format_money(total_usage)],
            ["Credits", format_money(total_credit)],
            ["Usage + Credits", format_money(net_cost)],
            ["Other Charges", format_money(total_other)]
        ])
    else:
        summary_table.append(["Usage Cost", format_money(total_usage)])

    summary = Table(
        summary_table,
        colWidths=[
            105 * mm,
            50 * mm
        ],
        hAlign="LEFT"                 # Align table with other tables
    )

    summary_style = [
            # Header
            ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

            # Alignment
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),

            # Vertical alignment
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

            # Borders
            ("GRID", (0, 0), (-1, -1), 0.6, WHITE),

            # Padding
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]

    if include_credits:
        summary_style.extend([
            ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BLUE),
            ("BACKGROUND", (0, 2), (-1, 2), LIGHT_GRAY),
            ("BACKGROUND", (0, 3), (-1, 3), LIGHT_GREEN),
            ("BACKGROUND", (0, 4), (-1, 4), LIGHT_BLUE),
            ("BACKGROUND", (0, 5), (-1, 5), LIGHT_GRAY),
            ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 1), (-1, 1), DARK_BLUE),
            ("FONTNAME", (0, 4), (-1, 4), "Helvetica-Bold"),
            ("TEXTCOLOR", (0, 4), (-1, 4), DARK_BLUE),
        ])
    else:
        summary_style.append(("BACKGROUND", (0, 1), (-1, 1), LIGHT_BLUE))

    summary.setStyle(TableStyle(summary_style))

    content.append(summary)

    content.append(
        Spacer(1, 15)
    )


    # ========================================================
    # SERVICE-WISE COST
    # ========================================================

    content.append(
        Paragraph(
            "Service-wise Cost",
            heading_style
        )
    )

    service_table = [[
        Paragraph("Service", header_style),
        Paragraph("Usage", header_style)
    ]]

    if include_credits:
        service_table[0].extend([
            Paragraph("Credit", header_style),
            Paragraph("Usage + Credits", header_style),
            Paragraph("Total Cost", header_style)
        ])

    for service in sorted(service_total if include_credits else service_usage):

        usage = service_usage[service]
        credit = service_credit[service]
        net = usage + credit
        total = service_total[service]

        # Skip completely zero rows
        if abs(usage) < 0.005 and (
            not include_credits or abs(total) < 0.005
        ):
            continue

        row = [
            Paragraph(
                service,
                service_name_style
            ),
            Paragraph(
                format_money(usage),
                value_style
            )
        ]

        if include_credits:
            row.extend([
                Paragraph(format_money(credit), value_style),
                Paragraph(format_money(net), value_style),
                Paragraph(format_money(total), value_style)
            ])

        service_table.append(row)

    # Fixed column widths
    service_report = Table(
        service_table,
        colWidths=(
            [65 * mm, 23 * mm, 23 * mm, 23 * mm, 26 * mm]
            if include_credits else [115 * mm, 45 * mm]
        ),
        repeatRows=1,
        hAlign="LEFT"
    )

    service_style = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), BLUE),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # Service column
        ("ALIGN", (0, 0), (0, -1), "LEFT"),

        # Numeric columns
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),

        # Vertical alignment
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        # Borders
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        # Padding
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6)
    ]

    # Alternating row background
    for row in range(1, len(service_table)):

        if row % 2 == 0:
            service_style.append(
                (
                    "BACKGROUND",
                    (0, row),
                    (-1, row),
                    LIGHT_GRAY
                )
            )

    service_report.setStyle(
        TableStyle(service_style)
    )

    content.append(service_report)

    content.append(
        Spacer(1, 15)
    )


    # ========================================================
    # DAILY COST
    # ========================================================

    content.append(
        Paragraph(
            "Daily Cost",
            heading_style
        )
    )

    daily_table = [[
        Paragraph("Date", header_style),
        Paragraph("Usage", header_style)
    ]]

    if include_credits:
        daily_table[0].extend([
            Paragraph("Credit", header_style),
            Paragraph("Usage + Credits", header_style),
            Paragraph("Total Cost", header_style)
        ])

    for date in sorted(daily_total if include_credits else daily_usage):

        usage = daily_usage[date]
        credit = daily_credit[date]
        net = usage + credit
        total = daily_total[date]
        # Convert AWS date:
        #
        # 2026-08-01
        #
        # to:
        #
        # 01-08-2026

        display_date = format_report_date(date)

        row = [
            Paragraph(
                display_date,
                date_style
            ),
            Paragraph(
                format_money(usage),
                value_style
            )
        ]

        if include_credits:
            row.extend([
                Paragraph(format_money(credit), value_style),
                Paragraph(format_money(net), value_style),
                Paragraph(format_money(total), value_style)
            ])

        daily_table.append(row)

    # Fixed column widths
    daily_report = Table(
        daily_table,
        colWidths=(
            [50 * mm, 27.5 * mm, 27.5 * mm, 27.5 * mm, 27.5 * mm]
            if include_credits else [80 * mm, 80 * mm]
        ),
        repeatRows=1,
        hAlign="LEFT"
    )

    daily_style = [
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), GREEN),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),

        # Date column - CENTER
        ("ALIGN", (0, 0), (0, -1), "CENTER"),

        # Numeric columns - RIGHT
        ("ALIGN", (1, 0), (-1, -1), "RIGHT"),

        # Vertical alignment
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),

        # Borders
        ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),

        # Padding
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6)
    ]

    # Alternating row background
    for row in range(1, len(daily_table)):

        if row % 2 == 0:
            daily_style.append(
                (
                    "BACKGROUND",
                    (0, row),
                    (-1, row),
                    LIGHT_GRAY
                )
            )

    daily_report.setStyle(
        TableStyle(daily_style)
    )

    content.append(daily_report)

    content.append(
        Spacer(1, 15)
    )


    # ========================================================
    # OTHER CHARGES
    # ========================================================

    if include_credits:
        content.append(
            Paragraph(
                "Other Charges",
                heading_style
            )
        )

        other_charges_table = [
            [
                Paragraph("Record Type", header_style),
                Paragraph("Amount", header_style)
            ]
        ]

        for record_type in sorted(
            other_record_types,
            key=str.casefold
        ):
            amount = other_record_types[record_type]

            if abs(amount) < 0.005:
                continue

            other_charges_table.append([
                Paragraph(record_type, service_name_style),
                Paragraph(format_money(amount), value_style)
            ])

        if len(other_charges_table) == 1:
            other_charges_table.append([
                Paragraph("No other charges", service_name_style),
                Paragraph(format_money(0), value_style)
            ])

        other_charges_report = Table(
            other_charges_table,
            colWidths=[105 * mm, 50 * mm],
            hAlign="LEFT"
        )

        other_charges_style = [
            ("BACKGROUND", (0, 0), (-1, 0), DARK_BLUE),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (0, 0), (0, -1), "LEFT"),
            ("ALIGN", (1, 0), (1, -1), "RIGHT"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6)
        ]

        for row in range(1, len(other_charges_table)):
            if row % 2 == 0:
                other_charges_style.append(
                    ("BACKGROUND", (0, row), (-1, row), LIGHT_GRAY)
                )

        other_charges_report.setStyle(
            TableStyle(other_charges_style)
        )
        content.append(other_charges_report)
        content.append(Spacer(1, 15))


    # ========================================================
    # NOTE
    # ========================================================

    note_text = (
        "<b>Note:</b> Total AWS Cost includes all AWS Cost Explorer "
        "UnblendedCost record types, including usage, credits, taxes, "
        "and refunds. Usage, Credit, and Usage + Credits columns are shown "
        "separately for reference."
        if include_credits else
        "<b>Note:</b> This report includes only AWS Cost Explorer "
        "UnblendedCost usage records. Credits, taxes, refunds, "
        "and other Cost Explorer record types are excluded."
    )

    note_table = Table(
        [
            [
                Paragraph(
                    note_text,
                    small_style
                )
            ]
        ],
        colWidths=[
            160 * mm
        ]
    )

    note_table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), LIGHT_BLUE),
            ("BOX", (0, 0), (-1, -1), 0.7, BLUE),

            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),

            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),

            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")
        ])
    )

    content.append(note_table)


    # ========================================================
    # BUILD PDF
    # ========================================================

    document.build(content)

    return filename
