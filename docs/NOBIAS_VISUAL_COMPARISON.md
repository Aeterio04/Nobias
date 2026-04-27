# NoBias Platform - Visual Comparison Guide

> **Side-by-side comparison of all three audit systems**

---

## System Comparison at a Glance

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         NOBIAS PLATFORM                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ DATASET AUDIT    │  │  MODEL AUDIT     │  │  AGENT AUDIT     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ Input:           │  │ Input:           │  │ Input:           │     │
│  │ • CSV/Excel      │  │ • Trained model  │  │ • LLM prompt     │     │
│  │ • Parquet        │  │ • Test data      │  │ • API endpoint   │     │
│  │ • DataFrame      │  │ • Protected      │  │ • Logs           │     │
│  │                  │  │   attributes     │  │                  │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ Detects:         │  │ Detects:         │  │ Detects:         │     │
│  │ • Representation │  │ • Group fairness │  │ • Explicit bias  │     │
│  │ • Label bias     │  │ • Individual     │  │ • Implicit bias  │     │
│  │ • Proxy features │  │   fairness       │  │ • Contextual     │     │
│  │ • Missing data   │  │ • Intersectional │  │ • Reasoning      │     │
│  │ • Intersectional │  │ • Calibration    │  │                  │     │
│  │ • Distribution   │  │                  │  │                  │     │
│  │ • Correlation    │  │                  │  │                  │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ Speed: 2-10 sec  │  │ Speed: 15-60 sec │  │ Speed: 2-30 min  │     │
│  │ Cost: $0         │  │ Cost: $0         │  │ Cost: $0.03-$0.27│     │
│  │ Privacy: 100%    │  │ Privacy: 100%    │  │ Privacy: Optional│     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Metrics Comparison

### Dataset Audit Metrics

```
┌─────────────────────────────────────────────────────────────┐
│ REPRESENTATION BIAS                                          │
│ ├─ Group Size: Absolute count per group                    │
│ ├─ Representation Ratio: group_size / total_size           │
│ └─ Balance Score: smallest / largest                       │
│                                                              │
│ LABEL BIAS                                                   │
│ ├─ Selection Rate: P(Y=1 | A=a)                            │
│ ├─ Selection Rate Difference (SRD): |P(Y=1|A=a) - P(Y=1|A=b)| │
│ └─ Disparate Impact Ratio (DIR): min_rate / max_rate      │
│                                                              │
│ PROXY FEATURES                                               │
│ ├─ Pearson Correlation: Linear relationship                │
│ ├─ Mutual Information: Non-linear relationship             │
│ └─ Predictive Power: Can feature predict attribute?        │
│                                                              │
│ MISSING DATA BIAS                                            │
│ ├─ Missingness Rate: P(missing | A=a)                      │
│ └─ Missingness Difference: |P(missing|A=a) - P(missing|A=b)| │
│                                                              │
│ INTERSECTIONAL BIAS                                          │
│ ├─ Expected Size: P(A=a) × P(B=b) × total                 │
│ └─ Actual vs Expected: Deviation ratio                     │
│                                                              │
│ DISTRIBUTION SHIFT                                           │
│ └─ KL Divergence: Σ P(x) log(P(x)/Q(x))                   │
└─────────────────────────────────────────────────────────────┘
```

### Model Audit Metrics

