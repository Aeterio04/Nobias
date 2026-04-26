# Model Audit Module

Comprehensive fairness auditing for trained machine learning models.

## Overview

The Model Audit module provides tools to audit trained ML models for bias and fairness violations. It supports:

- **Counterfactual Testing**: Flip protected attributes to detect individual fairness violations
- **Group Fairness Metrics**: Demographic parity, equalized odds, disparate impact, and more
- **Intersectional Analysis**: Detect compounded bias across multiple protected attributes
- **Severity Classification**: Automatic severity grading (CRITICAL/MODERATE/LOW/CLEAR)
- **Mitigation Recommendations**: Actionable strategies to reduce bias

## Quick Start

```python
from nobias.model_audit import audit_model

# Audit a trained model
report = audit_model(
    model="path/to/model.pkl",           # or pass model object directly
    test_data="path/to/test.csv",        # or pass DataFrame
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1,
)

# View results
print(report)
print(f"Overall Severity: {report.overall_severity}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")

# Export report
report.export("audit_report.json")
```

## Features

### 1. Counterfactual Flip Testing

Tests individual fairness by creating counterfactual versions of each sample with protected attributes changed:

```python
# Automatically included in audit_model()
cf_result = report.counterfactual_result

print(f"Flip Rate: {cf_result.flip_rate:.2%}")
print(f"Flips by attribute: {cf_result.flips_by_attribute}")

# View specific flip examples
for example in cf_result.top_flip_examples[:5]:
    print(example)
```

### 2. Group Fairness Metrics

Computes standard fairness metrics:

- **Demographic Parity Difference (DPD)**: Difference in approval rates
- **Disparate Impact Ratio (DIR)**: Ratio of approval rates (80% rule)
- **Equalized Odds**: Difference in FPR and FNR across groups
- **Predictive Parity**: Difference in precision across groups
- **Calibration**: Difference in calibration across groups

```python
# View scorecard
for metric_name, result in report.scorecard.items():
    print(result)
```

### 3. Intersectional Analysis

Detects compounded bias when multiple protected attributes intersect:

```python
for finding in report.intersectional_findings:
    print(f"{finding.attributes}: {finding.metric_value:.2%} vs {finding.baseline_value:.2%}")
```

### 4. Mitigation Recommendations

Get actionable recommendations to reduce bias:

```python
for mitigation in report.mitigation_options:
    print(f"{mitigation.strategy_name} [{mitigation.category}]")
    print(f"  Impact: {mitigation.expected_impact}")
    print(f"  Complexity: {mitigation.implementation_complexity}")
    print(f"  Requires retraining: {mitigation.requires_retraining}")
```

## Configuration

Customize the audit with `ModelAuditConfig`:

```python
from nobias.model_audit import audit_model, ModelAuditConfig

config = ModelAuditConfig(
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1,
    run_shap=False,  # Disable SHAP analysis
    run_intersectional=True,
    counterfactual_sample_limit=1000,  # Limit samples for speed
    fairness_thresholds={
        "demographic_parity": 0.05,  # Stricter threshold
        "disparate_impact": 0.85,
    },
)

report = audit_model(
    model="model.pkl",
    test_data="test.csv",
    config=config,
)
```

## Supported Models

The module supports any model with a `predict()` method:

- **scikit-learn**: All classifiers and regressors
- **XGBoost**: XGBClassifier, XGBRegressor
- **LightGBM**: LGBMClassifier, LGBMRegressor
- **Custom models**: Any object with `predict()` and optionally `predict_proba()`

Models can be loaded from:
- Pickle files (`.pkl`)
- Joblib files (`.joblib`)
- Passed directly as objects

## Report Export

Export reports in multiple formats:

```python
# JSON format (detailed)
report.export("audit_report.json", format="json")

# Text format (human-readable summary)
report.export("audit_report.txt", format="text")

# Or use the report utilities directly
from nobias.model_audit import export_report, generate_text_summary

export_report(report, "report.json", format="json")
summary = generate_text_summary(report)
print(summary)
```

## API Reference

### Main Functions

#### `audit_model()`

```python
audit_model(
    model: Union[str, Path, Any],
    test_data: Union[str, Path, pd.DataFrame],
    protected_attributes: list[str],
    target_column: str,
    positive_value: Any = 1,
    config: Optional[ModelAuditConfig] = None,
) -> ModelAuditReport
```

Main entry point for model auditing.

**Parameters:**
- `model`: Path to model file or model object
- `test_data`: Path to CSV or DataFrame
- `protected_attributes`: List of protected attribute column names
- `target_column`: Name of target/label column
- `positive_value`: Value representing positive class (default: 1)
- `config`: Optional configuration object

**Returns:** `ModelAuditReport` object

#### `quick_audit()`

```python
quick_audit(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    protected_attributes: list[str],
    positive_value: Any = 1,
) -> ModelAuditReport
```

Quick audit for models already loaded in memory.

### Report Object

The `ModelAuditReport` object contains:

```python
report.model_name              # Model name
report.model_type              # ModelType enum
report.overall_severity        # Severity enum (CRITICAL/MODERATE/LOW/CLEAR)
report.scorecard               # Dict of fairness metrics
report.counterfactual_result   # Counterfactual testing results
report.findings                # List of ModelFinding objects
report.mitigation_options      # List of MitigationOption objects
report.intersectional_findings # List of IntersectionalFinding objects
report.baseline_metrics        # Overall performance metrics
report.per_group_metrics       # Per-group performance metrics

# Methods
report.to_dict()                    # Convert to dictionary
report.get_critical_findings()      # Get critical findings only
report.get_findings_by_category()   # Filter findings by category
report.export(path, format)         # Export report
```

## Severity Levels

Findings are automatically classified into severity levels:

- **CRITICAL**: DPD > 0.20 with p < 0.01, OR DIR < 0.60, OR flip rate > 15%
- **MODERATE**: DPD > 0.10 with p < 0.05, OR DIR < 0.80, OR flip rate > 5%
- **LOW**: DPD > 0.05, OR flip rate > 2%
- **CLEAR**: All metrics within thresholds

## Examples

See `examples/model_audit_example.py` for a complete working example.

## Dependencies

```
pandas >= 2.0
numpy >= 1.24
scipy >= 1.11
scikit-learn >= 1.3
```

Optional dependencies for specific features:
```
shap >= 0.43          # For SHAP explainability (future)
matplotlib >= 3.7     # For visualization (future)
```

## Limitations

Current version (0.1.0) limitations:

- SHAP analysis not yet implemented (planned for v0.2.0)
- PDF export not yet implemented (planned for v0.2.0)
- Adversarial debiasing not yet implemented (planned for v0.3.0)
- Only supports binary and multiclass classification (regression support partial)

## References

- Hardt et al. (2016): "Equality of Opportunity in Supervised Learning"
- Chouldechova (2017): "Fair prediction with disparate impact"
- Feldman et al. (2015): "Certifying and removing disparate impact"
- EEOC 80% Rule: https://www.eeoc.gov/laws/guidance/

## License

Part of the Nobias fairness toolkit.
