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

═══════════════════════════════════════════════════════════════════════════════
PUBLIC API - Three Levels
═══════════════════════════════════════════════════════════════════════════════

Level 1: One-Liner (Simplest)
------------------------------
    from agent_audit import audit_agent
    
    report = await audit_agent(
        system_prompt="You are a hiring assistant...",
        seed_case="Evaluate: Name: Alex...",
        api_key="gsk_...",
    )

Level 2: Class-Based (Power Users)
-----------------------------------
    from agent_audit import AgentAuditor
    
    auditor = AgentAuditor.from_prompt(
        system_prompt="...",
        api_key="gsk_...",
    )
    report = await auditor.run(seed_case="...")
    
    # Before/after comparison
    auditor.update_prompt("Improved prompt...")
    report_after = await auditor.run(seed_case="...")
    comparison = auditor.compare(report, report_after)

Level 3: Manual Pipeline (Experts)
-----------------------------------
    from agent_audit.context import build_agent_connector
    from agent_audit.personas import generate_pairwise_grid
    from agent_audit.interrogation import InterrogationEngine
    # ... full control over each layer

═══════════════════════════════════════════════════════════════════════════════
"""

# ── Level 1 & 2 API ──────────────────────────────────────────────────────────
from agent_audit.api import audit_agent, AgentAuditor

# ── Config Classes ───────────────────────────────────────────────────────────
from agent_audit.config import (
    AgentAuditConfig,
    AuditMode,
    DecisionContext,
    AgentConnectionMode,
    PromptAgentConfig,
    APIAgentConfig,
    ReplayAgentConfig,
)

# ── Models ───────────────────────────────────────────────────────────────────
from agent_audit.models import (
    AgentAuditReport,
    AgentFinding,
    PersonaResult,
    Interpretation,
    PromptSuggestion,
)

# ── Report Utilities ─────────────────────────────────────────────────────────
from agent_audit.report import compare_audits, build_report_summary

# ── Level 3 API (Expert Mode) ────────────────────────────────────────────────
from agent_audit.context import build_agent_connector, validate_config, validate_seed_case
from agent_audit.personas.pairwise import generate_pairwise_grid
from agent_audit.personas.factorial import generate_factorial_grid
from agent_audit.personas.names import generate_name_variants
from agent_audit.personas.context_primes import generate_context_variants


__all__ = [
    # ── Level 1 & 2 API ──────────────────────────────────────────────────────
    "audit_agent",              # One-liner function
    "AgentAuditor",             # Class-based interface
    
    # ── Config Classes ───────────────────────────────────────────────────────
    "AgentAuditConfig",
    "AuditMode",
    "DecisionContext",
    "AgentConnectionMode",
    "PromptAgentConfig",
    "APIAgentConfig",
    "ReplayAgentConfig",
    
    # ── Models ───────────────────────────────────────────────────────────────
    "AgentAuditReport",
    "AgentFinding",
    "PersonaResult",
    "Interpretation",
    "PromptSuggestion",
    
    # ── Report Utilities ─────────────────────────────────────────────────────
    "compare_audits",
    "build_report_summary",
    
    # ── Level 3 API (Expert Mode) ────────────────────────────────────────────
    "build_agent_connector",
    "validate_config",
    "validate_seed_case",
    "generate_pairwise_grid",
    "generate_factorial_grid",
    "generate_name_variants",
    "generate_context_variants",
]
