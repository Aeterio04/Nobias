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


__all__ = [
    "build_health_section",
    "build_config_section",
    "build_results_section",
    "build_interpretation_section",
    "build_raw_data_section",
]
