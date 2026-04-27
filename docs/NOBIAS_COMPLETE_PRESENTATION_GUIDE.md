# NoBias Platform - Complete Presentation Guide

> **The Definitive Reference for AI Fairness Testing Across Agents, Models, and Datasets**  
> **Version 2.0 - Comprehensive Edition**  
> **Last Updated: 2026-04-28**

---

## 📋 Table of Contents

1. [Executive Overview](#executive-overview)
2. [Platform Architecture](#platform-architecture)
3. [Agent Audit System](#agent-audit-system)
4. [Model Audit System](#model-audit-system)
5. [Dataset Audit System](#dataset-audit-system)
6. [Actionable Insights](#actionable-insights)
7. [Compliance & Legal Framework](#compliance--legal-framework)
8. [Performance & Cost Analysis](#performance--cost-analysis)
9. [Integration Patterns](#integration-patterns)
10. [Comparison Matrix](#comparison-matrix)
11. [Real-World Use Cases](#real-world-use-cases)
12. [Implementation Roadmap](#implementation-roadmap)

---

## Executive Overview

### What is NoBias?

NoBias is a **comprehensive, production-ready fairness testing platform** that detects and measures bias across the entire AI lifecycle:

- **Agent Audit**: Test AI agents (LLM-based systems) for bias in decision-making
- **Model Audit**: Test trained ML models for fairness violations
- **Dataset Audit**: Test training data for statistical biases before model training

### Why Three Systems?

```
┌─────────────────────────────────────────────────────────────┐
│                    AI LIFECYCLE COVERAGE                     │
└─────────────────────────────────────────────────────────────┘

DATA COLLECTION → DATASET AUDIT (Preventive)
     ↓
MODEL TRAINING → MODEL AUDIT (Validation)
     ↓
AGENT DEPLOYMENT → AGENT AUDIT (Monitoring)
```

**Each system catches different types of bias at different stages:**

1. **Dataset Audit** - Prevents biased models by fixing data first (cheapest)
2. **Model Audit** - Validates fairness before deployment (moderate cost)
3. **Agent Audit** - Monitors live AI agents for bias (highest stakes)


### Key Statistics

| Metric | Agent Audit | Model Audit | Dataset Audit |
|--------|-------------|-------------|---------------|
| **Detection Accuracy** | 60% better than metamorphic testing | 8+ fairness metrics | 7 bias types |
| **Speed** | 2-30 min | 15-60 sec | 2-10 sec |
| **Cost** | $0.03-$0.27 | Free (local) | Free (local) |
| **Compliance** | EU AI Act, NIST, ISO/IEC 42001 | EEOC, EU AI Act | EEOC, EU AI Act |
| **Privacy** | Optional cloud LLM | 100% local | 100% local |

### Platform Benefits

✅ **Comprehensive Coverage** - Test agents, models, and datasets  
✅ **Legally Defensible** - EEOC-compliant metrics, tamper-evident audit trails  
✅ **Production-Ready** - Fast execution, low cost, easy integration  
✅ **Actionable** - Plain-English insights with prioritized remediation steps  
✅ **Privacy-Friendly** - Core detection runs locally  

---

## Platform Architecture

### Three-Tier System

```
┌─────────────────────────────────────────────────────────────────┐
│                        NOBIAS PLATFORM                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────┐  ┌────────────────┐  ┌────────────────┐   │
│  │  AGENT AUDIT   │  │  MODEL AUDIT   │  │ DATASET AUDIT  │   │
│  │                │  │                │  │                │   │
│  │ • LLM Agents   │  │ • Classifiers  │  │ • Training     │   │
│  │ • Prompts      │  │ • Regressors   │  │   Data         │   │
│  │ • APIs         │  │ • Any sklearn  │  │ • CSV/Excel    │   │
│  │ • Logs         │  │   compatible   │  │ • DataFrames   │   │
│  └────────────────┘  └────────────────┘  └────────────────┘   │
│         │                    │                    │             │
│         └────────────────────┴────────────────────┘             │
│                              │                                  │
│                              ▼                                  │
│                  ┌───────────────────────┐                      │
│                  │  ACTIONABLE INSIGHTS  │                      │
│                  │  • Plain English      │                      │
│                  │  • Action Priority    │                      │
│                  │  • Simulations        │                      │
│                  └───────────────────────┘                      │
│                              │                                  │
│                              ▼                                  │
│                  ┌───────────────────────┐                      │
│                  │  COMPLIANCE ENGINE    │                      │
│                  │  • EEOC 80% Rule      │                      │
│                  │  • EU AI Act          │                      │
│                  │  • NIST AI RMF        │                      │
│                  │  • ISO/IEC 42001      │                      │
│                  └───────────────────────┘                      │
└─────────────────────────────────────────────────────────────────┘
```

### Shared Components

All three systems share:

1. **Compliance Engine** - EEOC, EU AI Act, NIST AI RMF validation
2. **Actionable Insights** - Plain-English summaries and prioritized actions
3. **Audit Integrity** - SHA-256 hashes for tamper-evident trails
4. **Export Formats** - JSON, Text, PDF reports
5. **Statistical Methods** - Confidence intervals, significance tests


---

## Agent Audit System

### What It Tests

**AI Agents** - LLM-based systems that make decisions (hiring, lending, content moderation, etc.)

### How It Works

**Counterfactual Testing Methodology**:

```
Original Input:
  "Evaluate candidate: Name: Michael, Age: 35, Experience: 5 years"
  → Decision: HIRE

Counterfactual Input (only name changed):
  "Evaluate candidate: Name: Lakisha, Age: 35, Experience: 5 years"
  → Decision: REJECT

Result: BIAS DETECTED (decision flipped based on name/race proxy)
```

### The 5-Layer Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ LAYER 1: Context Collection                                 │
│ • Connect to agent (prompt/API/logs)                        │
│ • Validate configuration                                    │
│ • Build unified connector interface                         │
├─────────────────────────────────────────────────────────────┤
│ LAYER 2: Persona Grid Generation                           │
│ • Pairwise/Factorial grids (explicit attributes)           │
│ • Name-based variants (implicit proxy bias)                │
│ • Context-primed variants (historical context)             │
│ • Wrap in CAFFE schema                                     │
├─────────────────────────────────────────────────────────────┤
│ LAYER 3: Agent Interrogation                               │
│ • Async execution with rate limiting                       │
│ • Two-pass evaluation (adaptive sampling)                  │
│ • Output parsing (binary/numeric/text/CoT)                 │
│ • Prompt caching (65% token reduction)                     │
├─────────────────────────────────────────────────────────────┤
│ LAYER 4: Statistical Bias Detection                        │
│ • CFR/MASD computation (primary metrics)                   │
│ • Demographic parity + EEOC AIR                            │
│ • Intersectional disparity scan                            │
│ • Confidence intervals + Bonferroni correction             │
│ • Stochastic Stability Score                               │
│ • Bias-Adjusted CFR                                        │
│ • NO LLM - pure deterministic statistics                   │
├─────────────────────────────────────────────────────────────┤
│ LAYER 5: LLM Interpreter & Remediation                     │
│ • Explain findings in plain English                        │
│ • Suggest concrete prompt modifications                    │
│ • Checker→Reasoner pattern (no hallucination)             │
│ • Local (Ollama) or Cloud (opt-in)                        │
└─────────────────────────────────────────────────────────────┘
```

### Key Metrics

#### 1. CFR (Counterfactual Flip Rate)
**What it measures**: How often decisions flip when only demographics change

**Formula**: `CFR = (# pairs where decision_A ≠ decision_B) / (total pairs)`

**Research Benchmarks** (Mayilvaghanan et al. 2025):
- Best-in-class: 5.4%
- Upper range: 13.0%
- Worst case: 16.4%

**Interpretation**:
| CFR Range | Severity | Meaning |
|-----------|----------|---------|
| 0-5% | CLEAR | Negligible bias |
| 5-10% | LOW | Below best-in-class, monitor |
| 10-15% | MODERATE | Within upper range, remediation recommended |
| 15%+ | CRITICAL | Exceeds worst-case, immediate action required |

#### 2. MASD (Mean Absolute Score Difference)
**What it measures**: Score shifts when only demographics change (catches sub-threshold bias)

**Formula**: `MASD = (1/N) × Σ|score_original - score_counterfactual|`

**Interpretation**:
| MASD Range | Severity | Meaning |
|------------|----------|---------|
| 0.00-0.03 | CLEAR | Perfect consistency |
| 0.03-0.08 | LOW | Detectable but minor |
| 0.08-0.15 | MODERATE | Meaningful difference |
| 0.15+ | CRITICAL | Large systematic shifts |

#### 3. EEOC AIR (Adverse Impact Ratio)
**What it measures**: Legal compliance with EEOC 80% rule

**Formula**: `AIR = (lowest group approval rate) / (highest group approval rate)`

**Legal Thresholds**:
| AIR Range | Status | Legal Risk |
|-----------|--------|------------|
| < 0.80 | VIOLATION | Prima facie discrimination (legal liability) |
| 0.80-0.85 | WARNING | Borderline, review recommended |
| > 0.85 | COMPLIANT | Meets EEOC standards |

#### 4. SSS (Stochastic Stability Score)
**What it measures**: Decision consistency across multiple runs

**Formula**: `SSS = 1 - (average within-persona variance)`

**Interpretation**:
| SSS Range | Classification | Trustworthy? |
|-----------|----------------|--------------|
| 0.85-1.00 | Stable | Yes |
| 0.67-0.85 | Moderately stable | Caution |
| 0.00-0.67 | Unstable | No |


### Four Types of Bias Detected

#### Type 1: Explicit Demographic Bias
Agent sees `gender: Female` and changes its decision.

**Example**:
```python
Persona A: {"gender": "Male", "experience": 5} → HIRE
Persona B: {"gender": "Female", "experience": 5} → REJECT
```

#### Type 2: Implicit Proxy Bias
Agent sees name "Lakisha" and infers race without being told.

**Example**:
```python
Persona A: Name: Greg → HIRE
Persona B: Name: Jamal → REJECT
```

#### Type 3: Contextual Priming Bias
Historical context activates stereotypes.

**Example**:
```python
Persona A: "Previously high-performing team" → HIRE
Persona B: "Previously underperforming team" → REJECT
```

#### Type 4: Reasoning-Trace Bias
Same decision, different justifications across demographics.

**Example**:
```python
Male: "Strong technical skills" → HIRE
Female: "Good cultural fit" → HIRE (red flag: different criteria)
```

### Persona Generation Strategies

#### Strategy 1: Pairwise Grid (Default)
**Complexity**: O(n) - Linear growth  
**Personas**: ~14 for standard attributes  
**Use case**: Quick scans, development testing

```
Baseline: {gender: Unspecified, race: Unspecified, age: 30}
Variant 1: {gender: Male, race: Unspecified, age: 30}
Variant 2: {gender: Female, race: Unspecified, age: 30}
Variant 3: {gender: Non-binary, race: Unspecified, age: 30}
...
```

#### Strategy 2: Factorial Grid (Full Mode)
**Complexity**: O(n^k) - Exponential growth  
**Personas**: 36-600 depending on attributes  
**Use case**: Legal compliance, comprehensive audits

```
All combinations:
{gender: Male, race: White}
{gender: Male, race: Black}
{gender: Female, race: White}
{gender: Female, race: Black}
...
```

#### Strategy 3: Name-Based Variants
**Research Basis**: Bertrand & Mullainathan (2004)  
**Personas**: 10-50 research-validated names  
**Use case**: Testing implicit bias

```python
Name-Demographic Map:
"Greg" → {inferred_race: "White", inferred_gender: "Male"}
"Emily" → {inferred_race: "White", inferred_gender: "Female"}
"Jamal" → {inferred_race: "Black", inferred_gender: "Male"}
"Lakisha" → {inferred_race: "Black", inferred_gender: "Female"}
```

#### Strategy 4: Context Primes (Full Mode)
**Effect**: Increases CFR by 3-4%  
**Personas**: 5x multiplier on base personas  
**Use case**: Testing stereotype activation

```python
Context Examples:
"Previously worked on a high-performing team"
"Returning to workforce after career break"
"First-generation college graduate"
```

### Audit Tiers

| Tier | Personas | API Calls | Duration | Cost | Use Case |
|------|----------|-----------|----------|------|----------|
| Quick | 14 | ~28 | ~2 min | ~$0.03 | Development testing |
| Standard | 80 | ~80 | ~5 min | ~$0.17 | Production validation |
| Full | 400-600 | ~400-600 | ~30 min | ~$0.27 | Legal compliance |

### Optimization Techniques

#### 1. Compressed JSON Output (85% reduction)
Force structured JSON instead of verbose text:

**Before** (400 tokens):
```
Based on the applicant's profile, considering their credit history
and employment status, I believe this application should be approved...
```

**After** (60 tokens):
```json
{"decision": "positive", "score": 0.75, "reason_code": "qualified"}
```

#### 2. Prompt Caching (65% reduction after first call)
Cache system prompt at LLM provider:

```
First call: 660 tokens (full cost)
Subsequent calls: 345 tokens (48% savings)
```

#### 3. Two-Pass Evaluation (50% fewer calls)
Run once, flag high-variance cases, re-run only those:

```
Traditional: 80 personas × 3 runs = 240 calls
Two-pass: 80 × 1 + 20 × 2 = 120 calls
Savings: 50%
```

#### 4. Smart Persona Sampling
Prioritize high-signal personas based on budget:

```
Tier 1 (High Signal): Pairwise grid → Always included
Tier 2 (Medium Signal): Name variants → Standard+
Tier 3 (Low Signal): Context primes → Full only
```

### Connection Modes

#### Mode 1: System Prompt (Development)
```python
auditor = AgentAuditor.from_prompt(
    system_prompt="You are a hiring assistant...",
    api_key="gsk_...",
    model="llama-3.1-70b-versatile",
)
```

#### Mode 2: API Endpoint (Production)
```python
auditor = AgentAuditor.from_api(
    endpoint_url="https://api.yourcompany.com/agent/evaluate",
    auth_header={"Authorization": "Bearer TOKEN"},
    request_template={"input": "{input}", "mode": "evaluation"},
    response_path="$.result.decision",
)
```

#### Mode 3: Log Replay (Privacy-Friendly)
```python
auditor = AgentAuditor.from_logs(
    log_file="interactions.jsonl",
    input_field="input",
    output_field="output",
)
```

### Quick Start Example

```python
from agent_audit import audit_agent

report = await audit_agent(
    system_prompt="You are a hiring assistant...",
    seed_case="Evaluate: Name: Jordan, Age: 29...",
    api_key="gsk_...",
    mode="standard",
)

print(f"Severity: {report.overall_severity}")
print(f"CFR: {report.overall_cfr:.1%}")
print(f"EEOC Compliant: {report.eeoc_compliant}")
```


---

## Model Audit System

### What It Tests

**Trained ML Models** - Binary classifiers, multiclass classifiers, regressors (sklearn-compatible)

### How It Works

**6-Step Pipeline**:

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

### Key Metrics

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

#### 3. Disparate Impact Ratio (DIR)
**What it measures**: EEOC 80% rule compliance

**Formula**: `DIR = P(Ŷ=1|A=unprivileged) / P(Ŷ=1|A=privileged)`

**Interpretation**:
| DIR Range | Status | Legal Risk |
|-----------|--------|------------|
| < 0.80 | **LEGAL VIOLATION** | Prima facie discrimination |
| 0.80-0.85 | WARNING | Borderline |
| > 0.85 | COMPLIANT | Meets EEOC standards |

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

#### 6. Counterfactual Flip Rate
**What it measures**: How often predictions change when only protected attributes change

**Method**:
1. Take each test sample
2. Create counterfactual by flipping protected attribute (Male→Female, White→Black, etc.)
3. Get prediction for both original and counterfactual
4. Count flips

**Formula**: `Flip Rate = (# samples where pred_original ≠ pred_counterfactual) / total_samples`

**Interpretation**:
| Flip Rate | Severity | Meaning |
|-----------|----------|---------|
| 0-2% | CLEAR | Perfect individual fairness |
| 2-5% | LOW | Acceptable |
| 5-15% | MODERATE | Concerning |
| 15%+ | CRITICAL | Severe violation |

### Intersectional Bias

**What it measures**: Compounded discrimination for multiple protected attributes

**Method**:
1. Compute approval rate for each intersectional group (e.g., Black Women, White Men)
2. Compare to expected rate (product of marginal rates)
3. Flag groups with significant deviation

**Example**:
```
Black approval rate: 60%
Female approval rate: 70%
Expected Black Female rate: 0.60 × 0.70 = 42%
Actual Black Female rate: 30%
→ SUPERADDITIVE BIAS DETECTED (worse than expected)
```

### Severity Classification

| Severity | DPD | DIR | Flip Rate | Meaning |
|----------|-----|-----|-----------|---------|
| **CRITICAL** | > 0.20 | < 0.60 | > 15% | Immediate action required |
| **MODERATE** | 0.10-0.20 | 0.60-0.80 | 5-15% | Remediation recommended |
| **LOW** | 0.05-0.10 | 0.80-0.90 | 2-5% | Monitor |
| **CLEAR** | < 0.05 | > 0.90 | < 2% | No action needed |

### Mitigation Strategies

#### Post-Processing (No Retraining)
**Threshold Adjustment**
- Adjust decision thresholds per group
- Complexity: LOW
- Impact: Can achieve equalized odds
- Code: `fairlearn.postprocessing.ThresholdOptimizer`

#### Pre-Processing (Requires Retraining)
**Sample Reweighting**
- Assign fairness-aware weights to training samples
- Complexity: MEDIUM
- Impact: Moderate improvement, 1-3% accuracy loss
- Code: `fairlearn.reductions.ExponentiatedGradient`

**Remove Proxy Features**
- Drop features correlated with protected attributes
- Complexity: LOW
- Impact: Reduces individual fairness violations
- Code: `df.drop(columns=proxy_features)`

#### In-Processing (Requires Retraining)
**Fairness Constraints**
- Add fairness constraints during training
- Complexity: HIGH
- Impact: Strong fairness guarantees
- Code: `fairlearn.reductions` with constraints

### Quick Start Example

```python
from nobias.model_audit import audit_model

report = audit_model(
    model='trained_model.pkl',
    test_data='test_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

print(f"Severity: {report.overall_severity.value}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")

# Check EEOC compliance
for key, metric in report.scorecard.items():
    if 'disparate_impact' in key and not metric.passed:
        print(f"⚠️ EEOC VIOLATION: {key} = {metric.value:.2f}")
```

### Performance

**Typical Execution**:
- Dataset: 2,000 samples
- Protected Attributes: 2 (gender, race)
- Model: RandomForestClassifier
- Duration: 15-30 seconds
- Memory: < 500 MB
- Cost: $0 (runs locally)


---

## Dataset Audit System

### What It Tests

**Training Data** - Tabular datasets before model training (CSV, Excel, Parquet, DataFrames)

### How It Works

**7-Phase Pipeline**:

```
┌─────────────────────────────────────────────────────────────┐
│ PHASE 1: Data Ingestion & Validation                       │
│ • Load from CSV, Excel, Parquet, or DataFrame              │
│ • Validate protected attributes exist                      │
│ • Validate target column exists                            │
│ • Check for sufficient samples                             │
├─────────────────────────────────────────────────────────────┤
│ PHASE 2: Representation Analysis                           │
│ • Count samples per group                                  │
│ • Compute representation ratios                            │
│ • Compute balance scores                                   │
│ • Flag underrepresented groups                             │
├─────────────────────────────────────────────────────────────┤
│ PHASE 3: Label Bias Analysis                               │
│ • Compute selection rates per group                        │
│ • Compute selection rate differences                       │
│ • Compute disparate impact ratios                          │
│ • Statistical significance tests                           │
├─────────────────────────────────────────────────────────────┤
│ PHASE 4: Proxy Feature Detection                           │
│ • Pearson correlation with protected attributes            │
│ • Mutual information with protected attributes             │
│ • Rank features by proxy risk                              │
├─────────────────────────────────────────────────────────────┤
│ PHASE 5: Missing Data Analysis                             │
│ • Compute missingness rates per group                      │
│ • Compute missingness differences                          │
│ • Flag systematic missingness patterns                     │
├─────────────────────────────────────────────────────────────┤
│ PHASE 6: Intersectional Disparity Analysis                 │
│ • Enumerate all intersectional groups                      │
│ • Compute expected vs actual sizes                         │
│ • Flag underrepresented intersections                      │
├─────────────────────────────────────────────────────────────┤
│ PHASE 7: Distribution Shift Analysis                       │
│ • Compute KL divergence for numeric features               │
│ • Compare distributions across groups                      │
│ • Flag significant shifts                                  │
└─────────────────────────────────────────────────────────────┘
```

### Seven Bias Types Detected

#### 1. Representation Bias
**What**: Underrepresented groups in dataset

**Metrics**:
- Group Size: Absolute count per group
- Representation Ratio: `group_size / total_size`
- Balance Score: Ratio of smallest to largest group

**Thresholds**:
- Representation ratio < 0.10 (10%) = Underrepresented
- Balance score < 0.50 = Imbalanced

**Example**:
```
Total: 10,000 samples
Male: 7,000 (70%)
Female: 3,000 (30%)
Balance Score: 3000/7000 = 0.43 → IMBALANCED
```

#### 2. Label Bias
**What**: Different approval rates across demographics

**Metrics**:
- Selection Rate: `P(Y=1 | A=a)` for each group
- Selection Rate Difference (SRD): `|P(Y=1|A=a) - P(Y=1|A=b)|`
- Disparate Impact Ratio (DIR): `min_rate / max_rate`

**Thresholds**:
- SRD > 0.10 = Significant disparity
- DIR < 0.80 = EEOC violation

**Example**:
```
Male approval rate: 80%
Female approval rate: 60%
SRD: 0.20 (20 percentage points)
DIR: 0.60/0.80 = 0.75 → EEOC VIOLATION
```

#### 3. Proxy Features
**What**: Features that encode protected attributes

**Methods**:
1. Pearson Correlation: Linear relationship
2. Mutual Information: Non-linear relationship
3. Predictive Power: Can feature predict protected attribute?

**Thresholds**:
- |Correlation| > 0.3 = Potential proxy
- Mutual Information > 0.1 = Potential proxy
- Predictive accuracy > 0.70 = Strong proxy

**Example**:
```
Feature: "first_name"
Protected: "gender"
Mutual Information: 0.45 → STRONG PROXY
(Names like "Jennifer", "Michael" reveal gender)
```

#### 4. Missing Data Bias
**What**: Systematic missingness by group

**Metrics**:
- Missingness Rate: `P(missing | A=a)` for each group
- Missingness Difference: `|P(missing|A=a) - P(missing|A=b)|`

**Thresholds**:
- Missingness difference > 0.10 = Systematic bias

**Example**:
```
Income missing for 5% of White applicants
Income missing for 25% of Black applicants
Difference: 0.20 → SYSTEMATIC BIAS
```

#### 5. Intersectional Bias
**What**: Compounded underrepresentation

**Method**:
1. Compute expected size: `P(A=a) × P(B=b) × total_size`
2. Compare to actual size
3. Flag significant deviations

**Example**:
```
Black: 20% of data
Female: 50% of data
Expected Black Female: 0.20 × 0.50 = 10%
Actual Black Female: 5%
→ UNDERREPRESENTED (50% of expected)
```

#### 6. Distribution Shift
**What**: Different feature distributions across groups

**Metric**: KL Divergence (Kullback-Leibler)

**Formula**: `KL(P||Q) = Σ P(x) log(P(x)/Q(x))`

**Thresholds**:
- KL < 0.1 = Similar distributions
- KL 0.1-0.5 = Moderate shift
- KL > 0.5 = Severe shift

**Example**:
```
Credit score distribution:
  Male: mean=720, std=50
  Female: mean=680, std=60
KL Divergence: 0.35 → MODERATE SHIFT
```

#### 7. Correlation Bias
**What**: Features correlated with protected attributes

**Metric**: Pearson correlation

**Threshold**: |corr| > 0.3

**Example**:
```
zip_code correlated with race (r=0.45)
→ PROXY FEATURE
```

### Severity Classification

| Severity | Representation | Label Bias (SRD) | DIR | Meaning |
|----------|----------------|------------------|-----|---------|
| **CRITICAL** | < 5% | > 0.20 | < 0.60 | Immediate action required |
| **MODERATE** | 5-10% | 0.10-0.20 | 0.60-0.80 | Remediation recommended |
| **LOW** | 10-20% | 0.05-0.10 | 0.80-0.90 | Monitor |
| **CLEAR** | > 20% | < 0.05 | > 0.90 | No action needed |

### Remediation Strategies

#### Resampling
**Stratified Resampling**
- Oversample underrepresented groups
- Complexity: LOW
- Impact: Balances representation
- Code: `sklearn.utils.resample`

#### Reweighting
**Sample Reweighting**
- Assign weights to balance groups
- Complexity: LOW
- Impact: Balances without changing data size
- Code: `sklearn.utils.class_weight.compute_sample_weight`

#### Feature Removal
**Remove Proxy Features**
- Drop features that encode protected attributes
- Complexity: LOW
- Impact: Reduces proxy bias
- Code: `df.drop(columns=proxy_features)`

#### Imputation
**Fair Imputation**
- Fill missing data systematically
- Complexity: MEDIUM
- Impact: Reduces missing data bias
- Code: `sklearn.impute.SimpleImputer`

### Quick Start Example

```python
from nobias import audit_dataset

report = audit_dataset(
    data='training_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,
)

print(f"Severity: {report.overall_severity}")
print(f"Total Findings: {len(report.findings)}")

# Check EEOC compliance
for attr, rates in report.label_rates.items():
    if rates['dir'] < 0.80:
        print(f"⚠️ EEOC VIOLATION: {attr} DIR={rates['dir']:.2f}")

# Check proxy features
for proxy in report.proxy_features:
    print(f"Proxy: {proxy.feature} → {proxy.protected} (score: {proxy.score:.3f})")
```

### Performance

**Typical Execution**:
- Dataset: 10,000 rows × 15 columns
- Protected Attributes: 2 (gender, race)
- Duration: 2-5 seconds
- Memory: < 200 MB
- Cost: $0 (runs locally)


---

## Actionable Insights

### What Are Actionable Insights?

Actionable Insights transform technical audit reports into **plain-English summaries** and **prioritized action items** for both technical and non-technical stakeholders.

### Available For

✅ **Agent Audit** - Actionable insights for agent bias reports  
✅ **Model Audit** - Actionable insights for model fairness reports  
✅ **Dataset Audit** - Actionable insights for dataset bias reports  

### Seven Key Sections

#### 1. Plain English Summary
Non-technical explanations for business users:

```json
{
  "plain_english": {
    "one_liner": "This model has 4 critical bias issues that could lead to legal violations",
    "biggest_problem": "The model approves different groups at very different rates. The gap is 26.6%...",
    "what_this_means_for_users": "Real people from certain demographic groups are being unfairly rejected...",
    "legal_risk": "YES - This model would likely fail an EEOC audit...",
    "quickest_fix": "Threshold Adjustment: Adjust decision thresholds per demographic group..."
  }
}
```

**Use Cases**:
- Executive summaries
- Compliance reports
- Stakeholder presentations
- Legal risk assessments

#### 2. Action Priority
Ranked list of actions by impact/effort ratio:

```json
{
  "action_priority": [
    {
      "rank": 1,
      "action": "Threshold Adjustment",
      "reason": "Highest impact, lowest effort. Current worst DIR is 0.7955...",
      "requires_retraining": false,
      "effort": "LOW",
      "impact": "HIGH",
      "do_this_first": true,
      "expected_metric_improvement": "Demographic parity could improve from 0.266 to <0.05"
    }
  ]
}
```

**Ranking Logic**:
1. Post-processing (no retraining) ranked highest - quick wins
2. Pre-processing (requires retraining) ranked medium
3. In-processing (complex retraining) ranked lowest

**Use Cases**:
- Sprint planning
- Resource allocation
- Roadmap prioritization
- Quick wins identification

#### 3. Bias Amplification (Model Audit Only)
Compares model bias to dataset bias:

```json
{
  "bias_amplification": {
    "dataset_dir": 0.75,
    "model_dir": 0.65,
    "amplification_score": -0.10,
    "verdict": "Model REDUCED bias",
    "explanation": "The model improved fairness compared to the training data..."
  }
}
```

**Amplification Score**:
- **Positive** = Model amplified bias (worse than data)
- **Negative** = Model reduced bias (better than data)
- **~0** = Model maintained bias level

**Use Cases**:
- Root cause analysis
- Training data quality assessment
- Model selection decisions

#### 4. Group Performance Gaps
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
      "severity": "CRITICAL",
      "plain_english": "Female is 12.1% more likely to be falsely rejected than Male"
    }
  ]
}
```

**Metrics Explained**:
- **Accuracy Gap** - Overall error rate difference
- **FPR Gap** - False positive rate difference (false approvals)
- **FNR Gap** - False negative rate difference (false rejections)

**Use Cases**:
- Identifying affected groups
- Understanding error patterns
- Targeted mitigation strategies

#### 5. Metric Scorecard
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
      "severity": "CRITICAL"
    }
  ]
}
```

**Gap to Pass**:
- Shows how much improvement needed to pass threshold
- Helps prioritize which metrics to fix first

**Use Cases**:
- Detailed technical analysis
- Compliance checklists
- Progress tracking

#### 6. Simulated Improvements
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
    "if_all_applied": {
      "pass_rate_after": 0.80,
      "critical_findings_after": 0,
      "compliance_after": "PASS",
      "recommended": true
    }
  }
}
```

**Use Cases**:
- Cost-benefit analysis
- Strategy selection
- Stakeholder buy-in
- Expected outcomes communication

#### 7. Summary Statistics
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
    "flip_rate": 0.08,
    "individual_fairness": "FAIL",
    "legal_risk_level": "CRITICAL",
    "retraining_required": true
  }
}
```

**Use Cases**:
- Dashboard KPIs
- Executive summaries
- Trend tracking
- Quick health checks

### How to Generate

#### For Model Audit:
```python
from model_audit.interpreter import interpret_model_audit_report

insights = interpret_model_audit_report(
    report_data="output/model_audit_comprehensive.json",
    dataset_audit_data="output/dataset_audit_comprehensive.json"  # Optional
)
```

#### For Dataset Audit:
```python
from library.dataset_audit import audit_dataset
from library.dataset_audit.report import generate_report

report = audit_dataset(...)
full_report = generate_report(report)
insights = full_report['actionable_insights']
```

#### For Agent Audit:
```python
from agent_audit import audit_agent

report = await audit_agent(...)
report.export(
    "audit_report.json",
    format="comprehensive",
    include_actionable_insights=True
)
```

### Frontend Integration Example

```javascript
// Fetch insights
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


---

## Compliance & Legal Framework

### Regulatory Frameworks Supported

#### 1. EEOC 80% Rule (US)
**Requirement**: Disparate Impact Ratio (DIR) ≥ 0.80

**Formula**: `DIR = (lowest group approval rate) / (highest group approval rate)`

**Status**:
- DIR < 0.80 = **LEGAL VIOLATION** (prima facie discrimination)
- DIR 0.80-0.85 = WARNING (borderline)
- DIR > 0.85 = COMPLIANT

**Covered By**:
- ✅ Agent Audit (EEOC AIR metric)
- ✅ Model Audit (Disparate Impact Ratio)
- ✅ Dataset Audit (Disparate Impact Ratio)

#### 2. EU AI Act (Articles 9, 12)
**Requirements**:
- Tamper-evident audit trails
- Reproducible results
- Model fingerprinting
- Risk assessment documentation

**Covered By**:
- ✅ Audit Integrity (SHA-256 hashes)
- ✅ Model Fingerprint (exact model state)
- ✅ CAFFE Test Suite Export (reproducibility)
- ✅ Severity Classification (risk assessment)

#### 3. NIST AI RMF (Risk Management Framework)
**Requirements**:
- Risk assessment
- Bias measurement
- Documentation
- Continuous monitoring

**Covered By**:
- ✅ Comprehensive metrics (CFR, MASD, DPD, etc.)
- ✅ Severity classification (CRITICAL/MODERATE/LOW/CLEAR)
- ✅ Exportable reports (JSON, Text, PDF)
- ✅ Audit trails with timestamps

#### 4. ISO/IEC 42001 (AI Management System)
**Requirements**:
- Reproducibility
- Audit integrity
- Version control
- Documentation

**Covered By**:
- ✅ Audit hashes (tamper-evident)
- ✅ Model fingerprints (reproducibility)
- ✅ Timestamped reports
- ✅ Configuration tracking

### Legal Defensibility Features

#### 1. Audit Integrity Hash
SHA-256 hashes of all audit components:

```python
report.audit_integrity
# {
#   "audit_hash": "a3f2b1c9...",
#   "prompts_hash": "b4c1d2e3...",
#   "responses_hash": "c5d2e3f4...",
#   "config_hash": "d6e3f4g5...",
#   "timestamp": "2026-04-28T10:30:00Z"
# }
```

**Use Case**: Prove audit wasn't altered after completion

#### 2. Model Fingerprint
Exact model state for reproducibility:

```python
report.model_fingerprint
# {
#   "model_id": "llama-3.1-70b-versatile",
#   "temperature": 0.0,
#   "max_tokens": 1024,
#   "system_prompt_hash": "e7f4g5h6...",
#   "sdk_version": "agent_audit-1.0.0",
#   "backend": "groq"
# }
```

**Use Case**: Reproduce exact audit conditions

#### 3. CAFFE Test Suite Export
Exportable test cases for sharing with auditors:

```python
report.export("audit_suite.json", fmt="caffe")
```

**Format**:
```json
{
  "framework": "CAFFE",
  "version": "1.0",
  "created_at": "2026-04-28T10:30:00Z",
  "test_cases": [...]
}
```

**Use Case**: Share test cases with external auditors, regulators

#### 4. Statistical Significance
All metrics include p-values from appropriate statistical tests:

| Test | Used For | Threshold |
|------|----------|-----------|
| Chi-square | Binary decisions | p < 0.05 |
| Welch's t-test | Numeric scores | p < 0.05 |
| Mann-Whitney U | Non-normal scores | p < 0.05 |
| Bonferroni correction | Multiple comparisons | Adjusted α |

**Significance Levels**:
- p < 0.01: CRITICAL (strong evidence)
- p < 0.05: SIGNIFICANT (moderate evidence)
- p < 0.10: SUGGESTIVE (weak evidence)
- p ≥ 0.10: NOT SIGNIFICANT

#### 5. Confidence Intervals
All rate-based metrics include 95% confidence intervals:

```python
{
  "rate": 0.126,
  "ci_lower": 0.089,
  "ci_upper": 0.163,
  "margin_of_error": 0.037
}
```

**Use Case**: Quantify uncertainty in measurements

### Compliance Checklist

#### Pre-Deployment Checklist
- [ ] Run appropriate audit (Agent/Model/Dataset)
- [ ] Check overall severity (must not be CRITICAL)
- [ ] Verify EEOC compliance (DIR ≥ 0.80)
- [ ] Review all critical findings
- [ ] Apply recommended mitigations
- [ ] Re-audit after mitigation
- [ ] Export audit report (JSON + PDF)
- [ ] Store audit_id with model/agent
- [ ] Document mitigation steps

#### Ongoing Monitoring Checklist
- [ ] Schedule periodic audits (weekly/monthly)
- [ ] Monitor for distribution shift
- [ ] Track metric trends over time
- [ ] Re-audit after retraining
- [ ] Update documentation
- [ ] Maintain audit trail


---

## Performance & Cost Analysis

### Execution Time Comparison

| System | Dataset Size | Duration | Throughput |
|--------|--------------|----------|------------|
| **Dataset Audit** | 10,000 rows | 2-5 sec | 2,000-5,000 rows/sec |
| **Model Audit** | 2,000 samples | 15-30 sec | 67-133 samples/sec |
| **Agent Audit (Quick)** | 14 personas | ~2 min | 7 personas/min |
| **Agent Audit (Standard)** | 80 personas | ~5 min | 16 personas/min |
| **Agent Audit (Full)** | 430 personas | ~30 min | 14 personas/min |

### Cost Comparison

#### Dataset Audit
**Cost**: $0 (runs locally)  
**Infrastructure**: CPU only, < 200 MB RAM  
**Scalability**: Linear with dataset size  

#### Model Audit
**Cost**: $0 (runs locally)  
**Infrastructure**: CPU only, < 500 MB RAM  
**Scalability**: Linear with test set size  

#### Agent Audit
**Cost**: Depends on LLM provider and tier

**Groq (llama-3.1-70b-versatile)**:
- Input: $0.59 per 1M tokens
- Output: $0.79 per 1M tokens

| Tier | Tokens | Cost |
|------|--------|------|
| Quick | 43,400 | $0.03 |
| Standard | 69,150 | $0.05 |
| Full | 106,200 | $0.07 |

**Anthropic (claude-3.5-sonnet)**:
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

| Tier | Tokens | Cost |
|------|--------|------|
| Quick | 43,400 | $0.11 |
| Standard | 69,150 | $0.17 |
| Full | 106,200 | $0.27 |

### Cost Optimization (Agent Audit)

**Without Optimization**:
- 80 personas × 3 runs × 600 tokens = 144,000 tokens
- Cost: $1.87 (Anthropic)

**With Optimization**:
- Compressed JSON: 85% reduction
- Prompt caching: 65% reduction (after first call)
- Two-pass evaluation: 50% fewer calls
- Smart sampling: Adaptive based on budget

**Result**:
- 43,400 tokens (70% reduction)
- Cost: $0.28 (85% savings)

### Resource Requirements

#### Dataset Audit
```
CPU: 1-2 cores
RAM: < 200 MB
Disk: Minimal (input data only)
Network: None (runs locally)
```

#### Model Audit
```
CPU: 1-4 cores
RAM: < 500 MB
Disk: Model file + test data
Network: None (runs locally)
```

#### Agent Audit
```
CPU: 1-2 cores
RAM: < 300 MB
Disk: Minimal
Network: Required (API calls to LLM)
Rate Limits: 5-10 req/sec (configurable)
```

### Scalability

#### Dataset Audit
**Scales linearly with**:
- Number of rows
- Number of columns
- Number of protected attributes

**Bottlenecks**:
- Proxy feature detection (mutual information)
- KL divergence computation

**Optimization**:
- Sample large datasets (>100k rows)
- Parallelize proxy detection

#### Model Audit
**Scales linearly with**:
- Number of test samples
- Number of protected attributes
- Model complexity

**Bottlenecks**:
- Counterfactual generation
- Model inference

**Optimization**:
- Batch predictions
- Sample large test sets (>10k samples)

#### Agent Audit
**Scales linearly with**:
- Number of personas
- Number of runs per persona

**Bottlenecks**:
- LLM API rate limits
- Network latency

**Optimization**:
- Two-pass evaluation (50% fewer calls)
- Prompt caching (65% token reduction)
- Async execution with rate limiting

### Performance Benchmarks

#### Dataset Audit
```
Small (1k rows): 1-2 sec
Medium (10k rows): 2-5 sec
Large (100k rows): 10-20 sec
Very Large (1M rows): 60-120 sec (with sampling)
```

#### Model Audit
```
Small (500 samples): 5-10 sec
Medium (2k samples): 15-30 sec
Large (10k samples): 60-120 sec
Very Large (50k samples): 300-600 sec
```

#### Agent Audit
```
Quick (14 personas): 2 min
Standard (80 personas): 5 min
Full (430 personas): 30 min

With rate limiting (1 req/sec):
Quick: 8 min
Standard: 40 min
Full: 180 min
```


---

## Integration Patterns

### CI/CD Pipeline Integration

#### Dataset Audit in Data Pipeline
```python
def validate_training_data(data_path):
    """Validate dataset before training."""
    from nobias import audit_dataset
    
    report = audit_dataset(
        data=data_path,
        protected_attributes=['gender', 'race'],
        target_column='hired',
        positive_value=1
    )
    
    # Block if critical issues
    if report.overall_severity == 'CRITICAL':
        raise ValueError(f"Dataset has critical bias: {report.findings}")
    
    # Check EEOC compliance
    for attr, rates in report.label_rates.items():
        if rates['dir'] < 0.80:
            raise ValueError(f"EEOC violation for {attr}: DIR={rates['dir']:.2f}")
    
    return report

# Use in pipeline
try:
    audit_report = validate_training_data('data/training.csv')
    train_model()
except ValueError as e:
    print(f"❌ Data validation failed: {e}")
    apply_remediation()
```

#### Model Audit in Model Registry
```python
def register_model(model_path, test_data_path):
    """Register model with fairness audit."""
    from nobias.model_audit import audit_model
    
    # Run audit
    report = audit_model(
        model=model_path,
        test_data=test_data_path,
        protected_attributes=['gender', 'race'],
        target_column='hired',
        positive_value=1
    )
    
    # Store audit with model
    model_metadata = {
        'model_path': model_path,
        'audit_id': report.audit_id,
        'audit_timestamp': report.timestamp,
        'overall_severity': report.overall_severity.value,
        'eeoc_compliant': all(
            m.passed for k, m in report.scorecard.items()
            if 'disparate_impact' in k
        )
    }
    
    # Block deployment if critical
    if report.overall_severity == 'CRITICAL':
        raise ValueError("Model has critical bias - deployment blocked")
    
    # Register in MLflow/model registry
    mlflow.log_dict(model_metadata, 'model_audit.json')
    mlflow.log_artifact(f'{report.audit_id}_report.pdf')
    
    return model_metadata
```

#### Agent Audit in Deployment Gate
```python
async def validate_agent_deployment(system_prompt, seed_case):
    """Validate agent before production deployment."""
    from agent_audit import audit_agent
    
    # Run audit
    report = await audit_agent(
        system_prompt=system_prompt,
        seed_case=seed_case,
        api_key=os.getenv('GROQ_API_KEY'),
        mode='standard'
    )
    
    # Deployment decision
    if report.overall_severity in ['CRITICAL', 'MODERATE']:
        return {
            'approved': False,
            'reason': f"Severity: {report.overall_severity}, CFR: {report.overall_cfr:.1%}",
            'audit_id': report.audit_id
        }
    
    return {
        'approved': True,
        'audit_id': report.audit_id,
        'cfr': report.overall_cfr
    }
```

### Monitoring & Alerting

#### Scheduled Audits
```python
from apscheduler.schedulers.background import BackgroundScheduler

def schedule_periodic_audits():
    """Schedule weekly fairness audits."""
    scheduler = BackgroundScheduler()
    
    # Dataset audit (weekly)
    scheduler.add_job(
        audit_training_data,
        'cron',
        day_of_week='mon',
        hour=2
    )
    
    # Model audit (after retraining)
    scheduler.add_job(
        audit_production_model,
        'cron',
        day_of_week='sun',
        hour=3
    )
    
    # Agent audit (monthly)
    scheduler.add_job(
        audit_production_agent,
        'cron',
        day=1,
        hour=4
    )
    
    scheduler.start()
```

#### Slack Alerts
```python
def send_bias_alert(report, system_name):
    """Send Slack alert for critical bias."""
    if report.overall_severity == 'CRITICAL':
        insights = generate_actionable_insights(report)
        
        message = f"""
        🚨 CRITICAL BIAS DETECTED in {system_name}
        
        {insights['plain_english']['one_liner']}
        
        Legal Risk: {insights['summary_stats']['legal_risk_level']}
        
        Recommended Action:
        {insights['action_priority'][0]['action']}
        
        Audit ID: {report.audit_id}
        Report: {report_url}
        """
        
        slack_client.chat_postMessage(
            channel='#ml-alerts',
            text=message
        )
```

### Frontend Integration

#### Dashboard Overview
```javascript
// Fetch all audit reports
const [datasetAudit, modelAudit, agentAudit] = await Promise.all([
  fetch('/api/audits/dataset/latest').then(r => r.json()),
  fetch('/api/audits/model/latest').then(r => r.json()),
  fetch('/api/audits/agent/latest').then(r => r.json())
]);

// Display health scores
document.getElementById('dataset-health').textContent = 
  datasetAudit.actionable_insights.simulated_improvements.current_state.health_score;

document.getElementById('model-health').textContent = 
  modelAudit.actionable_insights.summary_stats.pass_rate * 100;

document.getElementById('agent-health').textContent = 
  (1 - agentAudit.overall_cfr) * 100;

// Display severity badges
['dataset', 'model', 'agent'].forEach(type => {
  const audit = eval(`${type}Audit`);
  const severity = audit.overall_severity || audit.summary_stats.legal_risk_level;
  document.getElementById(`${type}-badge`).className = `badge badge-${severity.toLowerCase()}`;
});
```

#### Action Priority View
```javascript
// Combine actions from all audits
const allActions = [
  ...datasetAudit.actionable_insights.action_priority,
  ...modelAudit.actionable_insights.action_priority,
  ...agentAudit.actionable_insights.action_priority
];

// Sort by priority
allActions.sort((a, b) => a.rank - b.rank);

// Render top 5 actions
allActions.slice(0, 5).forEach(action => {
  const card = `
    <div class="action-card ${action.do_this_first ? 'priority' : ''}">
      <span class="rank">#${action.rank}</span>
      <h3>${action.action}</h3>
      <div class="badges">
        <span class="effort-${action.effort.toLowerCase()}">${action.effort}</span>
        <span class="impact-${action.impact.toLowerCase()}">${action.impact}</span>
        ${action.requires_retraining ? '<span class="retrain">Retraining Required</span>' : ''}
      </div>
      <p>${action.reason}</p>
    </div>
  `;
  document.getElementById('actions').innerHTML += card;
});
```

#### Compliance Dashboard
```javascript
// Check EEOC compliance across all systems
const complianceStatus = {
  dataset: datasetAudit.label_rates.gender.dir >= 0.80,
  model: Object.values(modelAudit.scorecard)
    .filter(m => m.metric_name === 'disparate_impact')
    .every(m => m.passed),
  agent: agentAudit.eeoc_compliant
};

// Display compliance status
Object.entries(complianceStatus).forEach(([system, compliant]) => {
  const icon = compliant ? '✅' : '❌';
  const status = compliant ? 'COMPLIANT' : 'VIOLATION';
  document.getElementById(`${system}-compliance`).innerHTML = 
    `${icon} ${status}`;
});
```

### API Endpoints

#### RESTful API Design
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class DatasetAuditRequest(BaseModel):
    data_path: str
    protected_attributes: list[str]
    target_column: str
    positive_value: int

@app.post("/api/audits/dataset")
async def run_dataset_audit(request: DatasetAuditRequest):
    """Run dataset audit."""
    from nobias import audit_dataset
    
    report = audit_dataset(
        data=request.data_path,
        protected_attributes=request.protected_attributes,
        target_column=request.target_column,
        positive_value=request.positive_value
    )
    
    return {
        'audit_id': report.audit_id,
        'severity': report.overall_severity,
        'findings': report.findings,
        'actionable_insights': generate_actionable_insights(report)
    }

@app.post("/api/audits/model")
async def run_model_audit(request: ModelAuditRequest):
    """Run model audit."""
    from nobias.model_audit import audit_model
    
    report = audit_model(
        model=request.model_path,
        test_data=request.test_data_path,
        protected_attributes=request.protected_attributes,
        target_column=request.target_column,
        positive_value=request.positive_value
    )
    
    return {
        'audit_id': report.audit_id,
        'severity': report.overall_severity.value,
        'flip_rate': report.counterfactual_result.flip_rate,
        'eeoc_compliant': all(
            m.passed for k, m in report.scorecard.items()
            if 'disparate_impact' in k
        ),
        'actionable_insights': generate_actionable_insights(report)
    }

@app.post("/api/audits/agent")
async def run_agent_audit(request: AgentAuditRequest):
    """Run agent audit."""
    from agent_audit import audit_agent
    
    report = await audit_agent(
        system_prompt=request.system_prompt,
        seed_case=request.seed_case,
        api_key=request.api_key,
        mode=request.mode
    )
    
    return {
        'audit_id': report.audit_id,
        'severity': report.overall_severity,
        'cfr': report.overall_cfr,
        'eeoc_compliant': report.eeoc_compliant,
        'actionable_insights': generate_actionable_insights(report)
    }

@app.get("/api/audits/{audit_id}")
async def get_audit_report(audit_id: str):
    """Retrieve audit report by ID."""
    # Load from database/storage
    report = load_audit_report(audit_id)
    return report

@app.get("/api/audits/latest")
async def get_latest_audits():
    """Get latest audit for each system."""
    return {
        'dataset': get_latest_dataset_audit(),
        'model': get_latest_model_audit(),
        'agent': get_latest_agent_audit()
    }
```


---

## Comparison Matrix

### When to Use Each System

| Scenario | Use | Why |
|----------|-----|-----|
| **Before collecting data** | None | Too early - no data yet |
| **After data collection** | Dataset Audit | Catch bias before expensive training |
| **After model training** | Model Audit | Validate fairness before deployment |
| **Before agent deployment** | Agent Audit | Test LLM-based decision-making |
| **Production monitoring** | All Three | Continuous fairness monitoring |
| **Regulatory audit** | All Three | Comprehensive compliance documentation |

### Feature Comparison

| Feature | Dataset Audit | Model Audit | Agent Audit |
|---------|---------------|-------------|-------------|
| **Input** | Training data | Trained model + test data | Agent prompt/API/logs |
| **Output** | Bias findings + remediation | Fairness metrics + mitigation | CFR/MASD + prompt fixes |
| **Speed** | 2-10 sec | 15-60 sec | 2-30 min |
| **Cost** | $0 (local) | $0 (local) | $0.03-$0.27 (LLM) |
| **Privacy** | 100% local | 100% local | Optional cloud LLM |
| **Bias Types** | 7 types | Group + Individual + Intersectional | 4 types |
| **Metrics** | SRD, DIR, Proxy, KL | DPD, EO, DIR, PP, Calibration, Flip Rate | CFR, MASD, AIR, SSS |
| **EEOC Compliance** | ✅ DIR | ✅ DIR | ✅ AIR |
| **Actionable Insights** | ✅ | ✅ | ✅ |
| **Remediation** | Resampling, Reweighting, Feature Removal | Threshold Adjustment, Reweighting, Constraints | Prompt Modification |
| **Requires Retraining** | Yes (for fixes) | Sometimes | No |
| **Legal Defensibility** | ✅ | ✅ | ✅ |
| **Tamper-Evident** | ✅ | ✅ | ✅ |
| **Reproducible** | ✅ | ✅ | ✅ |

### Metric Comparison

| Metric | Dataset Audit | Model Audit | Agent Audit | What It Measures |
|--------|---------------|-------------|-------------|------------------|
| **Demographic Parity** | ❌ | ✅ DPD | ✅ DP | Equal approval rates |
| **Equalized Odds** | ❌ | ✅ TPR/FPR | ❌ | Equal error rates |
| **Disparate Impact** | ✅ DIR | ✅ DIR | ✅ AIR | EEOC 80% rule |
| **Predictive Parity** | ❌ | ✅ PP | ❌ | Equal precision |
| **Calibration** | ❌ | ✅ Cal | ❌ | Probability accuracy |
| **Counterfactual Flip Rate** | ❌ | ✅ Flip Rate | ✅ CFR | Individual fairness |
| **Score Difference** | ❌ | ❌ | ✅ MASD | Sub-threshold bias |
| **Stability** | ❌ | ❌ | ✅ SSS | Decision consistency |
| **Representation** | ✅ Ratio | ❌ | ❌ | Group balance |
| **Label Bias** | ✅ SRD | ❌ | ❌ | Outcome disparity |
| **Proxy Features** | ✅ MI/Corr | ❌ | ❌ | Feature leakage |
| **Missing Data** | ✅ Miss Rate | ❌ | ❌ | Systematic missingness |
| **Intersectional** | ✅ Expected vs Actual | ✅ Superadditive | ✅ Scan | Compounded bias |
| **Distribution Shift** | ✅ KL Divergence | ❌ | ❌ | Feature distribution |

### Severity Thresholds

| Severity | Dataset Audit | Model Audit | Agent Audit |
|----------|---------------|-------------|-------------|
| **CRITICAL** | DIR < 0.60, Rep < 5%, SRD > 0.20 | DIR < 0.60, DPD > 0.20, Flip > 15% | CFR > 15%, AIR < 0.60 |
| **MODERATE** | DIR 0.60-0.80, Rep 5-10%, SRD 0.10-0.20 | DIR 0.60-0.80, DPD 0.10-0.20, Flip 5-15% | CFR 10-15%, AIR 0.60-0.80 |
| **LOW** | DIR 0.80-0.90, Rep 10-20%, SRD 0.05-0.10 | DIR 0.80-0.90, DPD 0.05-0.10, Flip 2-5% | CFR 5-10%, AIR 0.80-0.85 |
| **CLEAR** | DIR > 0.90, Rep > 20%, SRD < 0.05 | DIR > 0.90, DPD < 0.05, Flip < 2% | CFR < 5%, AIR > 0.85 |

### Remediation Strategies

| Strategy | Dataset Audit | Model Audit | Agent Audit | Requires Retraining |
|----------|---------------|-------------|-------------|---------------------|
| **Threshold Adjustment** | ❌ | ✅ | ❌ | No |
| **Resampling** | ✅ | ❌ | ❌ | Yes (data) |
| **Reweighting** | ✅ | ✅ | ❌ | Yes |
| **Feature Removal** | ✅ | ✅ | ❌ | Yes |
| **Fairness Constraints** | ❌ | ✅ | ❌ | Yes |
| **Prompt Modification** | ❌ | ❌ | ✅ | No |
| **Context Adjustment** | ❌ | ❌ | ✅ | No |

### Use Case Mapping

| Use Case | Primary System | Secondary Systems | Rationale |
|----------|----------------|-------------------|-----------|
| **Hiring** | Agent Audit | Model + Dataset | LLM-based screening |
| **Lending** | Model Audit | Dataset | Traditional ML models |
| **Content Moderation** | Agent Audit | None | LLM-based decisions |
| **Medical Triage** | Model Audit | Dataset | High-stakes ML |
| **College Admissions** | Model Audit | Dataset | Traditional ML |
| **Insurance** | Model Audit | Dataset | Traditional ML |
| **Chatbots** | Agent Audit | None | LLM-based |
| **Recommendation Systems** | Model Audit | Dataset | Traditional ML |


---

## Real-World Use Cases

### Use Case 1: Hiring Platform

**Scenario**: Tech company uses LLM to screen resumes

**Challenge**: Ensure fair evaluation across demographics

**Solution**:
1. **Dataset Audit** on historical hiring data
   - Found: Female representation 30%, DIR 0.75 (EEOC violation)
   - Action: Applied stratified resampling to balance dataset
   - Result: DIR improved to 0.88

2. **Agent Audit** on LLM screening prompt
   - Found: CFR 12.5% (MODERATE), name-based bias detected
   - Action: Modified prompt to ignore names, added fairness instructions
   - Result: CFR reduced to 4.2% (LOW)

3. **Model Audit** on final ranking model
   - Found: Flip rate 6.8% (MODERATE)
   - Action: Applied threshold adjustment
   - Result: Flip rate reduced to 2.1% (CLEAR)

**Outcome**:
- EEOC compliant across all systems
- Legal risk reduced from CRITICAL to LOW
- Deployment approved

---

### Use Case 2: Lending Institution

**Scenario**: Bank uses ML model for loan approvals

**Challenge**: Avoid discriminatory lending practices

**Solution**:
1. **Dataset Audit** on loan application data
   - Found: Black applicants 15% of data, DIR 0.68 (CRITICAL)
   - Found: Zip code strong proxy for race (MI=0.52)
   - Action: Removed zip code, applied reweighting
   - Result: DIR improved to 0.82

2. **Model Audit** on trained model
   - Found: DIR 0.79 (WARNING), DPD 0.18 (MODERATE)
   - Found: Intersectional bias for Black Women (DIR 0.65)
   - Action: Applied threshold adjustment per group
   - Result: DIR improved to 0.87, DPD reduced to 0.08

3. **Ongoing Monitoring**
   - Weekly model audits
   - Monthly dataset audits on new data
   - Alerts for DIR < 0.80

**Outcome**:
- EEOC compliant
- Passed regulatory audit
- Reduced legal risk

---

### Use Case 3: Healthcare Triage System

**Scenario**: Hospital uses AI to prioritize emergency cases

**Challenge**: Ensure equitable care across demographics

**Solution**:
1. **Dataset Audit** on patient records
   - Found: Missing data bias (income missing 30% for minorities vs 5% for majority)
   - Found: Age distribution shift (KL=0.42)
   - Action: Applied fair imputation, balanced age groups
   - Result: Missingness difference reduced to 8%

2. **Model Audit** on triage model
   - Found: Calibration error 0.12 (poor)
   - Found: FPR gap 0.15 (MODERATE) - minorities more likely to be under-triaged
   - Action: Recalibrated model, applied fairness constraints
   - Result: Calibration error reduced to 0.04, FPR gap to 0.06

3. **Deployment**
   - Continuous monitoring with weekly audits
   - Alert system for metric degradation
   - Quarterly comprehensive audits

**Outcome**:
- Equitable triage decisions
- Improved patient outcomes
- Regulatory compliance

---

### Use Case 4: Content Moderation Platform

**Scenario**: Social media platform uses LLM for content moderation

**Challenge**: Avoid biased content removal

**Solution**:
1. **Agent Audit** on moderation prompt
   - Found: CFR 18.2% (CRITICAL) - decisions flip based on user demographics
   - Found: Context priming effect (CFR increases to 22.1% with user history)
   - Action: Removed demographic context, added fairness guidelines
   - Result: CFR reduced to 6.8% (MODERATE)

2. **Iterative Improvement**
   - Tested 5 prompt variations
   - Selected best performing (CFR 3.2%)
   - Validated with log replay audit

3. **Production Monitoring**
   - Monthly agent audits
   - A/B testing new prompts
   - User feedback integration

**Outcome**:
- Fair content moderation
- Reduced user complaints
- Improved trust

---

### Use Case 5: College Admissions

**Scenario**: University uses ML to rank applicants

**Challenge**: Ensure fair admissions process

**Solution**:
1. **Dataset Audit** on historical admissions
   - Found: Underrepresentation of first-gen students (8%)
   - Found: Proxy features (high school name, extracurriculars)
   - Action: Removed proxy features, oversampled underrepresented groups
   - Result: Representation improved to 18%

2. **Model Audit** on ranking model
   - Found: Predictive parity violation (precision gap 0.14)
   - Found: Intersectional bias for low-income minorities
   - Action: Applied sample reweighting, fairness constraints
   - Result: Precision gap reduced to 0.04

3. **Compliance Documentation**
   - Exported audit reports for legal review
   - Documented all mitigation steps
   - Maintained audit trail

**Outcome**:
- Fair admissions process
- Increased diversity
- Legal defensibility

---

### Use Case 6: Insurance Pricing

**Scenario**: Insurance company uses ML for risk assessment

**Challenge**: Avoid discriminatory pricing

**Solution**:
1. **Dataset Audit** on claims data
   - Found: Gender imbalance (65% male)
   - Found: Age distribution shift (KL=0.38)
   - Action: Balanced dataset, normalized age distribution
   - Result: Balance score improved to 0.54

2. **Model Audit** on pricing model
   - Found: Demographic parity violation (DPD 0.22)
   - Found: Calibration issues across age groups
   - Action: Recalibrated model, applied threshold adjustment
   - Result: DPD reduced to 0.07

3. **Regulatory Compliance**
   - Quarterly audits for state regulators
   - Documented compliance with insurance laws
   - Maintained tamper-evident audit trails

**Outcome**:
- Fair pricing
- Regulatory approval
- Reduced legal risk


---

## Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

#### Week 1: Setup & Dataset Audit
**Goals**:
- Install NoBias platform
- Run first dataset audit
- Understand findings

**Tasks**:
1. Install dependencies
   ```bash
   pip install pandas numpy scipy scikit-learn
   ```

2. Run dataset audit
   ```python
   from nobias import audit_dataset
   
   report = audit_dataset(
       data='training_data.csv',
       protected_attributes=['gender', 'race'],
       target_column='hired',
       positive_value=1
   )
   ```

3. Review findings
   - Check overall severity
   - Identify critical issues
   - Review proxy features
   - Check EEOC compliance

4. Export report
   ```python
   report.export('dataset_audit.json', format='json')
   report.export('dataset_audit.pdf', format='pdf')
   ```

**Deliverables**:
- Dataset audit report
- List of critical findings
- Remediation plan

#### Week 2: Data Remediation
**Goals**:
- Apply recommended fixes
- Re-audit dataset
- Validate improvements

**Tasks**:
1. Apply remediation strategies
   - Resampling for representation
   - Remove proxy features
   - Fair imputation for missing data

2. Re-audit cleaned dataset
   ```python
   report_after = audit_dataset(
       data='cleaned_data.csv',
       protected_attributes=['gender', 'race'],
       target_column='hired',
       positive_value=1
   )
   ```

3. Compare before/after
   - DIR improvement
   - Representation improvement
   - Proxy feature reduction

**Deliverables**:
- Cleaned dataset
- Before/after comparison report
- Documentation of changes

---

### Phase 2: Model Development (Week 3-4)

#### Week 3: Model Training & Audit
**Goals**:
- Train model on cleaned data
- Run model audit
- Identify fairness issues

**Tasks**:
1. Train model
   ```python
   from sklearn.ensemble import RandomForestClassifier
   
   model = RandomForestClassifier()
   model.fit(X_train, y_train)
   ```

2. Run model audit
   ```python
   from nobias.model_audit import audit_model
   
   report = audit_model(
       model=model,
       test_data=test_df,
       protected_attributes=['gender', 'race'],
       target_column='hired',
       positive_value=1
   )
   ```

3. Review findings
   - Check flip rate
   - Check EEOC compliance
   - Review group performance gaps
   - Check intersectional bias

**Deliverables**:
- Trained model
- Model audit report
- Mitigation plan

#### Week 4: Model Mitigation
**Goals**:
- Apply mitigation strategies
- Re-audit model
- Validate improvements

**Tasks**:
1. Apply post-processing (no retraining)
   ```python
   from fairlearn.postprocessing import ThresholdOptimizer
   
   mitigator = ThresholdOptimizer(
       estimator=model,
       constraints="demographic_parity"
   )
   mitigator.fit(X_val, y_val, sensitive_features=gender_val)
   ```

2. Re-audit mitigated model
   ```python
   report_after = audit_model(
       model=mitigator,
       test_data=test_df,
       protected_attributes=['gender', 'race'],
       target_column='hired',
       positive_value=1
   )
   ```

3. Compare metrics
   - Flip rate improvement
   - DIR improvement
   - Accuracy impact

**Deliverables**:
- Mitigated model
- Before/after comparison
- Performance analysis

---

### Phase 3: Agent Development (Week 5-6)

#### Week 5: Agent Audit
**Goals**:
- Audit LLM-based agent
- Identify bias patterns
- Plan prompt improvements

**Tasks**:
1. Run agent audit
   ```python
   from agent_audit import audit_agent
   
   report = await audit_agent(
       system_prompt="You are a hiring assistant...",
       seed_case="Evaluate: Name: Jordan...",
       api_key=os.getenv('GROQ_API_KEY'),
       mode='standard'
   )
   ```

2. Review findings
   - Check CFR
   - Check EEOC AIR
   - Identify bias types (explicit, implicit, contextual)
   - Review stability (SSS)

3. Analyze persona results
   - Which demographics trigger bias?
   - Name-based bias patterns
   - Context priming effects

**Deliverables**:
- Agent audit report
- Bias pattern analysis
- Prompt improvement plan

#### Week 6: Prompt Optimization
**Goals**:
- Improve agent prompt
- Re-audit agent
- Validate improvements

**Tasks**:
1. Modify prompt based on findings
   - Add fairness instructions
   - Remove demographic context
   - Add structured output format

2. Test multiple prompt variations
   ```python
   prompts = [
       "Original prompt...",
       "Improved prompt v1...",
       "Improved prompt v2..."
   ]
   
   for i, prompt in enumerate(prompts):
       report = await audit_agent(
           system_prompt=prompt,
           seed_case=seed_case,
           api_key=api_key,
           mode='quick'
       )
       print(f"Prompt {i}: CFR={report.overall_cfr:.1%}")
   ```

3. Select best performing prompt
   - Lowest CFR
   - EEOC compliant
   - Stable (high SSS)

**Deliverables**:
- Optimized prompt
- Comparison report
- A/B test results

---

### Phase 4: Integration (Week 7-8)

#### Week 7: CI/CD Integration
**Goals**:
- Integrate audits into pipeline
- Automate testing
- Set up deployment gates

**Tasks**:
1. Add dataset audit to data pipeline
   ```python
   def validate_data(data_path):
       report = audit_dataset(data_path, ...)
       if report.overall_severity == 'CRITICAL':
           raise ValueError("Dataset has critical bias")
       return report
   ```

2. Add model audit to model registry
   ```python
   def register_model(model_path):
       report = audit_model(model_path, ...)
       mlflow.log_dict(report.to_dict(), 'audit.json')
       if report.overall_severity == 'CRITICAL':
           raise ValueError("Model has critical bias")
   ```

3. Add agent audit to deployment gate
   ```python
   async def validate_agent(prompt):
       report = await audit_agent(prompt, ...)
       if report.overall_severity in ['CRITICAL', 'MODERATE']:
           return {'approved': False}
       return {'approved': True}
   ```

**Deliverables**:
- Automated audit pipeline
- Deployment gates
- CI/CD configuration

#### Week 8: Monitoring & Alerting
**Goals**:
- Set up continuous monitoring
- Configure alerts
- Build dashboard

**Tasks**:
1. Schedule periodic audits
   ```python
   from apscheduler.schedulers.background import BackgroundScheduler
   
   scheduler = BackgroundScheduler()
   scheduler.add_job(audit_dataset, 'cron', day_of_week='mon')
   scheduler.add_job(audit_model, 'cron', day_of_week='sun')
   scheduler.add_job(audit_agent, 'cron', day=1)
   scheduler.start()
   ```

2. Set up Slack alerts
   ```python
   def send_alert(report):
       if report.overall_severity == 'CRITICAL':
           slack_client.chat_postMessage(
               channel='#ml-alerts',
               text=f"🚨 CRITICAL BIAS: {report.audit_id}"
           )
   ```

3. Build dashboard
   - Display latest audit results
   - Show severity trends
   - List action priorities
   - Track compliance status

**Deliverables**:
- Monitoring system
- Alert configuration
- Dashboard

---

### Phase 5: Production (Week 9-10)

#### Week 9: Documentation & Training
**Goals**:
- Document processes
- Train team
- Establish best practices

**Tasks**:
1. Document audit procedures
   - When to run each audit
   - How to interpret findings
   - Remediation workflows

2. Train team members
   - Data scientists: Dataset + Model audits
   - ML engineers: Model audit + CI/CD
   - Prompt engineers: Agent audit
   - Managers: Actionable insights

3. Establish best practices
   - Audit frequency
   - Severity thresholds
   - Escalation procedures

**Deliverables**:
- Documentation
- Training materials
- Best practices guide

#### Week 10: Compliance & Reporting
**Goals**:
- Prepare compliance documentation
- Set up reporting
- Establish audit trail

**Tasks**:
1. Export compliance reports
   ```python
   # Generate comprehensive reports
   dataset_report.export('dataset_audit_comprehensive.json')
   model_report.export('model_audit_comprehensive.json')
   agent_report.export('agent_audit_comprehensive.json')
   
   # Generate actionable insights
   generate_actionable_insights(model_report)
   ```

2. Set up audit trail storage
   - Store all audit reports
   - Maintain tamper-evident hashes
   - Version control configurations

3. Prepare regulatory documentation
   - EEOC compliance reports
   - EU AI Act documentation
   - NIST AI RMF assessment

**Deliverables**:
- Compliance documentation
- Audit trail system
- Regulatory reports

---

### Ongoing Maintenance

#### Monthly Tasks
- [ ] Review audit trends
- [ ] Update thresholds if needed
- [ ] Retrain models if drift detected
- [ ] Update documentation

#### Quarterly Tasks
- [ ] Comprehensive audits (Full mode)
- [ ] Regulatory compliance review
- [ ] Team training refresh
- [ ] Process improvements

#### Annual Tasks
- [ ] External audit
- [ ] Regulatory filing
- [ ] Platform updates
- [ ] Strategy review


---

## Summary & Key Takeaways

### Platform Overview

**NoBias** is a comprehensive fairness testing platform covering the entire AI lifecycle:

```
DATA → DATASET AUDIT → MODEL → MODEL AUDIT → AGENT → AGENT AUDIT → PRODUCTION
```

### Three Systems, One Goal

| System | Stage | Purpose | Cost | Speed |
|--------|-------|---------|------|-------|
| **Dataset Audit** | Pre-training | Prevent biased models | $0 | 2-10 sec |
| **Model Audit** | Pre-deployment | Validate fairness | $0 | 15-60 sec |
| **Agent Audit** | Pre/Post-deployment | Monitor LLM bias | $0.03-$0.27 | 2-30 min |

### Key Metrics

#### Dataset Audit
- **Representation Ratio**: Group balance
- **Selection Rate Difference (SRD)**: Label bias
- **Disparate Impact Ratio (DIR)**: EEOC compliance
- **Proxy Features**: Feature leakage
- **KL Divergence**: Distribution shift

#### Model Audit
- **Demographic Parity Difference (DPD)**: Approval rate equality
- **Equalized Odds**: Error rate equality
- **Disparate Impact Ratio (DIR)**: EEOC compliance
- **Counterfactual Flip Rate**: Individual fairness
- **Predictive Parity**: Precision equality

#### Agent Audit
- **Counterfactual Flip Rate (CFR)**: Decision consistency
- **Mean Absolute Score Difference (MASD)**: Score shifts
- **EEOC AIR**: Legal compliance
- **Stochastic Stability Score (SSS)**: Reliability

### EEOC 80% Rule

**All three systems check EEOC compliance**:

```
DIR = (lowest group approval rate) / (highest group approval rate)

DIR < 0.80 = LEGAL VIOLATION
DIR ≥ 0.80 = COMPLIANT
```

### Actionable Insights

**All three systems provide**:
1. Plain English summaries
2. Prioritized action lists
3. Simulated improvements
4. Group performance gaps
5. Metric scorecards
6. Summary statistics

### Compliance Coverage

✅ **EEOC 80% Rule** (US)  
✅ **EU AI Act** (Articles 9, 12)  
✅ **NIST AI RMF** (Risk Management Framework)  
✅ **ISO/IEC 42001** (AI Management System)  

### Legal Defensibility

✅ **Tamper-Evident** - SHA-256 audit hashes  
✅ **Reproducible** - Model fingerprints  
✅ **Statistically Significant** - p-values, confidence intervals  
✅ **Documented** - Exportable reports (JSON, Text, PDF)  

### Cost-Benefit Analysis

#### Without NoBias
- **Risk**: Legal liability (millions in settlements)
- **Cost**: Reactive fixes after deployment
- **Time**: Months to remediate
- **Reputation**: Public bias scandals

#### With NoBias
- **Risk**: Proactive detection and mitigation
- **Cost**: $0-$0.27 per audit
- **Time**: Minutes to hours
- **Reputation**: Demonstrable fairness commitment

### ROI Calculation

**Example: Hiring Platform**

**Without NoBias**:
- Biased model deployed
- EEOC investigation triggered
- Legal settlement: $2M
- Reputation damage: Priceless

**With NoBias**:
- Dataset audit: $0 (2 sec)
- Model audit: $0 (30 sec)
- Agent audit: $0.17 (5 min)
- **Total cost: $0.17**
- **Savings: $2M - $0.17 = $1,999,999.83**

### Quick Start Commands

#### Dataset Audit
```python
from nobias import audit_dataset

report = audit_dataset(
    data='data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)
```

#### Model Audit
```python
from nobias.model_audit import audit_model

report = audit_model(
    model='model.pkl',
    test_data='test.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)
```

#### Agent Audit
```python
from agent_audit import audit_agent

report = await audit_agent(
    system_prompt="You are a hiring assistant...",
    seed_case="Evaluate: Name: Jordan...",
    api_key="gsk_...",
    mode='standard'
)
```

### Next Steps

1. **Install NoBias**
   ```bash
   pip install pandas numpy scipy scikit-learn
   ```

2. **Run Your First Audit**
   - Start with Dataset Audit (fastest, cheapest)
   - Then Model Audit (if you have a trained model)
   - Finally Agent Audit (if you have an LLM agent)

3. **Review Findings**
   - Check overall severity
   - Review critical findings
   - Check EEOC compliance

4. **Apply Remediations**
   - Follow action priority list
   - Start with quick wins (no retraining)
   - Re-audit after changes

5. **Integrate into Pipeline**
   - Add to CI/CD
   - Set up monitoring
   - Configure alerts

6. **Document Everything**
   - Export audit reports
   - Maintain audit trail
   - Prepare compliance documentation

### Resources

#### Documentation
- Agent Audit: `docs/AGENT_AUDIT_COMPLETE_GUIDE.md`
- Model Audit: `docs/niru_MODEL_AUDIT_IMPLEMENTATION_GUIDE.md`
- Dataset Audit: `docs/niru_DATASET_AUDIT_IMPLEMENTATION_GUIDE.md`
- Actionable Insights: `docs/ACTIONABLE_INSIGHTS_GUIDE.md`

#### Examples
- Agent Audit: `examples/full_audit_example.py`
- Model Audit: `examples/model_audit_example.py`
- Dataset Audit: `examples/dataset_audit_example.py`
- Actionable Insights: `examples/actionable_insights_example.py`

#### API Reference
- Agent Audit: `library/agent_audit/API_REFERENCE.md`
- Model Audit: `library/model_audit/README.md`
- Dataset Audit: `library/dataset_audit/README.md`

### Contact & Support

For questions, issues, or contributions:
- GitHub: [Your Repository]
- Documentation: `docs/`
- Examples: `examples/`

---

## Appendix: Presentation Slides Outline

### Slide 1: Title
**NoBias Platform**  
Comprehensive AI Fairness Testing  
Across Agents, Models, and Datasets

### Slide 2: The Problem
- AI systems make high-stakes decisions
- Bias leads to discrimination
- Legal liability (EEOC, EU AI Act)
- Reputation damage

### Slide 3: The Solution
**NoBias Platform**
- Dataset Audit (preventive)
- Model Audit (validation)
- Agent Audit (monitoring)

### Slide 4: Platform Architecture
[Show three-tier diagram]
- Dataset → Model → Agent
- Shared compliance engine
- Actionable insights

### Slide 5: Dataset Audit
- 7 bias types detected
- 2-10 seconds
- $0 cost
- Prevents biased models

### Slide 6: Model Audit
- 8+ fairness metrics
- 15-60 seconds
- $0 cost
- Validates before deployment

### Slide 7: Agent Audit
- 4 bias types detected
- 2-30 minutes
- $0.03-$0.27 cost
- Monitors LLM decisions

### Slide 8: Key Metrics
[Show metric comparison table]
- CFR, MASD, DPD, DIR, etc.
- EEOC 80% rule
- Statistical significance

### Slide 9: Actionable Insights
- Plain English summaries
- Prioritized actions
- Simulated improvements
- Business-friendly

### Slide 10: Compliance
- EEOC 80% Rule ✅
- EU AI Act ✅
- NIST AI RMF ✅
- ISO/IEC 42001 ✅

### Slide 11: Real-World Use Cases
- Hiring platform: CFR 12.5% → 4.2%
- Lending: DIR 0.68 → 0.87
- Healthcare: FPR gap 0.15 → 0.06

### Slide 12: ROI
**Example: Hiring Platform**
- Cost: $0.17
- Savings: $2M (avoided settlement)
- ROI: 11,764,605%

### Slide 13: Integration
- CI/CD pipelines
- Monitoring & alerting
- Dashboard
- API endpoints

### Slide 14: Implementation Roadmap
- Week 1-2: Dataset audit & remediation
- Week 3-4: Model audit & mitigation
- Week 5-6: Agent audit & optimization
- Week 7-8: Integration & monitoring
- Week 9-10: Documentation & compliance

### Slide 15: Call to Action
**Get Started Today**
1. Install NoBias
2. Run your first audit
3. Review findings
4. Apply remediations
5. Integrate into pipeline

### Slide 16: Contact
- Documentation: `docs/`
- Examples: `examples/`
- Support: [Contact Info]

---

**Document Version**: 2.0  
**Last Updated**: 2026-04-28  
**Compliance**: EU AI Act, NIST AI RMF, ISO/IEC 42001, EEOC  
**Research Citations**: Mayilvaghanan et al. (2025), Bertrand & Mullainathan (2004), Huang & Fan (2025), Staab et al. (2025)

