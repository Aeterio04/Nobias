# Dataset Audit Report - Frontend Data Specification

## Overview
This document describes all the data available from the **Dataset Audit Report** for frontend visualization. The report comes in 3 formats:
- **Basic JSON** (`dataset_audit_basic.json`) - Simplified structure for quick integration
- **Comprehensive JSON** (`dataset_audit_comprehensive.json`) - Full structured data for detailed dashboards
- **Detailed Text** (`dataset_audit_detailed.txt`) - Human-readable report

> **Note:** This is for DATASET audits. For MODEL audits, see `FRONTEND_REPORT_DATA_SPEC.md`

---

## 📊 Report Structure (8 Main Sections)

### 1. HEALTH & METADATA
**What it shows:** Overall dataset health and audit summary

```json
{
  "health": {
    "overall_severity": "CRITICAL",        // CLEAR | LOW | MODERATE | CRITICAL
    "health_score": 45.5,                  // 0-100 score
    "total_findings": 20,
    "critical_findings": 5,
    "moderate_findings": 11,
    "low_findings": 4,
    "proxy_features_detected": 10,
    "timestamp": "2026-04-26T14:20:27.724306"
  }
}
```

**Frontend Display Ideas:**
- 🎯 Health score gauge (45.5/100) with color gradient
- 🚦 Severity badge (CRITICAL = red)
- 📈 Findings breakdown donut chart
- ⚠️ Proxy features alert badge

---

### 2. CONFIGURATION
**What it shows:** Dataset metadata and audit configuration

```json
{
  "config": {
    "dataset_name": "test_data_biased.csv",
    "row_count": 600,
    "column_count": 13,
    "audit_timestamp": "2026-04-26T14:20:27.724330"
  }
}
```

**Frontend Display Ideas:**
- 📋 Dataset info card
- 📊 Size indicators (rows × columns)
- 🕐 Audit timestamp

---

### 3. REPRESENTATION ANALYSIS
**What it shows:** Demographic distribution and balance issues

#### 3.1 Group Distributions
```json
{
  "representation": {
    "group_distributions": {
      "gender": {
        "Male": {
          "count": 349,
          "percentage": 58.17,
          "ratio_to_majority": 1.0
        },
        "Female": {
          "count": 251,
          "percentage": 41.83,
          "ratio_to_majority": 0.719
        }
      },
      "race": {
        "White": {
          "count": 333,
          "percentage": 55.5,
          "ratio_to_majority": 1.0
        },
        "Asian": {
          "count": 105,
          "percentage": 17.5,
          "ratio_to_majority": 0.315
        },
        "Black": {
          "count": 88,
          "percentage": 14.67,
          "ratio_to_majority": 0.264
        },
        "Hispanic": {
          "count": 74,
          "percentage": 12.33,
          "ratio_to_majority": 0.222
        }
      }
    }
  }
}
```

**Frontend Display Ideas:**
- 📊 Stacked bar chart showing group percentages
- 🥧 Pie chart for each protected attribute
- 📉 Ratio to majority visualization
- ⚠️ Under-representation warnings (<35%)

#### 3.2 Label Rates (Positive Outcome Rates)
```json
{
  "label_rates": {
    "gender": {
      "Female": {
        "positive_rate": 0.1076,          // 10.76% positive rate
        "count": 251,
        "positive_count": 27
      },
      "Male": {
        "positive_rate": 0.3582,          // 35.82% positive rate
        "count": 349,
        "positive_count": 125
      }
    },
    "race": {
      "Asian": {
        "positive_rate": 0.1429,
        "count": 105,
        "positive_count": 15
      }
      // ... more groups
    }
  }
}
```

**Frontend Display Ideas:**
- 📊 Side-by-side bar chart comparing positive rates
- 🎯 Disparity indicators (Female: 10.76% vs Male: 35.82%)
- 📈 Positive count vs total count visualization

#### 3.3 KL Divergence (Distribution Shift)
```json
{
  "kl_divergences": {
    "gender": {
      "Female": 0.1648,                   // Higher = more shift
      "Male": 0.0                         // Baseline (majority group)
    },
    "race": {
      "Asian": 0.097,
      "White": 0.0,                       // Baseline
      "Hispanic": 0.0646,
      "Black": 0.1044
    }
  }
}
```

**What it means:** How much each group's label distribution differs from the majority group (0 = no difference, higher = more shift)

**Frontend Display Ideas:**
- 📊 Divergence bar chart
- ⚠️ Alert if KL > 0.1 (significant shift)
- 📈 Heatmap showing distribution differences

