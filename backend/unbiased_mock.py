"""
Mock unbiased library for demonstration
This provides the same interface as the real unbiased library would have
"""
import pandas as pd
import numpy as np
from datetime import datetime
import uuid

def audit_dataset(data, protected_attributes, target_column, positive_value):
    """Mock dataset audit function"""
    # Load data
    if isinstance(data, str):
        df = pd.read_csv(data)
    else:
        df = data
    
    # Generate mock audit results
    findings = []
    metrics = []
    
    for attr in protected_attributes:
        if attr in df.columns:
            # Mock finding
            severity = np.random.choice(['critical', 'moderate', 'low', 'clear'])
            findings.append({
                'attribute': attr,
                'severity': severity,
                'description': f'Representation bias detected in {attr}',
                'impact_score': round(np.random.uniform(0.1, 0.9), 2),
                'recommendation': f'Balance the distribution of {attr} in your dataset'
            })
            
            # Mock metric
            metrics.append({
                'name': f'{attr} Distribution',
                'value': round(np.random.uniform(0.5, 0.95), 2),
                'threshold': 0.80,
                'status': 'passed' if severity in ['low', 'clear'] else 'failed'
            })
    
    # Determine overall severity
    severities = [f['severity'] for f in findings]
    if 'critical' in severities:
        overall_severity = 'critical'
    elif 'moderate' in severities:
        overall_severity = 'moderate'
    elif 'low' in severities:
        overall_severity = 'low'
    else:
        overall_severity = 'clear'
    
    return {
        'audit_id': str(uuid.uuid4())[:8],
        'dataset_name': 'uploaded_dataset.csv',
        'timestamp': datetime.now().isoformat(),
        'row_count': len(df),
        'column_count': len(df.columns),
        'protected_attributes': protected_attributes,
        'target_column': target_column,
        'overall_severity': overall_severity,
        'finding_count': len(findings),
        'findings': findings,
        'metrics': metrics,
        'summary': f'Analyzed {len(df)} rows across {len(protected_attributes)} protected attributes'
    }

def audit_model(model_path, test_data, protected_attributes, target_column, positive_value):
    """Mock model audit function"""
    return {
        'audit_id': str(uuid.uuid4())[:8],
        'model_name': model_path.split('/')[-1],
        'timestamp': datetime.now().isoformat(),
        'overall_severity': 'moderate',
        'finding_count': 3,
        'findings': [
            {
                'severity': 'critical',
                'description': 'Demographic parity violation detected',
                'attribute': protected_attributes[0] if protected_attributes else 'gender',
                'metric_value': 0.63
            }
        ],
        'metrics': [
            {'name': 'Demographic Parity', 'value': 0.63, 'threshold': 0.80, 'status': 'failed'},
            {'name': 'Equalized Odds', 'value': 0.88, 'threshold': 0.80, 'status': 'passed'}
        ]
    }

def audit_agent(system_prompt, llm_model, api_key, protected_attributes, audit_mode='standard'):
    """Mock agent audit function"""
    return {
        'audit_id': str(uuid.uuid4())[:8],
        'timestamp': datetime.now().isoformat(),
        'overall_severity': 'moderate',
        'overall_cfr': '11.2%',
        'finding_count': 4,
        'api_calls': 28 if audit_mode == 'standard' else 100,
        'findings': [
            {
                'severity': 'critical',
                'description': 'Gender bias detected in hiring decisions',
                'attribute': 'gender',
                'cfr': '12.6%'
            },
            {
                'severity': 'moderate',
                'description': 'Name-based racial bias detected',
                'attribute': 'race',
                'cfr': '9.1%'
            }
        ]
    }

__version__ = '0.0.0'
