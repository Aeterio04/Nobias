"""
nobias.agent_audit — Black-Box Bias Auditor for LLM Agents
===========================================================

Accept an LLM agent (system prompt or API endpoint) + decision context
+ seed case → generate counterfactual persona grids (pairwise + name-based
+ context-primed) → interrogate the agent → statistically detect bias using
CFR/MASD → interpret findings with a constrained LLM → produce a
severity-graded report + prompt surgery suggestions.

Research foundations:
    - CAFFE (Parziale et al. 2025)
    - CFR/MASD (Mayilvaghanan et al. 2025)
    - Structured Reasoning (Huang & Fan 2025)
    - Adaptive Probing (Staab et al. 2025)
    - Bertrand & Mullainathan (2004) name-demographic associations

Public API:
    audit_agent()       — One-liner async audit entry point
    AgentAuditor        — Granular control via class-based interface
    AgentAuditConfig    — Configuration dataclass
    AgentAuditReport    — Structured report object
    compare_audits()    — Before/after comparison
"""

from agent_audit.config import AgentAuditConfig, AuditMode, DecisionContext
from agent_audit.models import AgentAuditReport, AgentFinding, PersonaResult
from agent_audit.report import compare_audits

__all__ = [
    "audit_agent",
    "AgentAuditor",
    "AgentAuditConfig",
    "AgentAuditReport",
    "compare_audits",
]


class AgentAuditor:
    """
    Main orchestrator for the agent bias audit pipeline.

    Coordinates all five layers:
        Layer 1 — Context Collection & Agent Interface
        Layer 2 — Persona Grid Generation
        Layer 3 — Agent Interrogation Engine
        Layer 4 — Statistical Bias Detection (pure Python, no LLM)
        Layer 5 — LLM Interpreter & Remediation
    """

    def __init__(self, config: AgentAuditConfig):
        self.config = config

    async def run(self, system_prompt: str, seed_case: str) -> AgentAuditReport:
        """Execute the full audit pipeline and return a structured report."""
        raise NotImplementedError("Pipeline orchestration — implement in Phase 2")


async def audit_agent(
    system_prompt: str,
    seed_case: str,
    mode: str = "standard",
    attributes: list[str] | None = None,
    backend: str = "openai",
    api_key: str | None = None,
    context: dict | None = None,
) -> AgentAuditReport:
    """
    One-liner async audit entry point.

    Args:
        system_prompt: The agent's system prompt text.
        seed_case: One representative input to the agent.
        mode: Audit depth — "quick" | "standard" | "full".
        attributes: Protected attributes to test (e.g. ["gender", "race", "age"]).
        backend: LLM backend — "openai" | "anthropic" | "ollama".
        api_key: API key for the chosen backend.
        context: Decision context dict with keys: domain, positive, negative.

    Returns:
        AgentAuditReport with findings, severity, and remediation suggestions.
    """
    ctx = context or {}
    config = AgentAuditConfig(
        mode=AuditMode(mode),
        domain=ctx.get("domain", "general"),
        positive_outcome=ctx.get("positive", "approved"),
        negative_outcome=ctx.get("negative", "rejected"),
        output_type="binary",
        protected_attributes=attributes or ["gender", "race", "age"],
        backend=backend,
        api_key=api_key,
    )
    auditor = AgentAuditor(config)
    return await auditor.run(system_prompt=system_prompt, seed_case=seed_case)