#### 3.4 Intersectional Disparities
```json
{
  "intersectional_disparities": [
    {
      "attributes": ["gender", "race"],
      "best_group": ["Male", "White"],
      "worst_group": ["Female", "Black"],
      "best_rate": 0.484,                 // 48.4% positive rate
      "worst_rate": 0.0278,               // 2.78% positive rate
      "dir": 0.057,                       // Disparate Impact Ratio
      "disparity_pct": 94.26              // 94.26% disparity!
    }
  ]
}
```

**Frontend Display Ideas:**
- 🔥 Disparity heatmap (gender × race)
- 📊 Best vs worst group comparison
- 🚨 Critical alert for >90% disparity
- 📈 Intersectional positive rate matrix

---

### 4. PROXY FEATURES DETECTION
**What it shows:** Features that may leak protected attribute information

```json
{
  "proxy_features": {
    "total_proxy_features": 10,
    "high_risk_proxies": 6,
    "medium_risk_proxies": 4,
    "low_risk_proxies": 0,
    "proxy_features": [
      {
        "feature": "gender_Female",
        "protected_attribute": "gender",
        "detection_method": "point_biserial",
        "correlation_score": 1.0,
        "normalized_mutual_info": 1.0,
        "risk_level": "HIGH"              // HIGH | MEDIUM | LOW
      },
      {
        "feature": "interview_score",
        "protected_attribute": "gender",
        "detection_method": "point_biserial",
        "correlation_score": 0.043,
        "normalized_mutual_info": 0.326,
        "risk_level": "MEDIUM"
      }
      // ... more proxy features
    ]
  }
}
```

**Detection Methods:**
- `point_biserial` - For binary protected attributes
- `eta_squared` - For categorical protected attributes

**Frontend Display Ideas:**
- 📋 Proxy features table with risk badges
- 🎯 Risk level breakdown (6 high, 4 medium, 0 low)
- 📊 Correlation score visualization
- 🔍 Feature-to-attribute mapping
- ⚠️ High-risk feature alerts

---

### 5. FINDINGS & ISSUES
**What it shows:** Specific bias issues detected in the dataset

```json
{
  "findings": {
    "total_findings": 20,
    "findings_by_severity": {
      "CRITICAL": [
        {
          "check_type": "label_bias",
          "message": "Severe disparate impact in 'gender': group 'Female' has 0.30x positive rate vs 'Male' (p=0.0000)",
          "metric_name": "DIR",
          "metric_value": 0.3004,
          "threshold": 0.6,
          "confidence": 0.8,
          "severity": "CRITICAL"
        },
        {
          "check_type": "intersectional_disparity",
          "message": "Intersectional disparity: (gender=Female, race=Black) has 94.3% lower positive rate than (gender=Male, race=White)",
          "metric_name": "DIR",
          "metric_value": 0.0574,
          "threshold": 0.9,
          "confidence": 0.6,
          "severity": "CRITICAL"
        }
        // ... more critical findings
      ],
      "MODERATE": [
        {
          "check_type": "representation",
          "message": "Group 'Asian' in 'race' is under-represented (105 samples, 17.5% of dataset)",
          "metric_name": "percentage",
          "metric_value": 17.5,
          "threshold": 35.0,
          "confidence": 0.8,
          "severity": "MODERATE"
        },
        {
          "check_type": "superadditive_bias",
          "message": "Superadditive bias detected: intersectional disparity (0.456) exceeds individual attribute disparities",
          "metric_name": "disparity_ratio",
          "metric_value": 1.8207,
          "threshold": 1.2,
          "confidence": 0.8,
          "severity": "MODERATE"
        }
        // ... more moderate findings
      ],
      "LOW": [ /* ... */ ]
    },
    "summary": "Dataset shows 5 critical bias issue(s) requiring immediate attention."
  }
}
```

**Finding Check Types:**
- `label_bias` - Disparate impact in positive label rates
- `representation` - Under-representation of groups
- `intersectional_representation` - Under-representation of intersectional groups
- `intersectional_disparity` - Compounded bias across attributes
- `superadditive_bias` - Intersectional bias exceeds individual biases
- `kl_divergence` - Label distribution shift

**Metrics:**
- `DIR` - Disparate Impact Ratio (should be ≥0.8 for EEOC compliance)
- `SPD` - Statistical Parity Difference (should be near 0)
- `KL` - Kullback-Leibler divergence (distribution shift)

