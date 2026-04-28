# Model Audit Report - Frontend Data Specification

## Overview
This document describes all the data available from the Model Audit Report for frontend visualization. The report comes in 3 formats:
- **Basic JSON** (`model_audit_basic.json`) - Simplified structure for quick integration
- **Comprehensive JSON** (`model_audit_comprehensive.json`) - Full structured data for detailed dashboards
- **Detailed Text** (`model_audit_detailed.txt`) - Human-readable report

---

## 📊 Report Structure (7 Main Sections)

### 1. HEALTH & METADATA
**What it shows:** Overall model health and audit summary

```json
{
  "health": {
    "model_info": {
      "model_name": "biased_model",
      "model_type": "binary_classifier",
      "test_sample_count": 600
    },
    "overall_health": {
      "severity": "MODERATE",           // CLEAR | LOW | MODERATE | CRITICAL
      "critical_findings": 4,
      "moderate_findings": 9,
      "low_findings": 2
    },
    "metrics_summary": {
      "total_metrics": 20,
      "passed_metrics": 6,
      "failed_metrics": 14,
      "pass_rate": 0.3                  // 30% pass rate
    }
  }
}
```

**Frontend Display Ideas:**
- 🎯 Health score gauge/meter (30% pass rate)
- 🚦 Severity badge with color coding (red=critical, yellow=moderate, green=clear)
- 📈 Findings breakdown pie chart (4 critical, 9 moderate, 2 low)
- 📊 Metrics pass/fail bar chart

---

### 2. TEST CONFIGURATION
**What it shows:** What was tested and baseline model performance

```json
{
  "config": {
    "protected_attributes": ["gender", "race"],
    "test_configuration": {
      "total_samples": 600,
      "attributes_tested": 2
    },
    "baseline_performance": {
      "accuracy": 0.9517,
      "precision": 0.8968,
      "recall": 0.9145,
      "f1": 0.9055,
      "true_positives": 432,
      "true_negatives": 139,
      "false_positives": 13,
      "false_negatives": 16,
      "tpr": 0.9643,                    // True Positive Rate
      "tnr": 0.9145,                    // True Negative Rate
      "fpr": 0.0855,                    // False Positive Rate
      "fnr": 0.0357,                    // False Negative Rate
      "ppv": 0.9708                     // Positive Predictive Value
    }
  }
}
```

**Frontend Display Ideas:**
- 📋 Configuration summary card
- 📊 Confusion matrix visualization (TP, TN, FP, FN)
- 📈 Performance metrics dashboard (accuracy, precision, recall, F1)
- 🎯 ROC curve metrics display

---

### 3. RESULTS & STATISTICS
**What it shows:** Detailed fairness metrics for each protected attribute

#### 3.1 Overall Results
```json
{
  "results": {
    "overall": {
      "severity": "MODERATE",
      "flip_rate": 0.0,                 // Counterfactual flip rate (0-1)
      "total_findings": 15
    }
  }
}
```

#### 3.2 Fairness Metrics by Attribute
Each protected attribute has multiple fairness metrics tested:

```json
{
  "fairness_metrics": {
    "gender": [
      {
        "metric_name": "Demographic Parity Difference",
        "value": 0.2660,
        "threshold": 0.1,
        "passed": false,
        "p_value": 2.07e-13,
        "privileged_group": "gender=Female",
        "unprivileged_group": "gender=Male"
      },
      {
        "metric_name": "Disparate Impact Ratio",
        "value": 3.5683,
        "threshold": 0.8,
        "passed": true,
        "p_value": null,
        "privileged_group": "gender=Female",
        "unprivileged_group": "gender=Male"
      }
      // ... more metrics
    ],
    "race": [
      // Similar structure for race comparisons
    ]
  }
}
```

**Available Fairness Metrics:**
1. **Demographic Parity Difference** - Difference in approval rates between groups
2. **Disparate Impact Ratio** - Ratio of approval rates (EEOC 80% rule)
3. **Equalized Odds Difference** - Difference in error rates (FPR, FNR)
4. **Predictive Parity** - Difference in precision between groups
5. **Calibration Difference** - Difference in prediction calibration

