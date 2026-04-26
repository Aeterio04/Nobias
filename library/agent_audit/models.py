"""
agent_audit.models — Core data models for the audit pipeline
==============================================================

All dataclasses that flow through the pipeline as results:
    - PersonaResult       — Per-persona raw decision data
    - AgentFinding        — A single bias finding with severity
    - Interpretation      — LLM-generated explanation of findings
    - PromptSuggestion    — Specific prompt addition for remediation
    - StressTestReport    — Results from adaptive stress testing
    - AuditIntegrity      — Tamper-evident audit record (FairSight compliance)
    - ModelFingerprint    — Exact model state for reproducibility
    - AgentAuditReport    — The complete audit report object
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Any


# ── Per-Persona Results ──────────────────────────────────────────────────────

@dataclass
class PersonaResult:
    """
    Raw decision data for a single persona (one row in the results matrix).

    Attributes:
        persona_id: Unique identifier for this persona test case.
        attributes: Dict of attribute values (e.g. {"gender": "Female", "race": "Black"}).
        test_type: How the persona was generated — "factorial" | "name_proxy" | "context_primed".
        decision: Majority-vote decision — "positive" | "negative" | "ambiguous".
        score: Mean numeric score (0-1) if applicable, else None.
        decision_variance: Fraction of runs that disagreed (0.0 = unanimous).
        score_std: Standard deviation of numeric scores across runs.
        raw_outputs: All raw agent outputs for this persona.
        context_prime: Name of context prime if applicable.
        name: Name used in name-proxy testing if applicable.
    """
    persona_id: str = ""
    attributes: dict[str, str] = field(default_factory=dict)
    test_type: str = "factorial"
    decision: str = "ambiguous"
    score: float | None = None
    decision_variance: float = 0.0
    score_std: float | None = None
    raw_outputs: list[str] = field(default_factory=list)
    context_prime: str = "none"
    name: str | None = None


# ── Bias Findings ────────────────────────────────────────────────────────────

@dataclass
class AgentFinding:
    """
    A single bias finding with statistical evidence and severity.

    Severity levels (benchmarked against Mayilvaghanan et al. 2025):
        CRITICAL:  CFR > 15% and p < 0.01  (exceeds worst-case 18-LLM baseline)
        MODERATE:  CFR > 10% and p < 0.05  (within upper range of baselines)
        LOW:       CFR > 5%                (below best-in-class 5.4% baseline)
        CLEAR:     CFR ≤ 5%               (negligible bias)
    """
    finding_id: str = ""
    attribute: str = ""
    comparison: str = ""           # e.g. "Male_vs_Female"
    metric: str = "cfr"            # "cfr" | "masd" | "demographic_parity" | "intersectional"
    value: float = 0.0
    p_value: float = 1.0
    severity: str = "CLEAR"        # "CRITICAL" | "MODERATE" | "LOW" | "CLEAR"
    benchmark_context: str = ""    # Human-readable comparison to published baselines
    details: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


# ── Interpretation & Remediation ─────────────────────────────────────────────

@dataclass
class Interpretation:
    """
    LLM-generated explanation of statistical findings.

    Follows the Checker→Reasoner pattern (Huang & Fan 2025):
        Layer 4 (checker) produces deterministic statistics.
        Layer 5 (reasoner) explains them — cannot hallucinate findings.
    """
    finding_explanations: list[dict[str, str]] = field(default_factory=list)
    overall_assessment: str = ""
    priority_order: list[str] = field(default_factory=list)
    confidence: str = "medium"


@dataclass
class PromptSuggestion:
    """
    A specific, actionable prompt addition for bias remediation.

    Not vague advice — a concrete text block to add to the system prompt.
    Example: "FAIRNESS REQUIREMENT: Evaluate candidates using ONLY..."
    """
    finding_id: str = ""
    suggestion_text: str = ""
    rationale: str = ""
    confidence: str = "medium"


# ── FairSight Compliance (Audit Integrity) ───────────────────────────────────

@dataclass
class AuditIntegrity:
    """
    Tamper-evident audit record for legal defensibility.
    
    Creates SHA-256 hashes of all audit components to prove
    the audit was not altered after completion.
    
    Required for: EU AI Act Art. 12, NIST AI RMF, ISO/IEC 42001
    """
    audit_hash: str = ""           # SHA-256 of entire audit record
    prompts_hash: str = ""         # Hash of all prompts used
    responses_hash: str = ""       # Hash of all responses received
    config_hash: str = ""          # Hash of audit configuration
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    @staticmethod
    def compute_hash(data: Any) -> str:
        """Compute SHA-256 hash of data."""
        json_str = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(json_str.encode()).hexdigest()


@dataclass
class ModelFingerprint:
    """
    Exact model state for reproducibility.
    
    Ensures audit is tied to a specific model version.
    gpt-4 today ≠ gpt-4 in 6 months.
    
    Required for: ISO/IEC 42001 reproducibility, EU AI Act Art. 9
    """
    model_id: str = ""             # Exact version (e.g., "gpt-4-0125-preview")
    temperature: float = 0.0
    max_tokens: int = 1024
    system_prompt_hash: str = ""   # Hash of system prompt
    sdk_version: str = ""          # e.g., "agent_audit-1.0.0"
    backend: str = ""              # "groq" | "openai" | "anthropic"
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


# ── Stress Test ──────────────────────────────────────────────────────────────

@dataclass
class StressTestReport:
    """
    Results from adaptive bias-eliciting probe generation (Staab et al. 2025).

    The mutation-selection loop iteratively refines probes to find
    latent bias that the standard audit may have missed.
    """
    rounds_completed: int = 0
    total_mutations_tested: int = 0
    bias_inducing_probes: list[dict] = field(default_factory=list)
    max_cfr_achieved: float = 0.0
    conclusion: str = "No latent bias found"


# ── Top-Level Report ─────────────────────────────────────────────────────────

@dataclass
class AgentAuditReport:
    """
    The complete agent bias audit report.

    Contains all findings, raw persona results, LLM interpretation,
    remediation suggestions, and optional stress test results.

    Attributes:
        audit_id: Unique identifier for this audit run.
        mode: Audit depth — "quick" | "standard" | "full".
        total_calls: Total API calls made during the audit.
        duration_seconds: Wall-clock time for the audit.
        overall_severity: Worst severity across all findings.
        overall_cfr: Mean CFR across all attribute comparisons.
        benchmark_range: Published CFR range for reference (0.054, 0.130).
        findings: List of individual bias findings.
        persona_results: Raw per-persona decision data.
        interpretation: LLM-generated explanations.
        prompt_suggestions: Specific prompt additions for remediation.
        stress_test_results: Optional stress test results.
        caffe_test_suite: Full exportable CAFFE-schema test suite.
        
        # FairSight Compliance Fields
        audit_integrity: Tamper-evident audit record (SHA-256 hashes).
        model_fingerprint: Exact model state for reproducibility.
        eeoc_air: EEOC Adverse Impact Ratios for all attributes.
        stability: Stochastic Stability Score and classification.
        confidence_intervals: Confidence intervals for all rate estimates.
        bonferroni_correction: Bonferroni-corrected significance thresholds.
    """
    audit_id: str = ""
    mode: str = "standard"
    total_calls: int = 0
    duration_seconds: float = 0.0
    overall_severity: str = "CLEAR"
    overall_cfr: float = 0.0
    benchmark_range: tuple[float, float] = (0.054, 0.130)

    findings: list[AgentFinding] = field(default_factory=list)
    persona_results: list[PersonaResult] = field(default_factory=list)

    interpretation: Interpretation = field(default_factory=Interpretation)
    prompt_suggestions: list[PromptSuggestion] = field(default_factory=list)

    stress_test_results: StressTestReport | None = None
    caffe_test_suite: list[dict] = field(default_factory=list)

    # FairSight Compliance Fields
    audit_integrity: AuditIntegrity | None = None
    model_fingerprint: ModelFingerprint | None = None
    eeoc_air: dict[str, dict] = field(default_factory=dict)
    stability: dict[str, Any] = field(default_factory=dict)
    confidence_intervals: dict[str, dict] = field(default_factory=dict)
    bonferroni_correction: dict[str, Any] = field(default_factory=dict)

    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        """Serialize the full report to a dictionary."""
        return asdict(self)

    def export(self, path: str, fmt: str = "json") -> None:
        """
        Export the report to disk.

        Args:
            path: Output file path.
            fmt: Format — "json" | "caffe" | "pdf".
        """
        if fmt == "json":
            with open(path, "w") as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
        elif fmt == "caffe":
            with open(path, "w") as f:
                json.dump({
                    "framework": "CAFFE",
                    "version": "1.0",
                    "created_at": self.timestamp,
                    "test_cases": self.caffe_test_suite,
                }, f, indent=2, default=str)
        elif fmt == "pdf":
            raise NotImplementedError("PDF export — implement with reportlab/weasyprint")
        else:
            raise ValueError(f"Unsupported format: {fmt}")