**Frontend Display Ideas:**
- 🚨 Findings list with severity badges
- 📊 Findings by check type breakdown
- 🔍 Expandable finding cards with details
- 📈 Metric value vs threshold visualization
- 🎯 Confidence level indicators
- ⚠️ Priority queue (critical first)

---

### 6. REMEDIATION STRATEGIES
**What it shows:** Recommended strategies to fix dataset bias

```json
{
  "remediation": {
    "total_strategies": 3,
    "recommended_strategies": [
      {
        "strategy_name": "reweighting",
        "description": "Adjust sample weights to equalize positive label rates across groups",
        "estimated_dir_after": 0.95,
        "estimated_spd_after": -0.02,
        "implementation_complexity": "LOW",
        "expected_impact": "HIGH"
      },
      {
        "strategy_name": "disparate_impact_remover",
        "description": "Transform feature distributions to reduce group-dependent variation (repair level: 0.8)",
        "estimated_dir_after": 0.88,
        "estimated_spd_after": -0.05,
        "implementation_complexity": "MEDIUM",
        "expected_impact": "MEDIUM"
      },
      {
        "strategy_name": "smote",
        "description": "Oversample under-represented intersectional groups using SMOTE",
        "estimated_dir_after": 0.87,
        "estimated_spd_after": -0.06,
        "implementation_complexity": "MEDIUM",
        "expected_impact": "MEDIUM"
      }
    ],
    "priority_order": [
      "reweighting",
      "disparate_impact_remover",
      "smote"
    ]
  }
}
```

**Available Strategies:**
- `reweighting` - Adjust sample weights (no data modification)
- `disparate_impact_remover` - Transform features to reduce bias
- `smote` - Synthetic oversampling for minority groups

**Frontend Display Ideas:**
- 📋 Strategy cards with complexity/impact badges
- 📊 Before/after metric comparison (DIR, SPD)
- 🎯 Priority order timeline
- 📈 Expected improvement visualization
- 💡 Implementation complexity indicators

---

### 7. COMPLIANCE STATUS
**What it shows:** Legal compliance with EEOC 80% rule

```json
{
  "compliance": {
    "eeoc_80_rule": {
      "total_violations": 4,
      "violations": [
        {
          "attribute": "gender",
          "group": "Female",
          "selection_rate": 0.1076,       // 10.76%
          "max_rate": 0.3582,             // 35.82% (Male)
          "ratio": 0.3004,                // 30.04% (FAIL - needs ≥80%)
          "passes_80_rule": false
        },
        {
          "attribute": "race",
          "group": "Asian",
          "selection_rate": 0.1429,
          "max_rate": 0.3363,
          "ratio": 0.4249,                // 42.49% (FAIL)
          "passes_80_rule": false
        }
        // ... more violations
      ],
      "compliant": false
    },
    "representation_balance": {
      "total_issues": 1,
      "issues": [
        {
          "attribute": "race",
          "imbalance_ratio": 0.2222,
          "concern": "Severe underrepresentation detected"
        }
      ]
    },
    "overall_compliance_status": "FAIL",
    "recommendations": [
      "Address EEOC 80% rule violations through resampling or reweighting to ensure selection rates across groups meet the 4/5ths threshold.",
      "Improve demographic representation balance through targeted data collection or synthetic data augmentation for underrepresented groups."
    ]
  }
}
```

**Frontend Display Ideas:**
- ⚖️ Compliance status banner (PASS/FAIL)
- 🚨 Violations list with ratios
- 📊 80% rule gauge for each group
- 📈 Selection rate comparison chart
- 💡 Compliance recommendations

---

### 8. STATISTICAL VALIDITY
**What it shows:** Reliability and limitations of the audit

```json
{
  "validity": {
    "average_confidence": 0.67,
    "sample_size": 600,
    "sample_adequacy": "MARGINAL",      // INADEQUATE | MARGINAL | ADEQUATE | EXCELLENT
    "data_completeness": 1.0,           // 0-1 (1.0 = no missing data)
    "statistical_power": "HIGH",        // LOW | MEDIUM | HIGH
    "limitations": [
      "No major limitations identified in the audit methodology."
    ]
  }
}
```

**Frontend Display Ideas:**
- 📊 Confidence level indicator
- 📈 Sample adequacy badge
- ✓ Data completeness percentage
- ⚡ Statistical power indicator
- ℹ️ Limitations info panel

---

### 8. STATISTICAL VALIDITY

