"""
Nobias Library Diagnostic -- Run: python backend/diagnose.py
"""
import sys
print("=== NOBIAS LIBRARY DIAGNOSTIC ===\n")

# 1. Check real package imports
print("--- Checking real library packages ---")
ok = True
for pkg in ["dataset_audit", "model_audit", "agent_audit"]:
    try:
        mod = __import__(pkg)
        print(f"OK  {pkg} imported. Version: {getattr(mod, '__version__', 'unknown')}")
    except ImportError as e:
        print(f"FAIL {pkg}: {e}")
        ok = False

if not ok:
    print("\nRun: pip install unbiased==0.0.0")
    sys.exit(1)
print()

# 2. Check function signatures
print("--- Function signatures ---")
import inspect
from dataset_audit import audit_dataset
from model_audit import audit_model
from agent_audit import audit_agent
print(f"audit_dataset: {inspect.signature(audit_dataset)}")
print(f"audit_model:   {inspect.signature(audit_model)}")
print(f"audit_agent:   {inspect.signature(audit_agent)}")
print()

# 3. Run real dataset audit
print("--- Running REAL dataset audit ---")
try:
    import pandas as pd, numpy as np
    np.random.seed(42)
    n = 300
    df = pd.DataFrame({
        "gender": np.random.choice(["Male","Female"], n, p=[0.65,0.35]),
        "race":   np.random.choice(["White","Black","Hispanic"], n),
        "hired":  np.random.choice([0,1], n, p=[0.4,0.6]),
    })
    df.loc[df["gender"]=="Female","hired"] = np.random.choice([0,1],(df["gender"]=="Female").sum(),p=[0.65,0.35])
    report = audit_dataset(data=df, protected_attributes=["gender","race"], target_column="hired", positive_value=1)
    print(f"OK  overall_severity: {report.overall_severity}")
    print(f"    findings: {len(report.findings)}")
    print(f"    label_rates keys: {list(report.label_rates.keys())}")
    print(f"    report type: {type(report).__name__}")
except Exception as e:
    print(f"FAIL dataset audit: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
print()

# 4. Run real model audit
print("--- Running REAL model audit ---")
try:
    import pandas as pd, numpy as np, joblib, tempfile, os
    from sklearn.ensemble import RandomForestClassifier
    np.random.seed(42)
    n = 200
    X = pd.DataFrame({"exp": np.random.randint(0,20,n), "gpa": np.random.uniform(2.5,4.0,n)})
    y = np.random.choice([0,1], n, p=[0.4,0.6])
    model = RandomForestClassifier(n_estimators=5, random_state=42).fit(X, y)
    with tempfile.NamedTemporaryFile(suffix=".pkl", delete=False) as f:
        joblib.dump(model, f.name); mp = f.name
    test = X.copy(); test["gender"] = np.random.choice(["Male","Female"],n); test["hired"] = y
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False, mode="w") as f:
        test.to_csv(f.name, index=False); dp = f.name
    report = audit_model(model=mp, test_data=dp, protected_attributes=["gender"], target_column="hired", positive_value=1)
    print(f"OK  overall_severity: {report.overall_severity}")
    print(f"    findings: {len(report.findings)}")
    print(f"    scorecard keys: {len(report.scorecard)}")
    print(f"    counterfactual: {report.counterfactual_result}")
    print(f"    report type: {type(report).__name__}")
    os.unlink(mp); os.unlink(dp)
except ImportError as e:
    print(f"WARN sklearn not installed: {e}")
except Exception as e:
    print(f"FAIL model audit: {type(e).__name__}: {e}")
    import traceback; traceback.print_exc()
print()

# 5. Health check
print("--- Backend health check ---")
try:
    import urllib.request
    with urllib.request.urlopen("http://127.0.0.1:8000/api/health", timeout=3) as r:
        print(f"OK  {r.read().decode()}")
except Exception as e:
    print(f"WARN backend not running: {e}")
    print("    Start with: python backend/main.py")

print("\n=== DIAGNOSTIC COMPLETE ===")
