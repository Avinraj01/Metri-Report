import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from app.models import Report, TestSession, Instrument, ComplianceResult, CalculationResult

def generate_pdf_report(report: Report, output_path: str) -> str:
    """
    Generates an official-grade PDF test report strictly complying with OIML R 76-1:2006 format.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()
    
    # Custom styles
    header_title_style = ParagraphStyle(
        'GovHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#0f172a')
    )
    header_sub_style = ParagraphStyle(
        'GovSubHeader',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=13,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#334155')
    )
    doc_title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        leading=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=10
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=12,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#1e293b')
    )
    body_bold = ParagraphStyle(
        'BodyDarkBold',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0f172a')
    )
    disclaimer_style = ParagraphStyle(
        'Disclaimer',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=8,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor('#64748b')
    )

    story = []
    session: TestSession = report.session
    instrument: Instrument = session.instrument

    # Official Header
    story.append(Paragraph("GOVERNMENT OF INDIA", header_title_style))
    story.append(Paragraph("MINISTRY OF CONSUMER AFFAIRS, FOOD & PUBLIC DISTRIBUTION", header_sub_style))
    story.append(Paragraph("DEPARTMENT OF CONSUMER AFFAIRS — LEGAL METROLOGY DIVISION", header_sub_style))
    story.append(Paragraph("NATIONAL LEGAL METROLOGY TESTING CENTRE", header_sub_style))
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e3a8a'), spaceAfter=15))

    story.append(Paragraph("TYPE EVALUATION TEST REPORT", doc_title_style))
    story.append(Paragraph("<b>Non-Automatic Weighing Instrument (NAWI) as per OIML R 76-1:2006 (E)</b>", header_sub_style))
    story.append(Spacer(1, 15))

    # Metadata Banner Table
    overall_val = report.overall_result.value if hasattr(report.overall_result, 'value') else str(report.overall_result)
    if overall_val == "MANUAL_REVIEW":
        overall_display = "MANUAL REVIEW / INCOMPLETE"
        overall_color = "#b45309"
    elif overall_val == "PASS":
        overall_display = "PASS"
        overall_color = "#166534"
    elif overall_val == "FAIL":
        overall_display = "FAIL"
        overall_color = "#991b1b"
    else:
        overall_display = overall_val.replace('_', ' ')
        overall_color = "#64748b"

    status_val = report.status.value if hasattr(report.status, 'value') else str(report.status)
    status_color = "#166534" if status_val in ["APPROVED", "FINALIZED"] else ("#991b1b" if status_val == "CHANGES_REQUESTED" else "#b45309")

    banner_data = [
        [
            Paragraph(f"<b>Report Number:</b> {report.report_number}", body_style),
            Paragraph(f"<b>Date:</b> {datetime.utcnow().strftime('%d-%b-%Y')}", body_style)
        ],
        [
            Paragraph(f"<b>Session ID:</b> {session.session_number}", body_style),
            Paragraph(f"<b>Report Status:</b> <font color='{status_color}'><b>{status_val} (v{report.version})</b></font>", body_style)
        ],
        [
            Paragraph(f"<b>Overall Result:</b> <font color='{overall_color}'><b>{overall_display}</b></font>", body_style),
            Paragraph("<b>Standard:</b> OIML R 76-1 Edition 2006 (E)", body_style)
        ]
    ]
    banner_table = Table(banner_data, colWidths=[260, 260])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 15))

    # 1. Applicant and Manufacturer
    story.append(Paragraph("1. Applicant & Manufacturer Information", section_heading))
    party_data = [
        [Paragraph("<b>Applicant Name:</b>", body_bold), Paragraph(instrument.applicant_name, body_style)],
        [Paragraph("<b>Applicant Address:</b>", body_bold), Paragraph(instrument.applicant_address or "N/A", body_style)],
        [Paragraph("<b>Manufacturer:</b>", body_bold), Paragraph(instrument.manufacturer, body_style)],
        [Paragraph("<b>Manufacturer Address:</b>", body_bold), Paragraph(instrument.manufacturer_address or "N/A", body_style)],
        [Paragraph("<b>Country of Manufacture:</b>", body_bold), Paragraph(instrument.country_of_manufacture, body_style)],
    ]
    party_table = Table(party_data, colWidths=[150, 370])
    party_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(party_table)
    story.append(Spacer(1, 12))

    # 2. Instrument Metrological Characteristics
    story.append(Paragraph("2. Technical & Metrological Characteristics", section_heading))
    metro_data = [
        [Paragraph("<b>Instrument Model:</b>", body_bold), Paragraph(instrument.model, body_style), Paragraph("<b>Accuracy Class:</b>", body_bold), Paragraph(f"Class {instrument.accuracy_class.value}", body_style)],
        [Paragraph("<b>Max Capacity (Max):</b>", body_bold), Paragraph(f"{instrument.max_capacity} {instrument.unit}", body_style), Paragraph("<b>Min Capacity (Min):</b>", body_bold), Paragraph(f"{instrument.min_capacity} {instrument.unit}", body_style)],
        [Paragraph("<b>Scale Interval (e):</b>", body_bold), Paragraph(f"{instrument.e_value} {instrument.unit}", body_style), Paragraph("<b>Division (d):</b>", body_bold), Paragraph(f"{instrument.d_value} {instrument.unit}", body_style)],
        [Paragraph("<b>Interval Count (n):</b>", body_bold), Paragraph(str(instrument.n_intervals), body_style), Paragraph("<b>Serial Number:</b>", body_bold), Paragraph(instrument.serial_number, body_style)],
        [Paragraph("<b>Load Receptor:</b>", body_bold), Paragraph(f"{instrument.load_receptor_type} ({instrument.num_support_points} pts)", body_style), Paragraph("<b>Electronic:</b>", body_bold), Paragraph("Yes" if instrument.is_electronic else "No", body_style)],
        [Paragraph("<b>Power Supply:</b>", body_bold), Paragraph(instrument.power_supply, body_style), Paragraph("<b>Temperature Range:</b>", body_bold), Paragraph(f"{instrument.temp_min}°C to {instrument.temp_max}°C", body_style)],
    ]
    metro_table = Table(metro_data, colWidths=[130, 130, 130, 130])
    metro_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(metro_table)
    story.append(Spacer(1, 12))

    # 3. Laboratory Environmental Conditions
    story.append(Paragraph("3. Laboratory Environmental Conditions", section_heading))
    env_data = [
        [Paragraph("<b>Ambient Temperature:</b>", body_bold), Paragraph(f"{session.ambient_temp} °C", body_style), Paragraph("<b>Relative Humidity:</b>", body_bold), Paragraph(f"{session.ambient_humidity} %", body_style)],
        [Paragraph("<b>Atmospheric Pressure:</b>", body_bold), Paragraph(f"{session.ambient_pressure} hPa", body_style), Paragraph("<b>Mains Voltage:</b>", body_bold), Paragraph(f"{session.ambient_voltage} V AC", body_style)],
    ]
    env_table = Table(env_data, colWidths=[130, 130, 130, 130])
    env_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f8fafc')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(env_table)
    story.append(Spacer(1, 12))

    # 4. Test Applicability Matrix
    story.append(Paragraph("4. OIML R-76 Test Applicability & Coverage Matrix", section_heading))
    from sqlalchemy.orm import object_session
    from app.models import TestCatalogItem
    from app.rules.applicability import ApplicabilityEngine

    db = object_session(report)
    catalog_items = db.query(TestCatalogItem).filter(TestCatalogItem.is_active == True).all() if db else []
    applicable_matrix = ApplicabilityEngine.get_applicable_tests(instrument, catalog_items) if catalog_items else []
    executed_codes = {cr.test_code: cr for cr in session.compliance_results}

    app_rows = [[
        Paragraph("<b>Code</b>", body_bold),
        Paragraph("<b>Clause</b>", body_bold),
        Paragraph("<b>Test Procedure</b>", body_bold),
        Paragraph("<b>Applicability</b>", body_bold),
        Paragraph("<b>Execution</b>", body_bold),
        Paragraph("<b>Status</b>", body_bold),
    ]]

    for item in applicable_matrix:
        is_app = item["is_applicable"]
        t_code = item["test_code"]
        is_exec = t_code in executed_codes
        
        if is_exec:
            exec_status_text = "<font color='#166534'><b>EXECUTED</b></font>"
            comp_obj = executed_codes[t_code]
            res_color = "#166534" if comp_obj.status.value == "PASS" else ("#991b1b" if comp_obj.status.value == "FAIL" else "#b45309")
            comp_status_text = f"<font color='{res_color}'><b>{comp_obj.status.value}</b></font>"
        elif not is_app:
            exec_status_text = "<font color='#64748b'>N/A</font>"
            comp_status_text = "<font color='#64748b'>NOT APPLICABLE</font>"
        else:
            exec_status_text = "<font color='#b45309'>NOT TESTED</font>"
            comp_status_text = "<font color='#b45309'>PENDING</font>"

        app_badge = "<font color='#166534'><b>APPLICABLE</b></font>" if is_app else "<font color='#64748b'>EXEMPT / N/A</font>"

        app_rows.append([
            Paragraph(t_code, body_style),
            Paragraph(item["clause"], body_style),
            Paragraph(item["test_name"], body_style),
            Paragraph(app_badge, body_style),
            Paragraph(exec_status_text, body_style),
            Paragraph(comp_status_text, body_style),
        ])

    if len(app_rows) == 1:
        app_rows.append([Paragraph("No catalog tests defined.", body_style), "", "", "", "", ""])

    app_table = Table(app_rows, colWidths=[55, 80, 155, 80, 75, 75])
    app_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1f5f9')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    story.append(app_table)
    story.append(Spacer(1, 12))

    # 5. Compliance & Test Summary Table
    story.append(Paragraph("5. Summary of Executed Test Results & Metrological Compliance", section_heading))
    comp_results = session.compliance_results
    
    table_rows = [[
        Paragraph("<b>Clause</b>", body_bold),
        Paragraph("<b>Test Description</b>", body_bold),
        Paragraph("<b>Observed Result</b>", body_bold),
        Paragraph("<b>Permissible Limit</b>", body_bold),
        Paragraph("<b>Result</b>", body_bold),
    ]]

    for cr in comp_results:
        res_color = "#166534" if cr.status.value == "PASS" else ("#991b1b" if cr.status.value == "FAIL" else "#b45309")
        table_rows.append([
            Paragraph(cr.clause, body_style),
            Paragraph(cr.test_name, body_style),
            Paragraph(cr.observed_summary, body_style),
            Paragraph(cr.permissible_summary, body_style),
            Paragraph(f"<font color='{res_color}'><b>{cr.status.value}</b></font>", body_style)
        ])

    if len(table_rows) == 1:
        table_rows.append([Paragraph("No tests recorded yet.", body_style), "", "", "", ""])

    comp_table = Table(table_rows, colWidths=[80, 140, 130, 110, 60])
    comp_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e2e8f0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(comp_table)
    story.append(Spacer(1, 15))

    # 6. Signatures and Approvals
    story.append(Paragraph("6. Review & Authorization", section_heading))
    
    # Reviewer status line
    if report.status.value in ["APPROVED", "FINALIZED"]:
        rev_status_html = f"<br/><font color='#166534'><b>Status: {report.status.value}</b></font>"
    elif report.status.value == "CHANGES_REQUESTED":
        rev_status_html = "<br/><font color='#991b1b'><b>Status: CHANGES REQUESTED</b></font>"
    elif report.status.value in ["READY_FOR_REVIEW", "UNDER_REVIEW"]:
        rev_status_html = f"<br/><font color='#b45309'><b>Status: {report.status.value.replace('_', ' ')}</b> (Pending Review)</font>"
    else:
        rev_status_html = "<br/>Status: <i>DRAFT</i>"

    # Approver status line
    if report.status.value == "FINALIZED":
        final_date_str = f"Date: {report.finalized_at.strftime('%d-%b-%Y')}" if report.finalized_at else "Status: FINALIZED"
        app_status_html = f"<br/><font color='#166534'><b>Status: FINALIZED / SEALED</b></font><br/>{final_date_str}"
    elif report.status.value == "APPROVED":
        app_status_html = "<br/><font color='#166534'><b>Status: APPROVED</b> (Pending Final Seal)</font>"
    else:
        app_status_html = "<br/>Status: <i>Pending Final Approval</i>"

    sig_data = [
        [
            Paragraph(f"<b>Evaluated By:</b><br/><br/>_______________________<br/><b>Test Engineer</b><br/>Date: {datetime.utcnow().strftime('%d-%b-%Y')}", body_style),
            Paragraph(f"<b>Reviewed By:</b><br/><br/>_______________________<br/><b>Technical Reviewer</b>{rev_status_html}", body_style),
            Paragraph(f"<b>Approved By:</b><br/><br/>_______________________<br/><b>Director / Lab In-Charge</b>{app_status_html}", body_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[173, 173, 174])
    sig_table.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#94a3b8')),
        ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(sig_table)
    story.append(Spacer(1, 20))

    # Official Disclaimer
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#94a3b8'), spaceAfter=8))
    story.append(Paragraph(
        "<b>LEGAL DISCLAIMER / NOTICE:</b> This document is a prototype evaluation test report generated by METRIREPORT for SIH 2026. "
        "It does not constitute an official Legal Metrology Model Approval Certificate under Section 22 of the Legal Metrology Act, 2009 without statutory Gazette notification.",
        disclaimer_style
    ))

    doc.build(story)
    return output_path
