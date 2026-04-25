"""
agent_audit.report.formatters.pdf_formatter — PDF Export
=========================================================

Export reports to PDF format with charts and tables.
"""

from __future__ import annotations

from pathlib import Path
import io

from agent_audit.models import AgentAuditReport
from agent_audit.report.sections import (
    build_health_section,
    build_results_section,
    build_interpretation_section,
)


def export_pdf(report: AgentAuditReport, output_path: str | Path) -> None:
    """
    Export report to PDF format with charts and tables.
    
    Args:
        report: The AgentAuditReport to export.
        output_path: Path to save the PDF file.
    
    Raises:
        ImportError: If reportlab or matplotlib are not installed.
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        from reportlab.lib import colors
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
            PageBreak, Image
        )
        from reportlab.lib.enums import TA_CENTER
        import matplotlib.pyplot as plt
    except ImportError:
        raise ImportError(
            "PDF export requires reportlab and matplotlib. "
            "Install with: pip install reportlab matplotlib"
        )
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create PDF document
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=30,
        alignment=TA_CENTER,
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
    story.append(Paragraph("Agent Bias Audit Report", title_style))
    story.append(Spacer(1, 0.2 * inch))
    
    # Section 1: Health & Metadata
    health = build_health_section(report)
    story.append(Paragraph("1. Health & Metadata", heading_style))
    
    health_data = [
        ["Audit ID", health['audit_id']],
        ["Timestamp", health['timestamp']],
        ["Mode", health['mode']],
        ["Duration", health['duration_formatted']],
        ["Total API Calls", str(health['api_calls']['total'])],
        ["Estimated Tokens", f"{health['estimated_tokens']['total']:,}"],
        ["Personas Tested", str(health['performance']['personas_tested'])],
    ]
    
    health_table = Table(health_data, colWidths=[2.5*inch, 4*inch])
    health_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(health_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Section 2: Results Overview
    results = build_results_section(report)
    story.append(Paragraph("2. Results Overview", heading_style))
    
    # Severity badge with color
    severity = report.overall_severity
    severity_color = {
        "CRITICAL": colors.red,
        "MODERATE": colors.orange,
        "LOW": colors.yellow,
        "CLEAR": colors.green,
    }.get(severity, colors.grey)
    
    results_data = [
        ["Overall Severity", severity],
        ["Overall CFR", results['overall']['overall_cfr_percent']],
        ["Benchmark Range", f"{results['overall']['benchmark_range']['min_percent']} - {results['overall']['benchmark_range']['max_percent']}"],
        ["Total Findings", str(results['overall']['total_findings'])],
    ]
    
    results_table = Table(results_data, colWidths=[2.5*inch, 4*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('BACKGROUND', (1, 0), (1, 0), severity_color),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))
    story.append(results_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Chart: Severity breakdown
    if results['severity_breakdown']:
        fig, ax = plt.subplots(figsize=(6, 4))
        severities = [k for k, v in results['severity_breakdown'].items() if v > 0]
        counts = [v for k, v in results['severity_breakdown'].items() if v > 0]
        colors_map = [
            'red' if s == 'CRITICAL' else 
            'orange' if s == 'MODERATE' else 
            'yellow' if s == 'LOW' else 
            'green' 
            for s in severities
        ]
        
        ax.bar(severities, counts, color=colors_map, alpha=0.7)
        ax.set_xlabel('Severity')
        ax.set_ylabel('Count')
        ax.set_title('Findings by Severity')
        ax.grid(axis='y', alpha=0.3)
        
        # Save chart to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        # Add to PDF
        img = Image(buf, width=5*inch, height=3.3*inch)
        story.append(img)
        story.append(Spacer(1, 0.3 * inch))
    
    # Section 3: Findings Detail
    story.append(PageBreak())
    story.append(Paragraph("3. Detailed Findings", heading_style))
    
    if report.findings:
        findings_data = [["Attribute", "Metric", "Value", "P-Value", "Severity"]]
        for finding in report.findings[:20]:  # Limit to top 20
            findings_data.append([
                finding.attribute,
                finding.metric,
                f"{finding.value:.4f}",
                f"{finding.p_value:.4f}",
                finding.severity,
            ])
        
        findings_table = Table(findings_data, colWidths=[1.3*inch, 1.3*inch, 1*inch, 1*inch, 1*inch])
        findings_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
        ]))
        story.append(findings_table)
    else:
        story.append(Paragraph("No significant bias findings detected.", styles['Normal']))
    
    story.append(Spacer(1, 0.3 * inch))
    
    # Section 4: Remediation
    interp = build_interpretation_section(report)
    if interp['prompt_suggestions']:
        story.append(PageBreak())
        story.append(Paragraph("4. Remediation Suggestions", heading_style))
        
        for i, suggestion in enumerate(interp['prompt_suggestions'][:5], 1):  # Top 5
            story.append(Paragraph(f"<b>Suggestion {i}</b> [{suggestion['confidence'].upper()}]", styles['Normal']))
            story.append(Paragraph(suggestion['suggestion_text'], styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))
    
    # Build PDF
    doc.build(story)


__all__ = ["export_pdf"]
