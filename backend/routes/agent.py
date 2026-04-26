from fastapi import APIRouter, Form, UploadFile, File, HTTPException
import json, tempfile, os

router = APIRouter()

@router.post("/run")
async def run_agent_audit(
    system_prompt: str = Form(...),
    llm_model: str = Form("gpt-4o"),
    api_key: str = Form(...),
    protected_attributes: str = Form('["gender","race"]'),
    audit_mode: str = Form("standard"),
):
    try:
        attrs = json.loads(protected_attributes)
        
        try:
            from unbiased import audit_agent
        except ImportError:
            import sys
            sys.path.insert(0, os.path.dirname(__file__) + '/..')
            from unbiased_mock import audit_agent
        
        report = audit_agent(
            system_prompt=system_prompt,
            llm_model=llm_model,
            api_key=api_key,
            protected_attributes=attrs,
            audit_mode=audit_mode,
        )
        
        from services.serializer import serialize_agent_report
        result = serialize_agent_report(report)
        
        from services.history import save_audit_to_history
        save_audit_to_history({
            "audit_type": "agent",
            "audit_id": result["audit_id"],
            "name": f"Agent Audit ({llm_model})",
            "severity": result["overall_severity"],
            "finding_count": len(result["findings"]),
            "result": result,
        })
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        err = str(e)
        if "api_key" in err.lower() or "401" in err:
            raise HTTPException(401, "Invalid API key")
        elif "rate limit" in err.lower() or "429" in err:
            raise HTTPException(429, "LLM API rate limit hit")
        elif "model" in err.lower() and "not found" in err.lower():
            raise HTTPException(400, f"Model '{llm_model}' not found")
        elif "timeout" in err.lower():
            raise HTTPException(504, "Agent audit timed out")
        else:
            raise HTTPException(500, f"Agent audit failed: {err}")

@router.post("/upload-logs")
async def upload_log_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.jsonl'):
            raise HTTPException(400, "Log file must be JSONL format")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl') as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        with open(tmp_path, encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        try:
            first = json.loads(lines[0])
            fields = list(first.keys())
        except:
            raise HTTPException(400, "JSONL file is malformed")
        return {"tmp_path": tmp_path, "line_count": len(lines), "detected_fields": fields}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to process log file: {str(e)}")

@router.post("/compare")
async def compare_audits(audit_id_before: str = Form(...), audit_id_after: str = Form(...)):
    from services.history import get_audit_by_id
    before = get_audit_by_id(audit_id_before)
    after = get_audit_by_id(audit_id_after)
    if not before or not after:
        raise HTTPException(404, "One or both audit IDs not found")
    before_cfr = before["result"].get("overall_cfr", 0)
    after_cfr = after["result"].get("overall_cfr", 0)
    return {
        "before": before,
        "after": after,
        "improvement": {
            "cfr_change": round(after_cfr - before_cfr, 4),
            "cfr_reduction_pct": round((before_cfr - after_cfr) / before_cfr * 100, 1) if before_cfr > 0 else 0,
            "severity_before": before["severity"],
            "severity_after": after["severity"],
        }
    }
