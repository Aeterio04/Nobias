# NoBias Platform - Quick Reference Card

> **One-page reference for all three audit systems**

---

## Three Systems Overview

| System | Input | Output | Speed | Cost | Use When |
|--------|-------|--------|-------|------|----------|
| **Dataset Audit** | Training data (CSV/Excel/Parquet) | 7 bias types | 2-10 sec | $0 | Before training |
| **Model Audit** | Trained model + test data | 8+ fairness metrics | 15-60 sec | $0 | Before deployment |
| **Agent Audit** | LLM prompt/API/logs | CFR, MASD, AIR, SSS | 2-30 min | $0.03-$0.27 | Before/after deployment |

---

## Quick Start Commands

### Dataset Audit
```python
from nobias import audit_dataset

report = audit_dataset(
    data='data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Severity: {report.overall_severity}")
print(f"DIR: {report.label_rates['gender']['dir']:.2f}")
```

### Model Audit
```python
from nobias.model_audit import audit_model

report = audit_model(
    model='model.pkl',
    test_data='test.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Severity: {report.overall_severity.value}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
```

### Agent Audit
```python
from agent_audit import audit_agent

report = await audit_agent(
    system_prompt="You are a hiring assistant...",
    seed_case="Evaluate: Name: Jordan...",
    api_key="gsk_...",
    mode='standard'
)

print(f"Severity: {report.overall_severity}")
print(f"CFR: {report.overall_cfr:.1%}")
```

---

## Key Metrics Cheat Sheet

### Dataset Audit
- **DIR** (Disparate Impact Ratio): < 0.80 = EEOC violation
- **SRD** (Selection Rate Difference): > 0.10 = significant
- **Representation**: < 10% = underrepresented
- **Proxy Score**: > 0.3 = potential proxy

### Model Audit
- **DPD** (Demographic Parity Difference): > 0.10 = violation
- **DIR** (Disparate Impact Ratio): < 0.80 = EEOC violation
- **Flip Rate**: > 5% = concerning, > 15% = critical
- **Equalized Odds**: > 0.10 = violation

### Agent Audit
- **CFR** (Counterfactual Flip Rate): > 10% = moderate, > 15% = critical
- **MASD** (Mean Absolute Score Difference): > 0.08 = moderate
- **AIR** (Adverse Impact Ratio): < 0.80 = EEOC violation
- **SSS** (Stochastic Stability Score): < 0.67 = unstable

---

## Severity Levels

| Level | Dataset | Model | Agent | Action |
|-------|---------|-------|-------|--------|
| **CRITICAL** | DIR < 0.60 | DIR < 0.60, Flip > 15% | CFR > 15% | Immediate fix |
| **MODERATE** | DIR 0.60-0.80 | DIR 0.60-0.80, Flip 5-15% | CFR 10-15% | Remediation recommended |
| **LOW** | DIR 0.80-0.90 | DIR 0.80-0.90, Flip 2-5% | CFR 5-10% | Monitor |
| **CLEAR** | DIR > 0.90 | DIR > 0.90, Flip < 2% | CFR < 5% | No action |

---

## EEOC 80% Rule

**Formula**: `DIR = (lowest group rate) / (highest group rate)`

**Status**:
- DIR < 0.80 = **LEGAL VIOLATION**
- DIR ≥ 0.80 = COMPLIANT

**Checked by**: All three systems ✅

---

## Common Remediations

### Dataset Audit
1. **Resampling** - Oversample underrepresented groups
2. **Reweighting** - Assign weights to balance groups
3. **Remove Proxies** - Drop features that leak protected attributes
4. **Fair Imputation** - Fill missing data systematically

### Model Audit
1. **Threshold Adjustment** - Adjust decision thresholds per group (no retraining)
2. **Sample Reweighting** - Reweight training data (requires retraining)
3. **Fairness Constraints** - Add constraints during training (requires retraining)
4. **Remove Proxies** - Drop correlated features (requires retraining)

