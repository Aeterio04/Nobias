"""
agent_audit.report.sections — Report Section Builders
======================================================

Functions to build each section of the comprehensive report:
    - Section 1: Health & Metadata
    - Section 2: Test Configuration
    - Section 3: Results & Statistics
    - Section 4: Interpretation & Remediation
    - Section 5: Raw Data
"""

from __future__ import annotations

from typing import Any

from agent_audit.models import AgentAuditReport
from agent_audit.report.utils import (
    format_duration,
    estimate_tokens,
    std_dev,
    severity_badge,
)


def build_health_section(report: AgentAuditReport) -> dict[str, Any]:
    """
    Build health and metadata section.
    
    Includes:
    - Audit ID and timestamp
    - API calls and estimated tokens
    - Duration and performance metrics
    - Audit mode and configuration
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with health metrics.
    """
    tokens = estimate_tokens(report.total_calls)
    
    return {
        "audit_id": report.audit_id,
        "timestamp": report.timestamp,
        "mode": report.mode,
        "duration_seconds": round(report.duration_seconds, 2),
        "duration_formatted": format_duration(report.duration_seconds),
        "api_calls": {
            "total": report.total_calls,
            "per_persona": round(report.total_calls / max(len(report.persona_results), 1), 2),
            "calls_per_second": round(report.total_calls / max(report.duration_seconds, 1), 2),
        },
        "estimated_tokens": tokens,
        "performance": {
            "avg_call_latency_ms": round((report.duration_seconds * 1000) / max(report.total_calls, 1), 2),
            "personas_tested": len(report.persona_results),
            "findings_generated": len(report.findings),
        },
    }


def build_config_section(report: AgentAuditReport) -> dict[str, Any]:
    """
    Build test configuration section.
    
    Includes:
    - Protected attributes tested
    - Persona generation strategy
    - Test types and variants
    - Context primes used
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with configuration details.
    """
    # Analyze persona composition
    test_types = {}
    attributes_tested = set()
    context_primes = set()
    names_used = set()
    
    for persona in report.persona_results:
        test_types[persona.test_type] = test_types.get(persona.test_type, 0) + 1
        attributes_tested.update(persona.attributes.keys())
        if persona.context_prime and persona.context_prime != "none":
            context_primes.add(persona.context_prime)
        if persona.name:
            names_used.add(persona.name)
    
    return {
        "protected_attributes": sorted(list(attributes_tested)),
        "persona_generation": {
            "total_personas": len(report.persona_results),
            "test_types": test_types,
            "unique_names": len(names_used),
            "context_primes": len(context_primes),
        },
        "test_variants": {
            "factorial_grid": test_types.get("factorial", 0),
            "pairwise_grid": test_types.get("pairwise", 0),
            "name_proxy": test_types.get("name_proxy", 0),
            "context_primed": test_types.get("context_primed", 0),
        },
        "context_primes_used": sorted(list(context_primes)) if context_primes else [],
        "sample_names": sorted(list(names_used))[:10] if names_used else [],
    }


