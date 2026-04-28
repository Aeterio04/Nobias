# Model Audit Actionable Insights

## Overview

The Model Audit Actionable Insights feature transforms technical model audit reports into plain-English, business-friendly insights with prioritized actions. This makes bias audit results accessible to:

- **Business Managers** - Understand legal risk and business impact
- **Product Managers** - Prioritize remediation work
- **Compliance Teams** - Assess regulatory compliance
- **Frontend Developers** - Build intuitive dashboards
- **Executives** - Get high-level summaries

---

## What's New

### Before (Technical Report)
```json
{
  "scorecard": {
    "gender_Female_vs_Male_demographic_parity": {
      "value": 0.2660,
      "threshold": 0.1,
      "passed": false,
      "p_value": 2.07e-13
    }
  }
}
```

### After (Actionable Insights)
```json
{
  "plain_english": {
    "one_liner": "This model has 4 critical bias issues that could lead to legal violations",
    "biggest_problem": "The model approves different groups at very different rates. The gap is 26.6%, which means one group is 26.6% more likely to be approved than another.",
    "what_this_means_for_users": "Real people from certain demographic groups are being unfairly rejected...",
    "legal_risk": "YES - This model would likely fail an EEOC audit...",
    "quickest_fix": "Threshold Adjustment: Adjust decision thresholds per demographic group..."
  },
  "action_priority": [
    {
      "rank": 1,
      "action": "Threshold Adjustment",
      "requires_retraining": false,
      "effort": "LOW",
      "impact": "HIGH",
      "do_this_first": true,
      "expected_metric_improvement": "Demographic parity could improve from current violations to <0.05 difference"
    }
  ]
}
```

---

## Output Structure

The actionable insights JSON contains 7 main sections:

### 1. Plain English Summary
Non-technical explanations for business users:

```json
{
  "plain_english": {
    "one_liner": "One sentence describing the biggest bias problem",
    "biggest_problem": "Explain the worst finding in simple terms",
    "what_this_means_for_users": "How bias affects real people",
    "legal_risk": "Would this fail an EEOC audit? Legal exposure?",
    "quickest_fix": "Fastest fix that requires no retraining"
  }
}
```

**Use Cases:**
- Executive summaries
- Compliance reports
- Stakeholder presentations
- Legal risk assessments

---

### 2. Action Priority
Ranked list of actions by impact/effort ratio:

```json
{
  "action_priority": [
    {
      "rank": 1,
      "action": "Specific action to take",
      "reason": "Why this is ranked #1 (with actual metric values)",
      "requires_retraining": false,
      "effort": "LOW | MEDIUM | HIGH",
      "impact": "LOW | MEDIUM | HIGH",
      "do_this_first": true,
      "expected_metric_improvement": "Demographic parity drops from X to Y"
    }
  ]
}
```

**Ranking Logic:**
1. **Post-processing** (no retraining) ranked highest - quick wins
2. **Pre-processing** (requires retraining) ranked medium
3. **In-processing** (complex retraining) ranked lowest

**Use Cases:**
- Sprint planning
- Resource allocation
- Roadmap prioritization
- Quick wins identification

---

### 3. Bias Amplification
Compares model bias to dataset bias:

```json
{
  "bias_amplification": {
    "dataset_dir": 0.75,
    "model_dir": 0.65,
    "amplification_score": -0.10,
    "verdict": "Model REDUCED bias | Model AMPLIFIED bias | No dataset audit available",
    "explanation": "Simple explanation of what this means"
  }
}
```

**Amplification Score:**
- **Positive** = Model amplified bias (worse than data)
- **Negative** = Model reduced bias (better than data)
- **~0** = Model maintained bias level

**Use Cases:**
- Root cause analysis
- Training data quality assessment
- Model selection decisions
- Fairness improvement tracking

---

### 4. Group Performance Gaps
Detailed performance differences between groups:

```json
{
  "group_performance_gaps": [
    {
      "attribute": "gender",
      "privileged_group": "Male",
      "unprivileged_group": "Female",
      "accuracy_gap": 0.0215,
      "fpr_gap": 0.1212,
      "fnr_gap": 0.0357,
      "severity": "CRITICAL | MODERATE | LOW",
      "plain_english": "Female is 12.1% more likely to be falsely rejected than Male"
    }
  ]
}
```

**Metrics Explained:**
- **Accuracy Gap** - Overall error rate difference
- **FPR Gap** - False positive rate difference (false approvals)
- **FNR Gap** - False negative rate difference (false rejections)

**Use Cases:**
- Identifying affected groups
- Understanding error patterns
- Targeted mitigation strategies
- Impact assessments

---

### 5. Metric Scorecard
All fairness metrics with pass/fail status:

```json
{
  "metric_scorecard": [
    {
      "metric": "Demographic Parity Difference",
      "attribute": "gender",
      "value": 0.2660,
      "threshold": 0.1,
      "passed": false,
      "gap_to_pass": 0.1660,
      "severity": "CRITICAL | MODERATE | LOW"
    }
  ]
}
```

**Gap to Pass:**
- Shows how much improvement needed to pass threshold
- Helps prioritize which metrics to fix first

