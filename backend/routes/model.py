from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile, os, json
import pandas as pd

router = APIRouter()


def safe(obj, attr, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def safe_float(val, default=0.0):
    """Convert to float, replacing inf/nan with None to keep JSON valid."""
    try:
        if val is None:
            return default
        f = float(val)
        import math
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return default


def clean_float(val):
    """Like safe_float but returns None instead of default for missing values."""
    import math
    try:
        if val is None:
            return None
        f = float(val)
        if math.isnan(f) or math.isinf(f):
            return None
        return f
    except (TypeError, ValueError):
        return None


def serialize_severity(sev):
    if sev is None:
        return "UNKNOWN"
    if hasattr(sev, 'value'):
        return str(sev.value)
    if hasattr(sev, 'name'):
        return str(sev.name)
    return str(sev)


def serialize_finding(f):
    import math
    evidence = safe(f, 'evidence') or {}
    clean_evidence = {}
    for k, v in evidence.items():
        if isinstance(v, float):
            if math.isnan(v) or math.isinf(v):
                clean_evidence[k] = None
            else:
                clean_evidence[k] = round(v, 4)
        elif isinstance(v, int):
            clean_evidence[k] = v
        else:
            clean_evidence[k] = str(v) if v is not None else None
    return {
        "finding_id": safe(f, 'finding_id', ''),
        "severity": serialize_severity(safe(f, 'severity')),
        "category": safe(f, 'category', ''),
        "title": safe(f, 'title', ''),
        "description": safe(f, 'description', ''),
        "evidence": clean_evidence,
        "affected_groups": list(safe(f, 'affected_groups') or []),
    }


def serialize_metric(m):
    return {
        "metric_name": safe(m, 'metric_name', ''),
        "value": clean_float(safe(m, 'value')),
        "threshold": clean_float(safe(m, 'threshold')),
        "passed": bool(safe(m, 'passed', False)),
        "p_value": clean_float(safe(m, 'p_value')),
        "privileged_group": str(safe(m, 'privileged_group', '') or ''),
        "unprivileged_group": str(safe(m, 'unprivileged_group', '') or ''),
        "description": safe(m, 'description', ''),
    }


def serialize_mitigation(m):
    return {
        "strategy_name": safe(m, 'strategy_name', ''),
        "category": safe(m, 'category', ''),
        "description": safe(m, 'description', ''),
        "expected_impact": safe(m, 'expected_impact', ''),
        "implementation_complexity": safe(m, 'implementation_complexity', ''),
        "requires_retraining": bool(safe(m, 'requires_retraining', False)),
        "code_example": safe(m, 'code_example', ''),
    }


def serialize_model_report(report):
    findings = safe(report, 'findings') or []
    scorecard_raw = safe(report, 'scorecard') or {}
    mitigations = safe(report, 'mitigation_options') or []
    cf_result = safe(report, 'counterfactual_result')

    scorecard = {}
    for key, metric in scorecard_raw.items():
        try:
            scorecard[key] = serialize_metric(metric)
        except Exception as e:
            scorecard[key] = {"error": str(e), "raw": str(metric)}

    severity_str = serialize_severity(safe(report, 'overall_severity'))

    result = {
        "audit_id": safe(report, 'audit_id', 'unknown'),
        "model_name": safe(report, 'model_name', 'Unknown Model'),
        "overall_severity": severity_str,
        "finding_count": len(findings),
        "critical_count": len([f for f in findings if serialize_severity(safe(f, 'severity')) == 'CRITICAL']),
        "moderate_count": len([f for f in findings if serialize_severity(safe(f, 'severity')) == 'MODERATE']),
        "findings": [serialize_finding(f) for f in findings],
        "scorecard": scorecard,
        "mitigation_options": [serialize_mitigation(m) for m in mitigations],
        "counterfactual": None,
        "_library_report_type": str(type(report).__name__),
    }

    if cf_result is not None:
        result["counterfactual"] = {
            "flip_rate": safe_float(safe(cf_result, 'flip_rate')),
            "flip_rate_pct": f"{safe_float(safe(cf_result, 'flip_rate')) * 100:.1f}%",
            "flips_by_attribute": {
                k: int(v) for k, v in (safe(cf_result, 'flips_by_attribute') or {}).items()
            },
        }

    return result


@router.post("/upload-model")
async def upload_model_file(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        if suffix not in ['.pkl', '.joblib', '.onnx', '.h5']:
            raise HTTPException(400, f"Unsupported format '{suffix}'. Use .pkl, .joblib, .onnx, or .h5")

        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        model_type = "Unknown"
        if suffix in ['.pkl', '.joblib']:
            try:
                import joblib, pickle
                model = joblib.load(tmp_path) if suffix == '.joblib' else pickle.load(open(tmp_path, 'rb'))
                model_type = type(model).__name__
            except Exception:
                pass

        return {
            "success": True,
            "tmp_path": tmp_path,
            "filename": file.filename,
            "model_type": model_type,
            "file_size_mb": round(len(content) / 1024 / 1024, 2),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to load model file: {str(e)}")


@router.post("/upload-testdata")
async def upload_test_data(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        if suffix not in ['.csv', '.xlsx', '.xls']:
            raise HTTPException(400, "Test data must be CSV or XLSX")

        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        df = pd.read_csv(tmp_path) if suffix == '.csv' else pd.read_excel(tmp_path)

        return {
            "success": True,
            "tmp_path": tmp_path,
            "filename": file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": df.columns.tolist(),
            "preview_headers": df.columns.tolist(),
            "preview_rows": df.head(5).fillna('').values.tolist(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to read test data: {str(e)}")


@router.post("/check-compatibility")
async def check_feature_compatibility(model_path: str = Form(...), testdata_path: str = Form(...)):
    try:
        import pickle, joblib
        suffix = os.path.splitext(model_path)[1].lower()
        model = joblib.load(model_path) if suffix == '.joblib' else pickle.load(open(model_path, 'rb'))
        model_features = []
        if hasattr(model, 'feature_names_in_'):
            model_features = list(model.feature_names_in_)
        elif hasattr(model, 'feature_importances_'):
            model_features = [f"feature_{i}" for i in range(len(model.feature_importances_))]
        test_suffix = os.path.splitext(testdata_path)[1].lower()
        df = pd.read_csv(testdata_path) if test_suffix == '.csv' else pd.read_excel(testdata_path)
        test_cols = df.columns.tolist()
        if model_features:
            matched = [f for f in model_features if f in test_cols]
            missing = [f for f in model_features if f not in test_cols]
            return {
                "compatible": len(missing) == 0,
                "matching_features": len(matched),
                "total_features": len(model_features),
                "missing_from_test": missing,
                "extra_in_test": [c for c in test_cols if c not in model_features],
            }
        return {"compatible": True, "matching_features": len(test_cols), "total_features": len(test_cols), "note": "Cannot read feature names"}
    except Exception as e:
        return {"compatible": None, "error": str(e)}


@router.post("/run")
async def run_model_audit(
    model_path: str = Form(...),
    testdata_path: str = Form(...),
    protected_attributes: str = Form(...),
    target_column: str = Form(...),
    positive_value: str = Form("1"),
):
    if not os.path.exists(model_path):
        raise HTTPException(400, "Model file not found. Please re-upload your model.")
    if not os.path.exists(testdata_path):
        raise HTTPException(400, "Test data file not found. Please re-upload your test data.")

    try:
        protected_attrs = json.loads(protected_attributes)
    except json.JSONDecodeError:
        raise HTTPException(400, f"protected_attributes must be JSON array. Got: {protected_attributes}")

    if not protected_attrs:
        raise HTTPException(400, "Select at least one protected attribute.")

    pos_val: object = positive_value
    if positive_value == '1':
        pos_val = 1
    elif positive_value == '0':
        pos_val = 0

    # Validate test data columns before calling library
    try:
        test_suffix = os.path.splitext(testdata_path)[1].lower()
        df = pd.read_csv(testdata_path) if test_suffix == '.csv' else pd.read_excel(testdata_path)
    except Exception as e:
        raise HTTPException(400, f"Could not read test data: {str(e)}")

    if target_column not in df.columns:
        raise HTTPException(400,
            f"Target column '{target_column}' not found in test data. "
            f"Available columns: {df.columns.tolist()}"
        )

    missing_attrs = [a for a in protected_attrs if a not in df.columns]
    if missing_attrs:
        raise HTTPException(400,
            f"Protected attribute(s) {missing_attrs} not found in test data. "
            f"Available columns: {df.columns.tolist()}"
        )

    # Validate target column is numeric (model predicts 0/1, target must match)
    target_vals = df[target_column].dropna().unique().tolist()
    target_dtype = df[target_column].dtype
    if not pd.api.types.is_numeric_dtype(target_dtype):
        raise HTTPException(400,
            f"Target column '{target_column}' contains non-numeric values: {target_vals[:5]}. "
            f"The model predicts numeric labels (0/1). "
            f"Please select a numeric column as the target, or encode your labels to 0/1 before uploading."
        )

    try:
        from model_audit import audit_model
    except ImportError:
        raise HTTPException(503, "model_audit library not installed. Run: pip install unbiased==0.0.0")

    try:
        report = audit_model(
            model=model_path,
            test_data=testdata_path,
            protected_attributes=protected_attrs,
            target_column=target_column,
            positive_value=pos_val,
        )
    except FileNotFoundError as e:
        raise HTTPException(400, f"File not found: {str(e)}")
    except KeyError as e:
        raise HTTPException(400, f"Column {e} not found in test data. Make sure protected attributes and target column exist in your CSV.")
    except TypeError as e:
        err = str(e)
        if "y_true" in err and "y_pred" in err:
            raise HTTPException(400,
                f"Label type mismatch: your target column contains values the model cannot predict. "
                f"Make sure the target column contains the same numeric labels (0/1) that the model was trained on. "
                f"Detail: {err}"
            )
        raise HTTPException(500, f"Library error in audit_model(): TypeError: {err}")
    except Exception as e:
        raise HTTPException(500, f"Library error in audit_model(): {type(e).__name__}: {str(e)}")

    result = serialize_model_report(report)

    from routes.dataset import _save_to_history
    _save_to_history("model", result)

    return result


@router.get("/report-structure")
def get_model_report_structure():
    """Runs a minimal model audit with synthetic data and returns the raw report structure."""
    try:
        import numpy as np
        import joblib, tempfile
        from sklearn.ensemble import RandomForestClassifier
        from model_audit import audit_model

        np.random.seed(0)
        n = 100
        X = pd.DataFrame({
            'feature1': np.random.randn(n),
            'feature2': np.random.randn(n),
        })
        y = np.random.choice([0, 1], n)
        model = RandomForestClassifier(n_estimators=5, random_state=0).fit(X, y)

        with tempfile.NamedTemporaryFile(suffix='.pkl', delete=False) as f:
            joblib.dump(model, f.name)
            m_path = f.name

        test = X.copy()
        test['gender'] = np.random.choice(['Male', 'Female'], n)
        test['outcome'] = y

        with tempfile.NamedTemporaryFile(suffix='.csv', delete=False, mode='w') as f:
            test.to_csv(f.name, index=False)
            d_path = f.name

        report = audit_model(
            model=m_path,
            test_data=d_path,
            protected_attributes=['gender'],
            target_column='outcome',
            positive_value=1,
        )

        structure = {}
        for attr in dir(report):
            if not attr.startswith('_'):
                try:
                    val = getattr(report, attr)
                    if not callable(val):
                        structure[attr] = str(type(val).__name__) + ": " + str(val)[:200]
                except Exception:
                    structure[attr] = "ERROR reading attribute"

        return {"report_type": str(type(report).__name__), "structure": structure}
    except Exception as e:
        import traceback
        return {"error": str(e), "traceback": traceback.format_exc()}
