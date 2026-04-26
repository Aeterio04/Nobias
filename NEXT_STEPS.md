# Next Steps - Post-Standardization

## Immediate Actions (Required)

### 1. Test the Changes ⚠️ CRITICAL

Run tests to verify everything works correctly:

```bash
# Test dataset audit
python -c "
from nobias import audit_dataset
import pandas as pd

# Create test data
df = pd.DataFrame({
    'gender': ['M', 'F'] * 50,
    'race': ['White', 'Black'] * 50,
    'hired': [1, 0] * 50
})

# Run audit
report = audit_dataset(
    data=df,
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

# Verify new fields
assert report.audit_id.startswith('dataset_audit_')
assert report.duration_seconds > 0
assert report.audit_integrity is not None
assert report.audit_integrity.audit_hash.startswith('sha256:') or len(report.audit_integrity.audit_hash) == 64

# Test export
report.export('test_dataset_audit.json', format='json')
report.export('test_dataset_audit.txt', format='text')

print('✅ Dataset audit works!')
"
```

```bash
# Test model audit
python -c "
from nobias.model_audit import audit_model
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
import numpy as np

# Create test data
np.random.seed(42)
X = pd.DataFrame({
    'gender': np.random.choice(['M', 'F'], 100),
    'race': np.random.choice(['White', 'Black'], 100),
    'feature1': np.random.randn(100),
    'feature2': np.random.randn(100),
})
y = pd.Series(np.random.choice([0, 1], 100))

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X[['feature1', 'feature2']], y)

# Add target to test data
X['hired'] = y

# Run audit
report = audit_model(
    model=model,
    test_data=X,
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

# Verify new fields
assert report.audit_id.startswith('model_audit_')
assert report.duration_seconds > 0
assert report.audit_integrity is not None
assert report.model_fingerprint is not None

# Test export
report.export('test_model_audit.json', format='json')

print('✅ Model audit works!')
"
```

### 2. Update Main README

Update `README.md` to reflect the standardized API:

```markdown
# NoBias - Unified Bias Auditing

## Quick Start

All three audit types now have a uniform interface:

### Dataset Audit
\`\`\`python
from nobias import audit_dataset

report = audit_dataset(
    data='data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Audit ID: {report.audit_id}")
print(f"Severity: {report.overall_severity}")
report.export('audit.json')
\`\`\`

### Model Audit
\`\`\`python
from nobias.model_audit import audit_model

report = audit_model(
    model='model.pkl',
    test_data='test.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Audit ID: {report.audit_id}")
print(f"Severity: {report.overall_severity}")
report.export('audit.json')
\`\`\`

### Agent Audit
\`\`\`python
from agent_audit import audit_agent

report = await audit_agent(
    system_prompt="...",
    seed_case="...",
    api_key="..."
)

print(f"Audit ID: {report.audit_id}")
print(f"Severity: {report.overall_severity}")
report.export('audit.json')
\`\`\`

## Unified Features

All audit reports include:
- ✅ Unique audit ID
- ✅ Timing information
- ✅ Severity classification (CRITICAL/MODERATE/LOW/CLEAR)
- ✅ Structured findings
- ✅ FairSight compliance (SHA-256 hashes)
- ✅ Export to JSON, text, PDF

See [API_REFERENCE.md](API_REFERENCE.md) for complete documentation.
```

### 3. Clean Up Test Outputs

Remove the test files created during testing:

```bash
rm -f test_dataset_audit.json test_dataset_audit.txt
rm -f test_model_audit.json test_model_audit.txt
```

## Short-Term Actions (Recommended)

### 4. Create Example Notebooks

Create Jupyter notebooks demonstrating the unified API:

**`examples/unified_api_demo.ipynb`**:
```python
# Cell 1: Dataset Audit
from nobias import audit_dataset
import pandas as pd

df = pd.read_csv('sample_data.csv')
dataset_report = audit_dataset(
    data=df,
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Dataset Audit ID: {dataset_report.audit_id}")
print(f"Duration: {dataset_report.duration_seconds:.2f}s")
print(f"Severity: {dataset_report.overall_severity}")

# Cell 2: Model Audit
from nobias.model_audit import audit_model
import joblib

model = joblib.load('trained_model.pkl')
model_report = audit_model(
    model=model,
    test_data='test_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Model Audit ID: {model_report.audit_id}")
print(f"Duration: {model_report.duration_seconds:.2f}s")
print(f"Severity: {model_report.overall_severity}")

# Cell 3: Compare Results
print("\n=== Audit Comparison ===")
print(f"Dataset: {len(dataset_report.findings)} findings")
print(f"Model: {len(model_report.findings)} findings")

# Cell 4: Export All
dataset_report.export('dataset_audit.json')
model_report.export('model_audit.json')
print("✅ All audits exported")
```

