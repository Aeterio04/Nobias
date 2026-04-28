# Model Audit - Quick Start Guide

Get started with NoBias Model Audit in 5 minutes.

---

## Installation

```bash
pip install pandas scikit-learn
# Your model dependencies (sklearn, xgboost, lightgbm, etc.)
```

---

## Basic Usage - Audit a Trained Model

### Step 1: Prepare Your Data

Your test data should include:
- All features used by the model
- Protected attributes (gender, race, age, etc.)
- Target column with actual labels

```python
import pandas as pd

# Load test data
test_data = pd.read_csv('test_data.csv')

# Example structure:
# gender, race, age, experience, education, credit_score, hired
# Male, White, 35, 5, Bachelor, 720, 1
# Female, Black, 28, 3, Master, 680, 0
```

### Step 2: Run the Audit

```python
from nobias.model_audit import audit_model

report = audit_model(
    model='trained_model.pkl',           # Path to your model
    test_data='test_data.csv',           # Path to test data
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)
```

### Step 3: Check Results

```python
# Overall assessment
print(f"Severity: {report.overall_severity.value}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")

# Critical findings
for finding in report.get_critical_findings():
    print(f"[{finding.severity.value}] {finding.title}")
```

---

## Quick Example - In-Memory Model

```python
from sklearn.ensemble import RandomForestClassifier
from nobias.model_audit import quick_audit
import pandas as pd

# Train your model
model = RandomForestClassifier()
model.fit(X_train, y_train)

# Prepare test data with protected attributes
X_test_full = X_test.copy()
X_test_full['gender'] = gender_test
X_test_full['race'] = race_test

# Quick audit
report = quick_audit(
    model=model,
    X_test=X_test_full,
    y_test=y_test,
    protected_attributes=['gender', 'race'],
    positive_value=1,
)

print(f"Severity: {report.overall_severity.value}")
```

---

## Understanding the Output

### Severity Levels

- **CRITICAL**: Immediate action required (flip rate > 15%, DIR < 0.60)
- **MODERATE**: Remediation recommended (flip rate 5-15%, DIR 0.60-0.80)
- **LOW**: Monitor (flip rate 2-5%, DIR 0.80-0.90)
- **CLEAR**: No significant bias (flip rate < 2%, DIR > 0.90)

### Key Metrics

**Counterfactual Flip Rate**: How often predictions change when only protected attributes change
- 0-2%: Excellent
- 2-5%: Acceptable
- 5-15%: Concerning
- >15%: Severe violation

**Disparate Impact Ratio (DIR)**: EEOC 80% rule compliance
- <0.80: **LEGAL VIOLATION**
- 0.80-0.85: Warning
- >0.85: Compliant

---

## Export Results

```python
# JSON format
report.export('audit_report.json', format='json')

# Text format
report.export('audit_report.txt', format='text')

# Get dictionary
data = report.to_dict()
```

---

## Common Use Cases

### 1. Pre-Deployment Check

```python
report = audit_model(model, test_data, protected_attributes, target_column, positive_value)

if report.overall_severity in ['CRITICAL', 'MODERATE']:
    print("⚠️ Bias detected - do not deploy")
else:
    print("✅ Model passed fairness check")
```

### 2. Compare Models

```python
models = ['lr_model.pkl', 'rf_model.pkl', 'gb_model.pkl']

for model_path in models:
    report = audit_model(model_path, test_data, protected_attributes, target_column, positive_value)
    print(f"{model_path}: {report.overall_severity.value}, Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
```

### 3. Check EEOC Compliance

```python
report = audit_model(model, test_data, protected_attributes, target_column, positive_value)

for key, metric in report.scorecard.items():
    if 'disparate_impact' in key and not metric.passed:
        print(f"⚠️ EEOC VIOLATION: {key} = {metric.value:.2f}")
```

---

## Next Steps

- **Detailed Analysis**: See [MODEL_AUDIT_IMPLEMENTATION_GUIDE.md](niru_MODEL_AUDIT_IMPLEMENTATION_GUIDE.md)
- **Visual Summary**: See [MODEL_AUDIT_VISUAL_SUMMARY.md](niru_MODEL_AUDIT_VISUAL_SUMMARY.md)
- **Mitigation**: Review `report.mitigation_options` for concrete fixes
- **Examples**: Check `examples/model_audit_example.py`

---

## Troubleshooting

**Issue**: "Model has no predict() method"
- **Solution**: Wrap your model with a class that has `predict()` method

**Issue**: "Protected attribute not in test data"
- **Solution**: Add protected attribute columns to your test DataFrame

**Issue**: "High flip rate"
- **Solution**: Review `report.mitigation_options` for remediation strategies

---

## Support

- Full Documentation: `library/model_audit/README.md`
- API Reference: `API_REFERENCE.md`
- Examples: `examples/model_audit_example.py`
