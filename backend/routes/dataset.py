from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse, FileResponse
import tempfile, os, json
import pandas as pd

router = APIRouter()

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "../samples/")

@router.post("/upload")
async def upload_dataset(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        if suffix not in ['.csv', '.xlsx', '.xls', '.parquet']:
            raise HTTPException(400, f"Unsupported file format: {suffix}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        if suffix == '.csv':
            df = pd.read_csv(tmp_path)
        elif suffix in ['.xlsx', '.xls']:
            df = pd.read_excel(tmp_path)
        elif suffix == '.parquet':
            df = pd.read_parquet(tmp_path)
        
        preview = df.head(5).fillna('').values.tolist()
        
        return {
            "tmp_path": tmp_path,
            "filename": file.filename,
            "row_count": len(df),
            "column_count": len(df.columns),
            "file_size_mb": round(len(content) / 1024 / 1024, 2),
            "columns": df.columns.tolist(),
            "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
            "preview_headers": df.columns.tolist(),
            "preview_rows": preview,
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
    positive_value: str = Form(...),
    audit_mode: str = Form("standard"),
):
    try:
        protected_attrs = json.loads(protected_attributes)
        pos_val = positive_value
        if positive_value.lower() in ['1', 'true', 'yes']:
            pos_val = 1 if positive_value == '1' else (True if positive_value.lower() == 'true' else 'Yes')
        
        try:
            from unbiased import audit_dataset
        except ImportError:
            # Fallback to mock implementation
            import sys
            sys.path.insert(0, os.path.dirname(__file__) + '/..')
            from unbiased_mock import audit_dataset
        
        report = audit_dataset(
            data=tmp_path,
            protected_attributes=protected_attrs,
            target_column=target_column,
            positive_value=pos_val,
        )
        
        from services.serializer import serialize_dataset_report
        result = serialize_dataset_report(report)
        
        from services.history import save_audit_to_history
        save_audit_to_history({
            "audit_type": "dataset",
            "audit_id": result["audit_id"],
            "name": result["dataset_name"],
            "severity": result["overall_severity"],
            "finding_count": result["finding_count"],
            "result": result,
        })
        
        return result
    except FileNotFoundError:
        raise HTTPException(400, "Uploaded file not found. Please re-upload your dataset.")
    except KeyError as e:
        raise HTTPException(400, f"Column not found: {e}. Check that column names match exactly (case-sensitive).")
    except Exception as e:
        raise HTTPException(500, f"Audit failed: {str(e)}")


@router.get("/samples")
def list_samples():
    """Returns available sample datasets"""
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
        {
            "id": "adult_census",
            "name": "Adult Census Income",
            "description": "Predicting income thresholds",
            "protected_attributes": ["gender", "race"],
            "target_column": "income",
            "positive_value": ">50K",
            "path": os.path.join(SAMPLES_DIR, "adult_census.csv"),
        },
        {
            "id": "german_credit",
            "name": "German Credit",
            "description": "Risk assessment and fairness",
            "protected_attributes": ["age", "sex"],
            "target_column": "credit_risk",
            "positive_value": 1,
            "path": os.path.join(SAMPLES_DIR, "german_credit.csv"),
        },
    ]
    return [s for s in samples if os.path.exists(s["path"])]


@router.post("/load-sample/{sample_id}")
def load_sample(sample_id: str):
    """Load a sample dataset — returns same shape as /upload"""
    # Sample definitions (even if files don't exist, generate synthetic data)
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
    
    # If sample file exists, use it
    if os.path.exists(sample_path):
        df = pd.read_csv(sample_path)
    else:
        # Generate synthetic sample data
        df = _generate_sample_data(sample_id, sample)
        os.makedirs(SAMPLES_DIR, exist_ok=True)
        df.to_csv(sample_path, index=False)
    
    return {
        "tmp_path": sample_path,
        "filename": f"{sample['name']}.csv",
        "row_count": len(df),
        "column_count": len(df.columns),
        "file_size_mb": round(os.path.getsize(sample_path) / 1024 / 1024, 2),
        "columns": df.columns.tolist(),
        "dtypes": {col: str(dtype) for col, dtype in df.dtypes.items()},
        "preview_headers": df.columns.tolist(),
        "preview_rows": df.head(5).fillna('').values.tolist(),
        "suggested_protected_attributes": sample["protected_attributes"],
        "suggested_target_column": sample["target_column"],
        "suggested_positive_value": sample["positive_value"],
    }


def _generate_sample_data(sample_id, sample):
    """Generate realistic synthetic sample data for demonstration"""
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
            "juv_fel_count": np.random.poisson(0.2, n),
            "juv_misd_count": np.random.poisson(0.3, n),
        })
        # Bias: African-American gets higher recid rate
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
            "capital_gain": (np.random.exponential(1000, n) * np.random.choice([0, 1], n, p=[0.7, 0.3])).astype(int),
            "occupation": np.random.choice(["Tech", "Sales", "Service", "Admin", "Craft", "Prof-specialty"], n),
        })
        # Bias: Males and Whites more likely to earn >50K
        base = np.random.uniform(0, 1, n)
        gender_bias = (df["gender"] == "Male").astype(float) * 0.12
        race_bias = (df["race"] == "White").astype(float) * 0.08
        df["income"] = np.where(
            (base + gender_bias + race_bias + df["education_num"] * 0.03) > 0.65,
            ">50K", "<=50K"
        )
        
    elif sample_id == "german_credit":
        df = pd.DataFrame({
            "age": np.random.randint(19, 75, n),
            "sex": np.random.choice(["male", "female"], n, p=[0.60, 0.40]),
            "job": np.random.choice([0, 1, 2, 3], n, p=[0.10, 0.25, 0.40, 0.25]),
            "housing": np.random.choice(["own", "rent", "free"], n, p=[0.55, 0.35, 0.10]),
            "credit_amount": np.random.lognormal(7.5, 0.8, n).astype(int),
            "duration": np.random.choice([6, 12, 18, 24, 36, 48], n),
            "purpose": np.random.choice(["car", "furniture", "education", "business", "other"], n),
        })
        # Bias: Younger people and females get lower credit scores
        base = np.random.uniform(0, 1, n)
        age_bias = ((df["age"] < 30).astype(float)) * 0.10
        sex_bias = (df["sex"] == "female").astype(float) * 0.08
        df["credit_risk"] = ((base - age_bias - sex_bias + df["job"] * 0.05) > 0.30).astype(int)
    
    else:
        df = pd.DataFrame({"x": range(n), "y": np.random.randn(n)})
    
    return df


@router.get("/export/{audit_id}")
def export_audit(audit_id: str, format: str = "json"):
    """Export an audit report as JSON or PDF"""
    from services.history import get_audit_by_id
    
    entry = get_audit_by_id(audit_id)
    if not entry:
        raise HTTPException(404, "Audit not found")
    
    result = entry["result"]
    
    if format == "json":
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            tmp_path = f.name
        return FileResponse(
            tmp_path,
            media_type="application/json",
            filename=f"nobias_dataset_audit_{audit_id}.json"
        )
    
    elif format == "pdf":
        raise HTTPException(400, "PDF export requires reportlab. Use JSON export for now.")
    
    raise HTTPException(400, f"Unknown format: {format}")
