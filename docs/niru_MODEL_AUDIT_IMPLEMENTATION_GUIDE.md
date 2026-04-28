# Model Audit System - Complete Implementation Guide

> **A comprehensive guide to understanding and using the NoBias Model Audit System**  
> **For both ML engineers and compliance teams**

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [What We're Building & Why](#what-were-building--why)
3. [Key Concepts](#key-concepts)
4. [System Architecture](#system-architecture)
5. [Implementation Details](#implementation-details)
6. [Example Workflows](#example-workflows)
7. [Input/Output Examples](#inputoutput-examples)
8. [Best Practices](#best-practices)
9. [Troubleshooting](#troubleshooting)

---

## Executive Summary

The NoBias Model Audit System is a **production-ready framework** for detecting and measuring bias in trained ML models. It combines group fairness metrics, counterfactual testing, and intersectional analysis to provide legally defensible audit reports.

### What Makes This Special

- **Comprehensive Testing**: Group fairness + individual fairness + intersectional bias
- **Legally Defensible**: EEOC-compliant metrics, tamper-evident audit trails
- **Production-Ready**: Works with any sklearn-compatible model
- **Actionable**: Concrete mitigation strategies with code examples
- **Fast**: Audits complete in seconds to minutes

### Quick Stats

- **Metrics Covered**: 8+ fairness metrics (demographic parity, equalized odds, disparate impact, etc.)
- **Speed**: 15-60 seconds for typical audits
- **Compliance**: EU AI Act, NIST AI RMF, ISO/IEC 42001 ready
- **Model Support**: Binary classifiers, multiclass classifiers, regressors

---

## What We're Building & Why

### The Problem

ML models make high-stakes decisions (hiring, lending, healthcare, criminal justice) but can exhibit bias in multiple ways:

1. **Group Fairness Violations**: Different approval rates across demographics
2. **Individual Fairness Violations**: Similar individuals treated differently
3. **Intersectional Bias**: Compounded discrimination for multiple protected attributes
4. **Proxy Feature Bias**: Model learns protected attributes through correlated features

Traditional testing misses these because:
- Manual testing doesn't scale
- Accuracy metrics don't reveal bias
- Existing tools are research-focused, not production-ready
- No legal defensibility

### Our Solution

A **6-step pipeline** that:

1. **Loads** any sklearn-compatible model and test data
2. **Computes** baseline performance metrics
3. **Tests** counterfactual fairness (flip protected attributes)
4. **Measures** group fairness metrics (demographic parity, equalized odds, etc.)
5. **Analyzes** intersectional bias
6. **Recommends** concrete mitigation strategies

### How It Ties to Our Goal

**Goal**: Make ML models fair, transparent, and legally compliant

**How we achieve it**:
- **Fairness**: Detect bias with industry-standard metrics
- **Transparency**: Tamper-evident audit trails, exportable reports
- **Compliance**: EU AI Act Art. 9/12, NIST AI RMF, ISO/IEC 42001 requirements

---

## Key Concepts

### Group Fairness Metrics

#### 1. Demographic Parity (Statistical Parity)
**What it measures**: Equal approval rates across groups

**Formula**: `P(Ŷ=1 | A=a) = P(Ŷ=1 | A=b)` for all groups a, b

**Metric**: Demographic Parity Difference (DPD) = |P(Ŷ=1|A=a) - P(Ŷ=1|A=b)|

**Interpretation**:
- 0.00 = Perfect parity
- < 0.10 = Acceptable (industry standard)
- > 0.20 = Severe violation

**Example**: If 80% of men are approved but only 60% of women, DPD = 0.20

#### 2. Equalized Odds
**What it measures**: Equal true positive and false positive rates across groups

**Formula**: 
- `P(Ŷ=1 | Y=1, A=a) = P(Ŷ=1 | Y=1, A=b)` (TPR)
- `P(Ŷ=1 | Y=0, A=a) = P(Ŷ=1 | Y=0, A=b)` (FPR)

**Metric**: Max difference in TPR or FPR

**Interpretation**:
- 0.00 = Perfect equality
- < 0.10 = Acceptable
- > 0.15 = Severe violation

**Example**: If TPR for men is 0.90 but 0.70 for women, violation = 0.20

#### 3. Disparate Impact Ratio (DIR)
**What it measures**: EEOC 80% rule compliance

**Formula**: `DIR = P(Ŷ=1|A=unprivileged) / P(Ŷ=1|A=privileged)`

**Interpretation**:
- < 0.80 = **LEGAL VIOLATION** (prima facie discrimination)
- 0.80-0.85 = WARNING (borderline)
- > 0.85 = COMPLIANT

**Example**: If 60% of protected group approved vs 80% of reference group, DIR = 0.75 (violation)

#### 4. Predictive Parity
**What it measures**: Equal precision across groups

**Formula**: `P(Y=1 | Ŷ=1, A=a) = P(Y=1 | Ŷ=1, A=b)`

**Metric**: Difference in precision

**Interpretation**:
- 0.00 = Perfect parity
- < 0.05 = Acceptable
- > 0.10 = Violation

#### 5. Calibration
**What it measures**: Predicted probabilities match actual outcomes across groups

**Formula**: For each score bin, `P(Y=1 | score, A=a) ≈ score`

**Metric**: Max calibration error across groups

**Interpretation**:
- 0.00 = Perfect calibration
- < 0.05 = Well-calibrated
- > 0.10 = Poor calibration

### Individual Fairness Metrics

#### Counterfactual Flip Rate
**What it measures**: How often predictions change when only protected attributes change

**Method**:
1. Take each test sample
2. Create counterfactual by flipping protected attribute (Male→Female, White→Black, etc.)
3. Get prediction for both original and counterfactual
4. Count flips

**Formula**: `Flip Rate = (# samples where pred_original ≠ pred_counterfactual) / total_samples`

**Interpretation**:
- 0% = Perfect individual fairness
- < 2% = Excellent
- 2-5% = Acceptable
- 5-15% = Concerning
- > 15% = Severe violation

**Example**: If 80 out of 1000 predictions flip, flip rate = 8%

### Intersectional Bias

**What it measures**: Compounded discrimination for multiple protected attributes

**Method**:
1. Compute approval rate for each intersectional group (e.g., Black Women, White Men)
2. Compare to expected rate (product of marginal rates)
3. Flag groups with significant deviation

**Example**:
- Black approval rate: 60%
- Female approval rate: 70%
- Expected Black Female rate: 0.60 × 0.70 = 42%
- Actual Black Female rate: 30%
- **Superadditive bias detected** (worse than expected)

### Severity Classification

Findings are classified into 4 levels:

| Severity | DPD | DIR | Flip Rate | Meaning |
|----------|-----|-----|-----------|---------|
| **CRITICAL** | > 0.20 | < 0.60 | > 15% | Immediate action required |
| **MODERATE** | 0.10-0.20 | 0.60-0.80 | 5-15% | Remediation recommended |
| **LOW** | 0.05-0.10 | 0.80-0.90 | 2-5% | Monitor |
| **CLEAR** | < 0.05 | > 0.90 | < 2% | No action needed |

---

## System Architecture

### The 6-Step Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Model & Data Loading                               │
│ • Load model (.pkl, .joblib, or object)                    │
│ • Load test data (CSV, Excel, Parquet, or DataFrame)       │
│ • Validate protected attributes exist                      │
│ • Extract feature names                                    │
├─────────────────────────────────────────────────────────────┤
│ STEP 2: Baseline Predictions                               │
│ • Get predictions on test set                              │
│ • Compute overall accuracy, precision, recall, F1          │
│ • Compute per-group metrics                                │
├─────────────────────────────────────────────────────────────┤
│ STEP 3: Counterfactual Testing                             │
│ • For each sample, flip protected attributes               │
│ • Get predictions on counterfactuals                       │
│ • Count flips and compute flip rate                        │
│ • Identify high-risk attributes                            │
├─────────────────────────────────────────────────────────────┤
│ STEP 4: Group Fairness Metrics                             │
│ • Demographic parity                                       │
│ • Equalized odds (TPR/FPR equality)                        │
│ • Disparate impact ratio (EEOC 80% rule)                   │
│ • Predictive parity                                        │
│ • Calibration                                              │
├─────────────────────────────────────────────────────────────┤
│ STEP 5: Intersectional Analysis                            │
│ • Compute approval rates for all intersectional groups     │
│ • Compare to expected rates                                │
│ • Flag superadditive bias                                  │
├─────────────────────────────────────────────────────────────┤
│ STEP 6: Mitigation Recommendations                         │
│ • Threshold adjustment (post-processing)                   │
│ • Sample reweighting (pre-processing)                      │
│ • Proxy feature removal (pre-processing)                   │
│ • In-processing fairness constraints                       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input
  ├─ Model (path or object)
  ├─ Test data (path or DataFrame)
  ├─ Protected attributes (e.g., ['gender', 'race'])
  └─ Target column + positive value
       │
       ▼
Step 1: Load & Validate
  ├─ Model type detection (binary/multiclass/regressor)
  ├─ Feature extraction
  └─ Data validation
       │
       ▼
Step 2: Baseline Predictions
  ├─ Overall metrics (accuracy, F1, etc.)
  └─ Per-group metrics
       │
       ▼
Step 3: Counterfactual Testing
  ├─ Generate counterfactuals
  ├─ Get predictions
  └─ Compute flip rates
       │
       ▼
Step 4: Group Fairness
  ├─ For each protected attribute:
  │   ├─ For each pair of groups:
  │   │   ├─ Demographic parity
  │   │   ├─ Equalized odds
  │   │   ├─ Disparate impact
  │   │   ├─ Predictive parity
  │   │   └─ Calibration
  │   └─ Statistical significance tests
  └─ Build scorecard
       │
       ▼
Step 5: Intersectional Analysis
  ├─ Enumerate all intersectional groups
  ├─ Compute approval rates
  ├─ Compare to expected rates
  └─ Flag superadditive bias
       │
       ▼
Step 6: Generate Findings & Recommendations
  ├─ Classify severity
  ├─ Generate mitigation options
  └─ Build audit report
       │
       ▼
ModelAuditReport
  ├─ audit_id, timestamp, duration
  ├─ overall_severity
  ├─ scorecard (all metrics)
  ├─ counterfactual_result
  ├─ findings (structured)
  ├─ mitigation_options (actionable)
  ├─ intersectional_findings
  ├─ audit_integrity (SHA-256 hashes)
  └─ model_fingerprint (reproducibility)
```

---

## Implementation Details

### Main API Function

```python
from nobias.model_audit import audit_model

report = audit_model(
    model='model.pkl',                    # Path or model object
    test_data='test.csv',                 # Path or DataFrame
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
    config=None,                          # Optional ModelAuditConfig
)
```

### Configuration Options

```python
from nobias.model_audit import ModelAuditConfig

config = ModelAuditConfig(
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
    
    # Optional analyses
    run_shap=True,                        # SHAP feature importance
    run_intersectional=True,              # Intersectional bias analysis
    
    # Sampling limits
    counterfactual_sample_limit=None,     # None = all samples
    shap_sample_limit=1000,               # Limit for SHAP (expensive)
    
    # Fairness thresholds
    fairness_thresholds={
        'demographic_parity': 0.10,       # Max acceptable DPD
        'equalized_odds': 0.10,           # Max acceptable TPR/FPR diff
        'disparate_impact': 0.80,         # Min acceptable DIR (EEOC)
        'predictive_parity': 0.05,        # Max acceptable precision diff
        'calibration': 0.05,              # Max acceptable calibration error
    },
    
    # Severity thresholds
    severity_thresholds={
        'CRITICAL': {'dpd': 0.20, 'dir': 0.60, 'flip_rate': 0.15},
        'MODERATE': {'dpd': 0.10, 'dir': 0.80, 'flip_rate': 0.05},
        'LOW': {'dpd': 0.05, 'dir': 0.90, 'flip_rate': 0.02},
    }
)

report = audit_model(model, test_data, config=config)
```

### Supported Model Types

**Binary Classifiers**:
- sklearn: LogisticRegression, RandomForestClassifier, GradientBoostingClassifier, SVC, etc.
- XGBoost: XGBClassifier
- LightGBM: LGBMClassifier
- CatBoost: CatBoostClassifier

**Multiclass Classifiers**:
- Same as binary, with `predict_proba()` method

**Regressors**:
- sklearn: LinearRegression, RandomForestRegressor, etc.
- XGBoost: XGBRegressor
- LightGBM: LGBMRegressor

**Requirements**:
- Must have `predict()` method
- Binary/multiclass: Should have `predict_proba()` for confidence scores
- Must be trained (fitted)

### Output Structure

```python
ModelAuditReport(
    # Identification
    audit_id='model_audit_a1b2c3d4',
    timestamp='2026-04-26T10:30:00.000Z',
    duration_seconds=15.32,
    
    # Configuration
    model_name='RandomForestClassifier',
    model_type=ModelType.CLASSIFIER_BINARY,
    test_sample_count=2000,
    protected_attributes=['gender', 'race'],
    
    # Severity
    overall_severity=Severity.CRITICAL,
    
    # Core Results
    scorecard={
        'gender_Male_vs_Female_demographic_parity': MetricResult(...),
        'gender_Male_vs_Female_equalized_odds': MetricResult(...),
        'gender_Male_vs_Female_disparate_impact': MetricResult(...),
        # ... more metrics
    },
    
    counterfactual_result=CounterfactualResult(
        total_samples=2000,
        total_comparisons=4000,
        total_flips=320,
        flip_rate=0.08,
        flips_by_attribute={'gender': 180, 'race': 140},
    ),
    
    findings=[
        ModelFinding(
            finding_id='F001',
            severity=Severity.CRITICAL,
            category='group_fairness',
            title='Demographic parity violation',
            description='...',
            evidence={...},
            affected_groups=['Male', 'Female'],
        ),
        # ... more findings
    ],
    
    mitigation_options=[
        MitigationOption(
            strategy_name='Threshold Adjustment',
            category='post_processing',
            description='...',
            expected_impact='...',
            implementation_complexity='low',
            requires_retraining=False,
            code_example='...',
        ),
        # ... more options
    ],
    
    # Optional
    intersectional_findings=[...],
    shap_analysis=None,
    
    # Metadata
    baseline_metrics={'accuracy': 0.85, 'f1': 0.82},
    per_group_metrics={...},
    
    # FairSight Compliance
    audit_integrity=ModelIntegrity(...),
    model_fingerprint=ModelFingerprint(...),
    confidence_intervals={...},
)
```

---

## Example Workflows

### Workflow 1: Quick Model Audit

**Scenario**: You've trained a model and want to check for bias before deployment

```python
from nobias.model_audit import audit_model

# Run audit
report = audit_model(
    model='trained_model.pkl',
    test_data='test_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

# Check results
print(f"Overall Severity: {report.overall_severity.value}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")

# Check EEOC compliance
for attr in report.protected_attributes:
    for key, metric in report.scorecard.items():
        if attr in key and 'disparate_impact' in key:
            if not metric.passed:
                print(f"⚠️ EEOC VIOLATION: {attr} DIR={metric.value:.2f}")
```

**Time**: ~15 seconds  
**Use case**: Pre-deployment validation

---

### Workflow 2: Detailed Analysis with Mitigation

**Scenario**: You found bias and want concrete remediation steps

```python
from nobias.model_audit import audit_model

# Run full audit
report = audit_model(
    model='model.pkl',
    test_data='test.csv',
    protected_attributes=['gender', 'race', 'age'],
    target_column='approved',
    positive_value=1,
)

# Export for documentation
report.export('audit_report.json', format='json')
report.export('audit_report.txt', format='text')

# Review findings
print(f"\n📋 Findings ({len(report.findings)} total):")
for finding in report.get_critical_findings():
    print(f"\n[{finding.severity.value}] {finding.title}")
    print(f"  {finding.description}")
    print(f"  Affected: {', '.join(finding.affected_groups)}")

# Review mitigation options
print(f"\n🔧 Mitigation Options:")
for i, option in enumerate(report.mitigation_options, 1):
    print(f"\n{i}. {option.strategy_name} [{option.category}]")
    print(f"   {option.description}")
    print(f"   Expected Impact: {option.expected_impact}")
    print(f"   Complexity: {option.implementation_complexity}")
    print(f"   Requires Retraining: {option.requires_retraining}")
    if option.code_example:
        print(f"   Code:\n{option.code_example}")
```

**Time**: ~30 seconds  
**Use case**: Detailed analysis and remediation planning

---

### Workflow 3: In-Memory Model Audit

**Scenario**: You have a model object in memory and want to audit it

```python
from sklearn.ensemble import RandomForestClassifier
from nobias.model_audit import quick_audit
import pandas as pd

# Train model
model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

# Prepare test data with protected attributes
X_test_with_protected = X_test.copy()
X_test_with_protected['gender'] = gender_test
X_test_with_protected['race'] = race_test

# Run quick audit
report = quick_audit(
    model=model,
    X_test=X_test_with_protected,
    y_test=y_test,
    protected_attributes=['gender', 'race'],
    positive_value=1,
)

print(f"Severity: {report.overall_severity.value}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
```

**Time**: ~10 seconds  
**Use case**: Development testing, Jupyter notebooks

---

### Workflow 4: Comparing Models

**Scenario**: You want to compare bias across multiple models

```python
from nobias.model_audit import audit_model

models = {
    'Logistic Regression': 'lr_model.pkl',
    'Random Forest': 'rf_model.pkl',
    'Gradient Boosting': 'gb_model.pkl',
}

results = {}

for name, model_path in models.items():
    print(f"\nAuditing {name}...")
    report = audit_model(
        model=model_path,
        test_data='test.csv',
        protected_attributes=['gender', 'race'],
        target_column='hired',
        positive_value=1,
    )
    
    results[name] = {
        'severity': report.overall_severity.value,
        'flip_rate': report.counterfactual_result.flip_rate,
        'critical_findings': len(report.get_critical_findings()),
    }

# Compare
print("\n📊 Model Comparison:")
for name, metrics in results.items():
    print(f"\n{name}:")
    print(f"  Severity: {metrics['severity']}")
    print(f"  Flip Rate: {metrics['flip_rate']:.2%}")
    print(f"  Critical Findings: {metrics['critical_findings']}")
```

**Time**: ~45 seconds (3 models)  
**Use case**: Model selection, A/B testing

---

## Input/Output Examples

### Example 1: Binary Classifier (Hiring)

**Input**:
```python
report = audit_model(
    model='hiring_model.pkl',
    test_data='test_candidates.csv',
    protected_attributes=['gender', 'race', 'age'],
    target_column='hired',
    positive_value=1,
)
```

**Test Data** (`test_candidates.csv`):
```csv
gender,race,age,experience,education,hired
Male,White,35,5,Bachelor,1
Female,Black,28,3,Master,0
Male,Asian,42,10,PhD,1
Female,White,31,4,Bachelor,1
...
```

**Output**:
```python
ModelAuditReport(
    audit_id='model_audit_a1b2c3d4',
    model_name='RandomForestClassifier',
    overall_severity=Severity.MODERATE,
    
    counterfactual_result=CounterfactualResult(
        flip_rate=0.08,  # 8% of predictions flip
        flips_by_attribute={
            'gender': 45,
            'race': 32,
            'age': 3,
        },
    ),
    
    findings=[
        ModelFinding(
            finding_id='F001',
            severity=Severity.MODERATE,
            category='group_fairness',
            title='Demographic parity violation for gender',
            description='Male candidates approved at 78% vs Female at 62% (DPD=0.16)',
            evidence={
                'male_approval_rate': 0.78,
                'female_approval_rate': 0.62,
                'dpd': 0.16,
                'p_value': 0.001,
            },
            affected_groups=['Male', 'Female'],
        ),
    ],
    
    mitigation_options=[
        MitigationOption(
            strategy_name='Threshold Adjustment',
            category='post_processing',
            description='Adjust decision thresholds per group to equalize approval rates',
            expected_impact='Can reduce DPD to <0.05 with <2% accuracy loss',
            implementation_complexity='low',
            requires_retraining=False,
            code_example='''
from fairlearn.postprocessing import ThresholdOptimizer

# Wrap your model
mitigator = ThresholdOptimizer(
    estimator=model,
    constraints="demographic_parity",
    objective="accuracy_score",
)

# Fit on validation set
mitigator.fit(X_val, y_val, sensitive_features=gender_val)

# Use for predictions
y_pred_fair = mitigator.predict(X_test, sensitive_features=gender_test)
            ''',
        ),
    ],
)
```

---

### Example 2: Lending Model with EEOC Violation

**Input**:
```python
report = audit_model(
    model='lending_model.pkl',
    test_data='loan_applications.csv',
    protected_attributes=['race', 'gender'],
    target_column='approved',
    positive_value=1,
)
```

**Output** (Critical Finding):
```python
ModelAuditReport(
    overall_severity=Severity.CRITICAL,
    
    scorecard={
        'race_White_vs_Black_disparate_impact': MetricResult(
            metric_name='disparate_impact',
            value=0.67,  # 67% - EEOC VIOLATION
            threshold=0.80,
            passed=False,
            p_value=0.0001,
            privileged_group='White',
            unprivileged_group='Black',
            description='Black applicants approved at 67% the rate of White applicants (EEOC 80% rule violation)',
        ),
    },
    
    findings=[
        ModelFinding(
            finding_id='F001',
            severity=Severity.CRITICAL,
            category='group_fairness',
            title='EEOC Disparate Impact Violation',
            description='Model violates EEOC 80% rule for race (DIR=0.67 < 0.80)',
            evidence={
                'white_approval_rate': 0.75,
                'black_approval_rate': 0.50,
                'disparate_impact_ratio': 0.67,
                'eeoc_threshold': 0.80,
                'legal_status': 'VIOLATION',
            },
            affected_groups=['White', 'Black'],
        ),
    ],
)
```

---

## Best Practices

### 1. Data Preparation

**DO**:
- Include protected attributes in test data
- Use representative test set (same distribution as production)
- Ensure sufficient samples per group (min 30)
- Handle missing values before audit

**DON'T**:
- Remove protected attributes from test data
- Use training data for audit (overfitting)
- Audit on imbalanced test sets

### 2. Model Selection

**DO**:
- Audit final production model
- Compare multiple models
- Re-audit after retraining

**DON'T**:
- Audit only on development models
- Skip audits for "simple" models
- Assume fairness without testing

### 3. Interpretation

**DO**:
- Review all findings, not just severity
- Check EEOC compliance (DIR < 0.80)
- Consider intersectional findings
- Document audit results

**DON'T**:
- Ignore "LOW" severity findings
- Focus only on accuracy
- Skip documentation

### 4. Remediation

**DO**:
- Start with post-processing (no retraining)
- Test mitigation effectiveness
- Re-audit after changes
- Document mitigation steps

**DON'T**:
- Immediately retrain model
- Apply multiple mitigations at once
- Skip validation

---

## Troubleshooting

### Issue: "Model has no predict() method"

**Cause**: Model object doesn't have required interface

**Solution**:
```python
# Wrap your model
class ModelWrapper:
    def __init__(self, model):
        self.model = model
    
    def predict(self, X):
        return self.model.forward(X)  # or whatever your method is
    
    def predict_proba(self, X):
        return self.model.predict_proba(X)

wrapped_model = ModelWrapper(your_model)
report = audit_model(wrapped_model, ...)
```

### Issue: "Protected attribute not in test data"

**Cause**: Test data missing protected attribute columns

**Solution**:
```python
# Add protected attributes to test data
X_test_with_protected = X_test.copy()
X_test_with_protected['gender'] = gender_values
X_test_with_protected['race'] = race_values

report = audit_model(model, X_test_with_protected, ...)
```

### Issue: "Insufficient samples for group"

**Cause**: Too few samples in some demographic groups

**Solution**:
- Use larger test set
- Combine rare categories
- Skip intersectional analysis for small groups

### Issue: "High flip rate but low group fairness violations"

**Cause**: Individual fairness violations without group-level bias

**Interpretation**: Model treats similar individuals differently, even if group rates are equal

**Solution**: Focus on counterfactual mitigation (remove proxy features, add fairness constraints)

---

## Summary

The Model Audit System provides:
- ✅ Comprehensive bias detection (group + individual + intersectional)
- ✅ Legal compliance (EEOC, EU AI Act, NIST)
- ✅ Actionable recommendations with code examples
- ✅ Fast execution (seconds to minutes)
- ✅ Production-ready with tamper-evident audit trails

**Next Steps**:
1. Run your first audit: `audit_model(model, test_data, protected_attributes, target_column, positive_value)`
2. Review findings and severity
3. Check EEOC compliance (DIR >= 0.80)
4. Apply recommended mitigations
5. Re-audit and document results

For more details, see:
- API Reference: `library/model_audit/README.md`
- Example Scripts: `examples/model_audit_example.py`
- Mitigation Guide: `docs/MITIGATION_STRATEGIES.md`