**Use Cases:**
- Detailed technical analysis
- Compliance checklists
- Progress tracking
- Metric-specific remediation

---

### 6. Simulated Improvements
Predicted outcomes from mitigation strategies:

```json
{
  "simulated_improvements": {
    "current_state": {
      "pass_rate": 0.30,
      "critical_findings": 4,
      "compliance": "FAIL",
      "worst_dir": 0.7955
    },
    "if_threshold_adjustment": {
      "pass_rate_after": 0.60,
      "critical_findings_after": 2,
      "compliance_after": "PASS",
      "requires_retraining": false,
      "accuracy_impact": "Typically <2% accuracy loss",
      "recommended": true
    },
    "if_reweighting": {
      "pass_rate_after": 0.70,
      "critical_findings_after": 1,
      "compliance_after": "PASS",
      "requires_retraining": true,
      "accuracy_impact": "1-3% accuracy loss expected"
    },
    "if_all_applied": {
      "pass_rate_after": 0.80,
      "critical_findings_after": 0,
      "compliance_after": "PASS",
      "recommended": true
    }
  }
}
```

**Use Cases:**
- Cost-benefit analysis
- Strategy selection
- Stakeholder buy-in
- Expected outcomes communication

---

### 7. Summary Statistics
High-level overview:

```json
{
  "summary_stats": {
    "total_metrics_tested": 20,
    "metrics_passed": 6,
    "metrics_failed": 14,
    "pass_rate": 0.30,
    "protected_attributes_tested": ["gender", "race"],
    "worst_performing_group": "gender=Female",
    "best_performing_group": "gender=Male",
    "flip_rate": 0.0,
    "individual_fairness": "PASS | FAIL",
    "legal_risk_level": "CRITICAL | HIGH | MEDIUM | LOW",
    "retraining_required": true
  }
}
```

**Use Cases:**
- Dashboard KPIs
- Executive summaries
- Trend tracking
- Quick health checks

---

## Usage

### Method 1: Generate from Existing Report

```python
from model_audit.interpreter import interpret_model_audit_report

# Generate insights from comprehensive JSON
insights = interpret_model_audit_report(
    report_data="output/model_audit_comprehensive.json",
    dataset_audit_data="output/dataset_audit_comprehensive.json"  # Optional
)

# Access insights
print(insights["plain_english"]["one_liner"])
print(insights["action_priority"][0]["action"])
```

### Method 2: Export During Audit

```python
from model_audit import audit_model

# Run audit
report = audit_model(
    model="model.pkl",
    test_data="test.csv",
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1
)

# Export with actionable insights
report.export(
    "audit_report.json",
    format="comprehensive",
    include_actionable_insights=True,  # Generates *_actionable.json
    dataset_audit_path="dataset_audit_comprehensive.json"  # Optional
)
```

### Method 3: Standalone Export

```python
from model_audit.interpreter import export_actionable_insights

export_actionable_insights(
    report_path="model_audit_comprehensive.json",
    output_path="actionable_insights.json",
    dataset_audit_path="dataset_audit_comprehensive.json"  # Optional
)
```

---

## Integration Examples

### Frontend Dashboard

```javascript
// Fetch actionable insights
const insights = await fetch('/api/audit/actionable-insights').then(r => r.json());

// Display one-liner
document.getElementById('summary').textContent = insights.plain_english.one_liner;

// Show severity badge
const severity = insights.summary_stats.legal_risk_level;
document.getElementById('risk-badge').className = `badge badge-${severity.toLowerCase()}`;

// Render action priority list
insights.action_priority.forEach(action => {
  const card = createActionCard(action);
  document.getElementById('actions').appendChild(card);
});
```

### Compliance Report

```python
# Generate compliance report
insights = interpret_model_audit_report("model_audit_comprehensive.json")

# Extract compliance info
legal_risk = insights["plain_english"]["legal_risk"]
compliance_status = insights["simulated_improvements"]["current_state"]["compliance"]
violations = [m for m in insights["metric_scorecard"] if m["severity"] == "CRITICAL"]

# Generate PDF report
generate_compliance_pdf(legal_risk, compliance_status, violations)
```

### Slack/Email Alerts

```python
# Check for critical issues
insights = interpret_model_audit_report("model_audit_comprehensive.json")

if insights["summary_stats"]["legal_risk_level"] in ["CRITICAL", "HIGH"]:
    send_alert(
        title="⚠️ Critical Bias Detected in Model",
        message=insights["plain_english"]["one_liner"],
        action=insights["plain_english"]["quickest_fix"],
        priority="HIGH"
    )
```

---

## Output Formats Comparison

| Format | File | Use Case | Audience |
|--------|------|----------|----------|
| **Basic JSON** | `model_audit_basic.json` | Quick integration | Developers |
| **Comprehensive JSON** | `model_audit_comprehensive.json` | Full technical details | ML Engineers |
| **Actionable Insights JSON** | `model_audit_actionable_insights.json` | Business decisions | Managers, PMs |
| **Detailed Text** | `model_audit_detailed.txt` | Documentation | All |
| **Summary Text** | `model_audit_summary.txt` | Quick overview | All |

