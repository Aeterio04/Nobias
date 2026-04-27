"""
Serializer — handles both real library objects (dataset_audit, model_audit, agent_audit)
and the mock fallback objects.
"""
from dataclasses import asdict
import numpy as np


def _to_float(v, default=0.0):
    if v is None:
        return None
    try:
        return round(float(v), 4)
    except (TypeError, ValueError):
        return default


def _safe(obj, attr, default=None):
    if isinstance(obj, dict):
        return obj.get(attr, default)
    return getattr(obj, attr, default)


def _severity_str(s):
    """Convert Severity enum or string to plain string."""
    if s is None:
        return 'UNKNOWN'
    if hasattr(s, 'value'):
        return str(s.value)
    return str(s)


def serialize_dataset_report(report) -> dict:
    findings = _safe(report, 'findings', [])
    proxy_features = _safe(report, 'proxy_features', [])
    remediations = _safe(report, 'remediation_suggestions', [])
    label_rates_raw = _safe(report, 'label_rates', {})

    # label_rates may be a dict of dicts or a LabelRates object
    label_rates = {}
    if isinstance(label_rates_raw, dict):
        for attr, rates in label_rates_raw.items():
            if isinstance(rates, dict):
                label_rates[attr] = {k: _to_float(v) if isinstance(v, (int, float, np.floating)) else v for k, v in rates.items()}
            elif hasattr(rates, '__dict__'):
                # Real library LabelRates object
                d = {}
                for g, rate in _safe(rates, 'rates', {}).items():
                    d[str(g)] = _to_float(rate)
                srd = _safe(rates, 'srd')
                dir_val = _safe(rates, 'dir')
                if srd is not None:
                    d['srd'] = _to_float(srd)
                if dir_val is not None:
                    d['dir'] = _to_float(dir_val)
                label_rates[attr] = d

    serialized_findings = []
    for f in findings:
        serialized_findings.append({
            "check": _safe(f, 'check', ''),
            "severity": _severity_str(_safe(f, 'severity', '')),
            "message": _safe(f, 'message', ''),
            "metric": _safe(f, 'metric', ''),
            "value": _to_float(_safe(f, 'value', 0)),
            "threshold": _to_float(_safe(f, 'threshold', 0)),
            "confidence": _to_float(_safe(f, 'confidence')) if _safe(f, 'confidence') is not None else None,
        })

    serialized_proxy = []
    for p in proxy_features:
        serialized_proxy.append({
            "feature": _safe(p, 'feature', ''),
            "protected": _safe(p, 'protected', ''),
            "method": _safe(p, 'method', ''),
            "score": _to_float(_safe(p, 'score', 0)),
            "nmi": _to_float(_safe(p, 'nmi')) if _safe(p, 'nmi') is not None else None,
        })

    serialized_remediations = []
    for r in remediations:
        serialized_remediations.append({
            "strategy": _safe(r, 'strategy', '') or _safe(r, 'strategy_name', ''),
            "description": _safe(r, 'description', ''),
            "estimated_dir_after": _to_float(_safe(r, 'estimated_dir_after')) if _safe(r, 'estimated_dir_after') is not None else None,
            "estimated_spd_after": _to_float(_safe(r, 'estimated_spd_after')) if _safe(r, 'estimated_spd_after') is not None else None,
        })

    return {
        "audit_id": _safe(report, 'audit_id', 'unknown'),
        "dataset_name": _safe(report, 'dataset_name', 'unknown'),
        "row_count": _safe(report, 'row_count', 0),
        "overall_severity": _severity_str(_safe(report, 'overall_severity', 'UNKNOWN')),
        "finding_count": len(serialized_findings),
        "findings": serialized_findings,
        "proxy_features": serialized_proxy,
        "label_rates": label_rates,
        "remediation_suggestions": serialized_remediations,
    }


def serialize_model_report(report) -> dict:
    severity_str = _severity_str(_safe(report, 'overall_severity', 'UNKNOWN'))

    # Scorecard
    scorecard = {}
    raw_scorecard = _safe(report, 'scorecard', {})
    if isinstance(raw_scorecard, dict):
        for key, metric in raw_scorecard.items():
            scorecard[key] = {
                "metric_name": _safe(metric, 'metric_name', ''),
                "value": _to_float(_safe(metric, 'value', 0)),
                "threshold": _to_float(_safe(metric, 'threshold', 0)),
                "passed": bool(_safe(metric, 'passed', False)),
                "p_value": _to_float(_safe(metric, 'p_value')) if _safe(metric, 'p_value') is not None else None,
                "privileged_group": str(_safe(metric, 'privileged_group', '') or ''),
                "unprivileged_group": str(_safe(metric, 'unprivileged_group', '') or ''),
                "description": _safe(metric, 'description', ''),
            }

    # Counterfactual
    cf_result = _safe(report, 'counterfactual_result')
    counterfactual = {
        "flip_rate": _to_float(_safe(cf_result, 'flip_rate', 0)) if cf_result else None,
        "flips_by_attribute": dict(_safe(cf_result, 'flips_by_attribute', {})) if cf_result else {},
    }

    # Findings
    findings = []
    for f in _safe(report, 'findings', []):
        evidence = _safe(f, 'evidence', {})
        if isinstance(evidence, dict):
            evidence = {k: (round(float(v), 4) if isinstance(v, (int, float, np.floating)) else v) for k, v in evidence.items()}
        findings.append({
            "finding_id": _safe(f, 'finding_id', ''),
            "severity": _severity_str(_safe(f, 'severity', '')),
            "category": _safe(f, 'category', ''),
            "title": _safe(f, 'title', ''),
            "description": _safe(f, 'description', ''),
            "evidence": evidence,
            "affected_groups": list(_safe(f, 'affected_groups', [])),
        })

    # Mitigation options
    mitigations = []
    for m in _safe(report, 'mitigation_options', []):
        mitigations.append({
            "strategy_name": _safe(m, 'strategy_name', ''),
            "category": _safe(m, 'category', ''),
            "description": _safe(m, 'description', ''),
            "expected_impact": _safe(m, 'expected_impact', ''),
            "implementation_complexity": _safe(m, 'implementation_complexity', ''),
            "requires_retraining": bool(_safe(m, 'requires_retraining', False)),
            "code_example": _safe(m, 'code_example', ''),
        })

    return {
        "audit_id": _safe(report, 'audit_id', 'unknown'),
        "model_name": _safe(report, 'model_name', 'unknown'),
        "overall_severity": severity_str,
        "counterfactual": counterfactual,
        "scorecard": scorecard,
        "findings": findings,
        "mitigation_options": mitigations,
    }


