# NoBias - Unified API Reference

## Overview

NoBias provides three audit types with a **standardized output format**:
- **Dataset Audit**: Detect bias in training data
- **Model Audit**: Detect bias in trained ML models
- **Agent Audit**: Detect bias in LLM agents

All three share the same output structure and export interface.

---

## Dataset Audit

### Basic Usage

```python
from nobias import audit_dataset

report = audit_dataset(
    data='hiring_data.csv',              # Path or DataFrame
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)
```

### Output Structure

```python
DatasetAuditReport(
    # Identification
    audit_id='dataset_audit_a1b2c3d4',
    timestamp='2024-01-15T10:30:00.000Z',
    duration_seconds=2.45,
    
    # Configuration
    dataset_name='hiring_data.csv',
    row_count=10000,
    column_count=15,
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
    
    # Severity
    overall_severity='MODERATE',  # CRITICAL | MODERATE | LOW | CLEAR
    
    # Findings
    findings=[
        DatasetFinding(
            check='representation',
            severity='MODERATE',
            message='Gender imbalance detected',
            metric='representation_ratio',
            value=0.35,
            threshold=0.40,
            confidence=0.95
        ),
        # ... more findings
    ],
    
    # Analysis Results
    representation={...},
    label_rates={...},
    proxy_features=[...],
    missing_data_matrix={...},
    intersectional_disparities=[...],
    kl_divergences={...},
    remediation_suggestions=[...],
    
    # FairSight Compliance
    audit_integrity=DatasetIntegrity(
        audit_hash='sha256:abc123...',
        data_hash='sha256:def456...',
        findings_hash='sha256:ghi789...',
        config_hash='sha256:jkl012...',
        timestamp='2024-01-15T10:30:00.000Z'
    ),
    confidence_intervals={...},
    
    # Logs
    logs=['Phase 1: Data ingestion...', ...]
)
```

### Export Methods

```python
# JSON export
report.export('audit.json', format='json')

# Text export
report.export('audit.txt', format='text')

# PDF export
report.export('audit.pdf', format='pdf')

# Dictionary
data = report.to_dict()

# Text summary
text = report.to_text()
```

### Helper Methods

```python
# Get critical findings only
critical = report.get_critical_findings()

# Get findings by check type
rep_findings = report.get_findings_by_check('representation')

# Print summary
print(report)
```

---

## Model Audit

### Basic Usage

```python
from nobias.model_audit import audit_model

report = audit_model(
    model='model.pkl',                   # Path or model object
    test_data='test.csv',                # Path or DataFrame
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)
```

### Output Structure

```python
ModelAuditReport(
    # Identification
    audit_id='model_audit_e5f6g7h8',
    timestamp='2024-01-15T10:35:00.000Z',
    duration_seconds=15.32,
    
    # Configuration
    model_name='RandomForestClassifier',
    model_type=ModelType.CLASSIFIER_BINARY,
    test_sample_count=2000,
    protected_attributes=['gender', 'race'],
    
    # Severity
    overall_severity='CRITICAL',  # CRITICAL | MODERATE | LOW | CLEAR
    
    # Core Results
    scorecard={
        'gender_Male_vs_Female_demographic_parity': MetricResult(
            metric_name='demographic_parity',
            value=0.15,
            threshold=0.10,
            passed=False,
            p_value=0.001,
            privileged_group='Male',
            unprivileged_group='Female',
            description='Demographic parity violation'
        ),
        # ... more metrics
    },
    
    counterfactual_result=CounterfactualResult(
        total_samples=2000,
        total_comparisons=4000,
        total_flips=320,
        flip_rate=0.08,
        flips_by_attribute={'gender': 180, 'race': 140},
        top_flip_examples=[...]
    ),
    
    findings=[
        ModelFinding(
            finding_id='F001',
            severity=Severity.CRITICAL,
            category='group_fairness',
            title='Demographic parity violation',
            description='Model shows significant bias...',
            evidence={...},
            affected_groups=['Male', 'Female'],
            metric_results=[...]
        ),
        # ... more findings
    ],
    
    mitigation_options=[
        MitigationOption(
            strategy_name='Threshold Adjustment',
            category='post_processing',
            description='Adjust decision thresholds...',
            expected_impact='Can achieve equalized odds...',
            implementation_complexity='low',
            requires_retraining=False,
            code_example='from fairlearn.postprocessing...'
        ),
        # ... more options
    ],
    
    # Optional Analyses
    intersectional_findings=[...],
    shap_analysis=None,
    
    # Metadata
    baseline_metrics={'accuracy': 0.85, 'f1': 0.82},
    per_group_metrics={...},
    
    # FairSight Compliance
    audit_integrity=ModelIntegrity(
        audit_hash='sha256:mno345...',
        model_hash='sha256:pqr678...',
        predictions_hash='sha256:stu901...',
        config_hash='sha256:vwx234...',
        timestamp='2024-01-15T10:35:00.000Z'
    ),
    model_fingerprint=ModelFingerprint(
        model_name='RandomForestClassifier',
        model_type='binary_classifier',
        feature_count=12,
        model_hash='sha256:pqr678...',
        timestamp='2024-01-15T10:35:00.000Z'
    ),
    confidence_intervals={...}
)
```

