# Actionable Insights for Dataset Audits

## Overview

The Actionable Insights feature transforms technical dataset audit reports into plain-English summaries and prioritized action items for both technical and non-technical users.

## What You Get

The actionable insights JSON contains **6 main sections**:

### 1. Plain English (`plain_english`)
Non-technical summaries for HR managers, executives, and stakeholders:

```json
{
  "plain_english": {
    "one_liner": "Women are being selected at only 30% the rate of men in your dataset.",
    "biggest_problem": "The biggest problem is severe imbalance in who gets positive outcomes...",
    "legal_risk": "YES - High legal risk. Your dataset fails the EEOC 80% rule...",
    "quickest_fix": "Apply sample reweighting - this adjusts the importance of each data point..."
  }
}
```

**Use for:**
- Executive summaries
- Stakeholder presentations
- Legal/compliance reviews

---

### 2. Action Priority (`action_priority`)
Ranked list of actions by impact/effort ratio:

```json
{
  "action_priority": [
    {
      "rank": 1,
      "action": "Apply sample reweighting to balance positive outcome rates",
      "reason": "Highest impact, lowest effort. Current worst DIR is 0.30...",
      "effort": "LOW",
      "impact": "HIGH",
      "do_this_first": true
    }
  ]
}
```

**Ranking Logic:**
- Rank 1 = Highest impact, lowest effort
- `do_this_first: true` = Critical priority
- Effort: LOW | MEDIUM | HIGH
- Impact: LOW | MEDIUM | HIGH

**Use for:**
- Sprint planning
- Resource allocation
- Quick wins identification

---

### 3. Improvement Checklist (`improvement_checklist`)
Task-by-task checklist with one item per finding:

```json
{
  "improvement_checklist": [
    {
      "id": "C001",
      "task": "Fix label_bias: Severe disparate impact in 'gender'...",
      "reason": "Critical severity issue. Group 'Female' has 0.30x positive rate...",
      "columns_affected": ["gender"],
      "status": "pending",
      "priority": 1,
      "effort": "LOW",
      "expected_outcome": "Disparate impact ratio improves to ≥0.80 (EEOC compliant)"
    }
  ]
}
```

**Use for:**
- Project tracking (Jira, Asana, etc.)
- Progress monitoring
- Team assignments

---

### 4. Column Risk Scores (`column_risk_scores`)
Risk assessment for every column (especially proxy features):

```json
{
  "column_risk_scores": [
    {
      "column": "gender_Female",
      "risk_score": 10,
      "risk_level": "HIGH",
      "reason": "Correlated with gender (method: point_biserial, score: 1.000)",
      "protected_attribute": "gender",
      "action": "REMOVE",
      "action_reason": "Perfect correlation with protected attribute - this is the protected attribute itself"
    }
  ]
}
```

**Risk Levels:**
- `CRITICAL` (9-10): Remove immediately
- `HIGH` (7-8): Remove or transform
- `MEDIUM` (4-6): Transform or monitor
- `LOW` (1-3): Monitor only

**Actions:**
- `REMOVE`: Delete column from dataset
- `TRANSFORM`: Apply debiasing transformation
- `MONITOR`: Watch for bias amplification
- `KEEP`: Safe to use

**Use for:**
- Feature engineering decisions
- Data cleaning pipelines
- Model input selection

---

### 5. Simulated Improvements (`simulated_improvements`)
Before/after scenarios showing expected improvements:

```json
{
  "simulated_improvements": {
    "current_state": {
      "health_score": 45.5,
      "dir": 0.3004,
      "critical_findings": 5,
      "compliance": "FAIL"
    },
    "if_reweighting_applied": {
      "health_score_after": 85.5,
      "dir_after": 0.95,
      "findings_resolved": 4,
      "findings_remaining": 16,
      "compliance_after": "PASS",
      "accuracy_impact": "No accuracy impact - reweighting does not change data"
    },
    "if_all_applied": {
      "health_score_after": 92.0,
      "dir_after": 0.95,
      "findings_resolved": 15,
      "findings_remaining": 5,
      "compliance_after": "PASS",
      "recommended": true
    }
  }
}
```

**Scenarios:**
- `current_state`: Baseline metrics
- `if_reweighting_applied`: After applying reweighting
- `if_smote_applied`: After applying SMOTE oversampling
- `if_all_applied`: After applying all strategies (recommended)

**Use for:**
- ROI calculations
- Strategy comparison
- Stakeholder buy-in

---

### 6. Summary Stats (`summary_stats`)
High-level statistics for quick assessment:

```json
{
  "summary_stats": {
    "total_columns_at_risk": 10,
    "columns_to_remove": 6,
    "columns_to_monitor": 4,
    "estimated_fix_time": "4-8 hours",
    "retraining_required": true,
    "legal_risk_level": "CRITICAL"
  }
}
```

**Legal Risk Levels:**
- `CRITICAL`: EEOC violations detected
- `HIGH`: Critical findings present
- `MEDIUM`: Multiple moderate findings
- `LOW`: Minor issues only

**Use for:**
- Dashboard KPIs
- Executive summaries
- Risk assessments

---

## How to Generate

### Option 1: Using the Report Generator

```python
from library.dataset_audit import audit_dataset
from library.dataset_audit.report import generate_report

# Run audit
report = audit_dataset(
    data='your_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

# Generate full report with actionable insights
full_report = generate_report(report)

# Extract actionable insights
insights = full_report['actionable_insights']

# Save to JSON
import json
with open('actionable_insights.json', 'w') as f:
    json.dump(insights, f, indent=2)
```

