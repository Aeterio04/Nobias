# Model Audit Interpreter

> Transform technical bias audit reports into actionable, plain-English insights for business users, compliance teams, and frontend applications.

---

## What Is This?

The **Model Audit Interpreter** is a new feature that takes technical model audit reports (with metrics like "Demographic Parity Difference: 0.2660") and converts them into business-friendly insights like:

> "This model has 4 critical bias issues that could lead to legal violations. The model approves different groups at very different rates. The gap is 26.6%, which means one group is 26.6% more likely to be approved than another."

---

## Why Do We Need This?

**Before:** Technical audit reports were hard to understand for non-ML engineers
- Metrics like "Disparate Impact Ratio: 0.7955" meant nothing to business users
- No clear prioritization of what to fix first
- No plain-English explanation of legal risk
- No quantified expected improvements

**After:** Actionable insights make audits accessible to everyone
- ✅ Plain-English summaries for executives
- ✅ Prioritized actions ranked by impact/effort
- ✅ Legal risk explained in business terms
- ✅ Expected improvements quantified
- ✅ Dashboard-ready JSON for frontend

---

## Quick Start

### 1. Generate Insights from Existing Report

```python
from model_audit.interpreter import interpret_model_audit_report

# Generate insights
insights = interpret_model_audit_report(
    report_data="output/model_audit_comprehensive.json",
    dataset_audit_data="output/dataset_audit_comprehensive.json"  # Optional
)

# Access insights
print(insights["plain_english"]["one_liner"])
# Output: "This model has 4 critical bias issues that could lead to legal violations"

print(insights["action_priority"][0]["action"])
# Output: "Threshold Adjustment: Adjust decision thresholds per demographic group..."
```

### 2. Export During Audit

```python
from model_audit import audit_model

# Run audit
report = audit_model(
    model="model.pkl",
    test_data="test.csv",
    protected_attributes=["gender", "race"],
    target_column="hired"
)

# Export with actionable insights (automatically generated)
report.export(
    "audit_report.json",
    format="comprehensive",
    include_actionable_insights=True  # Creates *_actionable.json
)
```

### 3. Run Example

```bash
cd Nobias
python examples/actionable_insights_example.py
```

**Output:**
- `output/model_audit_actionable_insights.json`
- Console output with formatted insights

---

## What's Included?

The actionable insights JSON contains **7 sections**:

### 1. Plain English Summary
Non-technical explanations for business users:
- One-sentence summary
- Biggest problem explained
- Impact on real users
- Legal risk assessment
- Quickest fix recommendation

### 2. Action Priority
Ranked list of remediation actions:
- Sorted by impact/effort ratio
- Quick wins (no retraining) ranked highest
- Expected metric improvements quantified
- Clear "do this first" guidance

### 3. Bias Amplification
Compares model bias to dataset bias:
- Determines if model amplified or reduced bias
- Calculates amplification score
- Plain-English verdict

### 4. Group Performance Gaps
Performance differences between groups:
- Accuracy, FPR, FNR gaps
- Severity classification
- Plain-English explanations

### 5. Metric Scorecard
All fairness metrics with context:
- Pass/fail status
- Gap to pass threshold
- Severity classification

### 6. Simulated Improvements
Predicted outcomes from mitigations:
- Current state baseline
- Expected improvements per strategy
- Accuracy impact estimates

### 7. Summary Statistics
High-level KPIs for dashboards:
- Pass rate, flip rate
- Worst/best performing groups
- Legal risk level
- Retraining required flag

---

## Output Example

```json
{
  "plain_english": {
    "one_liner": "This model has 4 critical bias issues that could lead to legal violations",
    "biggest_problem": "The model approves different groups at very different rates...",
    "what_this_means_for_users": "Real people from certain demographic groups are being unfairly rejected...",
    "legal_risk": "YES - This model would likely fail an EEOC audit...",
    "quickest_fix": "Threshold Adjustment: Adjust decision thresholds..."
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
  ],
  "summary_stats": {
    "pass_rate": 0.30,
    "legal_risk_level": "CRITICAL",
    "retraining_required": true
  }
}
```