```
┌─────────────────────────────────────────────────────────────┐
│ GROUP FAIRNESS                                               │
│ ├─ Demographic Parity Difference (DPD)                      │
│ │  └─ |P(Ŷ=1|A=a) - P(Ŷ=1|A=b)|                           │
│ ├─ Equalized Odds                                           │
│ │  ├─ TPR Difference: |P(Ŷ=1|Y=1,A=a) - P(Ŷ=1|Y=1,A=b)|   │
│ │  └─ FPR Difference: |P(Ŷ=1|Y=0,A=a) - P(Ŷ=1|Y=0,A=b)|   │
│ ├─ Disparate Impact Ratio (DIR)                             │
│ │  └─ P(Ŷ=1|A=unprivileged) / P(Ŷ=1|A=privileged)         │
│ ├─ Predictive Parity                                        │
│ │  └─ |P(Y=1|Ŷ=1,A=a) - P(Y=1|Ŷ=1,A=b)|                   │
│ └─ Calibration                                              │
│    └─ Max calibration error across groups                  │
│                                                              │
│ INDIVIDUAL FAIRNESS                                          │
│ ├─ Counterfactual Flip Rate                                │
│ │  └─ (# flips) / (total samples)                          │
│ └─ Mean Absolute Score Difference (MASD)                    │
│    └─ (1/N) × Σ|score_original - score_counterfactual|     │
│                                                              │
│ INTERSECTIONAL                                               │
│ └─ Superadditive Bias Detection                             │
└─────────────────────────────────────────────────────────────┘
```

### Agent Audit Metrics