---

## Best Practices

### 1. Always Include Dataset Audit
```python
# ✓ GOOD - Includes bias amplification analysis
insights = interpret_model_audit_report(
    "model_audit_comprehensive.json",
    dataset_audit_data="dataset_audit_comprehensive.json"
)

# ✗ LIMITED - Missing bias amplification
insights = interpret_model_audit_report("model_audit_comprehensive.json")
```

### 2. Use Action Priority for Planning
```python
# Get top 3 quick wins (no retraining)
quick_wins = [
    action for action in insights["action_priority"]
    if not action["requires_retraining"]
][:3]

# Plan sprint around quick wins
for action in quick_wins:
    create_jira_ticket(action)
```

### 3. Monitor Simulated Improvements
```python
# Track expected vs actual improvements
before = insights["simulated_improvements"]["current_state"]["pass_rate"]
expected = insights["simulated_improvements"]["if_threshold_adjustment"]["pass_rate_after"]

# After applying mitigation
actual = new_audit_report.pass_rate

if actual < expected:
    print("⚠️ Mitigation underperformed. Investigate further.")
```

### 4. Use Plain English for Stakeholders
```python
# Generate executive summary
summary = f"""
Model Bias Audit Summary
========================

{insights['plain_english']['one_liner']}

Legal Risk: {insights['summary_stats']['legal_risk_level']}

Recommended Action:
{insights['action_priority'][0]['action']}

Expected Impact:
{insights['action_priority'][0]['expected_metric_improvement']}
"""

send_email(to="executives@company.com", body=summary)
```

---

## Troubleshooting

### Issue: "No dataset audit available"
**Cause:** Dataset audit not provided for bias amplification analysis

**Solution:**
```python
# Run dataset audit first
from dataset_audit import audit_dataset

dataset_report = audit_dataset(
    data="training_data.csv",
    protected_attributes=["gender", "race"],
    target_column="hired"
)
dataset_report.export("dataset_audit_comprehensive.json", format="comprehensive")

# Then generate insights with amplification
insights = interpret_model_audit_report(
    "model_audit_comprehensive.json",
    dataset_audit_data="dataset_audit_comprehensive.json"
)
```

### Issue: Simulated improvements seem unrealistic
**Cause:** Simulations are estimates based on typical outcomes

**Solution:**
- Use simulations as rough guides, not guarantees
- Validate with actual mitigation experiments
- Adjust expectations based on your specific use case

### Issue: Action priority doesn't match my priorities
**Cause:** Ranking is based on effort/impact, not business priorities

**Solution:**
```python
# Re-rank based on your criteria
actions = insights["action_priority"]

# Prioritize by business impact
actions_sorted = sorted(
    actions,
    key=lambda a: (
        a["impact"] == "HIGH",
        not a["requires_retraining"],
        a["effort"] == "LOW"
    ),
    reverse=True
)
```

---

## API Reference

### `interpret_model_audit_report()`
```python
def interpret_model_audit_report(
    report_data: Union[str, Path, Dict],
    dataset_audit_data: Optional[Union[str, Path, Dict]] = None
) -> Dict[str, Any]:
    """
    Generate actionable insights from model audit report.
    
    Args:
        report_data: Path to comprehensive JSON or dict
        dataset_audit_data: Optional dataset audit for bias amplification
        
    Returns:
        Dict with 7 sections: plain_english, action_priority, 
        bias_amplification, group_performance_gaps, metric_scorecard,
        simulated_improvements, summary_stats
    """
```

### `export_actionable_insights()`
```python
def export_actionable_insights(
    report_path: Union[str, Path],
    output_path: Union[str, Path],
    dataset_audit_path: Optional[Union[str, Path]] = None
) -> None:
    """
    Generate and export actionable insights to JSON file.
    
    Args:
        report_path: Path to model_audit_comprehensive.json
        output_path: Path to save actionable insights JSON
        dataset_audit_path: Optional dataset audit path
    """
```

---

## Examples

See `examples/actionable_insights_example.py` for complete examples:

```bash
cd Nobias
python examples/actionable_insights_example.py
```

This generates:
- `output/model_audit_actionable_insights.json`
- `output/model_audit_actionable_insights_with_amplification.json`

---

## Related Documentation

- [Model Audit Implementation Guide](niru_MODEL_AUDIT_IMPLEMENTATION_GUIDE.md)
- [Frontend Report Data Spec](FRONTEND_REPORT_DATA_SPEC.md)
- [Model Audit API Reference](../library/model_audit/API_REFERENCE.md)

---

## Summary

The Actionable Insights feature bridges the gap between technical bias audits and business decision-making by providing:

✅ **Plain-English explanations** for non-technical stakeholders  
✅ **Prioritized actions** ranked by impact/effort  
✅ **Bias amplification analysis** comparing model to data  
✅ **Group performance gaps** with clear explanations  
✅ **Metric scorecard** with pass/fail status  
✅ **Simulated improvements** for strategy selection  
✅ **Summary statistics** for quick health checks  

This makes bias audits accessible to everyone from executives to frontend developers, enabling faster remediation and better compliance.