def build_results_section(report: AgentAuditReport) -> dict[str, Any]:
    """
    Build results and statistics section.
    
    Includes:
    - Overall severity and CFR
    - Per-attribute findings
    - Statistical metrics (CFR, MASD, parity)
    - Decision distribution
    - Variance analysis
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with results and statistics.
    """
    # Overall metrics
    overall = {
        "severity": report.overall_severity,
        "severity_badge": severity_badge(report.overall_severity),
        "overall_cfr": round(report.overall_cfr, 4),
        "overall_cfr_percent": f"{report.overall_cfr:.1%}",
        "benchmark_range": {
            "min": report.benchmark_range[0],
            "max": report.benchmark_range[1],
            "min_percent": f"{report.benchmark_range[0]:.1%}",
            "max_percent": f"{report.benchmark_range[1]:.1%}",
        },
        "total_findings": len(report.findings),
    }
    
    # Findings by severity
    findings_by_severity = {
        "CRITICAL": [],
        "MODERATE": [],
        "LOW": [],
        "CLEAR": [],
    }
    for finding in report.findings:
        findings_by_severity[finding.severity].append(finding.to_dict())
    
    severity_counts = {k: len(v) for k, v in findings_by_severity.items()}
    
    # Findings by attribute
    findings_by_attribute = {}
    for finding in report.findings:
        attr = finding.attribute
        if attr not in findings_by_attribute:
            findings_by_attribute[attr] = []
        findings_by_attribute[attr].append({
            "metric": finding.metric,
            "value": round(finding.value, 4),
            "p_value": round(finding.p_value, 4),
            "severity": finding.severity,
            "comparison": finding.comparison,
        })
    
    # Findings by metric type
    findings_by_metric = {}
    for finding in report.findings:
        metric = finding.metric
        if metric not in findings_by_metric:
            findings_by_metric[metric] = []
        findings_by_metric[metric].append({
            "attribute": finding.attribute,
            "value": round(finding.value, 4),
            "severity": finding.severity,
        })
    
    # Decision distribution
    decision_dist = {"positive": 0, "negative": 0, "ambiguous": 0}
    score_values = []
    variance_values = []
    
    for persona in report.persona_results:
        decision_dist[persona.decision] = decision_dist.get(persona.decision, 0) + 1
        if persona.score is not None:
            score_values.append(persona.score)
        variance_values.append(persona.decision_variance)
    
    total_personas = max(len(report.persona_results), 1)
    decision_stats = {
        "distribution": decision_dist,
        "distribution_percent": {
            k: f"{(v / total_personas) * 100:.1f}%"
            for k, v in decision_dist.items()
        },
        "positive_rate": round(decision_dist["positive"] / total_personas, 4),
    }
    
    # Score statistics
    score_stats = None
    if score_values:
        score_stats = {
            "mean": round(sum(score_values) / len(score_values), 4),
            "min": round(min(score_values), 4),
            "max": round(max(score_values), 4),
            "std": round(std_dev(score_values), 4),
        }
    
    # Variance statistics
    variance_stats = {
        "mean_variance": round(sum(variance_values) / max(len(variance_values), 1), 4),
        "max_variance": round(max(variance_values) if variance_values else 0, 4),
        "high_variance_count": sum(1 for v in variance_values if v > 0.3),
    }
    
    return {
        "overall": overall,
        "severity_breakdown": severity_counts,
        "findings_by_severity": findings_by_severity,
        "findings_by_attribute": findings_by_attribute,
        "findings_by_metric": findings_by_metric,
        "decision_statistics": decision_stats,
        "score_statistics": score_stats,
        "variance_statistics": variance_stats,
    }


def build_interpretation_section(report: AgentAuditReport) -> dict[str, Any]:
    """
    Build interpretation and remediation section.
    
    Includes:
    - LLM-generated assessment
    - Finding explanations
    - Priority order
    - Prompt suggestions with confidence
    - Stress test results (if available)
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with interpretation and remediation data.
    """
    interpretation_data = {
        "overall_assessment": report.interpretation.overall_assessment if report.interpretation else "",
        "confidence": report.interpretation.confidence if report.interpretation else "medium",
        "finding_explanations": report.interpretation.finding_explanations if report.interpretation else [],
        "priority_order": report.interpretation.priority_order if report.interpretation else [],
    }
    
    suggestions_data = []
    for suggestion in report.prompt_suggestions:
        suggestions_data.append({
            "finding_id": suggestion.finding_id,
            "suggestion_text": suggestion.suggestion_text,
            "rationale": suggestion.rationale,
            "confidence": suggestion.confidence,
            "word_count": len(suggestion.suggestion_text.split()),
        })
    
    stress_test_data = None
    if report.stress_test_results:
        st = report.stress_test_results
        stress_test_data = {
            "rounds_completed": st.rounds_completed,
            "total_mutations_tested": st.total_mutations_tested,
            "max_cfr_achieved": round(st.max_cfr_achieved, 4),
            "max_cfr_percent": f"{st.max_cfr_achieved:.1%}",
            "conclusion": st.conclusion,
            "bias_inducing_probes_count": len(st.bias_inducing_probes),
        }
    
    return {
        "interpretation": interpretation_data,
        "prompt_suggestions": suggestions_data,
        "suggestions_count": len(suggestions_data),
        "stress_test": stress_test_data,
    }


