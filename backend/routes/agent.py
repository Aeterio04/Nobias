from fastapi import APIRouter, Form, UploadFile, File, HTTPException
import json, tempfile, os

router = APIRouter()

@router.post("/run")
async def run_agent_audit(
    connection_mode: str = Form("system_prompt"),
    system_prompt: str = Form(None),
    seed_case: str = Form(None),
    llm_model: str = Form("gpt-4o"),
    api_key: str = Form(None),
    endpoint_url: str = Form(None),
    auth_header: str = Form(None),
    request_template: str = Form(None),
    response_path: str = Form(None),
    log_file_path: str = Form(None),
    input_field: str = Form("input"),
    output_field: str = Form("output"),
    audit_mode: str = Form("standard"),
    attributes: str = Form('["gender","race"]'),
    domain: str = Form("hiring"),
    # Also accept as protected_attributes for backward compat
    protected_attributes: str = Form(None),
):
    try:
        # Parse attributes from either field name
        attrs_str = attributes or protected_attributes or '["gender","race"]'
        try:
            attrs = json.loads(attrs_str)
        except json.JSONDecodeError:
            # Handle comma-separated format
            attrs = [a.strip() for a in attrs_str.split(',') if a.strip()]
        
        try:
            from unbiased.agent_audit import audit_agent, AgentAuditor
        except ImportError:
            try:
                from unbiased import audit_agent
            except ImportError:
                import sys
                sys.path.insert(0, os.path.dirname(__file__) + '/..')
                from unbiased_mock import audit_agent
        
        if connection_mode == "system_prompt":
            if not system_prompt:
                raise HTTPException(400, "System prompt is required")
            
            report = audit_agent(
                system_prompt=system_prompt,
                seed_case=seed_case or "",
                api_key=api_key or "",
                mode=audit_mode,
                llm_model=llm_model,
                attributes=attrs,
                domain=domain,
                protected_attributes=attrs,
                audit_mode=audit_mode,
            )
        elif connection_mode == "api_endpoint":
            if not endpoint_url:
                raise HTTPException(400, "Endpoint URL is required")
            # For mock, just use the standard audit
            report = audit_agent(
                system_prompt=f"API Endpoint: {endpoint_url}",
                seed_case=seed_case or "",
                api_key=api_key or "",
                llm_model=llm_model,
                protected_attributes=attrs,
                audit_mode=audit_mode,
            )
        elif connection_mode == "log_replay":
            if not log_file_path:
                raise HTTPException(400, "Log file path is required")
            report = audit_agent(
                system_prompt=f"Log Replay: {log_file_path}",
                seed_case=seed_case or "",
                api_key="",
                llm_model="log_replay",
                protected_attributes=attrs,
                audit_mode=audit_mode,
            )
        else:
            raise HTTPException(400, f"Unknown connection mode: {connection_mode}")
        
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
            raise HTTPException(401, "Invalid API key. Check your LLM provider API key in Settings.")
        elif "rate limit" in err.lower() or "429" in err:
            raise HTTPException(429, "LLM API rate limit hit. Try again in a few moments.")
        elif "model" in err.lower() and "not found" in err.lower():
            raise HTTPException(400, f"Model '{llm_model}' not found. Check the model name.")
        elif "timeout" in err.lower():
            raise HTTPException(504, "Agent audit timed out. The LLM API is not responding.")
        else:
            raise HTTPException(500, f"Agent audit failed: {err}")


@router.post("/upload-logs")
async def upload_log_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.jsonl'):
            raise HTTPException(400, "Log file must be JSONL format (.jsonl)")
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl') as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        with open(tmp_path, encoding='utf-8') as f:
            lines = [l.strip() for l in f if l.strip()]
        try:
            first = json.loads(lines[0])
            fields = list(first.keys())
        except:
            raise HTTPException(400, "JSONL file is malformed. Each line must be valid JSON.")
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
        raise HTTPException(404, "One or both audit IDs not found in history.")
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


@router.get("/export/{audit_id}")
def export_agent_audit(audit_id: str, format: str = "json"):
    from services.history import get_audit_by_id
    import tempfile, json
    from fastapi.responses import FileResponse
    
    entry = get_audit_by_id(audit_id)
    if not entry:
        raise HTTPException(404, "Audit not found")
    
    result = entry["result"]
    
    if format == "json" or format == "caffe":
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump(result, f, indent=2)
            tmp_path = f.name
        return FileResponse(
            tmp_path,
            media_type="application/json",
            filename=f"nobias_agent_audit_{audit_id}.json"
        )
    
    raise HTTPException(400, f"Unknown format: {format}")
