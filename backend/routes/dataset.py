from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse
import tempfile, os, json
import pandas as pd

router = APIRouter()

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../samples/")


def safe(obj, attr, default=None):
    """Safely get attribute from object or dict."""
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def serialize_finding(f):
    return {
        "check": safe(f, 'check', ''),
        "severity": str(safe(f, 'severity', 'UNKNOWN')),
        "message": safe(f, 'message', ''),
        "metric": safe(f, 'metric', ''),
        "value": float(safe(f, 'value', 0) or 0),
        "threshold": float(safe(f, 'threshold', 0) or 0),
        "confidence": float(safe(f, 'confidence', 0) or 0) if safe(f, 'confidence') is not None else None,
    }


def serialize_proxy(p):
    return {
        "feature": safe(p, 'feature', ''),
        "protected": safe(p, 'protected', ''),
        "method": safe(p, 'method', ''),
        "score": float(safe(p, 'score', 0) or 0),
        "nmi": float(safe(p, 'nmi', 0) or 0) if safe(p, 'nmi') is not None else None,
    }


def serialize_remediation(r):
    return {
        "strategy": safe(r, 'strategy', '') or safe(r, 'strategy_name', ''),
        "estimated_dir_after": float(safe(r, 'estimated_dir_after', 0) or 0) if safe(r, 'estimated_dir_after') is not None else None,
        "estimated_spd_after": float(safe(r, 'estimated_spd_after', 0) or 0) if safe(r, 'estimated_spd_after') is not None else None,
        "description": safe(r, 'description', ''),
    }


def serialize_label_rates(label_rates_raw):
    """
    Normalize label_rates into { attr: { group: float, srd: float, dir: float } }.
    Handles real library shape: { attr: { group: { positive_rate, count, positive_count } } }
    and simple shape: { attr: { group: float } }
    """
    result = {}
    if not isinstance(label_rates_raw, dict):
        return result
    for attr, rates in label_rates_raw.items():
        if not isinstance(rates, dict):
            inner = safe(rates, 'rates', {})
            if isinstance(inner, dict):
                rates = inner
            else:
                continue
        flat = {}
        for group, val in rates.items():
            if group in ('srd', 'dir'):
                try:
                    flat[group] = float(val)
                except (TypeError, ValueError):
                    pass
            elif isinstance(val, dict):
                # Real library: { positive_rate, count, positive_count }
                pr = val.get('positive_rate')
                if pr is not None:
                    try:
                        flat[str(group)] = float(pr)
                    except (TypeError, ValueError):
                        pass
            else:
                try:
                    flat[str(group)] = float(val)
                except (TypeError, ValueError):
                    pass
        # Compute SRD and DIR if not already present
        group_rates = {k: v for k, v in flat.items() if k not in ('srd', 'dir')}
        if len(group_rates) >= 2 and 'srd' not in flat:
            vals = list(group_rates.values())
            max_r, min_r = max(vals), min(vals)
            flat['srd'] = round(max_r - min_r, 4)
            flat['dir'] = round(min_r / max_r, 4) if max_r > 0 else 0.0
        if flat:
            result[attr] = flat
    return result


def serialize_dataset_report(report):
    findings = safe(report, 'findings') or []
    proxies = safe(report, 'proxy_features') or []
    remeds = safe(report, 'remediation_suggestions') or []
    label_rates_raw = safe(report, 'label_rates') or {}

    severity = safe(report, 'overall_severity', 'UNKNOWN')
    if hasattr(severity, 'value'):
        severity = severity.value

    return {
        "audit_id": safe(report, 'audit_id', 'unknown'),
        "dataset_name": safe(report, 'dataset_name', 'unknown'),
        "row_count": int(safe(report, 'row_count', 0) or 0),
        "overall_severity": str(severity),
        "finding_count": len(findings),
        "critical_count": len([f for f in findings if str(safe(f, 'severity', '')).upper() == 'CRITICAL']),
        "moderate_count": len([f for f in findings if str(safe(f, 'severity', '')).upper() == 'MODERATE']),
        "low_count": len([f for f in findings if str(safe(f, 'severity', '')).upper() == 'LOW']),
        "clear_count": len([f for f in findings if str(safe(f, 'severity', '')).upper() == 'CLEAR']),
        "findings": [serialize_finding(f) for f in findings],
        "proxy_features": [serialize_proxy(p) for p in proxies],
        "label_rates": serialize_label_rates(label_rates_raw),
        "remediation_suggestions": [serialize_remediation(r) for r in remeds],
        "_library_report_type": str(type(report).__name__),
    }