### Dashboard Overview
```
┌─────────────────────────────────────────────────────┐
│  Dataset: test_data_biased.csv         [CRITICAL]  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  Health Score: 45.5/100  ████████░░░░░░░░░░░░░░░░  │
│                                                      │
│  Findings:  🔴 5 Critical  🟡 11 Moderate  🟢 4 Low │
│                                                      │
│  Proxy Features: ⚠️ 10 detected (6 high-risk)      │
│                                                      │
│  Compliance: ⚖️ FAIL (4 EEOC violations)           │
│                                                      │
│  Samples: 600 rows × 13 columns                     │
└─────────────────────────────────────────────────────┘
```

### Representation View
```
┌─────────────────────────────────────────────────────┐
│  Group Distribution: Gender                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  Male    ████████████████████ 58.17% (349)         │
│  Female  ██████████████ 41.83% (251)               │
│                                                      │
│  Positive Label Rates:                              │
│  Male    ████████████ 35.82%                        │
│  Female  ███ 10.76%  ⚠️ 30% of Male rate (FAIL)    │
│                                                      │
│  Disparity Impact Ratio: 0.30 (needs ≥0.80)        │
└─────────────────────────────────────────────────────┘
```

### Intersectional Disparity Heatmap
```
Positive Label Rates (%)

              Asian    Black    Hispanic   White
Female        🔴 0%    🔴 3%    🟡 6%      🟡 17%
Male          🟡 18%   🟡 15%   🟡 18%     🟢 48%

Best Group:  Male + White (48.4%)
Worst Group: Female + Black (2.78%)
Disparity:   94.26% 🚨 CRITICAL
```

### Proxy Features Table
```
┌─────────────────────────────────────────────────────┐
│  Proxy Features Detected: 10                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  Feature            Protected Attr   Risk   Corr    │
│  ─────────────────────────────────────────────────  │
│  gender_Female      gender          🔴 HIGH  1.00   │
│  gender_Male        gender          🔴 HIGH  1.00   │
│  race_White         race            🔴 HIGH  0.77   │
│  race_Asian         race            🔴 HIGH  0.63   │
│  interview_score    gender          🟡 MED   0.33   │
│  years_experience   race            🟡 MED   0.43   │
│  ... 4 more                                         │
└─────────────────────────────────────────────────────┘
```

### Findings List
```
┌─────────────────────────────────────────────────────┐
│  🔴 CRITICAL FINDINGS (5)                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  [1] Label Bias: Gender                             │
│      Female has 0.30x positive rate vs Male         │
│      DIR: 0.30 (threshold: 0.60) p<0.0001 ***      │
│                                                      │
│  [2] Intersectional Disparity                       │
│      Female+Black: 94.3% lower than Male+White      │
│      DIR: 0.057 (threshold: 0.90)                   │
│                                                      │
│  [3] Label Bias: Race (Asian)                       │
│      Asian has 0.42x positive rate vs White         │
│      DIR: 0.42 (threshold: 0.60) p=0.0061 **       │
│                                                      │
│  ... 2 more                                         │
└─────────────────────────────────────────────────────┘
```

### Remediation Strategies
```
┌─────────────────────────────────────────────────────┐
│  💡 RECOMMENDED REMEDIATION                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  1. Reweighting (Priority 1)                        │
│     Complexity: 🟢 Low                              │
│     Impact: 🔥 High                                 │
│     Expected DIR: 0.30 → 0.95 ✓                    │
│     Expected SPD: -0.25 → -0.02 ✓                  │
│                                                      │
│  2. Disparate Impact Remover                        │
│     Complexity: 🟡 Medium                           │
│     Impact: 🟡 Medium                               │
│     Expected DIR: 0.30 → 0.88                      │
│                                                      │
│  3. SMOTE Oversampling                              │
│     Complexity: 🟡 Medium                           │
│     Impact: 🟡 Medium                               │
│     Expected DIR: 0.30 → 0.87                      │
└─────────────────────────────────────────────────────┘
```

