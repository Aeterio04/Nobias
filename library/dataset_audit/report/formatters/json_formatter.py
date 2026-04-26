"""
JSON formatter for dataset audit reports.
"""

import json
from typing import Dict, Any
from pathlib import Path


class JSONFormatter:
    """Format dataset audit reports as JSON."""
    
    @staticmethod
    def format(report_data: Dict[str, Any], mode: str = 'comprehensive') -> str:
        """
        Format report data as JSON string.
        
        Args:
            report_data: Report data dictionary from generator
            mode: 'comprehensive' or 'basic'
        
        Returns:
            JSON string
        """
        if mode == 'basic':
            # Basic mode: only essential information
            basic_data = {
                'dataset_name': report_data.get('config', {}).get('dataset_name', 'Unknown'),
                'overall_severity': report_data.get('health', {}).get('overall_severity', 'UNKNOWN'),
                'health_score': report_data.get('health', {}).get('health_score', 0),
                'total_findings': report_data.get('health', {}).get('total_findings', 0),
                'critical_findings': report_data.get('health', {}).get('critical_findings', 0),
                'moderate_findings': report_data.get('health', {}).get('moderate_findings', 0),
                'proxy_features_detected': report_data.get('health', {}).get('proxy_features_detected', 0),
                'compliance_status': report_data.get('compliance', {}).get('overall_compliance_status', 'UNKNOWN'),
                'timestamp': report_data.get('health', {}).get('timestamp', ''),
            }
            return json.dumps(basic_data, indent=2)
        else:
            # Comprehensive mode: all sections
            return json.dumps(report_data, indent=2)
    
    @staticmethod
    def save(report_data: Dict[str, Any], filepath: str, mode: str = 'comprehensive') -> None:
        """
        Save report as JSON file.
        
        Args:
            report_data: Report data dictionary from generator
            filepath: Output file path
            mode: 'comprehensive' or 'basic'
        """
        json_str = JSONFormatter.format(report_data, mode)
        
        # Ensure directory exists
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
        
        print(f"Report exported to: {filepath}")
