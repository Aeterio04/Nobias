# Frontend Quick Reference: Actionable Insights JSON

## TL;DR

Use `model_audit_actionable_insights.json` for business-friendly dashboards. It contains 7 sections with plain-English explanations and prioritized actions.

---

## JSON Structure at a Glance

```json
{
  "plain_english": { /* 5 fields - executive summary */ },
  "action_priority": [ /* Ranked actions with effort/impact */ ],
  "bias_amplification": { /* Model vs dataset bias */ },
  "group_performance_gaps": [ /* Performance differences */ ],
  "metric_scorecard": [ /* All metrics with pass/fail */ ],
  "simulated_improvements": { /* Expected outcomes */ },
  "summary_stats": { /* KPIs for dashboard */ }
}
```

---

## Quick Access Patterns

### Display One-Liner Summary
```javascript
const insights = await fetchInsights();
document.getElementById('summary').textContent = 
  insights.plain_english.one_liner;
```

### Show Risk Badge
```javascript
const riskLevel = insights.summary_stats.legal_risk_level;
// Returns: "CRITICAL" | "HIGH" | "MEDIUM" | "LOW"

const badgeClass = {
  'CRITICAL': 'badge-danger',
  'HIGH': 'badge-warning',
  'MEDIUM': 'badge-info',
  'LOW': 'badge-success'
}[riskLevel];
```

### Render Action Cards
```javascript
insights.action_priority.forEach(action => {
  const card = `
    <div class="action-card ${action.do_this_first ? 'priority' : ''}">
      <h3>#${action.rank} ${action.action.split(':')[0]}</h3>
      <div class="badges">
        <span class="effort-${action.effort.toLowerCase()}">${action.effort}</span>
        <span class="impact-${action.impact.toLowerCase()}">${action.impact}</span>
        ${action.requires_retraining ? '<span class="retraining">Retraining</span>' : ''}
      </div>
      <p>${action.reason}</p>
      <p class="expected">${action.expected_metric_improvement}</p>
    </div>
  `;
  document.getElementById('actions').innerHTML += card;
});
```

### Display Metrics Pass Rate
```javascript
const stats = insights.summary_stats;
const passRate = (stats.metrics_passed / stats.total_metrics_tested * 100).toFixed(1);

document.getElementById('pass-rate').textContent = `${passRate}%`;
document.getElementById('metrics-passed').textContent = stats.metrics_passed;
document.getElementById('metrics-failed').textContent = stats.metrics_failed;
```

### Show Compliance Status
```javascript
const current = insights.simulated_improvements.current_state;
const statusClass = current.compliance === 'PASS' ? 'compliant' : 'non-compliant';

document.getElementById('compliance-badge').className = statusClass;
document.getElementById('compliance-text').textContent = current.compliance;
```

---

## Field Reference

### `plain_english` (Executive Summary)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `one_liner` | string | One sentence summary | "This model has 4 critical bias issues..." |
| `biggest_problem` | string | Worst finding explained | "The model approves different groups at..." |
| `what_this_means_for_users` | string | Impact on real people | "Real people from certain demographic groups..." |
| `legal_risk` | string | Legal exposure assessment | "YES - This model would likely fail an EEOC audit..." |
| `quickest_fix` | string | Fastest remediation | "Threshold Adjustment: Adjust decision thresholds..." |

**Use for:** Executive dashboards, compliance reports, stakeholder presentations

---

### `action_priority` (Ranked Actions)

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `rank` | number | Priority rank | 1, 2, 3... |
| `action` | string | Action description | "Threshold Adjustment: ..." |
| `reason` | string | Why this rank | "Ranked #1 because..." |
| `requires_retraining` | boolean | Needs retraining? | true / false |
| `effort` | string | Implementation effort | "LOW" / "MEDIUM" / "HIGH" |
| `impact` | string | Expected impact | "LOW" / "MEDIUM" / "HIGH" |
| `do_this_first` | boolean | Top priority flag | true / false |
| `expected_metric_improvement` | string | Expected outcome | "Demographic parity drops from..." |

**Use for:** Sprint planning, roadmap prioritization, resource allocation

**Sorting:** Already sorted by priority (rank 1 = highest)

---

### `bias_amplification` (Model vs Dataset)

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `dataset_dir` | number/null | Dataset disparate impact | 0.75 or null |
| `model_dir` | number | Model disparate impact | 0.65 |
| `amplification_score` | number/null | Difference (model - dataset) | -0.10 or null |
| `verdict` | string | Plain English verdict | "Model REDUCED bias" / "Model AMPLIFIED bias" / "No dataset audit available" |
| `explanation` | string | Detailed explanation | "The model actually reduced bias!..." |

**Use for:** Root cause analysis, model selection, training data quality assessment

**Note:** Requires dataset audit. If `dataset_dir` is null, verdict will be "No dataset audit available"

---