### 5. Update Type Hints

Add type hints to all functions for better IDE support:

```python
from typing import Union, List, Any
from pathlib import Path
import pandas as pd

def audit_dataset(
    data: Union[str, Path, pd.DataFrame],
    protected_attributes: List[str],
    target_column: str,
    positive_value: Any
) -> DatasetAuditReport:
    """..."""
```

### 6. Add Docstring Examples

Enhance docstrings with examples showing the new fields:

```python
def audit_dataset(...) -> DatasetAuditReport:
    """
    Audit a dataset for statistical biases.
    
    Returns:
        DatasetAuditReport with:
            - audit_id: Unique identifier (e.g., 'dataset_audit_a1b2c3d4')
            - timestamp: ISO 8601 timestamp
            - duration_seconds: Execution time
            - overall_severity: CRITICAL | MODERATE | LOW | CLEAR
            - findings: List of bias findings
            - audit_integrity: SHA-256 hashes for tamper-evidence
            - ... (see DatasetAuditReport for all fields)
    
    Example:
        >>> report = audit_dataset(
        ...     data='hiring_data.csv',
        ...     protected_attributes=['gender', 'race'],
        ...     target_column='hired',
        ...     positive_value=1
        ... )
        >>> print(report.audit_id)
        'dataset_audit_a1b2c3d4'
        >>> print(report.duration_seconds)
        2.45
        >>> report.export('audit.json')
    """
```

## Medium-Term Actions (Nice to Have)

### 7. Add Audit Comparison Utilities

Create utilities to compare before/after audits:

```python
# library/comparison.py
def compare_audits(before: AuditReport, after: AuditReport) -> dict:
    """
    Compare two audit reports to track improvements.
    
    Returns:
        dict with:
            - severity_change: Change in overall severity
            - findings_resolved: Number of resolved findings
            - findings_new: Number of new findings
            - duration_change: Change in execution time
    """
    return {
        'severity_change': f"{before.overall_severity} → {after.overall_severity}",
        'findings_resolved': len(before.findings) - len(after.findings),
        'findings_new': len([f for f in after.findings if f not in before.findings]),
        'duration_change': after.duration_seconds - before.duration_seconds,
    }
```

### 8. Add HTML Export

Add HTML export for better readability:

```python
def export_html(report: AuditReport, path: str) -> None:
    """Export audit report as interactive HTML."""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Audit Report - {report.audit_id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #f0f0f0; padding: 20px; }}
            .severity-CRITICAL {{ color: red; }}
            .severity-MODERATE {{ color: orange; }}
            .severity-LOW {{ color: yellow; }}
            .severity-CLEAR {{ color: green; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Audit Report</h1>
            <p>Audit ID: {report.audit_id}</p>
            <p>Timestamp: {report.timestamp}</p>
            <p>Duration: {report.duration_seconds:.2f}s</p>
            <p class="severity-{report.overall_severity}">
                Severity: {report.overall_severity}
            </p>
        </div>
        <!-- ... more content ... -->
    </body>
    </html>
    """
    with open(path, 'w') as f:
        f.write(html)
```

### 9. Add Markdown Export

Add Markdown export for documentation:

```python
def export_markdown(report: AuditReport, path: str) -> None:
    """Export audit report as Markdown."""
    md = f"""
# Audit Report

**Audit ID**: `{report.audit_id}`  
**Timestamp**: {report.timestamp}  
**Duration**: {report.duration_seconds:.2f}s  
**Severity**: **{report.overall_severity}**

## Findings

{len(report.findings)} findings detected:

"""
    for i, finding in enumerate(report.findings, 1):
        md += f"### {i}. [{finding.severity}] {finding.title}\n\n"
        md += f"{finding.description}\n\n"
    
    with open(path, 'w') as f:
        f.write(md)
```

### 10. Add CI/CD Tests

Add GitHub Actions workflow to test standardization:

```yaml
# .github/workflows/test-standardization.yml
name: Test Standardization

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      
      - name: Test Dataset Audit
        run: |
          python -c "
          from nobias import audit_dataset
          import pandas as pd
          df = pd.DataFrame({'gender': ['M', 'F']*50, 'hired': [1, 0]*50})
          report = audit_dataset(df, ['gender'], 'hired', 1)
          assert hasattr(report, 'audit_id')
          assert hasattr(report, 'duration_seconds')
          assert hasattr(report, 'audit_integrity')
          "
      
      - name: Test Model Audit
        run: |
          python -c "
          from nobias.model_audit import audit_model
          from sklearn.ensemble import RandomForestClassifier
          import pandas as pd
          import numpy as np
          X = pd.DataFrame({'f1': np.random.randn(100), 'gender': ['M', 'F']*50})
          y = pd.Series(np.random.choice([0, 1], 100))
          model = RandomForestClassifier().fit(X[['f1']], y)
          X['hired'] = y
          report = audit_model(model, X, ['gender'], 'hired', 1)
          assert hasattr(report, 'audit_id')
          assert hasattr(report, 'duration_seconds')
          assert hasattr(report, 'audit_integrity')
          "
```

## Long-Term Actions (Future Enhancements)

### 11. Add Audit History Tracking

Track audit history over time:

```python
class AuditHistory:
    """Track multiple audits over time."""
    
    def __init__(self):
        self.audits = []
    
    def add(self, report: AuditReport):
        self.audits.append(report)
    
    def get_trend(self) -> dict:
        """Get severity trend over time."""
        return {
            'timestamps': [a.timestamp for a in self.audits],
            'severities': [a.overall_severity for a in self.audits],
            'finding_counts': [len(a.findings) for a in self.audits],
        }
    
    def export_timeline(self, path: str):
        """Export audit timeline visualization."""
        # Use matplotlib or plotly to create timeline
        pass
```

### 12. Add Dashboard

Create a web dashboard to visualize audits:

```python
# dashboard/app.py
import streamlit as st
import json

st.title("NoBias Audit Dashboard")

uploaded_file = st.file_uploader("Upload audit report (JSON)")
if uploaded_file:
    report_data = json.load(uploaded_file)
    
    st.header(f"Audit: {report_data['audit_id']}")
    st.metric("Severity", report_data['overall_severity'])
    st.metric("Findings", len(report_data['findings']))
    st.metric("Duration", f"{report_data['duration_seconds']:.2f}s")
    
    # Show findings
    st.subheader("Findings")
    for finding in report_data['findings']:
        with st.expander(f"[{finding['severity']}] {finding.get('title', finding.get('check'))}"):
            st.write(finding.get('description', finding.get('message')))
```

### 13. Add API Server

Create a REST API for running audits:

```python
# api/server.py
from fastapi import FastAPI, UploadFile
from nobias import audit_dataset
from nobias.model_audit import audit_model
import pandas as pd

app = FastAPI()

@app.post("/audit/dataset")
async def audit_dataset_endpoint(
    file: UploadFile,
    protected_attributes: list[str],
    target_column: str,
    positive_value: str
):
    df = pd.read_csv(file.file)
    report = audit_dataset(df, protected_attributes, target_column, positive_value)
    return report.to_dict()

@app.post("/audit/model")
async def audit_model_endpoint(...):
    # Similar implementation
    pass
```

## Checklist

Use this checklist to track progress:

- [ ] **Test dataset audit** (CRITICAL)
- [ ] **Test model audit** (CRITICAL)
- [ ] **Update main README** (CRITICAL)
- [ ] **Clean up test outputs** (CRITICAL)
- [ ] Create example notebooks
- [ ] Update type hints
- [ ] Add docstring examples
- [ ] Add audit comparison utilities
- [ ] Add HTML export
- [ ] Add Markdown export
- [ ] Add CI/CD tests
- [ ] Add audit history tracking
- [ ] Add dashboard
- [ ] Add API server

## Questions?

If you encounter any issues:

1. Check `STANDARDIZATION_COMPLETE.md` for implementation details
2. Check `API_REFERENCE.md` for API documentation
3. Check `BEFORE_AFTER_COMPARISON.md` for what changed
4. Check the individual module READMEs:
   - `library/dataset_audit/README.md`
   - `library/model_audit/README.md`
   - `library/agent_audit/QUICKSTART.md`

## Summary

**Immediate**: Test the changes and update README  
**Short-term**: Add examples and improve documentation  
**Medium-term**: Add comparison utilities and more export formats  
**Long-term**: Add dashboard and API server

The standardization is complete and ready for testing! 🎉