def serialize_agent_report(report) -> dict:
    # Handle both real AgentAuditReport (dataclass) and mock
    # Real library: use to_dict() if available
    if hasattr(report, 'to_dict'):
        raw = report.to_dict()
        # Normalize findings
        findings = []
        for f in raw.get('findings', []):
            findings.append({
                "finding_id": f.get('finding_id', ''),
                "severity": _severity_str(f.get('severity', '')),
                "attribute": f.get('attribute', ''),
                "test_type": f.get('metric', f.get('test_type', '')),
                "cfr": _to_float(f.get('value', f.get('cfr', 0))),
                "description": f.get('benchmark_context', f.get('description', '')),
            })

        # Normalize persona_results
        personas = []
        for p in raw.get('persona_results', []):
            personas.append({
                "persona_id": p.get('persona_id', ''),
                "attributes": p.get('attributes', {}),
                "decision": p.get('decision', ''),
                "score": _to_float(p.get('score')) if p.get('score') is not None else None,
                "runs": p.get('runs', 1),
            })

        # Normalize prompt_suggestions
        suggestions = []
        for s in raw.get('prompt_suggestions', []):
            suggestions.append({
                "original_segment": s.get('finding_id', ''),
                "suggested_change": s.get('suggestion_text', ''),
                "rationale": s.get('rationale', ''),
            })

        # CFR by attribute — derive from findings if not present
        cfr_by_attr = {}
        for f in raw.get('findings', []):
            attr = f.get('attribute', '')
            val = _to_float(f.get('value', 0))
            if attr and val is not None:
                if attr not in cfr_by_attr or val > cfr_by_attr[attr]:
                    cfr_by_attr[attr] = val

        eeoc_air = raw.get('eeoc_air', {})

        return {
            "audit_id": raw.get('audit_id', 'unknown'),
            "overall_cfr": _to_float(raw.get('overall_cfr', 0)),
            "overall_severity": _severity_str(raw.get('overall_severity', 'UNKNOWN')),
            "overall_masd": None,
            "cfr_by_attribute": cfr_by_attr,
            "eeoc_air": eeoc_air,
            "findings": findings,
            "persona_results": personas,
            "prompt_suggestions": suggestions,
        }
    else:
        # Mock fallback
        return {
            "audit_id": _safe(report, 'audit_id', 'unknown'),
            "overall_cfr": _to_float(_safe(report, 'overall_cfr', 0)),
            "overall_severity": _severity_str(_safe(report, 'overall_severity', 'UNKNOWN')),
            "overall_masd": _to_float(_safe(report, 'overall_masd')) if _safe(report, 'overall_masd') is not None else None,
            "cfr_by_attribute": {k: _to_float(v) for k, v in _safe(report, 'cfr_by_attribute', {}).items()},
            "eeoc_air": _safe(report, 'eeoc_air', {}),
            "findings": [
                {
                    "finding_id": _safe(f, 'finding_id', ''),
                    "severity": _severity_str(_safe(f, 'severity', '')),
                    "attribute": _safe(f, 'attribute', ''),
                    "test_type": _safe(f, 'test_type', ''),
                    "cfr": _to_float(_safe(f, 'cfr', 0)),
                    "description": _safe(f, 'description', ''),
                }
                for f in _safe(report, 'findings', [])
            ],
            "persona_results": [
                {
                    "persona_id": _safe(p, 'persona_id', ''),
                    "attributes": _safe(p, 'attributes', {}),
                    "decision": _safe(p, 'decision', ''),
                    "score": _to_float(_safe(p, 'score')) if _safe(p, 'score') is not None else None,
                    "runs": _safe(p, 'runs', 1),
                }
                for p in _safe(report, 'persona_results', [])
            ],
            "prompt_suggestions": [
                {
                    "original_segment": _safe(s, 'original_segment', ''),
                    "suggested_change": _safe(s, 'suggested_change', ''),
                    "rationale": _safe(s, 'rationale', ''),
                }
                for s in _safe(report, 'prompt_suggestions', [])
            ],
        }