### `group_performance_gaps` (Performance Differences)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `attribute` | string | Protected attribute | "gender" / "race" |
| `privileged_group` | string | Reference group | "Male" |
| `unprivileged_group` | string | Comparison group | "Female" |
| `accuracy_gap` | number | Accuracy difference | 0.0215 |
| `fpr_gap` | number | False positive rate diff | 0.1212 |
| `fnr_gap` | number | False negative rate diff | 0.0357 |
| `severity` | string | Gap severity | "CRITICAL" / "MODERATE" / "LOW" |
| `plain_english` | string | Explanation | "Female is 12.1% more likely to be falsely rejected..." |

**Use for:** Identifying affected groups, understanding error patterns, targeted mitigation

**Positive gaps:** Unprivileged group has higher rate  
**Negative gaps:** Privileged group has higher rate

---

### `metric_scorecard` (All Metrics)

| Field | Type | Description | Values |
|-------|------|-------------|--------|
| `metric` | string | Metric name | "Demographic Parity Difference" |
| `attribute` | string | Protected attribute | "gender" / "race" |
| `value` | number | Metric value | 0.2660 |
| `threshold` | number | Pass threshold | 0.1 |
| `passed` | boolean | Pass/fail status | true / false |
| `gap_to_pass` | number | Improvement needed | 0.1660 |
| `severity` | string | Severity if failed | "CRITICAL" / "MODERATE" / "LOW" / "PASS" |

**Use for:** Detailed metric analysis, compliance checklists, progress tracking

**Filter failed metrics:**
```javascript
const failedMetrics = insights.metric_scorecard.filter(m => !m.passed);
```

---

### `simulated_improvements` (Expected Outcomes)

#### `current_state`
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pass_rate` | number | Current pass rate | 0.30 (30%) |
| `critical_findings` | number | Critical issues | 4 |
| `compliance` | string | EEOC compliance | "PASS" / "FAIL" |
| `worst_dir` | number | Worst disparate impact | 0.7955 |

#### `if_threshold_adjustment` (Post-processing)
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pass_rate_after` | number | Expected pass rate | 0.60 (60%) |
| `critical_findings_after` | number | Expected critical issues | 2 |
| `compliance_after` | string | Expected compliance | "PASS" / "FAIL" |
| `requires_retraining` | boolean | Needs retraining | false |
| `accuracy_impact` | string | Accuracy loss | "Typically <2% accuracy loss" |
| `recommended` | boolean | Recommended action | true |

#### `if_reweighting` (Pre-processing)
Same fields as threshold adjustment, but `requires_retraining: true`

#### `if_all_applied` (Combined)
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `pass_rate_after` | number | Expected pass rate | 0.80 (80%) |
| `critical_findings_after` | number | Expected critical issues | 0 |
| `compliance_after` | string | Expected compliance | "PASS" |
| `recommended` | boolean | Recommended action | true |

**Use for:** Cost-benefit analysis, strategy selection, stakeholder buy-in

---

### `summary_stats` (Dashboard KPIs)

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `total_metrics_tested` | number | Total metrics | 20 |
| `metrics_passed` | number | Passed metrics | 6 |
| `metrics_failed` | number | Failed metrics | 14 |
| `pass_rate` | number | Pass rate | 0.30 (30%) |
| `protected_attributes_tested` | array | Attributes tested | ["gender", "race"] |
| `worst_performing_group` | string | Worst group | "gender=Female" |
| `best_performing_group` | string | Best group | "gender=Male" |
| `flip_rate` | number | Counterfactual flip rate | 0.0 (0%) |
| `individual_fairness` | string | Individual fairness | "PASS" / "FAIL" |
| `legal_risk_level` | string | Legal risk | "CRITICAL" / "HIGH" / "MEDIUM" / "LOW" |
| `retraining_required` | boolean | Needs retraining | true |

**Use for:** Dashboard overview, executive summaries, KPI tracking

---

## Color Coding Recommendations

### Severity / Risk Levels
```css
.severity-critical, .risk-critical { color: #dc3545; } /* Red */
.severity-high, .risk-high { color: #fd7e14; } /* Orange */
.severity-moderate, .risk-medium { color: #ffc107; } /* Yellow */
.severity-low, .risk-low { color: #28a745; } /* Green */
.severity-pass { color: #20c997; } /* Teal */
```

### Effort Levels
```css
.effort-low { color: #28a745; } /* Green */
.effort-medium { color: #ffc107; } /* Yellow */
.effort-high { color: #dc3545; } /* Red */
```

### Impact Levels
```css
.impact-high { font-weight: bold; color: #007bff; } /* Blue */
.impact-medium { color: #6c757d; } /* Gray */
.impact-low { color: #adb5bd; } /* Light Gray */
```

### Compliance Status
```css
.compliant { color: #28a745; } /* Green */
.non-compliant { color: #dc3545; } /* Red */
```

---

## Common UI Patterns

