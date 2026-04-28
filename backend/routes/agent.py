from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import tempfile, os, json

router = APIRouter()


def safe(obj, attr, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def safe_float(val, default=0.0):
    try:
        return float(val) if val is not None else default
    except (TypeError, ValueError):
        return default


def serialize_agent_finding(f):
    return {
        "finding_id": safe(f, 'finding_id', ''),
        "severity": str(safe(f, 'severity', 'UNKNOWN')),
        "attribute": safe(f, 'attribute', ''),
        "test_type": safe(f, 'test_type', '') or safe(f, 'metric', ''),
        "cfr": safe_float(safe(f, 'cfr') if safe(f, 'cfr') is not None else safe(f, 'value')),
        "cfr_pct": f"{safe_float(safe(f, 'cfr') if safe(f, 'cfr') is not None else safe(f, 'value')) * 100:.1f}%",
        "description": safe(f, 'description', '') or safe(f, 'benchmark_context', ''),
    }


def serialize_persona(p):
    return {
        "persona_id": safe(p, 'persona_id', ''),
        "attributes": dict(safe(p, 'attributes') or {}),
        "decision": str(safe(p, 'decision', '')),
        "score": safe_float(safe(p, 'score')) if safe(p, 'score') is not None else None,
        "runs": int(safe(p, 'runs', 1) or 1),
    }


def serialize_prompt_suggestion(s):
    # Real library: finding_id, suggestion_text, rationale
    # Mock: original_segment, suggested_change, rationale
    return {
        "original_segment": safe(s, 'original_segment', '') or safe(s, 'finding_id', ''),
        "suggested_change": safe(s, 'suggested_change', '') or safe(s, 'suggestion_text', ''),
        "rationale": safe(s, 'rationale', ''),
    }


def serialize_agent_report(report):
    # Real library uses to_dict() — handle both
    if hasattr(report, 'to_dict'):
        raw = report.to_dict()
        findings_raw  = raw.get('findings', [])
        personas_raw  = raw.get('persona_results', [])
        suggest_raw   = raw.get('prompt_suggestions', [])
        cfr_by_attr   = {}
        for f in findings_raw:
            attr = f.get('attribute', '')
            val  = safe_float(f.get('value', f.get('cfr', 0)))
            if attr and val:
                if attr not in cfr_by_attr or val > cfr_by_attr[attr]:
                    cfr_by_attr[attr] = round(val, 4)
        eeoc_air      = raw.get('eeoc_air', {})
        overall_cfr   = safe_float(raw.get('overall_cfr', 0))
        severity      = str(raw.get('overall_severity', 'UNKNOWN'))
        audit_id      = raw.get('audit_id', 'unknown')
    else:
        findings_raw  = safe(report, 'findings') or []
        personas_raw  = safe(report, 'persona_results') or []
        suggest_raw   = safe(report, 'prompt_suggestions') or []
        cfr_by_attr   = {k: round(safe_float(v), 4) for k, v in (safe(report, 'cfr_by_attribute') or {}).items()}
        eeoc_air      = safe(report, 'eeoc_air') or {}
        overall_cfr   = safe_float(safe(report, 'overall_cfr'))
        sev           = safe(report, 'overall_severity', 'UNKNOWN')
        severity      = sev.value if hasattr(sev, 'value') else str(sev)
        audit_id      = safe(report, 'audit_id', 'unknown')

    findings  = [serialize_agent_finding(f) for f in findings_raw]
    personas  = [serialize_persona(p) for p in personas_raw]
    suggests  = [serialize_prompt_suggestion(s) for s in suggest_raw]

    return {
        "audit_id": audit_id,
        "overall_cfr": overall_cfr,
        "overall_cfr_pct": f"{overall_cfr * 100:.1f}%",
        "overall_severity": severity,
        "finding_count": len(findings),
        "critical_count": len([f for f in findings if f['severity'].upper() == 'CRITICAL']),
        "moderate_count": len([f for f in findings if f['severity'].upper() == 'MODERATE']),
        "cfr_by_attribute": cfr_by_attr,
        "cfr_by_attribute_pct": {k: f"{v * 100:.1f}%" for k, v in cfr_by_attr.items()},
        "eeoc_air": eeoc_air,
        "findings": findings,
        "persona_results": personas,
        "persona_count": len(personas),
        "prompt_suggestions": suggests,
        "_library_report_type": str(type(report).__name__),
    }


@router.post("/upload-logs")
async def upload_log_file(file: UploadFile = File(...)):
    try:
        if not file.filename.endswith('.jsonl'):
            raise HTTPException(400, "Log file must be .jsonl format. Each line is one JSON object.")
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jsonl') as tmp:
            tmp.write(content)
            tmp_path = tmp.name
        lines = [l.strip() for l in content.decode().splitlines() if l.strip()]
        if not lines:
            raise HTTPException(400, "Log file is empty.")
        try:
            first = json.loads(lines[0])
            fields = list(first.keys())
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSONL: first line is not valid JSON.")
        return {"success": True, "tmp_path": tmp_path, "line_count": len(lines), "detected_fields": fields}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(400, f"Failed to process log file: {str(e)}")


@router.post("/run")
async def run_agent_audit(
    connection_mode: str = Form(...),
    system_prompt: str = Form(None),
    seed_case: str = Form(None),
    llm_model: str = Form("gpt-4o"),
    api_key: str = Form(None),
    endpoint_url: str = Form(None),
    auth_header: str = Form("{}"),
    request_template: str = Form('{"input": "{input}"}'),
    response_path: str = Form("$.decision"),
    log_file_path: str = Form(None),
    input_field: str = Form("input"),
    output_field: str = Form("output"),
    audit_mode: str = Form("standard"),
    attributes: str = Form('["gender","race"]'),
    domain: str = Form("hiring"),
    positive_outcome: str = Form("hire"),
    negative_outcome: str = Form("reject"),
):
    try:
        attrs = json.loads(attributes)
    except json.JSONDecodeError:
        raise HTTPException(400, f"attributes must be JSON array. Got: {attributes}")

    try:
        from agent_audit import audit_agent, AgentAuditor
        _has_auditor_class = True
    except ImportError:
        try:
            from agent_audit import audit_agent
            AgentAuditor = None
            _has_auditor_class = False
        except ImportError:
            raise HTTPException(503, "agent_audit module not found. Run: pip install unbiased==0.0.0")

    try:
        import asyncio

        if connection_mode == "system_prompt":
            if not system_prompt or not system_prompt.strip():
                raise HTTPException(400, "System prompt cannot be empty.")
            if not api_key or not api_key.strip():
                raise HTTPException(400, "API key is required for system prompt mode.")
            if not seed_case or not seed_case.strip():
                raise HTTPException(400, "Seed case cannot be empty.")

            if asyncio.iscoroutinefunction(audit_agent):
                report = await audit_agent(
                    system_prompt=system_prompt,
                    seed_case=seed_case,
                    api_key=api_key,
                    mode=audit_mode,
                    model=llm_model,
                    attributes=attrs,
                    domain=domain,
                    positive_outcome=positive_outcome,
                    negative_outcome=negative_outcome,
                )
            else:
                report = audit_agent(
                    system_prompt=system_prompt,
                    seed_case=seed_case,
                    api_key=api_key,
                    mode=audit_mode,
                    model=llm_model,
                    attributes=attrs,
                    domain=domain,
                    positive_outcome=positive_outcome,
                    negative_outcome=negative_outcome,
                )

        elif connection_mode == "api_endpoint":
            if not endpoint_url:
                raise HTTPException(400, "Endpoint URL is required for API endpoint mode.")
            if not _has_auditor_class or AgentAuditor is None:
                raise HTTPException(503, "AgentAuditor class not available in this library version.")
            auth = json.loads(auth_header) if auth_header else {}
            req_tmpl = json.loads(request_template) if request_template else {"input": "{input}"}
            auditor = AgentAuditor.from_api(
                endpoint_url=endpoint_url,
                auth_header=auth,
                request_template=req_tmpl,
                response_path=response_path or "$.decision",
            )
            report = await auditor.run(seed_case=seed_case or "")

        elif connection_mode == "log_replay":
            if not log_file_path or not os.path.exists(log_file_path):
                raise HTTPException(400, "Log file not found. Please upload a JSONL file first.")
            if not _has_auditor_class or AgentAuditor is None:
                raise HTTPException(503, "AgentAuditor class not available in this library version.")
            auditor = AgentAuditor.from_logs(
                log_file=log_file_path,
                input_field=input_field,
                output_field=output_field,
            )
            report = await auditor.run(seed_case=seed_case or "")

        else:
            raise HTTPException(400, f"Unknown connection_mode: '{connection_mode}'. Use system_prompt, api_endpoint, or log_replay.")

    except HTTPException:
        raise
    except Exception as e:
        err = str(e)
        if "api_key" in err.lower() or "authentication" in err.lower() or "invalid_api_key" in err.lower() or "401" in err:
            raise HTTPException(401, f"Invalid API key. Check your key in Settings. Detail: {err}")
        elif "rate_limit" in err.lower() or "429" in err:
            raise HTTPException(429, f"LLM rate limit hit. Wait a moment and retry. Detail: {err}")
        elif "model_not_found" in err.lower() or "model not found" in err.lower():
            raise HTTPException(400, f"Model '{llm_model}' not found. Check the model name. Detail: {err}")
        elif "timeout" in err.lower():
            raise HTTPException(504, f"Request timed out. LLM API not responding. Detail: {err}")
        else:
            raise HTTPException(500, f"Agent audit failed: {type(e).__name__}: {err}")

    result = serialize_agent_report(report)

    from routes.dataset import _save_to_history
    _save_to_history("agent", result)

    return result


@router.post("/compare")
async def compare_agent_audits(
    audit_id_before: str = Form(...),
    audit_id_after: str = Form(...),
):
    from services.history import get_audit_by_id
    before = get_audit_by_id(audit_id_before)
    after  = get_audit_by_id(audit_id_after)
    if not before:
        raise HTTPException(404, f"Audit '{audit_id_before}' not found in history.")
    if not after:
        raise HTTPException(404, f"Audit '{audit_id_after}' not found in history.")
    before_cfr = before.get("result", {}).get("overall_cfr", 0) or 0
    after_cfr  = after.get("result", {}).get("overall_cfr", 0) or 0
    cfr_change = after_cfr - before_cfr
    reduction  = abs(cfr_change) / before_cfr * 100 if before_cfr > 0 else 0
    return {
        "before": before,
        "after": after,
        "improvement": {
            "cfr_change": round(cfr_change, 4),
            "cfr_change_pct": f"{'↓' if cfr_change < 0 else '↑'} {reduction:.1f}%",
            "cfr_reduced": cfr_change < 0,
            "severity_before": before.get("severity", "UNKNOWN"),
            "severity_after": after.get("severity", "UNKNOWN"),
        }
    }


@router.get("/export/{audit_id}")
def export_agent_audit(audit_id: str, format: str = "json"):
    import tempfile as _tmp
    from fastapi.responses import FileResponse
    from services.history import get_audit_by_id
    entry = get_audit_by_id(audit_id)
    if not entry:
        raise HTTPException(404, "Audit not found")
    if format in ["json", "caffe"]:
        with _tmp.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            import json as _json
            _json.dump(entry["result"], f, indent=2)
            tmp_path = f.name
        return FileResponse(tmp_path, media_type="application/json", filename=f"nobias_agent_audit_{audit_id}.json")
    raise HTTPException(400, f"Unknown format: {format}")
