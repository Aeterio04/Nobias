# Model Audit Module — Development Plan

> **Module purpose**: Accept a trained ML model + labelled test set + protected attribute labels →
> run counterfactual flip tests, compute group fairness metrics, generate SHAP explainability →
> return a fairness scorecard with severity-graded findings + mitigation strategies.

---

## 1. Public API Surface

```python
from nobias.model_audit import audit_model, ModelAuditConfig, ModelAuditReport

report: ModelAuditReport = audit_model(
    model="path/to/model.pkl",           # or sklearn/xgb/lightgbm estimator
    test_data="path/to/test.csv",        # or pd.DataFrame
    protected_attributes=["gender", "race"],
    target_column="hired",
    positive_value=1,
    run_shap=True,
)

print(report.scorecard)                  # Dict of metric → pass/fail
print(report.counterfactual_flips)       # Specific "identical-except-for-X" examples
print(report.shap_summary)              # SHAP feature importance rankings
report.export("fairness_report.pdf")
```

---

## 2. Core Detection Pipeline (implement in this order)

### Phase 1 — Model & Data Loading
- [ ] Accept serialised models: pickle (.pkl), joblib (.joblib), ONNX (.onnx)
- [ ] Accept sklearn-compatible estimators directly (duck typing on .predict / .predict_proba)
- [ ] Load test dataset (CSV/DataFrame), validate feature alignment with model
- [ ] Auto-detect model type (classifier vs regressor, binary vs multiclass)
- [ ] Extract feature names from model or dataset columns

### Phase 2 — Baseline Predictions
- [ ] Run model.predict() on full test set
- [ ] If model has predict_proba(), capture confidence scores
- [ ] Compute baseline accuracy, precision, recall, F1 on full test set
- [ ] Compute per-group accuracy (accuracy for each demographic subgroup)

### Phase 3 — Counterfactual Flip Test
- [ ] For each sample in test set:
  - For each protected attribute:
    - Create counterfactual copies by swapping attribute to each other value
    - If model uses attribute directly: swap the feature value
    - If model doesn't use attribute: swap proxy features (ZIP, name encodings)
    - Run model.predict() on counterfactual
    - Record if decision flipped