### Dashboard Overview Card
```javascript
const stats = insights.summary_stats;
const plain = insights.plain_english;

const overviewHTML = `
  <div class="overview-card">
    <h2>Model Bias Audit</h2>
    <p class="summary">${plain.one_liner}</p>
    
    <div class="metrics">
      <div class="metric">
        <span class="label">Pass Rate</span>
        <span class="value">${(stats.pass_rate * 100).toFixed(1)}%</span>
      </div>
      <div class="metric">
        <span class="label">Legal Risk</span>
        <span class="value risk-${stats.legal_risk_level.toLowerCase()}">
          ${stats.legal_risk_level}
        </span>
      </div>
      <div class="metric">
        <span class="label">Flip Rate</span>
        <span class="value">${(stats.flip_rate * 100).toFixed(2)}%</span>
      </div>
    </div>
  </div>
`;
```

### Action Priority List
```javascript
const actionsHTML = insights.action_priority.map(action => `
  <div class="action-item ${action.do_this_first ? 'priority' : ''}">
    <div class="action-header">
      <span class="rank">#${action.rank}</span>
      <h3>${action.action.split(':')[0]}</h3>
      ${action.do_this_first ? '<span class="badge">DO THIS FIRST</span>' : ''}
    </div>
    
    <div class="action-badges">
      <span class="badge effort-${action.effort.toLowerCase()}">${action.effort} Effort</span>
      <span class="badge impact-${action.impact.toLowerCase()}">${action.impact} Impact</span>
      ${action.requires_retraining ? '<span class="badge retraining">Retraining Required</span>' : '<span class="badge no-retraining">No Retraining</span>'}
    </div>
    
    <p class="reason">${action.reason}</p>
    <p class="expected"><strong>Expected:</strong> ${action.expected_metric_improvement}</p>
  </div>
`).join('');
```

### Metric Scorecard Table
```javascript
const failedMetrics = insights.metric_scorecard.filter(m => !m.passed);

const tableHTML = `
  <table class="metric-table">
    <thead>
      <tr>
        <th>Metric</th>
        <th>Attribute</th>
        <th>Value</th>
        <th>Threshold</th>
        <th>Gap to Pass</th>
        <th>Severity</th>
      </tr>
    </thead>
    <tbody>
      ${failedMetrics.map(m => `
        <tr class="severity-${m.severity.toLowerCase()}">
          <td>${m.metric}</td>
          <td>${m.attribute}</td>
          <td>${m.value.toFixed(4)}</td>
          <td>${m.threshold}</td>
          <td>${m.gap_to_pass.toFixed(4)}</td>
          <td><span class="badge severity-${m.severity.toLowerCase()}">${m.severity}</span></td>
        </tr>
      `).join('')}
    </tbody>
  </table>
`;
```

### Simulated Improvements Chart
```javascript
const sim = insights.simulated_improvements;

const chartData = {
  labels: ['Current', 'Threshold Adj', 'Reweighting', 'All Applied'],
  datasets: [{
    label: 'Pass Rate',
    data: [
      sim.current_state.pass_rate * 100,
      sim.if_threshold_adjustment.pass_rate_after * 100,
      sim.if_reweighting.pass_rate_after * 100,
      sim.if_all_applied.pass_rate_after * 100
    ],
    backgroundColor: ['#dc3545', '#ffc107', '#fd7e14', '#28a745']
  }]
};

// Use with Chart.js or similar
new Chart(ctx, {
  type: 'bar',
  data: chartData,
  options: {
    scales: {
      y: { beginAtZero: true, max: 100 }
    }
  }
});
```

---

## API Integration

### Fetch Insights
```javascript
async function fetchActionableInsights(auditId) {
  const response = await fetch(`/api/audits/${auditId}/actionable-insights`);
  if (!response.ok) throw new Error('Failed to fetch insights');
  return await response.json();
}
```

### Refresh Insights
```javascript
async function refreshInsights(auditId) {
  const response = await fetch(`/api/audits/${auditId}/regenerate-insights`, {
    method: 'POST'
  });
  return await response.json();
}
```

---

## Testing

### Sample Data
Use `Nobias/output/model_audit_actionable_insights.json` for testing

### Validate Structure
```javascript
function validateInsights(insights) {
  const required = [
    'plain_english',
    'action_priority',
    'bias_amplification',
    'group_performance_gaps',
    'metric_scorecard',
    'simulated_improvements',
    'summary_stats'
  ];
  
  return required.every(key => key in insights);
}
```

---

## Need More Details?

- **Full Documentation:** [MODEL_AUDIT_ACTIONABLE_INSIGHTS.md](MODEL_AUDIT_ACTIONABLE_INSIGHTS.md)
- **Implementation Guide:** [MODEL_AUDIT_INTERPRETER_SUMMARY.md](MODEL_AUDIT_INTERPRETER_SUMMARY.md)
- **Frontend Data Spec:** [FRONTEND_REPORT_DATA_SPEC.md](FRONTEND_REPORT_DATA_SPEC.md)

---

## Quick Links

- **Example File:** `Nobias/output/model_audit_actionable_insights.json`
- **Example Code:** `Nobias/examples/actionable_insights_example.py`
- **Source Code:** `Nobias/library/model_audit/interpreter.py`
