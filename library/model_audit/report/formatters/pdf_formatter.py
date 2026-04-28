"""
model_audit.report.formatters.pdf_formatter — PDF Export
=========================================================

Export reports to PDF format with charts and professional formatting.
"""

from __future__ import annotations

from pathlib import Path
from ...models import ModelAuditReport
from .string_formatter import export_string


def export_pdf(
    report: ModelAuditReport,
    output_path: str | Path,
) -> None:
    """
    Export report to PDF format with charts.
    
    Args:
        report: The ModelAuditReport to export.
        output_path: Path to save the PDF file.
        
    Raises:
        ImportError: If reportlab is not installed.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
        from reportlab.lib import colors
    except ImportError:
        raise ImportError(
            "PDF export requires reportlab. Install it with: pip install reportlab"
        )
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=1,  # Center
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=12,
    )
    
    # Title
    elements.append(Paragraph("MODEL FAIRNESS AUDIT REPORT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Overview Section
    elements.append(Paragraph("Overview", heading_style))
    overview_data = [
        ["Model Name:", report.model_name],
        ["Model Type:", report.model_type.value],
        ["Test Samples:", f"{report.test_sample_count:,}"],
        ["Protected Attributes:", ", ".join(report.protected_attributes)],
        ["Overall Severity:", report.overall_severity.value],
    ]
    overview_table = Table(overview_data, colWidths=[2*inch, 4*inch])
    overview_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(overview_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Findings Summary
    elements.append(Paragraph("Findings Summary", heading_style))
    critical = sum(1 for f in report.findings if f.severity.value == "CRITICAL")
    moderate = sum(1 for f in report.findings if f.severity.value == "MODERATE")
    low = sum(1 for f in report.findings if f.severity.value == "LOW")
    
    findings_data = [
        ["Severity", "Count"],
        ["Critical", str(critical)],
        ["Moderate", str(moderate)],
        ["Low", str(low)],
    ]
    findings_table = Table(findings_data, colWidths=[3*inch, 3*inch])
    findings_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
    ]))
    elements.append(findings_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Fairness Scorecard
    elements.append(Paragraph("Fairness Scorecard", heading_style))
    scorecard_data = [["Metric", "Value", "Threshold", "Status"]]
    for metric_name, result in list(report.scorecard.items())[:10]:
        status = "PASS" if result.passed else "FAIL"
        scorecard_data.append([
            result.metric_name[:30],
            f"{result.value:.4f}",
            f"{result.threshold:.4f}",
            status,
        ])
    
    scorecard_table = Table(scorecard_data, colWidths=[2.5*inch, 1.2*inch, 1.2*inch, 1.1*inch])
    scorecard_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(scorecard_table)
    elements.append(PageBreak())
    
    # Counterfactual Results
    elements.append(Paragraph("Counterfactual Testing", heading_style))
    cf = report.counterfactual_result
    cf_data = [
        ["Metric", "Value"],
        ["Flip Rate", f"{cf.flip_rate:.2%}"],
        ["Total Flips", f"{cf.total_flips:,}"],
        ["Total Comparisons", f"{cf.total_comparisons:,}"],
    ]
    cf_table = Table(cf_data, colWidths=[3*inch, 3*inch])
    cf_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
    ]))
    elements.append(cf_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Key Findings
    elements.append(Paragraph("Key Findings", heading_style))
    for i, finding in enumerate(report.findings[:5], 1):
        finding_text = f"<b>{i}. [{finding.severity.value}] {finding.title}</b><br/>{finding.description}"
        elements.append(Paragraph(finding_text, styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    # Mitigation Recommendations
    if report.mitigation_options:
        elements.append(PageBreak())
        elements.append(Paragraph("Recommended Mitigations", heading_style))
        for i, mitigation in enumerate(report.mitigation_options[:5], 1):
            retrain = " (requires retraining)" if mitigation.requires_retraining else ""
            mitigation_text = f"<b>{i}. {mitigation.strategy_name}{retrain}</b><br/>{mitigation.description}<br/><i>Expected Impact: {mitigation.expected_impact}</i>"
            elements.append(Paragraph(mitigation_text, styles['Normal']))
            elements.append(Spacer(1, 0.15*inch))
    
    # Build PDF
    doc.build(elements)
    print(f"PDF report exported to: {output_path}")


__all__ = ["export_pdf"]
