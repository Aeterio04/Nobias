"""
agent_audit.report.formatters.pdf_formatter — Comprehensive PDF Export
=======================================================================

Export detailed audit reports to PDF with EDA insights, charts, and tables.
Includes EEOC compliance, stability analysis, and benchmark comparisons.
"""

from __future__ import annotations

from pathlib import Path
import io
from typing import Any

from agent_audit.models import AgentAuditReport
from agent_audit.report.sections import (
    build_health_section,
    build_config_section,
    build_results_section,
    build_interpretation_section,
    build_compliance_section,
    build_validity_section,
)


def export_pdf(report: AgentAuditReport, output_path: str | Path) -> None:
    """
    Export comprehensive audit report to PDF format.
    
    Includes:
    - Executive summary with risk assessment
    - EEOC compliance analysis with AIR
    - Statistical validity (stability, confidence intervals)
    - Per-attribute deep dive with charts
    - Remediation recommendations
    
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
            PageBreak, Image, KeepTogether
        )
        from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        raise ImportError(
            "PDF export requires reportlab and matplotlib. "
            "Install with: pip install reportlab matplotlib"
        )
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build all sections
    health = build_health_section(report)
    config = build_config_section(report)
    results = build_results_section(report)
    interp = build_interpretation_section(report)
    compliance = build_compliance_section(report)
    validity = build_validity_section(report)
    
    # Create PDF document
    doc = SimpleDocTemplate(str(output_path), pagesize=letter,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=26,
        textColor=colors.HexColor('#1a1a1a'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold',
    )
    
    subtitle_style = ParagraphStyle(
        'CustomSubtitle',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#7f8c8d'),
        spaceAfter=30,
        alignment=TA_CENTER,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
        spaceBefore=20,
        fontName='Helvetica-Bold',
    )
    
    subheading_style = ParagraphStyle(
        'CustomSubheading',
        parent=styles['Heading3'],
        fontSize=13,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=8,
        spaceBefore=12,
        fontName='Helvetica-Bold',
    )
    
    # ═══════════════════════════════════════════════════════════════
    # TITLE PAGE
    # ═══════════════════════════════════════════════════════════════
    
    story.append(Spacer(1, 0.5 * inch))
    story.append(Paragraph("Agent Bias Audit Report", title_style))
    story.append(Paragraph(f"Audit ID: {report.audit_id}", subtitle_style))
    
    # Executive Summary Box
    severity_color = {
        "CRITICAL": colors.HexColor('#e74c3c'),
        "MODERATE": colors.HexColor('#f39c12'),
        "LOW": colors.HexColor('#f1c40f'),
        "CLEAR": colors.HexColor('#27ae60'),
    }.get(report.overall_severity, colors.grey)
    
    exec_summary_data = [
        ["EXECUTIVE SUMMARY", ""],
        ["Overall Verdict", report.overall_severity],
        ["Overall CFR", f"{report.overall_cfr:.2%}"],
        ["Benchmark Range", f"{report.benchmark_range[0]:.1%} - {report.benchmark_range[1]:.1%}"],
        ["Total Findings", str(len(report.findings))],
        ["Personas Tested", str(len(report.persona_results))],
        ["Duration", health['duration_formatted']],
    ]
    
    exec_table = Table(exec_summary_data, colWidths=[3*inch, 3.5*inch])
    exec_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('BACKGROUND', (1, 1), (1, 1), severity_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(exec_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # EEOC Compliance Summary
    if compliance and compliance.get('overall_status') != 'not_computed':
        story.append(Paragraph("EEOC Compliance Status", subheading_style))
        
        eeoc_status = compliance['overall_status']
        eeoc_color = {
            'COMPLIANT': colors.HexColor('#27ae60'),
            'WARNING': colors.HexColor('#f39c12'),
            'VIOLATION': colors.HexColor('#e74c3c'),
        }.get(eeoc_status, colors.grey)
        
        eeoc_data = [["EEOC Status", eeoc_status]]
        eeoc_table = Table(eeoc_data, colWidths=[3*inch, 3.5*inch])
        eeoc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (1, 0), (1, 0), eeoc_color),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('PADDING', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(eeoc_table)
        story.append(Spacer(1, 0.2 * inch))
    
    # Stability Summary
    if validity and 'stability' in validity:
        stab = validity['stability']
        story.append(Paragraph("Stochastic Stability", subheading_style))
        
        stab_data = [[
            "SSS Score", f"{stab['overall_sss']:.2f}",
            "Classification", stab['classification'],
            "Trustworthy", "Yes" if stab['trustworthy'] else "No"
        ]]
        stab_table = Table(stab_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
        stab_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#ecf0f1')),
            ('BACKGROUND', (2, 0), (2, 0), colors.HexColor('#ecf0f1')),
            ('FONTNAME', (0, 0), (0, 0), 'Helvetica-Bold'),
            ('FONTNAME', (2, 0), (2, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ]))
        story.append(stab_table)
    
    story.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 1: AUDIT METADATA
    # ═══════════════════════════════════════════════════════════════
    
    story.append(Paragraph("1. Audit Metadata", heading_style))
    
    metadata_data = [
        ["Audit ID", health['audit_id']],
        ["Timestamp", health['timestamp']],
        ["Mode", health['mode'].upper()],
        ["Duration", health['duration_formatted']],
        ["API Calls", f"{health['api_calls']['total']} total ({health['api_calls']['per_persona']:.1f} per persona)"],
        ["Estimated Tokens", f"{health['estimated_tokens']['total']:,} tokens"],
        ["Model", report.model_fingerprint.model_id if report.model_fingerprint else "N/A"],
        ["Backend", report.model_fingerprint.backend if report.model_fingerprint else "N/A"],
        ["Temperature", str(report.model_fingerprint.temperature) if report.model_fingerprint else "N/A"],
    ]
    
    metadata_table = Table(metadata_data, colWidths=[2.5*inch, 4*inch])
    metadata_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(metadata_table)
    story.append(Spacer(1, 0.2 * inch))
    
    # Test Configuration
    story.append(Paragraph("Test Configuration", subheading_style))
    
    config_data = [
        ["Protected Attributes", ", ".join(config['protected_attributes'])],
        ["Total Personas", str(config['persona_generation']['total_personas'])],
        ["Test Types", ", ".join(f"{k}: {v}" for k, v in config['test_variants'].items() if v > 0)],
    ]
    
    config_table = Table(config_data, colWidths=[2.5*inch, 4*inch])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(config_table)
    
    story.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 2: STATISTICAL RESULTS
    # ═══════════════════════════════════════════════════════════════
    
    story.append(Paragraph("2. Statistical Results", heading_style))
    
    # Overall metrics
    story.append(Paragraph("Overall Metrics", subheading_style))
    
    overall_data = [
        ["Metric", "Value", "Assessment"],
        ["Overall CFR", results['overall']['overall_cfr_percent'], results['overall']['severity']],
        ["Benchmark Range", f"{results['overall']['benchmark_range']['min_percent']} - {results['overall']['benchmark_range']['max_percent']}", "Industry Standard"],
        ["Total Findings", str(results['overall']['total_findings']), f"{results['severity_breakdown'].get('CRITICAL', 0)} Critical"],
    ]
    
    overall_table = Table(overall_data, colWidths=[2*inch, 2*inch, 2.5*inch])
    overall_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
    ]))
    story.append(overall_table)
    story.append(Spacer(1, 0.3 * inch))
    
    # Chart: Decision Distribution
    if results['decision_statistics']:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Decision distribution pie chart
        dec_dist = results['decision_statistics']['distribution']
        labels = [k.capitalize() for k, v in dec_dist.items() if v > 0]
        sizes = [v for v in dec_dist.values() if v > 0]
        colors_pie = ['#27ae60', '#e74c3c', '#95a5a6'][:len(sizes)]
        
        ax1.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors_pie, startangle=90)
        ax1.set_title('Decision Distribution')
        
        # Severity breakdown bar chart
        sev_labels = [k for k, v in results['severity_breakdown'].items() if v > 0]
        sev_counts = [v for k, v in results['severity_breakdown'].items() if v > 0]
        sev_colors = ['#e74c3c' if s == 'CRITICAL' else '#f39c12' if s == 'MODERATE' else '#f1c40f' if s == 'LOW' else '#27ae60' for s in sev_labels]
        
        ax2.bar(sev_labels, sev_counts, color=sev_colors, alpha=0.7)
        ax2.set_xlabel('Severity')
        ax2.set_ylabel('Count')
        ax2.set_title('Findings by Severity')
        ax2.grid(axis='y', alpha=0.3)
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close()
        
        img = Image(buf, width=6.5*inch, height=2.6*inch)
        story.append(img)
        story.append(Spacer(1, 0.3 * inch))
    
    story.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 3: EEOC COMPLIANCE
    # ═══════════════════════════════════════════════════════════════
    
    if compliance and compliance.get('overall_status') != 'not_computed':
        story.append(Paragraph("3. EEOC Compliance Analysis", heading_style))
        
        story.append(Paragraph(
            "The EEOC 80% Rule (29 CFR Part 1607) states that if the selection rate for any protected group is less than 80% of the rate for the highest group, this constitutes prima facie evidence of adverse impact.",
            styles['Normal']
        ))
        story.append(Spacer(1, 0.2 * inch))
        
        # Per-attribute EEOC results
        for attr, air_data in compliance['eeoc_air_by_attribute'].items():
            story.append(Paragraph(f"{attr.capitalize()} - AIR Analysis", subheading_style))
            
            legal_color = {
                'COMPLIANT': colors.HexColor('#27ae60'),
                'WARNING': colors.HexColor('#f39c12'),
                'VIOLATION': colors.HexColor('#e74c3c'),
            }.get(air_data['legal_status'], colors.grey)
            
            air_data_table = [
                ["Metric", "Value"],
                ["Adverse Impact Ratio (AIR)", f"{air_data['air_percent']} ({air_data['air']:.4f})"],
                ["Legal Status", air_data['legal_status']],
                ["Risk Level", air_data['risk_level']],
                ["Reference Group", f"{air_data['reference_group']} ({air_data['highest_rate']:.2%})"],
                ["Protected Group", f"{air_data['protected_group']} ({air_data['lowest_rate']:.2%})"],
                ["EEOC Threshold", "80%"],
            ]
            
            air_table = Table(air_data_table, colWidths=[3*inch, 3.5*inch])
            air_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (1, 2), (1, 2), legal_color),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(air_table)
            story.append(Spacer(1, 0.2 * inch))
        
        # Violations and warnings
        if compliance['violations']:
            story.append(Paragraph("⚠ Legal Violations Detected", subheading_style))
            for violation in compliance['violations']:
                story.append(Paragraph(f"• {violation['message']}", styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))
        
        if compliance['warnings']:
            story.append(Paragraph("⚠ Warnings", subheading_style))
            for warning in compliance['warnings']:
                story.append(Paragraph(f"• {warning['message']}", styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))
        
        story.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 4: STATISTICAL VALIDITY
    # ═══════════════════════════════════════════════════════════════
    
    if validity:
        story.append(Paragraph("4. Statistical Validity & Confidence", heading_style))
        
        # Stability analysis
        if 'stability' in validity:
            stab = validity['stability']
            story.append(Paragraph("Stochastic Stability Score (SSS)", subheading_style))
            
            stab_data = [
                ["Metric", "Value"],
                ["Overall SSS", f"{stab['overall_sss']:.4f}"],
                ["Classification", stab['classification']],
                ["Trustworthy", "Yes" if stab['trustworthy'] else "No"],
                ["Mean Persona SSS", f"{stab['mean_persona_sss']:.4f}"],
                ["Unstable Personas", str(stab['unstable_personas'])],
            ]
            
            stab_table = Table(stab_data, colWidths=[3*inch, 3.5*inch])
            stab_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(stab_table)
            story.append(Paragraph(stab['interpretation'], styles['Normal']))
            story.append(Spacer(1, 0.2 * inch))
        
        # Bias-Adjusted CFR
        if 'bias_adjusted_cfr' in validity and validity['bias_adjusted_cfr']:
            story.append(Paragraph("Bias-Adjusted CFR (BA-CFR)", subheading_style))
            
            ba_cfr_data = [["Attribute", "Raw CFR", "BA-CFR", "Noise Removed"]]
            for ba_finding in validity['bias_adjusted_cfr']:
                ba_cfr_data.append([
                    ba_finding['attribute'],
                    f"{ba_finding['raw_cfr']:.4f}",
                    f"{ba_finding['ba_cfr']:.4f}",
                    f"{ba_finding['noise_removed']:.4f}",
                ])
            
            ba_cfr_table = Table(ba_cfr_data, colWidths=[2*inch, 1.5*inch, 1.5*inch, 1.5*inch])
            ba_cfr_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(ba_cfr_table)
            story.append(Spacer(1, 0.2 * inch))
        
        # Bonferroni correction
        if 'bonferroni' in validity:
            bonf = validity['bonferroni']
            story.append(Paragraph("Multiple Testing Correction", subheading_style))
            
            bonf_data = [
                ["Original α", f"{bonf['original_alpha']:.4f}"],
                ["Corrected α (Bonferroni)", f"{bonf['corrected_alpha']:.6f}"],
                ["Number of Tests", str(bonf['n_tests'])],
                ["Significant After Correction", str(bonf['significant_after_correction'])],
            ]
            
            bonf_table = Table(bonf_data, colWidths=[3*inch, 3.5*inch])
            bonf_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('PADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ]))
            story.append(bonf_table)
        
        story.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 5: DETAILED FINDINGS
    # ═══════════════════════════════════════════════════════════════
    
    story.append(Paragraph("5. Detailed Findings", heading_style))
    
    if report.findings:
        # Group findings by attribute
        findings_by_attr = {}
        for finding in report.findings:
            if finding.attribute not in findings_by_attr:
                findings_by_attr[finding.attribute] = []
            findings_by_attr[finding.attribute].append(finding)
        
        for attr, findings in findings_by_attr.items():
            story.append(Paragraph(f"{attr.capitalize()} Findings", subheading_style))
            
            findings_data = [["Comparison", "Metric", "Value", "P-Value", "Severity"]]
            for finding in findings[:10]:  # Limit to top 10 per attribute
                findings_data.append([
                    finding.comparison,
                    finding.metric.upper(),
                    f"{finding.value:.4f}",
                    f"{finding.p_value:.4f}",
                    finding.severity,
                ])
            
            findings_table = Table(findings_data, colWidths=[1.8*inch, 1*inch, 1*inch, 1*inch, 0.8*inch])
            findings_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('PADDING', (0, 0), (-1, -1), 6),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')]),
            ]))
            story.append(findings_table)
            story.append(Spacer(1, 0.2 * inch))
    else:
        story.append(Paragraph("✓ No significant bias findings detected.", styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    
    story.append(PageBreak())
    
    # ═══════════════════════════════════════════════════════════════
    # SECTION 6: REMEDIATION
    # ═══════════════════════════════════════════════════════════════
    
    story.append(Paragraph("6. Remediation & Recommendations", heading_style))
    
    if interp['interpretation']['overall_assessment']:
        story.append(Paragraph("Overall Assessment", subheading_style))
        story.append(Paragraph(interp['interpretation']['overall_assessment'], styles['Normal']))
        story.append(Spacer(1, 0.2 * inch))
    
    if interp['prompt_suggestions']:
        story.append(Paragraph("Prompt Suggestions", subheading_style))
        
        for i, suggestion in enumerate(interp['prompt_suggestions'][:5], 1):
            story.append(Paragraph(
                f"<b>Suggestion {i}</b> [Confidence: {suggestion['confidence'].upper()}]",
                styles['Normal']
            ))
            story.append(Paragraph(suggestion['suggestion_text'], styles['Normal']))
            story.append(Paragraph(f"<i>Rationale: {suggestion['rationale']}</i>", styles['Normal']))
            story.append(Spacer(1, 0.15 * inch))
    else:
        story.append(Paragraph("No remediation suggestions needed - agent shows minimal bias.", styles['Normal']))
    
    # Build PDF
    doc.build(story)


__all__ = ["export_pdf"]