def build_raw_data_section(report: AgentAuditReport) -> dict[str, Any]:
    """
    Build raw data section.
    
    Includes:
    - All persona results
    - CAFFE test suite export
    - Raw outputs (truncated for readability)
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with raw data.
    """
    persona_data = []
    for persona in report.persona_results:
        persona_data.append({
            "persona_id": persona.persona_id,
            "attributes": persona.attributes,
            "test_type": persona.test_type,
            "decision": persona.decision,
            "score": round(persona.score, 4) if persona.score is not None else None,
            "decision_variance": round(persona.decision_variance, 4),
            "score_std": round(persona.score_std, 4) if persona.score_std is not None else None,
            "context_prime": persona.context_prime,
            "name": persona.name,
            "raw_outputs_count": len(persona.raw_outputs),
            "raw_outputs_preview": persona.raw_outputs[:2] if persona.raw_outputs else [],
        })
    
    return {
        "persona_results": persona_data,
        "caffe_test_suite": report.caffe_test_suite,
        "total_personas": len(persona_data),
        "total_caffe_cases": len(report.caffe_test_suite),
    }


def build_compliance_section(report: AgentAuditReport) -> dict[str, Any]:
    """
    Build legal compliance section (FairSight).
    
    Includes:
    - EEOC Adverse Impact Ratios
    - Legal compliance status
    - Risk levels and warnings
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with compliance metrics.
    """
    if not report.eeoc_air:
        return {"status": "not_computed"}
    
    compliance_data = {}
    violations = []
    warnings = []
    
    for attr, air_data in report.eeoc_air.items():
        compliance_data[attr] = {
            "air": round(air_data.get("air", 0.0), 4),
            "air_percent": f"{air_data.get('air', 0.0):.1%}",
            "reference_group": air_data.get("highest_group", air_data.get("reference_group", "unknown")),
            "protected_group": air_data.get("lowest_group", air_data.get("protected_group", "unknown")),
            "highest_rate": round(air_data.get("highest_rate", 0.0), 4),
            "lowest_rate": round(air_data.get("lowest_rate", 0.0), 4),
            "legal_status": air_data.get("legal_status", "UNKNOWN"),
            "risk_level": air_data.get("risk_level", "UNKNOWN"),
            "eeoc_threshold": 0.80,
        }
        
        if air_data["legal_status"] == "VIOLATION":
            violations.append({
                "attribute": attr,
                "air": air_data["air"],
                "message": f"LEGAL VIOLATION: {attr} AIR = {air_data['air']:.1%} < 80% threshold"
            })
        elif air_data["legal_status"] == "WARNING":
            warnings.append({
                "attribute": attr,
                "air": air_data["air"],
                "message": f"WARNING: {attr} AIR = {air_data['air']:.1%} is close to 80% threshold"
            })
    
    return {
        "eeoc_air_by_attribute": compliance_data,
        "violations": violations,
        "warnings": warnings,
        "overall_status": "VIOLATION" if violations else ("WARNING" if warnings else "COMPLIANT"),
        "eeoc_reference": "29 CFR Part 1607 (Uniform Guidelines on Employee Selection Procedures)",
    }