### Export Methods

```python
# JSON export
report.export('audit.json', format='json')

# Text export
report.export('audit.txt', format='text')

# PDF export (uses advanced report system)
from nobias.model_audit.report import export_pdf
export_pdf(report, 'audit.pdf')

# Dictionary
data = report.to_dict()
```

### Helper Methods

```python
# Get critical findings only
critical = report.get_critical_findings()

# Get findings by category
fairness_findings = report.get_findings_by_category('group_fairness')

# Print summary
print(report)
```

---

## Agent Audit

### Basic Usage

```python
from agent_audit import audit_agent

report = await audit_agent(
    system_prompt="You are a hiring assistant...",
    seed_case="Evaluate: Name: Alex, Experience: 5 years",
    api_key="gsk_...",
    mode="standard",  # quick | standard | full
    model="llama-3.1-70b-versatile"
)
```

### Output Structure

```python
AgentAuditReport(
    # Identification
    audit_id='agent_audit_i9j0k1l2',
    timestamp='2024-01-15T10:40:00.000Z',
    duration_seconds=45.67,
    
    # Configuration
    mode='standard',  # quick | standard | full
    total_calls=28,
    
    # Severity
    overall_severity='LOW',  # CRITICAL | MODERATE | LOW | CLEAR
    overall_cfr=0.06,
    benchmark_range=(0.054, 0.130),
    
    # Findings
    findings=[
        AgentFinding(
            finding_id='AF001',
            attribute='gender',
            comparison='Male_vs_Female',
            metric='cfr',
            value=0.08,
            p_value=0.03,
            severity='LOW',
            benchmark_context='Below best-in-class baseline',
            details={...}
        ),
        # ... more findings
    ],
    
    # Persona Results
    persona_results=[
        PersonaResult(
            persona_id='p001',
            attributes={'gender': 'Female', 'race': 'Black'},
            test_type='factorial',
            decision='positive',
            score=0.85,
            decision_variance=0.0,
            raw_outputs=['HIRE', 'HIRE', 'HIRE']
        ),
        # ... more personas
    ],
    
    # Interpretation & Remediation
    interpretation=Interpretation(
        finding_explanations=[...],
        overall_assessment='Minor bias detected...',
        priority_order=['gender', 'race'],
        confidence='high'
    ),
    
    prompt_suggestions=[
        PromptSuggestion(
            finding_id='AF001',
            suggestion_text='FAIRNESS REQUIREMENT: Evaluate candidates...',
            rationale='This addition will...',
            confidence='high'
        ),
        # ... more suggestions
    ],
    
    # Optional
    stress_test_results=None,
    caffe_test_suite=[...],
    
    # FairSight Compliance
    audit_integrity=AuditIntegrity(
        audit_hash='sha256:yza567...',
        prompts_hash='sha256:bcd890...',
        responses_hash='sha256:efg123...',
        config_hash='sha256:hij456...',
        timestamp='2024-01-15T10:40:00.000Z'
    ),
    model_fingerprint=ModelFingerprint(
        model_id='llama-3.1-70b-versatile',
        temperature=0.0,
        max_tokens=1024,
        system_prompt_hash='sha256:klm789...',
        sdk_version='agent_audit-1.0.0',
        backend='groq',
        timestamp='2024-01-15T10:40:00.000Z'
    ),
    eeoc_air={...},
    stability={...},
    confidence_intervals={...},
    bonferroni_correction={...}
)
```

### Export Methods

```python
# JSON export
report.export('audit.json', format='json')

# CAFFE export (test suite format)
report.export('test_suite.json', format='caffe')

# PDF export
report.export('audit.pdf', format='pdf')

# Dictionary
data = report.to_dict()
```

---

## Common Patterns

### Severity Levels

All audit types use the same severity classification:

| Severity | Description | Threshold |
|----------|-------------|-----------|
| **CRITICAL** | Severe bias requiring immediate action | CFR > 15%, p < 0.01 |
| **MODERATE** | Significant bias requiring attention | CFR > 10%, p < 0.05 |
| **LOW** | Minor bias worth monitoring | CFR > 5% |
| **CLEAR** | No significant bias detected | CFR ≤ 5% |

### FairSight Compliance

All reports include tamper-evident audit records:

```python
# Verify audit integrity
print(f"Audit Hash: {report.audit_integrity.audit_hash}")
print(f"Timestamp: {report.audit_integrity.timestamp}")

# Check model/data fingerprint
if hasattr(report, 'model_fingerprint'):
    print(f"Model: {report.model_fingerprint.model_name}")
    print(f"Model Hash: {report.model_fingerprint.model_hash}")
```

### Export Comparison

```python
# Export all three audit types the same way
dataset_report.export('dataset_audit.json', format='json')
model_report.export('model_audit.json', format='json')
agent_report.export('agent_audit.json', format='json')

# Text summaries
print(dataset_report.to_text())
print(model_report)  # Uses __repr__
print(agent_report)  # Uses __repr__
```

### Critical Findings

```python
# Get critical findings from any audit type
critical_dataset = dataset_report.get_critical_findings()
critical_model = model_report.get_critical_findings()
# Agent audit doesn't have this method yet, but findings are accessible:
critical_agent = [f for f in agent_report.findings if f.severity == 'CRITICAL']
```

---

## Configuration

### Dataset Audit Config

No explicit config object - parameters passed directly to `audit_dataset()`.

### Model Audit Config

```python
from nobias.model_audit import ModelAuditConfig

config = ModelAuditConfig(
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
    run_shap=True,
    run_intersectional=True,
    counterfactual_sample_limit=1000,
    fairness_thresholds={
        'demographic_parity': 0.10,
        'equalized_odds': 0.10,
        'disparate_impact': 0.80,
    },
    severity_thresholds={
        'CRITICAL': {'dpd': 0.20, 'dir': 0.60, 'flip_rate': 0.15},
        'MODERATE': {'dpd': 0.10, 'dir': 0.80, 'flip_rate': 0.05},
    }
)

report = audit_model(model, test_data, config=config)
```

### Agent Audit Config

```python
from agent_audit import AgentAuditConfig

config = AgentAuditConfig(
    mode='standard',  # quick | standard | full
    attributes=['gender', 'race', 'age'],
    domain='hiring',
    positive_outcome='hired',
    negative_outcome='rejected',
    output_type='binary',
    rate_limit_rps=10,
    enable_stress_test=False
)

# Config is passed via parameters to audit_agent()
report = await audit_agent(
    system_prompt="...",
    seed_case="...",
    api_key="...",
    mode=config.mode,
    attributes=config.attributes,
    # ... other config params
)
```

---

## Legal Compliance

All audit reports include fields required for:

- **EU AI Act Article 12**: Audit trail and documentation
- **NIST AI RMF**: Risk management documentation
- **ISO/IEC 42001**: Reproducibility and traceability

Key compliance features:
- SHA-256 hashes for tamper-evidence
- ISO 8601 timestamps
- Unique audit IDs
- Model/data fingerprints
- Confidence intervals
- Statistical significance testing

---

## Quick Reference

| Feature | Dataset Audit | Model Audit | Agent Audit |
|---------|--------------|-------------|-------------|
| **Main Function** | `audit_dataset()` | `audit_model()` | `audit_agent()` |
| **Report Class** | `DatasetAuditReport` | `ModelAuditReport` | `AgentAuditReport` |
| **Audit ID** | ✅ | ✅ | ✅ |
| **Timing** | ✅ | ✅ | ✅ |
| **Severity** | ✅ | ✅ | ✅ |
| **Findings** | ✅ | ✅ | ✅ |
| **Recommendations** | ✅ (Remediation) | ✅ (Mitigation) | ✅ (Prompt Suggestions) |
| **Integrity Hash** | ✅ | ✅ | ✅ |
| **Fingerprint** | ❌ | ✅ | ✅ |
| **Export JSON** | ✅ | ✅ | ✅ |
| **Export Text** | ✅ | ✅ | ❌ |
| **Export PDF** | ✅ | ✅ | ✅ |

---

## Examples

See the `examples/` directory for complete working examples:
- `examples/dataset_audit_example.py`
- `examples/model_audit_example.py`
- `examples/full_audit_example.py` (agent audit)

For more details, see:
- Dataset Audit: `library/dataset_audit/README.md`
- Model Audit: `library/model_audit/README.md`
- Agent Audit: `library/agent_audit/QUICKSTART.md`