**Frontend Display Ideas:**
- 📊 Metric comparison table with pass/fail indicators
- 🎯 Radar chart showing all metrics for each attribute
- 📈 Bar charts comparing privileged vs unprivileged groups
- 🚦 Traffic light indicators for each metric (green=pass, red=fail)
- 📉 P-value significance indicators

#### 3.3 Counterfactual Testing
```json
{
  "counterfactual": {
    "flip_rate": 0.0,                   // Overall flip rate
    "total_flips": 0,
    "total_comparisons": 2400,
    "flips_by_attribute": {
      "gender": 0,
      "race": 0
    },
    "flip_rates_by_attribute": {
      "gender": 0.0,
      "race": 0.0
    }
  }
}
```

**What it means:** How often predictions change when only protected attributes are modified (individual fairness test)

**Frontend Display Ideas:**
- 🔄 Flip rate gauge (0-100%)
- 📊 Attribute-specific flip rate comparison
- ⚠️ Alert if flip rate > 5% (high risk)

#### 3.4 Per-Group Performance Metrics
```json
{
  "per_group_metrics": {
    "gender": {
      "Female": {
        "accuracy": 0.9641,
        "precision": 0.8462,
        "recall": 0.8148,
        "f1": 0.8302,
        "sample_count": 251,
        "tpr": 0.9821,
        "fpr": 0.1852
      },
      "Male": {
        "accuracy": 0.9427,
        "precision": 0.9070,
        "recall": 0.9360,
        "f1": 0.9213,
        "sample_count": 349,
        "tpr": 0.9464,
        "fpr": 0.0640
      }
    },
    "race": {
      "Asian": { /* ... */ },
      "White": { /* ... */ },
      "Hispanic": { /* ... */ },
      "Black": { /* ... */ }
    }
  }
}
```

**Frontend Display Ideas:**
- 📊 Side-by-side group comparison charts
- 📈 Performance gap visualization
- 🎯 Sample size indicators (important for statistical validity)
- 📉 Error rate comparison (FPR, FNR)

---

### 4. FINDINGS & ISSUES
**What it shows:** Specific bias issues detected, categorized by severity

```json
{
  "findings": {
    "findings_by_severity": {
      "CRITICAL": [
        {
          "id": "F001",
          "category": "group_fairness",
          "title": "Demographic Parity Difference violation",
          "description": "Difference in approval rates: 0.2660 (threshold: ±0.1)",
          "affected_groups": ["gender=Female", "gender=Male"],
          "evidence": {
            "metric_value": 0.2660,
            "threshold": 0.1,
            "p_value": 2.07e-13
          }
        }
        // ... more critical findings
      ],
      "MODERATE": [ /* ... */ ],
      "LOW": [ /* ... */ ]
    },
    "intersectional_findings": [
      {
        "attributes": ["gender", "race"],
        "values": {
          "gender": "Female",
          "race": "Asian"
        },
        "metric": "approval_rate",
        "value": 0.0,                   // 0% approval rate
        "baseline": 0.1089,             // Expected 10.89%
        "superadditive": true,          // Compounded bias
        "severity": "MODERATE",
        "sample_count": 39
      }
      // ... more intersectional findings
    ],
    "total_findings": 15
  }
}
```

**Finding Categories:**
- `group_fairness` - Violations between demographic groups
- `counterfactual` - Individual fairness violations
- `intersectional` - Compounded bias across multiple attributes

**Frontend Display Ideas:**
- 🚨 Findings list with severity badges
- 📊 Findings by category breakdown
- 🔍 Expandable finding cards with evidence details
- 📈 Intersectional bias heatmap (gender × race)
- ⚠️ Priority queue (critical findings first)
- 📉 Metric value vs threshold visualization

---

### 5. MITIGATION & REMEDIATION
**What it shows:** Recommended strategies to fix bias issues