def build_validity_section(report: AgentAuditReport) -> dict[str, Any]:
    """
    Build statistical validity section (FairSight).
    
    Includes:
    - Stochastic Stability Score (SSS)
    - Bias-Adjusted CFR (BA-CFR)
    - Confidence intervals
    - Bonferroni correction
    - Audit integrity
    
    Args:
        report: The AgentAuditReport to process.
    
    Returns:
        Dict with validity metrics.
    """
    validity_data = {}
    
    # Stability
    if report.stability:
        validity_data["stability"] = {
            "overall_sss": round(report.stability.get("overall_sss", 0), 4),
            "classification": report.stability.get("classification", "unknown"),
            "trustworthy": report.stability.get("trustworthy", False),
            "mean_persona_sss": round(report.stability.get("mean_persona_sss", 0), 4),
            "unstable_personas": report.stability.get("unstable_personas", 0),
            "interpretation": _interpret_stability(report.stability),
        }
    
    # Bias-Adjusted CFR
    ba_cfr_findings = []
    for finding in report.findings:
        if finding.metric == "cfr" and "ba_cfr" in finding.details:
            ba_cfr_findings.append({
                "attribute": finding.attribute,
                "raw_cfr": round(finding.value, 4),
                "ba_cfr": round(finding.details["ba_cfr"], 4),
                "noise_removed": round(finding.value - finding.details["ba_cfr"], 4),
            })
    validity_data["bias_adjusted_cfr"] = ba_cfr_findings
    
    # Confidence Intervals
    if report.confidence_intervals:
        ci_data = []
        for finding_id, ci in report.confidence_intervals.items():
            finding = next((f for f in report.findings if f.finding_id == finding_id), None)
            if finding:
                ci_data.append({
                    "finding_id": finding_id,
                    "attribute": finding.attribute,
                    "metric": finding.metric,
                    "point_estimate": round(ci["rate"], 4),
                    "ci_lower": round(ci["ci_lower"], 4),
                    "ci_upper": round(ci["ci_upper"], 4),
                    "ci_width": round(ci["ci_upper"] - ci["ci_lower"], 4),
                })
        validity_data["confidence_intervals"] = ci_data
    
    # Bonferroni Correction
    if report.bonferroni_correction:
        validity_data["bonferroni"] = {
            "original_alpha": report.bonferroni_correction.get("original_alpha", 0.05),
            "corrected_alpha": round(report.bonferroni_correction.get("corrected_alpha", 0.05), 6),
            "n_tests": report.bonferroni_correction.get("n_tests", 0),
            "significant_after_correction": sum(
                1 for f in report.findings
                if f.details.get("bonferroni_significant", False)
            ),
        }
    
    # Audit Integrity
    if report.audit_integrity:
        validity_data["audit_integrity"] = {
            "audit_hash": report.audit_integrity.audit_hash[:16] + "...",
            "prompts_hash": report.audit_integrity.prompts_hash[:16] + "...",
            "responses_hash": report.audit_integrity.responses_hash[:16] + "...",
            "config_hash": report.audit_integrity.config_hash[:16] + "...",
            "timestamp": report.audit_integrity.timestamp,
            "tamper_evident": True,
        }
    
    # Model Fingerprint
    if report.model_fingerprint:
        validity_data["model_fingerprint"] = {
            "model_id": report.model_fingerprint.model_id,
            "temperature": report.model_fingerprint.temperature,
            "max_tokens": report.model_fingerprint.max_tokens,
            "backend": report.model_fingerprint.backend,
            "sdk_version": report.model_fingerprint.sdk_version,
            "system_prompt_hash": report.model_fingerprint.system_prompt_hash[:16] + "...",
            "timestamp": report.model_fingerprint.timestamp,
        }
    
    return validity_data


def _interpret_stability(stability: dict) -> str:
    """Interpret stability classification."""
    classification = stability.get("classification", "unknown")
    sss = stability.get("overall_sss", 0)
    
    if classification == "highly_stable":
        return f"Excellent stability (SSS={sss:.2f}). Results are highly trustworthy."
    elif classification == "stable":
        return f"Good stability (SSS={sss:.2f}). Results are generally trustworthy."
    elif classification == "moderately_stable":
        return f"Moderate stability (SSS={sss:.2f}). Results should be interpreted with caution."
    elif classification == "unstable":
        return f"Poor stability (SSS={sss:.2f}). Results are unreliable - agent is too stochastic."
    else:
        return "Stability not computed."


__all__ = [
    "build_health_section",
    "build_config_section",
    "build_results_section",
    "build_interpretation_section",
    "build_raw_data_section",
    "build_compliance_section",
    "build_validity_section",
]
