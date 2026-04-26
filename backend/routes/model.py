from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile, os, json
import pandas as pd

router = APIRouter()

@router.post("/upload-model")
async def upload_model_file(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        if suffix not in ['.pkl', '.joblib', '.onnx', '.h5']:
            raise HTTPException(400, f"Unsupported model format: {suffix}")
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        model_type = "Unknown"
        if suffix in ['.pkl', '.joblib']:
            try:
                import pickle, joblib
                model = joblib.load(tmp_path) if suffix == '.joblib' else pickle.load(open(tmp_path, 'rb'))
                model_type = type(model).__name__
            except:
                pass
        return {"model_path": tmp_path, "filename": file.filename, "model_type": model_type, "format": suffix}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to load model: {str(e)}")

@router.post("/upload-testdata")
async def upload_test_data(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        if suffix not in ['.csv', '.xlsx']:
            raise HTTPException(400, "Test data must be CSV or XLSX")
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        df = pd.read_csv(tmp_path) if suffix == '.csv' else pd.read_excel(tmp_path)
        return {
            "tmp_path": tmp_path,
            "filename": file.filename,
            "row_count": len(df),
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
        else:
            return {"compatible": True, "matching_features": len(test_cols), "total_features": len(test_cols), "note": "Cannot read feature names"}
    except Exception as e:
        return {"compatible": None, "error": str(e)}

@router.post("/run")
async def run_model_audit(
    model_path: str = Form(...),
    testdata_path: str = Form(...),
    protected_attributes: str = Form(...),
    target_column: str = Form(...),
    positive_value: str = Form(...),
):
    try:
        protected_attrs = json.loads(protected_attributes)
        pos_val = 1 if positive_value in ['1', '1.0'] else positive_value
        
        try:
            from unbiased import audit_model
        except ImportError:
            import sys
            sys.path.insert(0, os.path.dirname(__file__) + '/..')
            from unbiased_mock import audit_model
        
        report = audit_model(
            model_path=model_path,
            test_data=testdata_path,
            protected_attributes=protected_attrs,
            target_column=target_column,
            positive_value=pos_val,
        )
        
        from services.serializer import serialize_model_report
        result = serialize_model_report(report)
        
        from services.history import save_audit_to_history
        save_audit_to_history({
            "audit_type": "model",
            "audit_id": result["audit_id"],
            "name": result["model_name"],
            "severity": result["overall_severity"],
            "finding_count": len(result["findings"]),
            "result": result,
        })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        err = str(e)
        if "predict" in err.lower():
            raise HTTPException(400, "Model does not have a predict() method")
        elif "column" in err.lower() or "feature" in err.lower():
            raise HTTPException(400, f"Feature mismatch: {err}")
        else:
            raise HTTPException(500, f"Model audit failed: {err}")
