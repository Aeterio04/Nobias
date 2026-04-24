# Dataset Audit - Implementation Notes

## What This Module Does
Checks datasets for bias before model training. Detects 7 types of statistical bias and suggests fixes.

## Implementation

**12 Python files** implementing:
1. Data ingestion (CSV/Excel/Parquet)
2. Representation analysis
3. Label bias (DIR/SPD)
4. Proxy detection
5. Missing data analysis
6. Intersectional disparities
7. KL divergence
8. Severity classification
9. Remediation suggestions
10. Report generation

## Key Metrics

- **DIR** (Disparate Impact Ratio): < 0.80 fails EEOC 80% rule
- **SPD** (Statistical Parity Difference): < -0.10 is moderate bias
- **Confidence**: Based on sample size (30% to 100%)

## Severity Levels

- **CRITICAL**: DIR < 0.60 or SPD < -0.20
- **MODERATE**: DIR < 0.80 or SPD < -0.10
- **LOW**: DIR < 0.90 or SPD < -0.05
- **CLEAR**: No significant bias

## Dependencies

- pandas >= 2.0
- numpy >= 1.24
- scipy >= 1.11
- scikit-learn >= 1.3
- imbalanced-learn >= 0.11

## Changes from Original Spec

- Stricter thresholds (10% of majority, not total)
- Added confidence scoring
- Added `suggest_protected_columns()` helper
- JSON export only (no PDF yet)
- Logs list instead of print statements
