"""
PDF formatter for dataset audit reports.
"""

from typing import Dict, Any
from pathlib import Path


class PDFFormatter:
    """Format dataset audit reports as PDF documents."""
    
    @staticmethod
    def format(report_data: Dict[str, Any]) -> bytes:
        """
        Format report data as PDF bytes.
        
        Args:
            report_data: Report data dictionary from generator
        
        Returns:
            PDF bytes
        
        Raises:
            ImportError: If reportlab is not installed
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
                PageBreak, KeepTogether
            )
            from reportlab.lib.enums import TA_CENTER, TA_LEFT
            from io import BytesIO
        except ImportError:
            raise ImportError(
                "PDF export requires reportlab. Install it with: pip install reportlab"
            )
        
        # Create PDF buffer
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
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
        story.append(Paragraph("Dataset Fairness Audit Report", title_style))
        story.append(Spacer(1, 0.3 * inch))
        
        # Health Section
        if 'health' in report_data:
            story.extend(PDFFormatter._format_health_section(report_data['health'], heading_style, styles))
        
        # Config Section
        if 'config' in report_data:
            story.extend(PDFFormatter._format_config_section(report_data['config'], heading_style, styles))
        
        # Representation Section
        if 'representation' in report_data:
            story.extend(PDFFormatter._format_representation_section(report_data['representation'], heading_style, styles))
        
        # Proxy Features Section
        if 'proxy_features' in report_data:
            story.extend(PDFFormatter._format_proxy_section(report_data['proxy_features'], heading_style, styles))
        
        # Findings Section
        if 'findings' in report_data:
            story.extend(PDFFormatter._format_findings_section(report_data['findings'], heading_style, styles))
        
        # Remediation Section
        if 'remediation' in report_data:
            story.extend(PDFFormatter._format_remediation_section(report_data['remediation'], heading_style, styles))
        
        # Compliance Section
        if 'compliance' in report_data:
            story.extend(PDFFormatter._format_compliance_section(report_data['compliance'], heading_style, styles))
        
        # Validity Section
        if 'validity' in report_data:
            story.extend(PDFFormatter._format_validity_section(report_data['validity'], heading_style, styles))
        
        # Build PDF
        doc.build(story)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        return pdf_bytes
    
    @staticmethod
    def _format_health_section(health: Dict, heading_style, styles) -> list:
        """Format health section for PDF."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Health Overview", heading_style))
        
        # Health summary table
        data = [
            ['Metric', 'Value'],
            ['Overall Severity', health.get('overall_severity', 'UNKNOWN')],
            ['Health Score', f"{health.get('health_score', 0)}/100"],
            ['Total Findings', str(health.get('total_findings', 0))],
            ['Critical Findings', str(health.get('critical_findings', 0))],
            ['Moderate Findings', str(health.get('moderate_findings', 0))],
            ['Low Findings', str(health.get('low_findings', 0))],
            ['Proxy Features', str(health.get('proxy_features_detected', 0))],
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    @staticmethod
    def _format_config_section(config: Dict, heading_style, styles) -> list:
        """Format config section for PDF."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Dataset Configuration", heading_style))
        
        data = [
            ['Property', 'Value'],
            ['Dataset Name', config.get('dataset_name', 'Unknown')],
            ['Row Count', f"{config.get('row_count', 0):,}"],
            ['Column Count', str(config.get('column_count', 0))],
            ['Audit Timestamp', config.get('audit_timestamp', 'Unknown')],
        ]
        
        table = Table(data, colWidths=[3*inch, 3*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3 * inch))
        
        return elements
    
    @staticmethod
    def _format_representation_section(representation: Dict, heading_style, styles) -> list:
        """Format representation section for PDF."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Demographic Representation", heading_style))
        
        group_dists = representation.get('group_distributions', {})
        for attr, groups in group_dists.items():
            elements.append(Paragraph(f"<b>{attr}</b>", styles['Normal']))
            
            data = [['Group', 'Count', 'Percentage']]
            for group, stats in groups.items():
                data.append([
                    str(group),
                    f"{stats['count']:,}",
                    f"{stats['percentage']:.1f}%"
                ])
            
            table = Table(data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 0.2 * inch))
        
        return elements
    
    @staticmethod
    def _format_proxy_section(proxy_features: Dict, heading_style, styles) -> list:
        """Format proxy features section for PDF."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Proxy Features", heading_style))
        
        elements.append(Paragraph(
            f"Total Detected: {proxy_features.get('total_proxy_features', 0)} "
            f"(High Risk: {proxy_features.get('high_risk_proxies', 0)}, "
            f"Medium: {proxy_features.get('medium_risk_proxies', 0)}, "
            f"Low: {proxy_features.get('low_risk_proxies', 0)})",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.1 * inch))
        
        proxies = proxy_features.get('proxy_features', [])
        if proxies:
            data = [['Feature', 'Protected Attr', 'Risk', 'Correlation', 'NMI']]
            for proxy in proxies[:10]:  # Top 10
                data.append([
                    proxy['feature'][:20],  # Truncate long names
                    proxy['protected_attribute'],
                    proxy['risk_level'],
                    f"{proxy['correlation_score']:.3f}",
                    f"{proxy['normalized_mutual_info']:.3f}",
                ])
            
            table = Table(data, colWidths=[1.8*inch, 1.5*inch, 0.8*inch, 1*inch, 0.9*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
        
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    @staticmethod
    def _format_findings_section(findings: Dict, heading_style, styles) -> list:
        """Format findings section for PDF."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Bias Findings", heading_style))
        
        elements.append(Paragraph(
            f"<b>Total Findings:</b> {findings.get('total_findings', 0)}",
            styles['Normal']
        ))
        elements.append(Paragraph(
            f"<b>Summary:</b> {findings.get('summary', 'No summary available')}",
            styles['Normal']
        ))
        elements.append(Spacer(1, 0.2 * inch))
        
        findings_by_sev = findings.get('findings_by_severity', {})
        
        # Critical findings
        critical = findings_by_sev.get('CRITICAL', [])
        if critical:
            elements.append(Paragraph("<b>CRITICAL FINDINGS</b>", styles['Heading3']))
            for i, finding in enumerate(critical[:5], 1):  # Top 5
                text = (
                    f"{i}. [{finding['check_type']}] {finding['message']}<br/>"
                    f"&nbsp;&nbsp;&nbsp;Metric: {finding['metric_name']} = {finding['metric_value']:.4f} "
                    f"(Threshold: {finding['threshold']:.4f})"
                )
                elements.append(Paragraph(text, styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))
        
        # Moderate findings
        moderate = findings_by_sev.get('MODERATE', [])
        if moderate:
            elements.append(Paragraph(f"<b>MODERATE FINDINGS</b> ({len(moderate)} total)", styles['Heading3']))
            for i, finding in enumerate(moderate[:3], 1):  # Top 3
                text = (
                    f"{i}. [{finding['check_type']}] {finding['message']}<br/>"
                    f"&nbsp;&nbsp;&nbsp;Metric: {finding['metric_name']} = {finding['metric_value']:.4f}"
                )
                elements.append(Paragraph(text, styles['Normal']))
        
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    @staticmethod
    def _format_remediation_section(remediation: Dict, heading_style, styles) -> list:
        """Format remediation section for PDF."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Remediation Strategies", heading_style))
        
        strategies = remediation.get('recommended_strategies', [])
        priority = remediation.get('priority_order', [])
        
        if strategies:
            data = [['Priority', 'Strategy', 'Impact', 'Complexity']]
            for i, strategy_name in enumerate(priority[:5], 1):  # Top 5
                strategy = next((s for s in strategies if s['strategy_name'] == strategy_name), None)
                if strategy:
                    data.append([
                        str(i),
                        strategy['strategy_name'][:30],
                        strategy['expected_impact'],
                        strategy['implementation_complexity'],
                    ])
            
            table = Table(data, colWidths=[0.7*inch, 3*inch, 1*inch, 1.3*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            
            elements.append(table)
        
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    @staticmethod
    def _format_compliance_section(compliance: Dict, heading_style, styles) -> list:
        """Format compliance section for PDF."""
        from reportlab.platypus import Paragraph, Spacer
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Legal Compliance", heading_style))
        
        elements.append(Paragraph(
            f"<b>Overall Status:</b> {compliance.get('overall_compliance_status', 'UNKNOWN')}",
            styles['Normal']
        ))
        
        eeoc = compliance.get('eeoc_80_rule', {})
        elements.append(Paragraph(
            f"<b>EEOC 80% Rule:</b> {'PASS' if eeoc.get('compliant', False) else 'FAIL'} "
            f"({eeoc.get('total_violations', 0)} violations)",
            styles['Normal']
        ))
        
        recommendations = compliance.get('recommendations', [])
        if recommendations:
            elements.append(Spacer(1, 0.1 * inch))
            elements.append(Paragraph("<b>Recommendations:</b>", styles['Normal']))
            for i, rec in enumerate(recommendations, 1):
                elements.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    @staticmethod
    def _format_validity_section(validity: Dict, heading_style, styles) -> list:
        """Format validity section for PDF."""
        from reportlab.platypus import Paragraph, Spacer, Table, TableStyle
        from reportlab.lib import colors
        from reportlab.lib.units import inch
        
        elements = []
        elements.append(Paragraph("Statistical Validity", heading_style))
        
        data = [
            ['Metric', 'Value'],
            ['Average Confidence', f"{validity.get('average_confidence', 0):.2%}"],
            ['Sample Size', f"{validity.get('sample_size', 0):,}"],
            ['Sample Adequacy', validity.get('sample_adequacy', 'UNKNOWN')],
            ['Data Completeness', f"{validity.get('data_completeness', 0):.2%}"],
            ['Statistical Power', validity.get('statistical_power', 'UNKNOWN')],
        ]
        
        table = Table(data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        
        limitations = validity.get('limitations', [])
        if limitations:
            elements.append(Spacer(1, 0.2 * inch))
            elements.append(Paragraph("<b>Limitations:</b>", styles['Normal']))
            for i, limitation in enumerate(limitations[:5], 1):  # Top 5
                elements.append(Paragraph(f"{i}. {limitation}", styles['Normal']))
        
        elements.append(Spacer(1, 0.3 * inch))
        return elements
    
    @staticmethod
    def save(report_data: Dict[str, Any], filepath: str) -> None:
        """
        Save report as PDF file.
        
        Args:
            report_data: Report data dictionary from generator
            filepath: Output file path
        """
        try:
            pdf_bytes = PDFFormatter.format(report_data)
            
            # Ensure directory exists
            Path(filepath).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, 'wb') as f:
                f.write(pdf_bytes)
            
            print(f"Report exported to: {filepath}")
        except ImportError as e:
            print(f"[SKIP] {e}")