### Agent Audit
1. **Prompt Modification** - Add fairness instructions
2. **Remove Context** - Strip demographic information
3. **Structured Output** - Force JSON format
4. **Temperature Adjustment** - Reduce randomness

---

## Export Reports

```python
# JSON format
report.export('audit_report.json', format='json')

# Text format
report.export('audit_report.txt', format='text')

# PDF format (Model/Dataset only)
report.export('audit_report.pdf', format='pdf')

# Comprehensive JSON (with actionable insights)
report.export('audit_comprehensive.json', format='comprehensive')
```

---

## Actionable Insights

```python
# For Model Audit
from model_audit.interpreter import interpret_model_audit_report

insights = interpret_model_audit_report(
    report_data="model_audit_comprehensive.json",
    dataset_audit_data="dataset_audit_comprehensive.json"  # Optional
)

# For Dataset Audit
from library.dataset_audit.report import generate_report

full_report = generate_report(report)
insights = full_report['actionable_insights']

# Access insights
print(insights['plain_english']['one_liner'])
print(insights['action_priority'][0]['action'])
```

---

## Integration Patterns

### CI/CD Pipeline
```python
def test_fairness():
    report = audit_dataset(...)  # or audit_model(...) or audit_agent(...)
    assert report.overall_severity not in ['CRITICAL']
```

### Deployment Gate
```python
def approve_deployment(report):
    if report.overall_severity in ['CRITICAL', 'MODERATE']:
        return {'approved': False, 'reason': 'Bias detected'}
    return {'approved': True}
```

### Monitoring
```python
from apscheduler.schedulers.background import BackgroundScheduler

scheduler = BackgroundScheduler()
scheduler.add_job(audit_dataset, 'cron', day_of_week='mon')
scheduler.add_job(audit_model, 'cron', day_of_week='sun')
scheduler.add_job(audit_agent, 'cron', day=1)
scheduler.start()
```

---

## Compliance Checklist

- [ ] Run appropriate audit (Dataset/Model/Agent)
- [ ] Check overall severity (must not be CRITICAL)
- [ ] Verify EEOC compliance (DIR ≥ 0.80)
- [ ] Review all critical findings
- [ ] Apply recommended mitigations
- [ ] Re-audit after mitigation
- [ ] Export audit report
- [ ] Store audit_id with model/agent
- [ ] Document mitigation steps

---

## Cost Comparison

| System | Infrastructure | API Costs | Total |
|--------|----------------|-----------|-------|
| Dataset Audit | CPU only | $0 | **$0** |
| Model Audit | CPU only | $0 | **$0** |
| Agent Audit (Quick) | CPU + Network | $0.03-$0.11 | **$0.03-$0.11** |
| Agent Audit (Standard) | CPU + Network | $0.05-$0.17 | **$0.05-$0.17** |
| Agent Audit (Full) | CPU + Network | $0.07-$0.27 | **$0.07-$0.27** |

---

## When to Use Each System

| Scenario | Use |
|----------|-----|
| Before collecting data | None (too early) |
| After data collection | **Dataset Audit** |
| After model training | **Model Audit** |
| Before agent deployment | **Agent Audit** |
| Production monitoring | **All Three** |
| Regulatory audit | **All Three** |

---

## Resources

- **Full Guide**: `docs/NOBIAS_COMPLETE_PRESENTATION_GUIDE.md`
- **Agent Audit**: `docs/AGENT_AUDIT_COMPLETE_GUIDE.md`
- **Model Audit**: `docs/niru_MODEL_AUDIT_IMPLEMENTATION_GUIDE.md`
- **Dataset Audit**: `docs/niru_DATASET_AUDIT_IMPLEMENTATION_GUIDE.md`
- **Examples**: `examples/`

---

**Version**: 2.0 | **Updated**: 2026-04-28 | **Compliance**: EEOC, EU AI Act, NIST AI RMF, ISO/IEC 42001