@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        if suffix not in ['.csv', '.xlsx', '.xls', '.parquet']:
            raise HTTPException(400, f"Unsupported file format '{suffix}'. Use CSV, XLSX, or Parquet.")

        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        if suffix == '.csv':
            df = pd.read_csv(tmp_path)
        elif suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(tmp_path)
        else:
            df = pd.read_parquet(tmp_path)

        return {
            "success": True,
            "tmp_path": tmp_path,
            "filename": file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "file_size_mb": round(len(content) / 1024 / 1024, 2),
            "columns": df.columns.tolist(),
            "preview_headers": df.columns.tolist(),
            "preview_rows": df.head(5).fillna('').values.tolist(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to read file: {str(e)}")


@router.post("/run")
async def run_dataset_audit(
    tmp_path: str = Form(...),
    protected_attributes: str = Form(...),
    target_column: str = Form(...),
    positive_value: str = Form("1"),
    audit_mode: str = Form("standard"),
):
    # Parse inputs
    try:
        protected_attrs = json.loads(protected_attributes)
    except json.JSONDecodeError:
        raise HTTPException(400, f"protected_attributes must be a JSON array. Got: {protected_attributes}")

    if not protected_attrs:
        raise HTTPException(400, "Please select at least one protected attribute.")
    if not target_column:
        raise HTTPException(400, "Please select a target column.")

    # Verify file exists first
    if not os.path.exists(tmp_path):
        raise HTTPException(400, "Uploaded file not found. Please re-upload your dataset.")

    # Load the dataframe to validate inputs before calling the library
    try:
        suffix = os.path.splitext(tmp_path)[1].lower()
        if suffix == '.csv':
            df = pd.read_csv(tmp_path)
        elif suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(tmp_path)
        else:
            df = pd.read_parquet(tmp_path)
    except Exception as e:
        raise HTTPException(400, f"Could not read uploaded file: {str(e)}")

    # Validate target column exists
    if target_column not in df.columns:
        raise HTTPException(400, f"Target column '{target_column}' not found. Available columns: {df.columns.tolist()}")

    # Validate protected attributes exist
    missing = [a for a in protected_attrs if a not in df.columns]
    if missing:
        raise HTTPException(400, f"Protected attribute(s) not found in dataset: {missing}. Available columns: {df.columns.tolist()}")

    # Auto-detect positive_value type — try to match actual values in the column
    col_values = df[target_column].dropna().unique().tolist()
    col_values_str = [str(v) for v in col_values]

    pos_val: object = positive_value
    # Try exact match first
    if positive_value in col_values_str:
        # Find the original typed value
        for v in col_values:
            if str(v) == positive_value:
                pos_val = v
                break
    elif positive_value == '1' and 1 in col_values:
        pos_val = 1
    elif positive_value == '0' and 0 in col_values:
        pos_val = 0
    elif positive_value.lower() == 'true':
        pos_val = True
    elif positive_value.lower() in ['yes', 'y']:
        pos_val = 'Yes'
    else:
        # Try numeric conversion
        try:
            pos_val = int(positive_value)
        except ValueError:
            try:
                pos_val = float(positive_value)
            except ValueError:
                pos_val = positive_value

    # Validate that positive_value actually exists in the column
    if pos_val not in col_values:
        raise HTTPException(400,
            f"Positive outcome value '{positive_value}' not found in column '{target_column}'. "
            f"Actual values in that column: {col_values[:10]}. "
            f"Please enter one of these exact values as the Positive Outcome."
        )

    # Validate the target column has at least 2 unique values
    if len(col_values) < 2:
        raise HTTPException(400,
            f"Target column '{target_column}' only has {len(col_values)} unique value(s): {col_values}. "
            f"It must have at least 2 distinct values (e.g. 0 and 1, or Yes and No)."
        )

    # Import the real library
    try:
        from dataset_audit import audit_dataset
    except ImportError:
        raise HTTPException(503, "dataset_audit library not installed. Run: pip install unbiased==0.0.0")

    # Call the library
    try:
        report = audit_dataset(
            data=tmp_path,
            protected_attributes=protected_attrs,
            target_column=target_column,
            positive_value=pos_val,
        )
    except KeyError as e:
        raise HTTPException(400, f"Column not found: {e}. Check that column names are spelled exactly right (case-sensitive).")
    except ValueError as e:
        raise HTTPException(400, f"Invalid value: {str(e)}")
    except Exception as e:
        raise HTTPException(500, f"Library error in audit_dataset(): {type(e).__name__}: {str(e)}")

    # Serialize
    result = serialize_dataset_report(report)

    # Save to history
    _save_to_history("dataset", result)

    return result


def _save_to_history(audit_type: str, result: dict):
    from datetime import datetime
    import json as _json

    history_path = os.path.join(os.path.dirname(__file__), "../data/audit_history.json")
    os.makedirs(os.path.dirname(history_path), exist_ok=True)

    history = []
    if os.path.exists(history_path):
        try:
            with open(history_path) as f:
                history = _json.load(f)
        except Exception:
            history = []

    history.insert(0, {
        "audit_type": audit_type,
        "audit_id": result.get("audit_id", "unknown"),
        "name": result.get("dataset_name") or result.get("model_name") or f"{audit_type}_audit",
        "severity": result.get("overall_severity", "UNKNOWN"),
        "finding_count": result.get("finding_count", 0),
        "timestamp": datetime.now().isoformat(),
        "result": result,
    })

    with open(history_path, 'w') as f:
        _json.dump(history[:100], f, indent=2, default=str)


@router.get("/samples")
def list_samples():
    samples = [
        {
            "id": "compas",
            "name": "COMPAS Recidivism",
            "description": "Bias evaluation in criminal justice",
            "protected_attributes": ["race", "sex"],
            "target_column": "two_year_recid",
            "positive_value": 1,
            "path": os.path.join(SAMPLES_DIR, "compas.csv"),
        },
    ]
    return [s for s in samples if os.path.exists(s["path"])]


@router.post("/load-sample/{sample_id}")
def load_sample(sample_id: str):
    sample_defs = {
        "compas": {
            "name": "COMPAS Recidivism",
            "protected_attributes": ["race", "sex"],
            "target_column": "two_year_recid",
            "positive_value": 1,
        },
        "adult_census": {
            "name": "Adult Census Income",
            "protected_attributes": ["gender", "race"],
            "target_column": "income",
            "positive_value": ">50K",
        },
        "german_credit": {
            "name": "German Credit",
            "protected_attributes": ["age", "sex"],
            "target_column": "credit_risk",
            "positive_value": 1,
        },
    }
    if sample_id not in sample_defs:
        raise HTTPException(404, f"Sample '{sample_id}' not found")

    sample = sample_defs[sample_id]
    sample_path = os.path.join(SAMPLES_DIR, f"{sample_id}.csv")

    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
    else:
        df = _generate_sample_data(sample_id)
        os.makedirs(SAMPLES_DIR, exist_ok=True)
        df.to_csv(sample_path, index=False)

    return {
        "tmp_path": sample_path,
        "filename": f"{sample['name']}.csv",
        "row_count": len(df),
        "column_count": len(df.columns),
        "file_size_mb": round(os.path.getsize(sample_path) / 1024 / 1024, 2),
        "columns": df.columns.tolist(),
        "preview_headers": df.columns.tolist(),
        "preview_rows": df.head(5).fillna('').values.tolist(),
        "suggested_protected_attributes": sample["protected_attributes"],
        "suggested_target_column": sample["target_column"],
        "suggested_positive_value": str(sample["positive_value"]),
    }


def _generate_sample_data(sample_id: str) -> pd.DataFrame:
    import numpy as np
    np.random.seed(42)
    n = 1000

    if sample_id == "compas":
        df = pd.DataFrame({
            "race": np.random.choice(["African-American", "Caucasian", "Hispanic", "Other"], n, p=[0.35, 0.40, 0.15, 0.10]),
            "sex": np.random.choice(["Male", "Female"], n, p=[0.75, 0.25]),
            "age": np.random.randint(18, 65, n),
            "priors_count": np.random.poisson(3, n),
            "charge_degree": np.random.choice(["F", "M"], n, p=[0.4, 0.6]),
        })
        base = np.random.uniform(0, 1, n)
        race_bias = (df["race"] == "African-American").astype(float) * 0.15
        df["two_year_recid"] = ((base + race_bias + df["priors_count"] * 0.05) > 0.55).astype(int)
    elif sample_id == "adult_census":
        df = pd.DataFrame({
            "age": np.random.randint(18, 70, n),
            "gender": np.random.choice(["Male", "Female"], n, p=[0.67, 0.33]),
            "race": np.random.choice(["White", "Black", "Asian-Pac-Islander", "Other"], n, p=[0.6, 0.2, 0.1, 0.1]),
            "education_num": np.random.randint(1, 16, n),
            "hours_per_week": np.random.normal(40, 12, n).astype(int).clip(10, 80),
        })
        base = np.random.uniform(0, 1, n)
        gender_bias = (df["gender"] == "Male").astype(float) * 0.12
        df["income"] = np.where((base + gender_bias + df["education_num"] * 0.03) > 0.65, ">50K", "<=50K")
    elif sample_id == "german_credit":
        df = pd.DataFrame({
            "age": np.random.randint(19, 75, n),
            "sex": np.random.choice(["male", "female"], n, p=[0.60, 0.40]),
            "job": np.random.choice([0, 1, 2, 3], n, p=[0.10, 0.25, 0.40, 0.25]),
            "credit_amount": np.random.lognormal(7.5, 0.8, n).astype(int),
            "duration": np.random.choice([6, 12, 18, 24, 36, 48], n),
        })
        base = np.random.uniform(0, 1, n)
        age_bias = ((df["age"] < 30).astype(float)) * 0.10
        sex_bias = (df["sex"] == "female").astype(float) * 0.08
        df["credit_risk"] = ((base - age_bias - sex_bias + df["job"] * 0.05) > 0.30).astype(int)
    else:
        df = pd.DataFrame({"x": range(n), "y": np.random.randn(n)})

    return df


@router.get("/export/{audit_id}")
def export_audit(audit_id: str, format: str = "json"):
    from services.history import get_audit_by_id
    entry = get_audit_by_id(audit_id)
    if not entry:
        raise HTTPException(404, "Audit not found")
    result = entry["result"]
    if format == "json":
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            tmp_path = f.name
        return FileResponse(tmp_path, media_type="application/json", filename=f"nobias_dataset_audit_{audit_id}.json")
    raise HTTPException(400, f"Unknown format: {format}")