```
┌─────────────────────────────────────────────────────────────┐
│ PRIMARY METRICS                                              │
│ ├─ Counterfactual Flip Rate (CFR)                          │
│ │  └─ (# pairs where decision_A ≠ decision_B) / total      │
│ ├─ Mean Absolute Score Difference (MASD)                    │
│ │  └─ (1/N) × Σ|score_original - score_counterfactual|     │
│ ├─ EEOC Adverse Impact Ratio (AIR)                         │
│ │  └─ (lowest group rate) / (highest group rate)           │
│ └─ Stochastic Stability Score (SSS)                         │
│    └─ 1 - (average within-persona variance)                │
│                                                              │
│ SECONDARY METRICS                                            │
│ ├─ Bias-Adjusted CFR (BA-CFR)                              │
│ │  └─ CFR - (mean within-persona flip rate)                │
│ ├─ Demographic Parity                                       │
│ │  └─ max(approval_rates) - min(approval_rates)            │
│ └─ Intersectional Disparity                                 │
│    └─ Compounded bias at intersections                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Severity Thresholds Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         SEVERITY LEVELS                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  CRITICAL (Immediate Action Required)                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Dataset Audit    │  │  Model Audit     │  │  Agent Audit     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ • DIR < 0.60     │  │ • DIR < 0.60     │  │ • CFR > 15%      │     │
│  │ • Rep < 5%       │  │ • DPD > 0.20     │  │ • AIR < 0.60     │     │
│  │ • SRD > 0.20     │  │ • Flip > 15%     │  │ • MASD > 0.15    │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
│  MODERATE (Remediation Recommended)                                     │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Dataset Audit    │  │  Model Audit     │  │  Agent Audit     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ • DIR 0.60-0.80  │  │ • DIR 0.60-0.80  │  │ • CFR 10-15%     │     │
│  │ • Rep 5-10%      │  │ • DPD 0.10-0.20  │  │ • AIR 0.60-0.80  │     │
│  │ • SRD 0.10-0.20  │  │ • Flip 5-15%     │  │ • MASD 0.08-0.15 │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
│  LOW (Monitor)                                                          │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Dataset Audit    │  │  Model Audit     │  │  Agent Audit     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ • DIR 0.80-0.90  │  │ • DIR 0.80-0.90  │  │ • CFR 5-10%      │     │
│  │ • Rep 10-20%     │  │ • DPD 0.05-0.10  │  │ • AIR 0.80-0.85  │     │
│  │ • SRD 0.05-0.10  │  │ • Flip 2-5%      │  │ • MASD 0.03-0.08 │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
│  CLEAR (No Action Needed)                                               │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Dataset Audit    │  │  Model Audit     │  │  Agent Audit     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ • DIR > 0.90     │  │ • DIR > 0.90     │  │ • CFR < 5%       │     │
│  │ • Rep > 20%      │  │ • DPD < 0.05     │  │ • AIR > 0.85     │     │
│  │ • SRD < 0.05     │  │ • Flip < 2%      │  │ • MASD < 0.03    │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Remediation Strategies Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      REMEDIATION STRATEGIES                              │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Dataset Audit                                                          │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │ 1. Stratified Resampling                                      │      │
│  │    • Oversample underrepresented groups                       │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: YES                                 │      │
│  │                                                                │      │
│  │ 2. Sample Reweighting                                         │      │
│  │    • Assign weights to balance groups                         │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: YES                                 │      │
│  │                                                                │      │
│  │ 3. Remove Proxy Features                                      │      │
│  │    • Drop features that leak protected attributes             │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: YES                                 │      │
│  │                                                                │      │
│  │ 4. Fair Imputation                                            │      │
│  │    • Fill missing data systematically                         │      │
│  │    • Complexity: MEDIUM                                       │      │
│  │    • Requires Retraining: YES                                 │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│  Model Audit                                                            │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │ 1. Threshold Adjustment (POST-PROCESSING)                     │      │
│  │    • Adjust decision thresholds per group                     │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: NO ✅                               │      │
│  │                                                                │      │
│  │ 2. Sample Reweighting (PRE-PROCESSING)                        │      │
│  │    • Assign fairness-aware weights                            │      │
│  │    • Complexity: MEDIUM                                       │      │
│  │    • Requires Retraining: YES                                 │      │
│  │                                                                │      │
│  │ 3. Remove Proxy Features (PRE-PROCESSING)                     │      │
│  │    • Drop correlated features                                 │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: YES                                 │      │
│  │                                                                │      │
│  │ 4. Fairness Constraints (IN-PROCESSING)                       │      │
│  │    • Add constraints during training                          │      │
│  │    • Complexity: HIGH                                         │      │
│  │    • Requires Retraining: YES                                 │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
│  Agent Audit                                                            │
│  ┌──────────────────────────────────────────────────────────────┐      │
│  │ 1. Prompt Modification                                        │      │
│  │    • Add fairness instructions                                │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: NO ✅                               │      │
│  │                                                                │      │
│  │ 2. Remove Demographic Context                                 │      │
│  │    • Strip protected attribute information                    │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: NO ✅                               │      │
│  │                                                                │      │
│  │ 3. Structured Output Format                                   │      │
│  │    • Force JSON output                                        │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: NO ✅                               │      │
│  │                                                                │      │
│  │ 4. Temperature Adjustment                                     │      │
│  │    • Reduce randomness                                        │      │
│  │    • Complexity: LOW                                          │      │
│  │    • Requires Retraining: NO ✅                               │      │
│  └──────────────────────────────────────────────────────────────┘      │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Performance Comparison

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      PERFORMANCE METRICS                                 │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  Speed                                                                  │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Dataset Audit    │  │  Model Audit     │  │  Agent Audit     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ Small: 1-2 sec   │  │ Small: 5-10 sec  │  │ Quick: 2 min     │     │
│  │ Medium: 2-5 sec  │  │ Medium: 15-30 sec│  │ Standard: 5 min  │     │
│  │ Large: 10-20 sec │  │ Large: 60-120 sec│  │ Full: 30 min     │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
│  Cost                                                                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Dataset Audit    │  │  Model Audit     │  │  Agent Audit     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ $0               │  │ $0               │  │ Quick: $0.03-0.11│     │
│  │ (100% local)     │  │ (100% local)     │  │ Std: $0.05-0.17  │     │
│  │                  │  │                  │  │ Full: $0.07-0.27 │     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
│  Resource Usage                                                         │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │
│  │ Dataset Audit    │  │  Model Audit     │  │  Agent Audit     │     │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤     │
│  │ CPU: 1-2 cores   │  │ CPU: 1-4 cores   │  │ CPU: 1-2 cores   │     │
│  │ RAM: < 200 MB    │  │ RAM: < 500 MB    │  │ RAM: < 300 MB    │     │
│  │ Network: None    │  │ Network: None    │  │ Network: Required│     │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘     │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Use Case Decision Tree

```
START: Do you have an AI system to audit?
  │
  ├─ NO → Wait until you have data/model/agent
  │
  └─ YES → What stage are you at?
      │
      ├─ Data Collection Complete
      │   └─ Use: DATASET AUDIT
      │       • Prevents biased models
      │       • Cheapest to fix (no retraining yet)
      │       • 2-10 seconds, $0
      │
      ├─ Model Training Complete
      │   └─ Use: MODEL AUDIT
      │       • Validates fairness before deployment
      │       • Can fix without retraining (threshold adjustment)
      │       • 15-60 seconds, $0
      │
      ├─ LLM Agent Deployed/Planning
      │   └─ Use: AGENT AUDIT
      │       • Tests LLM decision-making
      │       • No retraining needed (prompt fixes)
      │       • 2-30 minutes, $0.03-$0.27
      │
      └─ Production System
          └─ Use: ALL THREE
              • Comprehensive monitoring
              • Continuous compliance
              • Scheduled audits