```json
{
  "mitigation": {
    "total_options": 2,
    "by_category": {
      "post_processing": [
        {
          "name": "Threshold Adjustment",
          "description": "Adjust decision thresholds per demographic group to equalize error rates",
          "expected_impact": "Can achieve equalized odds with minimal accuracy loss (typically <2%)",
          "complexity": "low",
          "requires_retraining": false,
          "parameters": {
            "method": "equalized_odds_postprocessing"
          }
        }
      ],
      "pre_processing": [
        {
          "name": "Sample Reweighting",
          "description": "Assign fairness-aware weights to training samples to reduce bias",
          "expected_impact": "Moderate improvement in fairness metrics, may reduce accuracy by 1-3%",
          "complexity": "medium",
          "requires_retraining": true,
          "parameters": {
            "method": "reweighting"
          }
        }
      ],
      "in_processing": []
    },
    "recommended_order": ["post_processing", "pre_processing", "in_processing"]
  }
}
```

**Mitigation Categories:**
- `post_processing` - Fix after model training (no retraining needed)
- `pre_processing` - Fix training data (requires retraining)
- `in_processing` - Fix during training (requires retraining)

**Frontend Display Ideas:**
- 📋 Mitigation strategy cards with complexity badges
- 🔄 Retraining required indicator
- 📊 Expected impact visualization
- 🎯 Recommended order timeline
- 💡 Implementation hints/code examples

---

### 6. LEGAL COMPLIANCE (EEOC)
**What it shows:** Legal compliance status with EEOC 80% rule

```json
{
  "compliance": {
    "overall_status": "NON-COMPLIANT",
    "eeoc_80_percent_rule": {
      "description": "EEOC Uniform Guidelines on Employee Selection Procedures (1978)",
      "threshold": 0.8,
      "reference": "https://www.eeoc.gov/laws/guidance/..."
    },
    "violations": [
      {
        "metric": "Disparate Impact Ratio",
        "value": 0.7955,
        "threshold": 0.8,
        "groups": "race=Black vs race=Asian",
        "message": "Disparate Impact Ratio 79.55% below EEOC 80% threshold"
      }
    ],
    "warnings": [],
    "compliant": false
  }
}
```

**Frontend Display Ideas:**
- ⚖️ Compliance status banner (compliant/non-compliant)
- 🚨 Legal violations alert list
- 📚 Reference links to EEOC guidelines
- 📊 Disparate impact ratio gauge (with 80% threshold line)

---

### 7. STATISTICAL VALIDITY
**What it shows:** Statistical confidence and reliability of results

```json
{
  "validity": {
    "confidence_intervals": {
      "Demographic Parity Difference": {
        "point_estimate": 0.2581,
        "lower_bound": 0.1601,
        "upper_bound": 0.3561,
        "confidence_level": 0.95
      }
    },
    "sample_size": 600,
    "statistical_power": "adequate",
    "notes": [
      "Confidence intervals provide range of plausible values for metrics",
      "Larger sample sizes provide more precise estimates",
      "P-values indicate statistical significance of observed differences"
    ]
  }
}
```

**Frontend Display Ideas:**
- 📊 Confidence interval error bars on charts
- 📈 Sample size adequacy indicator
- ℹ️ Statistical notes tooltip/info panel

---

## 🎨 Recommended Frontend Views

### Dashboard Overview
```
┌─────────────────────────────────────────────────────┐
│  Model: biased_model                    [MODERATE]  │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  Health Score: 30%  ████░░░░░░░░░░░░░░░░░░░░░░░░   │
│                                                      │
│  Findings:  🔴 4 Critical  🟡 9 Moderate  🟢 2 Low  │
│                                                      │
│  Flip Rate: 0.00%  ✓                                │
│                                                      │
│  Compliance: ⚖️ NON-COMPLIANT                       │
└─────────────────────────────────────────────────────┘
```

### Fairness Metrics View
```
┌─────────────────────────────────────────────────────┐
│  Protected Attribute: Gender                        │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  Female vs Male                                     │
│                                                      │
│  ❌ Demographic Parity:     0.266  (threshold: 0.1) │
│  ✅ Disparate Impact:       3.568  (threshold: 0.8) │
│  ❌ Equalized Odds:         0.121  (threshold: 0.1) │
│  ❌ Predictive Parity:      0.061  (threshold: 0.05)│
│  ❌ Calibration:            0.350  (threshold: 0.05)│
│                                                      │
│  Pass Rate: 1/5 (20%)                               │
└─────────────────────────────────────────────────────┘
```