- [ ] Compute Individual Fairness Flip Rate = (#flips / #total pairs)
- [ ] Flag flip rate > 5% as significant
- [ ] Store top-N most extreme counterfactual pairs as evidence examples
- [ ] For models with predict_proba: also compute Mean Absolute Score Difference (MASD)

### Phase 4 — Group Fairness Metrics (Scorecard)
- [ ] **Demographic Parity Difference**: approval_rate(unprivileged) - approval_rate(privileged)
  - Threshold: |DPD| > 0.10 → flag
- [ ] **Equalized Odds Difference**: max(|FPR_diff|, |FNR_diff|) across groups
  - Threshold: > 0.10 → flag
- [ ] **Disparate Impact Ratio**: approval_rate(min_group) / approval_rate(max_group)
  - Threshold: < 0.80 → flag (EEOC 80% rule)
- [ ] **Predictive Parity**: |PPV_privileged - PPV_unprivileged|
  - Threshold: > 0.05 → flag
- [ ] **Calibration Difference**: |P(Y=1 | score=s, A=0) - P(Y=1 | score=s, A=1)|
  - Bin scores into deciles, compare actual positive rates per group
  - Threshold: max bin diff > 0.05 → flag
- [ ] For each metric, compute per every pair of demographic groups

### Phase 5 — Intersectional Fairness
- [ ] Compute all Phase 4 metrics for 2-way attribute intersections
- [ ] Check for compounded bias (e.g., Black women worse than Black or women alone)
- [ ] Flag intersectional disparity > individual attribute disparity (superadditive bias)

### Phase 6 — SHAP Explainability
- [ ] Use shap.TreeExplainer (tree models) or shap.KernelExplainer (any model)
- [ ] Compute SHAP values on full test set (or sampled subset for large sets)
- [ ] **Global summary**: rank features by mean |SHAP value|
- [ ] **Proxy detection via SHAP**: for each feature in top-10 SHAP:
  - Compute correlation with each protected attribute
  - Flag if corr > 0.3 AND feature is top-5 SHAP importance
- [ ] **Per-group SHAP comparison**: compute feature importance separately per demographic
  - Flag features whose SHAP rank differs by > 3 positions across groups
  (model uses different reasoning for different demographics)
- [ ] Generate SHAP plots as PNG images:
  - Summary bee-swarm plot
  - Per-group bar chart comparison
  - Waterfall plot for individual examples (flipped counterfactual pairs)

---

## 3. Severity Classification

```
CRITICAL:  DPD > 0.20 and p < 0.01, OR DIR < 0.60, OR flip_rate > 15%
MODERATE:  DPD > 0.10 and p < 0.05, OR DIR < 0.80, OR flip_rate > 5%
LOW:       DPD > 0.05, OR flip_rate > 2%
CLEAR:     All metrics within thresholds
```

Reference: Chouldechova (2017) impossibility theorem — note in report when calibration
and equalized odds cannot both be satisfied simultaneously.

---

## 4. Mitigation Strategies

### Post-processing (no retraining)
- [ ] **Threshold adjustment per group**: Hardt et al. (2016) Equalized Odds Post-Processing
  - Find per-group thresholds that equalise FPR and FNR
  - Report accuracy cost of adjustment
  - Output adjusted thresholds as config JSON
- [ ] **Calibration recalibration**: Platt scaling per subgroup
  - Output recalibrated model or calibration lookup table

### Pre-processing (requires retraining)
- [ ] **Sample reweighting**: compute fairness-aware sample weights
  - Output weight column as CSV for retraining
- [ ] **Proxy feature removal**: rank proxy features by SHAP importance × correlation
  - Suggest removing highest-risk features
  - Output modified dataset without proxy columns

### In-processing (advanced)
- [ ] **Adversarial debiasing**: Zhang et al. (2018)
  - Train adversary to predict protected attribute from model's hidden representation
  - Penalise main model for encoding demographic info
  - Output debiased model as new .pkl file
  - Note: only feasible for neural net / PyTorch models in v1

---

## 5. Report Object Schema

```python
@dataclass
class ModelAuditReport:
    model_name: str
    model_type: str                            # "RandomForestClassifier", etc.
    test_sample_count: int
    overall_severity: str                      # CRITICAL | MODERATE | LOW | CLEAR
    
    scorecard: dict[str, MetricResult]         # metric_name → MetricResult
    counterfactual_flips: CounterfactualResult
    intersectional_findings: list[dict]
    shap_proxy_features: list[ProxyFeature]
    shap_group_divergence: dict                # feature → rank diff across groups
    findings: list[ModelFinding]
    mitigation_options: list[MitigationOption]
    
    def export(self, path: str): ...
    def to_dict(self) -> dict: ...
    def get_shap_plot(self, plot_type: str) -> bytes:  # returns PNG bytes
        ...
```

---

## 6. Dependencies

```
pandas >= 2.0          # data handling
numpy >= 1.24          # numerics
scipy >= 1.11          # statistical tests
scikit-learn           # model loading, metric computation, calibration
shap >= 0.43           # SHAP explainability
matplotlib >= 3.7      # SHAP plot rendering
joblib                 # model serialisation
xgboost                # optional: XGBoost model support
lightgbm               # optional: LightGBM model support
```

---

## 7. File Structure

```
model_audit/
├── __init__.py            # Public API: audit_model(), ModelAuditConfig
├── loading.py             # Model + dataset loading, type detection
├── baseline.py            # Baseline predictions, per-group accuracy
├── counterfactual.py      # Counterfactual flip test, MASD
├── fairness_metrics.py    # DPD, equalized odds, DIR, calibration
├── intersectional.py      # k-way intersection scans (shared with dataset_audit)
├── shap_analysis.py       # SHAP computation, proxy detection, plot generation
├── severity.py            # Severity classifier
├── mitigation.py          # Threshold adjustment, reweighting, adversarial debiasing
├── report.py              # ModelAuditReport, export (JSON/PDF/PNG)
└── models.py              # Dataclasses: ModelFinding, MetricResult, CounterfactualPair
```
