# How to Test Model Audit

## Quick Test (Already Done)

We've verified the model_audit module works correctly:

```bash
cd Nobias
python test_model_audit_comprehensive.py
```

**Results:**
- ✅ **Biased Model**: Correctly detected with 4 CRITICAL and 9 MODERATE findings
- ✅ **Unbiased Model**: Passed with 0 CRITICAL findings (75% metrics passed)
- ✅ **Comparison**: Biased model had 30% pass rate vs 75% for unbiased model

## Test Your Own Model

### Step 1: Prepare Your Files

You need two files:
1. **Model file** (.pkl or .joblib) - your trained model
2. **Test CSV** - your test data with:
   - All features the model needs
   - Protected attributes (gender, race, age, etc.)
   - Target column (the outcome you're predicting)

### Step 2: Run the Audit

```python
from library.model_audit import audit_model

report = audit_model(
    model='your_model.pkl',                    # Path to your model
    test_data='your_test_data.csv',            # Path to your test CSV
    protected_attributes=['gender', 'race'],   # Your protected attributes
    target_column='hired',                     # Your target column name
    positive_value=1,                          # What value means "positive"
)

# View results
print(report)
```

### Step 3: Understand the Results

The audit will tell you:

1. **Overall Severity**: CRITICAL / MODERATE / LOW / CLEAR
2. **Flip Rate**: % of predictions that change when protected attributes are flipped
3. **Fairness Metrics**: 
   - Demographic Parity (approval rate differences)
   - Disparate Impact (80% rule)
   - Equalized Odds (error rate differences)
   - Predictive Parity (precision differences)
   - Calibration (confidence calibration)
4. **Findings**: Specific violations with evidence
5. **Mitigation Options**: How to fix the issues

### Step 4: Export Reports

```python
# JSON format (for programmatic use)
report.export('audit_report.json', format='json')

# Text format (human-readable)
report.export('audit_report.txt', format='text')
```

## What Makes a Model "Good"?

### ✅ Good Model (Fair)
- **Overall Severity**: CLEAR or LOW
- **Flip Rate**: < 2%
- **Metrics Passed**: > 80%
- **Critical Findings**: 0
- **Demographic Parity**: < 0.10 difference
- **Disparate Impact**: > 0.80 ratio

### ⚠️ Moderate Model (Needs Review)
- **Overall Severity**: MODERATE
- **Flip Rate**: 2-5%
- **Metrics Passed**: 50-80%
- **Critical Findings**: 0-2
- **Some fairness violations** but not severe

### ❌ Bad Model (Biased)
- **Overall Severity**: CRITICAL
- **Flip Rate**: > 5%
- **Metrics Passed**: < 50%
- **Critical Findings**: > 2
- **Demographic Parity**: > 0.20 difference
- **Disparate Impact**: < 0.60 ratio

## Example: Hiring Model

### Scenario
You have a hiring model that predicts if a candidate should be hired.

**Files:**
- `hiring_model.pkl` - your trained model
- `test_candidates.csv` - test data with columns:
  - `years_experience`, `education_level`, `interview_score` (features)
  - `gender`, `race` (protected attributes)
  - `hired` (target: 1 = hired, 0 = not hired)

**Code:**
```python
from library.model_audit import audit_model

report = audit_model(
    model='hiring_model.pkl',
    test_data='test_candidates.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1,  # 1 means "hired"
)

print(f"Severity: {report.overall_severity.value}")
print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")

# Check critical findings
for finding in report.findings:
    if finding.severity.value == "CRITICAL":
        print(f"\nCRITICAL: {finding.title}")
        print(f"  {finding.description}")
        print(f"  Affected: {', '.join(finding.affected_groups)}")

# Export
report.export('hiring_audit.json')
```

## Interpreting Specific Metrics

### 1. Demographic Parity Difference (DPD)
**What it measures**: Difference in approval rates between groups

```
DPD = approval_rate(unprivileged) - approval_rate(privileged)
```

**Example:**
- Male approval rate: 60%
- Female approval rate: 40%
- DPD = 40% - 60% = -0.20 (FAIL - women 20% less likely to be approved)

**Threshold**: |DPD| < 0.10 (10%)

### 2. Disparate Impact Ratio (DIR)
**What it measures**: Ratio of approval rates (EEOC 80% rule)

```
DIR = approval_rate(unprivileged) / approval_rate(privileged)
```

**Example:**
- Male approval rate: 60%
- Female approval rate: 45%
- DIR = 45% / 60% = 0.75 (FAIL - below 80% threshold)

**Threshold**: DIR >= 0.80

### 3. Equalized Odds
**What it measures**: Difference in error rates (FPR and FNR) between groups

**Example:**
- Male FPR: 10%, Female FPR: 25%
- Difference: 15% (FAIL - women have higher false positive rate)

**Threshold**: < 0.10 (10%)

### 4. Counterfactual Flip Rate
**What it measures**: How often predictions change when you flip protected attributes

**Example:**
- Test 100 candidates
- Change "Male" to "Female" (keeping everything else same)
- 8 predictions flip from "hired" to "not hired"
- Flip rate: 8% (MODERATE concern)

**Threshold**: 
- < 2%: CLEAR
- 2-5%: MODERATE
- > 5%: CRITICAL

## Common Issues and Solutions

### Issue 1: Model trained with protected attributes
**Problem**: Model directly uses gender/race as features
**Solution**: Retrain without protected attributes

### Issue 2: Proxy features
**Problem**: ZIP code, name, etc. correlate with protected attributes
**Solution**: Remove or transform proxy features

### Issue 3: Biased training data
**Problem**: Historical data reflects past discrimination
**Solution**: Use sample reweighting or threshold adjustment

### Issue 4: High flip rate
**Problem**: Model is sensitive to protected attributes
**Solution**: Retrain with fairness constraints

## Testing Checklist

Before deploying your model:

- [ ] Run model audit on test data
- [ ] Check overall severity (should be CLEAR or LOW)
- [ ] Review all CRITICAL findings
- [ ] Verify flip rate < 2%
- [ ] Check demographic parity < 10%
- [ ] Verify disparate impact > 80%
- [ ] Review intersectional findings
- [ ] Document any remaining issues
- [ ] Implement recommended mitigations
- [ ] Re-audit after fixes

## Files Generated

After running the comprehensive test, you'll have:

```
biased_model.pkl              # Example biased model
unbiased_model.pkl            # Example fair model
test_data_biased.csv          # Test data for biased model
test_data_unbiased.csv        # Test data for unbiased model
biased_model_audit.json       # Detailed audit report (JSON)
biased_model_audit.txt        # Human-readable report (text)
unbiased_model_audit.json     # Detailed audit report (JSON)
unbiased_model_audit.txt      # Human-readable report (text)
```

**Review these files** to see what a biased vs fair model looks like!

## Next Steps

1. **Review the example reports**: Open `biased_model_audit.txt` and `unbiased_model_audit.txt`
2. **Test your own model**: Follow the template above
3. **Integrate with your app**: Use the audit_model() function in your backend
4. **Set up monitoring**: Re-audit models periodically

## Questions?

- See `library/model_audit/README.md` for detailed API documentation
- See `library/model_audit/IMPLEMENTATION_STATUS.md` for technical details
- See `examples/model_audit_example.py` for more examples