### Intersectional Bias Heatmap
```
              Asian    Black    Hispanic   White
Female        🔴 0%    🔴 0%    🟡 6%      🟡 17%
Male          🟡 18%   🟡 15%   ✓ 82%      ✓ 62%

🔴 Critical (<5%)  🟡 Moderate (5-15%)  ✓ Clear (>15%)
```

### Findings List
```
┌─────────────────────────────────────────────────────┐
│  🔴 CRITICAL FINDINGS (4)                           │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  [F001] Demographic Parity Difference violation     │
│         Affected: Female vs Male                    │
│         Value: 0.266 (threshold: 0.1)               │
│         P-value: 2.07e-13 ***                       │
│                                                      │
│  [F008] Equalized Odds Difference violation         │
│         Affected: Asian vs Hispanic                 │
│         Value: 0.179 (threshold: 0.1)               │
│                                                      │
│  ... 2 more                                         │
└─────────────────────────────────────────────────────┘
```

### Mitigation Recommendations
```
┌─────────────────────────────────────────────────────┐
│  💡 RECOMMENDED ACTIONS                             │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│                                                      │
│  1. Threshold Adjustment                            │
│     Category: Post-processing                       │
│     Complexity: 🟢 Low                              │
│     Retraining: ❌ Not required                     │
│     Impact: <2% accuracy loss                       │
│                                                      │
│  2. Sample Reweighting                              │
│     Category: Pre-processing                        │
│     Complexity: 🟡 Medium                           │
│     Retraining: ✅ Required                         │
│     Impact: 1-3% accuracy loss                      │
└─────────────────────────────────────────────────────┘
```

---

## 📦 Data Access Patterns

### Quick Summary (Basic JSON)
Use `model_audit_basic.json` for:
- Dashboard overview
- Quick health check
- Simple metric displays

### Detailed Analysis (Comprehensive JSON)
Use `model_audit_comprehensive.json` for:
- Full fairness metric details
- Per-group performance breakdowns
- Intersectional analysis
- Mitigation recommendations
- Legal compliance details

### Human-Readable (Text Report)
Use `model_audit_detailed.txt` for:
- PDF export
- Email reports
- Documentation

---

## 🎯 Key Metrics to Highlight

### Most Important for Users:
1. **Overall Severity** - CRITICAL/MODERATE/LOW/CLEAR
2. **Pass Rate** - % of fairness metrics passed
3. **Critical Findings Count** - Number of serious issues
4. **Compliance Status** - Legal compliance (EEOC)
5. **Flip Rate** - Individual fairness measure

### Most Important for Technical Users:
1. **Demographic Parity Difference** - Group fairness
2. **Equalized Odds** - Error rate fairness
3. **Disparate Impact Ratio** - EEOC 80% rule
4. **Intersectional Findings** - Compounded bias
5. **P-values** - Statistical significance

---

## 🚀 Implementation Tips

1. **Color Coding:**
   - 🔴 Red: CRITICAL, Failed, Non-compliant
   - 🟡 Yellow: MODERATE, Warning
   - 🟢 Green: CLEAR, Passed, Compliant

2. **Progressive Disclosure:**
   - Show summary first
   - Allow drill-down into details
   - Provide tooltips for technical terms

3. **Responsive Design:**
   - Mobile: Show summary cards
   - Desktop: Show detailed tables and charts

4. **Export Options:**
   - PDF report generation
   - CSV data export
   - JSON API access

5. **Interactivity:**
   - Filter by severity
   - Filter by protected attribute
   - Sort findings by impact
   - Compare groups side-by-side

---

## 📚 Glossary for Frontend

- **Demographic Parity**: Equal approval rates across groups
- **Disparate Impact**: Ratio of approval rates (EEOC 80% rule)
- **Equalized Odds**: Equal error rates (FPR, FNR) across groups
- **Predictive Parity**: Equal precision across groups
- **Calibration**: Prediction confidence matches actual outcomes
- **Flip Rate**: % of predictions that change when protected attributes change
- **Intersectional Bias**: Compounded bias across multiple attributes
- **P-value**: Statistical significance (< 0.05 = significant)

---

## 🔗 Related Files

- API Code: `Nobias/library/model_audit/api.py`
- Report Models: `Nobias/library/model_audit/models.py`
- Example Reports: `Nobias/output/model_audit_*.json`
