# How to Test Dataset Audit

## Quick Test (What You Just Did)

```bash
cd Nobias
python test_simple.py
```

This shows the full audit report in terminal.

## Step-by-Step Commands

### 1. Install Dependencies (First Time Only)
```bash
pip install pandas numpy scipy scikit-learn imbalanced-learn
```

### 2. Run Test
```bash
cd Nobias
python test_simple.py
```

### 3. Check Output Files
```bash
# View the JSON export
cat simple_audit.json

# Or on Windows
type simple_audit.json
```

## What You'll See

The terminal will show:
1. Dataset creation (1000 rows)
2. Suggested protected columns
3. Full audit report with:
   - Overall severity (CRITICAL/MODERATE/LOW/CLEAR)
   - All findings grouped by severity
   - Proxy features detected
   - Remediation suggestions
   - Representation summary
4. Actual hiring rates (for verification)

## Alternative: Test with Real Data

```bash
python test_adult.py
```

This downloads UCI Adult Income dataset and runs the audit.

## Quick Demo for Others

Just run:
```bash
cd Nobias
python test_simple.py
```

The output shows everything in the terminal - no need to open files!
