# Output Standardization Plan

## Analysis Summary

### Agent Audit (Reference Implementation)
- **Main API**: `audit_agent()` function and `AgentAuditor` class
- **Output**: `AgentAuditReport` dataclass with:
  - `audit_id`, `mode`, `total_calls`, `duration_seconds`
  - `overall_severity`, `overall_cfr`, `benchmark_range`
  - `findings` (list of `AgentFinding`)
  - `persona_results` (list of `PersonaResult`)
  - `interpretation`, `prompt_suggestions`
  - `stress_test_results`, `caffe_test_suite`
  - **FairSight Compliance**: `audit_integrity`, `model_fingerprint`, `eeoc_air`, `stability`, `confidence_intervals`, `bonferroni_correction`
  - `timestamp`
- **Export Methods**: `to_dict()`, `export(path, fmt)`
- **Report Formats**: JSON, CAFFE, PDF

### Model Audit (Needs Standardization)
- **Main API**: `audit_model()` function
- **Output**: `ModelAuditReport` dataclass with:
  - `model_name`, `model_type`, `test_sample_count`, `protected_attributes`
  - `overall_severity`
  - `scorecard`, `counterfactual_result`
  - `findings`, `mitigation_options`
  - `intersectional_findings`, `shap_analysis`
  - `baseline_metrics`, `per_group_metrics`
- **Export Methods**: `to_dict()`, `export(output_path, format)`
- **Missing**: FairSight compliance fields, audit_id, timestamp, duration tracking

### Dataset Audit (Needs Major Fixes)
- **Main API**: `audit_dataset()` function
- **Output**: `DatasetAuditReport` - **MISSING CLASS DEFINITION**
- **Current Structure** (from usage):
  - `dataset_name`, `row_count`, `column_count`
  - `overall_severity`
  - `findings`, `representation`, `label_rates`
  - `proxy_features`, `missing_data_matrix`
  - `intersectional_disparities`, `kl_divergences`
  - `remediation_suggestions`, `logs`
- **Missing**: Proper dataclass, export methods, FairSight compliance

## Standardization Goals

### 1. Uniform Report Structure
All three audit types should have:
- **Metadata**: `audit_id`, `timestamp`, `duration_seconds`, `mode`
- **Configuration**: What was audited and how
- **Severity**: `overall_severity` with consistent levels (CRITICAL, MODERATE, LOW, CLEAR)
- **Findings**: List of structured findings with severity, evidence, affected groups
- **Recommendations**: Actionable mitigation/remediation suggestions
- **Compliance**: FairSight fields for legal defensibility
- **Export Methods**: `to_dict()`, `export(path, fmt)` supporting JSON, text, PDF

### 2. Consistent Severity Classification
- **CRITICAL**: Severe bias requiring immediate action
- **MODERATE**: Significant bias requiring attention
- **LOW**: Minor bias worth monitoring
- **CLEAR**: No significant bias detected

### 3. Unified Export Interface
```python
report.export("output.json", format="json")
report.export("output.txt", format="text")
report.export("output.pdf", format="pdf")
```

## Implementation Tasks

### Task 1: Create DatasetAuditReport Dataclass
- Define complete dataclass in `dataset_audit/models.py`
- Add FairSight compliance fields
- Add `to_dict()` and `export()` methods
- Add `timestamp`, `audit_id`, `duration_seconds`

### Task 2: Standardize ModelAuditReport
- Add missing FairSight compliance fields
- Add `audit_id`, `timestamp`, `duration_seconds`
- Ensure export methods match agent_audit pattern
- Add mode parameter

### Task 3: Update API Functions
- Track execution time in all audit functions
- Generate unique audit_ids
- Add timestamps
- Compute FairSight compliance metrics

### Task 4: Clean Up Unnecessary Files
Remove test files and temporary outputs from root:
- `biased_model_audit.json/txt`
- `unbiased_model_audit.json/txt`
- `my_test_report.json/txt`
- `simple_audit.json`
- `test_audit_report.json/txt`
- `test_data_*.csv` files
- `*.pkl` model files
- Various test scripts in root
- Redundant documentation files

### Task 5: Consolidate Documentation
- Keep essential docs in `docs/` folder
- Remove redundant status/summary files from root
- Create single source of truth for each component

## Files to Remove

### Test Data & Models (Root Level)
- `biased_model.pkl`, `unbiased_model.pkl`
- `test_data_biased.csv`, `test_data_unbiased.csv`, `test_data_temp.csv`
- `biased_model_audit.json/txt`, `unbiased_model_audit.json/txt`
- `my_test_report.json/txt`, `simple_audit.json`, `test_audit_report.json/txt`

### Test Scripts (Root Level - Move to tests/)
- `test_adult.py`, `test_model_audit.py`, `test_model_audit_comprehensive.py`
- `test_my_model.py`, `test_simple.py`
- `test_new_dataset_reports.py`, `test_new_model_reports.py`

### Redundant Documentation (Root Level)
- `ADVANCED_REPORTS_COMPLETE.md`
- `IMPLEMENTATION_COMPLETE.md`, `IMPLEMENTATION_STATUS.md`
- `MODEL_AUDIT_NEW_REPORTS_SUMMARY.md`
- `NIRU_COMPLETE_SUMMARY.md`, `NIRU_SUMMARY.md`
- `PROJECT_STATUS.md`, `PULL_MERGE_SUMMARY.md`, `SECOND_PULL_SUMMARY.md`
- `PUSH_NOW.md`, `PUSH_COMMANDS.txt`
- `REPORT_COMPARISON.md`, `QUICK_START_NEW_REPORTS.md`
- `MERGE_GUIDE.md`, `COMMIT_GUIDE.md`

### Keep These
- `README.md` - Main project documentation
- `STRUCTURE.md` - Project structure
- `TEAM_GUIDE.md` - Team collaboration guide
- `TEST_GUIDE.md` - Testing instructions
- `HOW_TO_TEST_MODEL_AUDIT.md` - Specific testing guide
- `requirements.txt`, `setup.py` - Package configuration
- `.gitignore` - Git configuration
