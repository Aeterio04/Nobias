# NoBias Project Structure

## Your Work: Dataset Audit Module

**Location**: `/library/dataset_audit/`

**What to commit**:
```
library/dataset_audit/
├── __init__.py          # Main API
├── models.py            # Data classes
├── ingestion.py         # Load data
├── representation.py    # Group analysis
├── label_bias.py        # DIR/SPD
├── proxy_detection.py   # Correlations
├── missing_data.py      # Missingness
├── intersectional.py    # Group combos
├── divergence.py        # KL divergence
├── severity.py          # Classification
├── remediation.py       # Fixes
├── report.py            # Output
├── README.md            # Module overview
├── CHANGELOG.md         # Implementation notes
└── DEV_PLAN.md          # Original spec
```

## Project Root

```
Nobias/
├── library/
│   └── dataset_audit/   ← Your module
├── docs/                ← General documentation
├── test_simple.py       ← Test with synthetic data
├── test_adult.py        ← Test with UCI data
├── requirements.txt     ← Dependencies
├── setup.py             ← Package setup
└── README.md            ← Project overview
```

## Documentation

**Module docs** (in `/library/dataset_audit/`):
- README.md - Module overview
- CHANGELOG.md - Implementation notes
- DEV_PLAN.md - Original specification

**General docs** (in `/docs/`):
- dataset_audit_start_here.md - Setup guide
- how_to_run_dataset_audit.md - Usage guide
- dataset_audit_implementation.md - Technical details
- dataset_audit_complete.txt - Summary

## Git Workflow

```bash
# Work only in dataset_audit folder
cd Nobias/library/dataset_audit/

# Make changes to .py files

# When ready to commit:
git add library/dataset_audit/
git commit -m "dataset_audit: your changes"
git push
```

## What Gets Committed

✅ **Include**:
- All `.py` files in `library/dataset_audit/`
- Module docs (README.md, CHANGELOG.md, DEV_PLAN.md)
- Test scripts (test_simple.py, test_adult.py)
- requirements.txt

❌ **Exclude** (already in .gitignore):
- `__pycache__/`
- `*.pyc`
- `.pytest_cache/`
- `*.json` (audit outputs)

## Clean Structure

- **Code**: Only in `/library/dataset_audit/`
- **Module docs**: In `/library/dataset_audit/` (README, CHANGELOG, DEV_PLAN)
- **General docs**: In `/docs/`
- **Tests**: In root (test_simple.py, test_adult.py)
- **Config**: In root (requirements.txt, setup.py)
