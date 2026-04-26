"""
Unbiased - Comprehensive Bias Detection and Mitigation Library

Provides end-to-end fairness auditing across the ML pipeline:
- Dataset Audit: Detect biases in raw data
- Model Audit: Audit trained ML models
- Agent Audit: Black-box auditing for LLM agents
"""

from .dataset_audit import audit_dataset, DatasetAuditReport

__version__ = '0.0.0'

__all__ = [
    'audit_dataset',
    'DatasetAuditReport',
]

# Submodules are accessible via:
# - unbiased.dataset_audit
# - unbiased.model_audit
# - unbiased.agent_audit