---

## Use Cases

### For Business Managers
```python
insights = interpret_model_audit_report("model_audit_comprehensive.json")

# Get executive summary
print(insights["plain_english"]["one_liner"])
print(insights["plain_english"]["legal_risk"])

# Check if action needed
if insights["summary_stats"]["legal_risk_level"] in ["CRITICAL", "HIGH"]:
    print("⚠️ Immediate action required!")
```

### For Product Managers
```python
# Get prioritized actions for sprint planning
for action in insights["action_priority"]:
    if not action["requires_retraining"]:  # Quick wins
        print(f"#{action['rank']}: {action['action']}")
        print(f"  Effort: {action['effort']}, Impact: {action['impact']}")
        print(f"  Expected: {action['expected_metric_improvement']}")
```

### For Compliance Teams
```python
# Generate compliance report
legal_risk = insights["plain_english"]["legal_risk"]
compliance_status = insights["simulated_improvements"]["current_state"]["compliance"]
violations = [m for m in insights["metric_scorecard"] if m["severity"] == "CRITICAL"]

generate_compliance_pdf(legal_risk, compliance_status, violations)
```

### For Frontend Developers
```javascript
// Fetch insights
const insights = await fetch('/api/audit/actionable-insights').then(r => r.json());

// Display summary
document.getElementById('summary').textContent = insights.plain_english.one_liner;

// Show risk badge
const riskLevel = insights.summary_stats.legal_risk_level;
document.getElementById('risk-badge').className = `badge badge-${riskLevel.toLowerCase()}`;

// Render actions
insights.action_priority.forEach(action => {
  const card = createActionCard(action);
  document.getElementById('actions').appendChild(card);
});
```

---

## Files Created

### Core Implementation
- **`library/model_audit/interpreter.py`** - Main interpreter logic
- **`library/model_audit/report_export.py`** - Multi-format export support

### Documentation
- **`docs/MODEL_AUDIT_ACTIONABLE_INSIGHTS.md`** - Complete feature documentation
- **`docs/MODEL_AUDIT_INTERPRETER_SUMMARY.md`** - Implementation summary
- **`docs/FRONTEND_ACTIONABLE_INSIGHTS_QUICK_REF.md`** - Frontend quick reference

### Examples
- **`examples/actionable_insights_example.py`** - Demonstrates all features

### Output
- **`output/model_audit_actionable_insights.json`** - Generated insights

---

## Integration

### Updated Files
- **`library/model_audit/api.py`** - Now uses report_export
- **`library/model_audit/models.py`** - Updated export() method

### New Export Formats
The system now generates **5 output formats**:

| Format | Filename | Audience |
|--------|----------|----------|
| Basic JSON | `model_audit_basic.json` | Developers |
| Comprehensive JSON | `model_audit_comprehensive.json` | ML Engineers |
| **Actionable Insights JSON** | `model_audit_actionable_insights.json` | **Managers, PMs, Compliance** |
| Detailed Text | `model_audit_detailed.txt` | All |
| Summary Text | `model_audit_summary.txt` | All |

---

## Documentation

### For Different Audiences

**Business Users:**
- Start with: [MODEL_AUDIT_ACTIONABLE_INSIGHTS.md](docs/MODEL_AUDIT_ACTIONABLE_INSIGHTS.md)
- Focus on: Plain English section, Action Priority, Simulated Improvements

**Frontend Developers:**
- Start with: [FRONTEND_ACTIONABLE_INSIGHTS_QUICK_REF.md](docs/FRONTEND_ACTIONABLE_INSIGHTS_QUICK_REF.md)
- Focus on: JSON structure, UI patterns, API integration