```

---

## Compliance Coverage

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      REGULATORY COMPLIANCE                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  EEOC 80% Rule (US)                                                     │
│  ┌──────────────────┬──────────────────┬──────────────────┐            │
│  │ Dataset Audit    │  Model Audit     │  Agent Audit     │            │
│  ├──────────────────┼──────────────────┼──────────────────┤            │
│  │ ✅ DIR metric    │ ✅ DIR metric    │ ✅ AIR metric    │            │
│  │ Checks: < 0.80   │ Checks: < 0.80   │ Checks: < 0.80   │            │
│  └──────────────────┴──────────────────┴──────────────────┘            │
│                                                                          │
│  EU AI Act (Articles 9, 12)                                             │
│  ┌──────────────────┬──────────────────┬──────────────────┐            │
│  │ Dataset Audit    │  Model Audit     │  Agent Audit     │            │
│  ├──────────────────┼──────────────────┼──────────────────┤            │
│  │ ✅ Audit hashes  │ ✅ Audit hashes  │ ✅ Audit hashes  │            │
│  │ ✅ Reproducible  │ ✅ Reproducible  │ ✅ Reproducible  │            │
│  │ ✅ Risk assess   │ ✅ Risk assess   │ ✅ Risk assess   │            │
│  └──────────────────┴──────────────────┴──────────────────┘            │
│                                                                          │
│  NIST AI RMF                                                            │
│  ┌──────────────────┬──────────────────┬──────────────────┐            │
│  │ Dataset Audit    │  Model Audit     │  Agent Audit     │            │
│  ├──────────────────┼──────────────────┼──────────────────┤            │
│  │ ✅ Risk metrics  │ ✅ Risk metrics  │ ✅ Risk metrics  │            │
│  │ ✅ Documentation │ ✅ Documentation │ ✅ Documentation │            │
│  │ ✅ Monitoring    │ ✅ Monitoring    │ ✅ Monitoring    │            │
│  └──────────────────┴──────────────────┴──────────────────┘            │
│                                                                          │
│  ISO/IEC 42001                                                          │
│  ┌──────────────────┬──────────────────┬──────────────────┐            │
│  │ Dataset Audit    │  Model Audit     │  Agent Audit     │            │
│  ├──────────────────┼──────────────────┼──────────────────┤            │
│  │ ✅ Audit trails  │ ✅ Audit trails  │ ✅ Audit trails  │            │
│  │ ✅ Versioning    │ ✅ Versioning    │ ✅ Versioning    │            │
│  │ ✅ Integrity     │ ✅ Integrity     │ ✅ Integrity     │            │
│  └──────────────────┴──────────────────┴──────────────────┘            │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

**Version**: 2.0 | **Updated**: 2026-04-28 | **For**: Presentations & Quick Reference