### Compliance Status
```
┌─────────────────────────────────────────────────────┐
│  ⚖️ EEOC 80% RULE COMPLIANCE: FAIL                 │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  Violations: 4                                      │
│                                                      │
│  Gender - Female:                                   │
│    Selection Rate: 10.76% vs 35.82% (Male)         │
│    Ratio: 30.04%  ❌ (needs ≥80%)                  │
│                                                      │
│  Race - Asian:                                      │
│    Selection Rate: 14.29% vs 33.63% (White)        │
│    Ratio: 42.49%  ❌ (needs ≥80%)                  │
│                                                      │
│  ... 2 more violations                              │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Data Access Patterns

### Quick Summary (Basic JSON)
```json
{
  "dataset_name": "test_data_biased.csv",
  "overall_severity": "CRITICAL",
  "health_score": 45.5,
  "total_findings": 20,
  "critical_findings": 5,
  "proxy_features_detected": 10,
  "compliance_status": "FAIL"
}
```

Use for:
- Dashboard overview
- Quick health check
- Alert notifications

### Detailed Analysis (Comprehensive JSON)
Use for:
- Full representation analysis
- Proxy feature detection details
- Intersectional disparity analysis
- Remediation recommendations
- Compliance details

---

## 🎯 Key Metrics to Highlight

### Most Important for Users:
1. **Health Score** - 0-100 overall dataset quality
2. **Overall Severity** - CRITICAL/MODERATE/LOW/CLEAR
3. **Critical Findings Count** - Number of serious issues
4. **Compliance Status** - EEOC 80% rule compliance
5. **Proxy Features** - High-risk feature count

### Most Important for Technical Users:
1. **DIR (Disparate Impact Ratio)** - Should be ≥0.8
2. **SPD (Statistical Parity Difference)** - Should be near 0
3. **Intersectional Disparities** - Compounded bias
4. **KL Divergence** - Distribution shift
5. **Proxy Feature Correlations** - Feature leakage risk

---

## 🚀 Implementation Tips

1. **Color Coding:**
   - 🔴 Red: CRITICAL, FAIL, High-risk, <60% DIR
   - 🟡 Yellow: MODERATE, Medium-risk, 60-80% DIR
   - 🟢 Green: CLEAR, PASS, Low-risk, ≥80% DIR

2. **Progressive Disclosure:**
   - Show health score and severity first
   - Drill down into representation, findings, proxies
   - Provide tooltips for technical metrics

3. **Comparison Views:**
   - Before/after remediation metrics
   - Group-to-group comparisons
   - Intersectional heatmaps

4. **Export Options:**
   - PDF compliance report
   - CSV findings export
   - JSON API access

5. **Interactivity:**
   - Filter findings by severity/type
   - Filter by protected attribute
   - Sort by metric value
   - Expand/collapse finding details

---

## 📚 Glossary for Frontend

- **DIR (Disparate Impact Ratio)**: Ratio of selection rates between groups (EEOC requires ≥0.8)
- **SPD (Statistical Parity Difference)**: Difference in positive rates (should be near 0)
- **KL Divergence**: Measure of distribution shift from majority group
- **Proxy Feature**: Feature correlated with protected attributes (potential bias source)
- **Intersectional Disparity**: Compounded bias across multiple protected attributes
- **Superadditive Bias**: When intersectional bias exceeds sum of individual biases
- **EEOC 80% Rule**: Legal requirement that selection rate for any group ≥80% of highest group
- **Reweighting**: Adjust sample importance without changing data
- **SMOTE**: Synthetic Minority Over-sampling Technique

---

## 🔗 Related Files

- Dataset Audit API: `Nobias/library/dataset_audit/api.py`
- Example Reports: `Nobias/output/dataset_audit_*.json`
- Model Audit Spec: `Nobias/docs/FRONTEND_REPORT_DATA_SPEC.md`
- **Actionable Insights Guide**: `Nobias/docs/ACTIONABLE_INSIGHTS_GUIDE.md` ⭐ NEW!
- **Actionable Insights Example**: `Nobias/examples/dataset_actionable_insights_example.py` ⭐ NEW!

---

## ⭐ NEW: Section 9 - Actionable Insights

The comprehensive JSON now includes an `actionable_insights` section with plain-English summaries and prioritized actions.

**See full documentation:** `docs/ACTIONABLE_INSIGHTS_GUIDE.md`

**Key subsections:**
1. `plain_english` - Non-technical summaries for stakeholders
2. `action_priority` - Ranked actions by impact/effort ratio
3. `improvement_checklist` - Task-by-task checklist
4. `column_risk_scores` - Risk assessment for each column
5. `simulated_improvements` - Before/after scenarios
6. `summary_stats` - High-level statistics

**Example usage:**
```javascript
const report = await fetch('/api/dataset-audit/comprehensive').then(r => r.json());
const insights = report.actionable_insights;

// Display one-liner for executives
document.getElementById('summary').textContent = insights.plain_english.one_liner;

// Show prioritized actions
insights.action_priority.forEach(action => {
  // Render action card with effort/impact badges
});

// Display column risks
insights.column_risk_scores.forEach(col => {
  // Render risk table with action buttons
});
```

For complete integration examples, see `docs/ACTIONABLE_INSIGHTS_GUIDE.md`.
