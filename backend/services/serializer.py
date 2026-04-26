def safe_get(obj, attr, default=None):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)

def serialize_dataset_report(report) -> dict:
    return {
        "audit_id": safe_get(report, 'audit_id', 'unknown'),
        "dataset_name": safe_get(report, 'dataset_name', 'unknown'),
        "row_count": safe_get(report, 'row_count', 0),
        "overall_severity": safe_get(report, 'overall_severity', 'UNKNOWN'),
        "finding_count": len(safe_get(report, 'findings', [])),
        "findings": [
            {
                "check": safe_get(f, 'check', ''),
                "severity": safe_get(f, 'severity', ''),
                "message": safe_get(f, 'message', ''),
                "metric": safe_get(f, 'metric', ''),
                "value": round(float(safe_get(f, 'value', 0)), 4),
                "threshold": round(float(safe_get(f, 'threshold', 0)), 4),
                "confidence": round(float(safe_get(f, 'confidence', 0)), 4) if safe_get(f, 'confidence') else None,
            }
            for f in safe_get(report, 'findings', [])
        ],
        "proxy_features": [
            {
                "feature": safe_get(p, 'feature', ''),
                "protected": safe_get(p, 'protected', ''),
                "method": safe_get(p, 'method', ''),
                "score": round(float(safe_get(p, 'score', 0)), 4),
                "nmi": round(float(safe_get(p, 'nmi', 0)), 4) if safe_get(p, 'nmi') else None,
            }
            for p in safe_get(report, 'proxy_features', [])
        ],
        "label_rates": safe_get(report, 'label_rates', {}),
        "remediation_suggestions": [
            {
                "strategy": safe_get(r, 'strategy', ''),
                "estimated_dir_after": round(float(safe_get(r, 'estimated_dir_after', 0)), 4) if safe_get(r, 'estimated_dir_after') else None,
                "estimated_spd_after": round(float(safe_get(r, 'estimated_spd_after', 0)), 4) if safe_get(r, 'estimated_spd_after') else None,
                "description": safe_get(r, 'description', ''),
            }
            for r in safe_get(report, 'remediation_suggestions', [])
        ],
    }

def serialize_model_report(report) -> dict:
    severity = safe_get(report, 'overall_severity', 'UNKNOWN')
    severity_str = severity.value if hasattr(severity, 'value') else str(severity)
    scorecard = {}
    if safe_get(report, 'scorecard'):
        for key, metric in safe_get(report, 'scorecard', {}).items():
            scorecard[key] = {
                "metric_name": safe_get(metric, 'metric_name', ''),
                "value": round(float(safe_get(metric, 'value', 0)), 4),
                "threshold": round(float(safe_get(metric, 'threshold', 0)), 4),
                "passed": bool(safe_get(metric, 'passed', False)),
                "p_value": round(float(safe_get(metric, 'p_value', 0)), 6) if safe_get(metric, 'p_value') else None,
                "privileged_group": safe_get(metric, 'privileged_group', ''),
                "unprivileged_group": safe_get(metric, 'unprivileged_group', ''),
                "description": safe_get(metric, 'description', ''),
            }
    cf_result = safe_get(report, 'counterfactual_result')
    return {
        "audit_id": safe_get(report, 'audit_id', 'unknown'),
        "model_name": safe_get(report, 'model_name', 'unknown'),
        "overall_severity": severity_str,
        "counterfactual": {
            "flip_rate": round(float(safe_get(cf_result, 'flip_rate', 0)), 4) if cf_result else None,
            "flips_by_attribute": dict(safe_get(cf_result, 'flips_by_attribute', {})) if cf_result else {},
        },
        "scorecard": scorecard,
        "findings": [
            {
                "finding_id": safe_get(f, 'finding_id', ''),
                "severity": safe_get(f, 'severity', {}).value if hasattr(safe_get(f, 'severity', {}), 'value') else str(safe_get(f, 'severity', '')),
                "category": safe_get(f, 'category', ''),
                "title": safe_get(f, 'title', ''),
                "description": safe_get(f, 'description', ''),
                "evidence": {k: (round(float(v), 4) if isinstance(v, float) else v) for k, v in safe_get(f, 'evidence', {}).items()},
                "affected_groups": safe_get(f, 'affected_groups', []),
            }
            for f in safe_get(report, 'findings', [])
        ],
        "mitigation_options": [
            {
                "strategy_name": safe_get(m, 'strategy_name', ''),
                "category": safe_get(m, 'category', ''),
                "description": safe_get(m, 'description', ''),
                "expected_impact": safe_get(m, 'expected_impact', ''),
                "implementation_complexity": safe_get(m, 'implementation_complexity', ''),
                "requires_retraining": bool(safe_get(m, 'requires_retraining', False)),
                "code_example": safe_get(m, 'code_example', ''),
            }
            for m in safe_get(report, 'mitigation_options', [])
        ],
    }

def serialize_agent_report(report) -> dict:
    return {
        "audit_id": safe_get(report, 'audit_id', 'unknown'),
        "overall_cfr": round(float(safe_get(report, 'overall_cfr', 0)), 4),
        "overall_severity": safe_get(report, 'overall_severity', 'UNKNOWN'),
        "overall_masd": round(float(safe_get(report, 'overall_masd', 0)), 4) if safe_get(report, 'overall_masd') else None,
        "cfr_by_attribute": {k: round(float(v), 4) for k, v in safe_get(report, 'cfr_by_attribute', {}).items()},
        "eeoc_air": safe_get(report, 'eeoc_air', {}),
        "findings": [
            {
                "finding_id": safe_get(f, 'finding_id', ''),
                "severity": safe_get(f, 'severity', ''),
                "attribute": safe_get(f, 'attribute', ''),
                "test_type": safe_get(f, 'test_type', ''),
                "cfr": round(float(safe_get(f, 'cfr', 0)), 4),
                "description": safe_get(f, 'description', ''),
            }
            for f in safe_get(report, 'findings', [])
        ],
        "persona_results": [
            {
                "persona_id": safe_get(p, 'persona_id', ''),
                "attributes": safe_get(p, 'attributes', {}),
                "decision": safe_get(p, 'decision', ''),
                "score": round(float(safe_get(p, 'score', 0)), 4) if safe_get(p, 'score') is not None else None,
                "runs": safe_get(p, 'runs', 1),
            }
            for p in safe_get(report, 'persona_results', [])
        ],
        "prompt_suggestions": [
            {
                "original_segment": safe_get(s, 'original_segment', ''),
                "suggested_change": safe_get(s, 'suggested_change', ''),
                "rationale": safe_get(s, 'rationale', ''),
            }
            for s in safe_get(report, 'prompt_suggestions', [])
        ],
    }