**ML Engineers:**
- Start with: [MODEL_AUDIT_INTERPRETER_SUMMARY.md](docs/MODEL_AUDIT_INTERPRETER_SUMMARY.md)
- Focus on: Implementation details, integration points

**Compliance Teams:**
- Start with: [MODEL_AUDIT_ACTIONABLE_INSIGHTS.md](docs/MODEL_AUDIT_ACTIONABLE_INSIGHTS.md)
- Focus on: Legal risk, compliance status, EEOC violations

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

### `ModelAuditReport.export()`
```python
def export(
    self,
    output_path: str,
    format: str = "json",
    include_actionable_insights: bool = True,
    dataset_audit_path: Optional[str] = None
) -> None:
    """
    Export report to file.
    
    Args:
        output_path: Path to save report
        format: "json", "comprehensive", "text", "summary", "actionable"
        include_actionable_insights: Auto-generate actionable insights
        dataset_audit_path: Optional dataset audit for bias amplification
    """
```

---

## Testing

### Run Example
```bash
cd Nobias
python examples/actionable_insights_example.py
```

### Verify Output
```bash
# Check generated file
cat output/model_audit_actionable_insights.json | python -m json.tool

# Validate structure
python -c "
import json
with open('output/model_audit_actionable_insights.json') as f:
    insights = json.load(f)
    assert 'plain_english' in insights
    assert 'action_priority' in insights
    print('✓ Valid structure')
"
```

---

## Performance

- **Generation Time:** <1 second for typical reports
- **Memory Usage:** Minimal (processes JSON in memory)
- **File Size:** Actionable insights JSON ~10-50KB
- **Scalability:** Handles reports with 100+ metrics

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

---

## Troubleshooting

### Issue: "No dataset audit available"
**Solution:** Run dataset audit first, then provide path to interpreter

### Issue: Simulated improvements seem unrealistic
**Solution:** Use simulations as rough guides, not guarantees. Validate with actual experiments.

### Issue: Action priority doesn't match my priorities
**Solution:** Re-rank based on your business criteria (see documentation for examples)

---

## Future Enhancements

Potential additions (not yet implemented):

- PDF report generation with charts
- Trend analysis across multiple audits
- Custom severity thresholds
- Multi-language support
- Interactive HTML dashboards
- Slack/Email integration
- Jira ticket auto-creation

---

## Related Documentation

- [Model Audit Implementation Guide](docs/niru_MODEL_AUDIT_IMPLEMENTATION_GUIDE.md)
- [Frontend Report Data Spec](docs/FRONTEND_REPORT_DATA_SPEC.md)
- [Model Audit API Reference](library/model_audit/API_REFERENCE.md)

---

## Summary

The Model Audit Interpreter bridges the gap between technical bias audits and business decision-making by:

✅ **Translating** technical metrics into plain English  
✅ **Prioritizing** actions by impact and effort  
✅ **Quantifying** expected improvements  
✅ **Assessing** legal risk in business terms  
✅ **Identifying** affected groups clearly  
✅ **Simulating** mitigation outcomes  
✅ **Providing** dashboard-ready JSON  

This makes bias audits accessible to everyone from executives to frontend developers, enabling faster remediation and better compliance.

---

## Questions?

- **Full Documentation:** [docs/MODEL_AUDIT_ACTIONABLE_INSIGHTS.md](docs/MODEL_AUDIT_ACTIONABLE_INSIGHTS.md)
- **Frontend Quick Ref:** [docs/FRONTEND_ACTIONABLE_INSIGHTS_QUICK_REF.md](docs/FRONTEND_ACTIONABLE_INSIGHTS_QUICK_REF.md)
- **Implementation Summary:** [docs/MODEL_AUDIT_INTERPRETER_SUMMARY.md](docs/MODEL_AUDIT_INTERPRETER_SUMMARY.md)

---

**Ready to get started?**

```bash
cd Nobias
python examples/actionable_insights_example.py
```
