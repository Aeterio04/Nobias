"""
Report generator for dataset audits.

Orchestrates the generation of comprehensive audit reports by combining
multiple sections and formatting them according to the requested output format.
"""

from typing import Dict, Any, List
from .sections import (
    HealthSection,
    ConfigSection,
    RepresentationSection,
    ProxyFeaturesSection,
    FindingsSection,
    RemediationSection,
    ComplianceSection,
    ValiditySection,
)


def generate_report(audit_report, sections: List[str] = None) -> Dict[str, Any]:
    """
    Generate a comprehensive report from audit results.
    
    Args:
        audit_report: DatasetAuditReport object
        sections: List of section names to include. If None, includes all sections.
                 Valid sections: 'health', 'config', 'representation', 'proxy_features',
                                'findings', 'remediation', 'compliance', 'validity'
    
    Returns:
        Dictionary containing all requested report sections
    """
    # Default to all sections if not specified
    if sections is None:
        sections = [
            'health',
            'config',
            'representation',
            'proxy_features',
            'findings',
            'remediation',
            'compliance',
            'validity',
        ]
    
    report_data = {}
    
    # Generate each requested section
    if 'health' in sections:
        report_data['health'] = HealthSection.generate(audit_report)
    
    if 'config' in sections:
        report_data['config'] = ConfigSection.generate(audit_report)
    
    if 'representation' in sections:
        report_data['representation'] = RepresentationSection.generate(audit_report)
    
    if 'proxy_features' in sections:
        report_data['proxy_features'] = ProxyFeaturesSection.generate(audit_report)
    
    if 'findings' in sections:
        report_data['findings'] = FindingsSection.generate(audit_report)
    
    if 'remediation' in sections:
        report_data['remediation'] = RemediationSection.generate(audit_report)
    
    if 'compliance' in sections:
        report_data['compliance'] = ComplianceSection.generate(audit_report)
    
    if 'validity' in sections:
        report_data['validity'] = ValiditySection.generate(audit_report)
    
    return report_data
