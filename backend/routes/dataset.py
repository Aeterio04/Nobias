from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile, os, json
import pandas as pd

router = APIRouter()

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
        raise HTTPException(400, "Uploaded file not found")
    except KeyError as e:
        raise HTTPException(400, f"Column not found: {e}")
    except Exception as e:
        raise HTTPException(500, f"Audit failed: {str(e)}")