### Option 2: Generate Only Actionable Insights

```python
from library.dataset_audit import audit_dataset
from library.dataset_audit.report import generate_report

# Run audit
report = audit_dataset(...)

# Generate only actionable insights section
insights_only = generate_report(report, sections=['actionable_insights'])
```

### Option 3: Using Existing Report Files

If you already have a comprehensive JSON report:

```python
import json
from library.dataset_audit.report.sections import ActionableInsightsSection
from library.dataset_audit.models import DatasetAuditReport

# Load existing report
with open('output/dataset_audit_comprehensive.json', 'r') as f:
    report_data = json.load(f)

# Reconstruct report object (if needed)
# Or directly use ActionableInsightsSection if you have the report object

# Generate insights
insights = ActionableInsightsSection.generate(report)
```

---

## Frontend Integration

### Dashboard Overview

```javascript
// Fetch insights
const insights = await fetch('/api/dataset-audit/insights').then(r => r.json());

// Display one-liner
document.getElementById('summary').textContent = insights.plain_english.one_liner;

// Display health score
const currentHealth = insights.simulated_improvements.current_state.health_score;
document.getElementById('health-score').textContent = `${currentHealth}/100`;

// Display legal risk badge
const riskLevel = insights.summary_stats.legal_risk_level;
document.getElementById('risk-badge').className = `badge badge-${riskLevel.toLowerCase()}`;
```

### Action Priority List

```javascript
// Render prioritized actions
insights.action_priority.forEach(action => {
  const card = `
    <div class="action-card ${action.do_this_first ? 'priority' : ''}">
      <h3>#${action.rank} - ${action.action}</h3>
      <div class="badges">
        <span class="effort-${action.effort.toLowerCase()}">${action.effort}</span>
        <span class="impact-${action.impact.toLowerCase()}">${action.impact}</span>
      </div>
      <p>${action.reason}</p>
    </div>
  `;
  document.getElementById('actions').innerHTML += card;
});
```

### Column Risk Table

```javascript
// Render column risks
const table = insights.column_risk_scores.map(col => `
  <tr class="risk-${col.risk_level.toLowerCase()}">
    <td>${col.column}</td>
    <td>${col.risk_score}/10</td>
    <td><span class="badge">${col.action}</span></td>
    <td>${col.action_reason}</td>
  </tr>
`).join('');

document.getElementById('column-risks').innerHTML = table;
```

### Improvement Simulator

```javascript
// Show before/after comparison
const current = insights.simulated_improvements.current_state;
const after = insights.simulated_improvements.if_all_applied;

const chart = new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['Current', 'After Fix'],
    datasets: [{
      label: 'Health Score',
      data: [current.health_score, after.health_score_after],
      backgroundColor: ['#ff6b6b', '#51cf66']
    }]
  }
});
```

---

## Example Output

See `examples/dataset_actionable_insights_example.py` for a complete working example.

Run it:
```bash
cd Nobias
python examples/dataset_actionable_insights_example.py
```

This will generate `output/dataset_actionable_insights.json` with the full insights structure.

---

## API Reference

### `ActionableInsightsSection.generate(audit_report)`

Generates actionable insights from a dataset audit report.

**Parameters:**
- `audit_report` (DatasetAuditReport): The audit report object

**Returns:**
- `dict`: Dictionary containing all 6 insight sections

**Example:**
```python
from library.dataset_audit.report.sections import ActionableInsightsSection

insights = ActionableInsightsSection.generate(report)
```

---

## Best Practices

### For Technical Users

1. **Start with action_priority**: Focus on rank 1 items first
2. **Use column_risk_scores**: Guide feature engineering decisions
3. **Reference improvement_checklist**: Track progress systematically
4. **Validate simulations**: Run actual fixes and compare to predictions

### For Non-Technical Users

1. **Read plain_english first**: Understand the problem in simple terms
2. **Focus on legal_risk**: Understand compliance implications
3. **Use quickest_fix**: Get immediate actionable guidance
4. **Show simulated_improvements**: Demonstrate ROI to stakeholders

### For Managers

1. **Use summary_stats**: Quick assessment of scope
2. **Reference estimated_fix_time**: Resource planning
3. **Show action_priority**: Sprint planning and prioritization
4. **Track improvement_checklist**: Progress monitoring

---

## Troubleshooting

### "No actionable insights generated"

**Cause:** Report has no findings
**Solution:** This is good! Your dataset has no bias issues.

### "Simulations show null values"

**Cause:** No remediation strategies were suggested
**Solution:** Check if your dataset has critical findings. Remediations are only suggested when issues are detected.

### "Column risk scores empty"

**Cause:** No proxy features detected
**Solution:** This is good! No features are leaking protected attribute information.

---

## Related Documentation

- [Dataset Audit Implementation Guide](niru_DATASET_AUDIT_IMPLEMENTATION_GUIDE.md)
- [Frontend Dataset Report Spec](FRONTEND_DATASET_REPORT_SPEC.md)
- [Dataset Audit Quick Start](niru_DATASET_AUDIT_QUICK_START.md)

---

## Support

For questions or issues:
1. Check the example script: `examples/dataset_actionable_insights_example.py`
2. Review the frontend spec: `docs/FRONTEND_DATASET_REPORT_SPEC.md`
3. Examine the source: `library/dataset_audit/report/sections.py`
