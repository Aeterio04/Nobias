"""
agent_audit.api — Public API (Levels 1 & 2)
=============================================

Provides two levels of API:
    Level 1: audit_agent() - One-liner function
    Level 2: AgentAuditor - Class-based interface

Both wrap the internal PipelineOrchestrator.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Callable

from agent_audit.config import (
    AgentAuditConfig,
    AgentConnectionMode,
    AuditMode,
    PromptAgentConfig,
    APIAgentConfig,
    ReplayAgentConfig,
)
from agent_audit.context import build_agent_connector, validate_config, validate_seed_case
from agent_audit.models import AgentAuditReport
from agent_audit.orchestrator import PipelineOrchestrator
from agent_audit.report import compare_audits

# Configure logger
logger = logging.getLogger(__name__)


# ══════════════════════════════════════════════════════════════════════════════
# Level 1: One-Liner Function API
# ══════════════════════════════════════════════════════════════════════════════

async def audit_agent(
    system_prompt: str,
    seed_case: str,
    api_key: str,
    mode: str = "standard",
    model: str = "llama-3.1-70b-versatile",
    attributes: list[str] | None = None,
    domain: str = "general",
    positive_outcome: str = "approved",
    negative_outcome: str = "rejected",
    output_type: str = "binary",
    rate_limit_rps: int = 10,
    enable_stress_test: bool = False,
    progress_callback: Callable[[str, int, int], None] | None = None,
) -> AgentAuditReport:
    """
    One-liner audit function - simplest way to audit an agent.

    Args:
        system_prompt: The agent's system prompt.
        seed_case: Template input case (e.g., "Evaluate: Name: Alex...").
        api_key: API key for the LLM backend (Groq, OpenAI, etc.).
        mode: Audit depth - "quick" | "standard" | "full".
        model: Model name (auto-detects backend: llama→Groq, gpt→OpenAI).
        attributes: Protected attributes to test (default: ["gender", "race", "age"]).
        domain: Decision domain (e.g., "hiring", "lending").
        positive_outcome: Positive decision string (e.g., "hired").
        negative_outcome: Negative decision string (e.g., "rejected").
        output_type: How to parse output - "binary" | "numeric_score" | "free_text" | "chain_of_thought".
        rate_limit_rps: Requests per second limit.
        enable_stress_test: Whether to run adaptive stress test.
        progress_callback: Optional callback(stage, current, total).

    Returns:
        AgentAuditReport with findings, severity, and remediation suggestions.

    Example:
        >>> report = await audit_agent(
        ...     system_prompt="You are a hiring assistant...",
        ...     seed_case="Evaluate: Name: Alex, Experience: 5 years",
        ...     api_key="gsk_...",
        ... )
        >>> print(report.overall_severity)
        >>> print(report.overall_cfr)
    """
    logger.info("=== audit_agent() called ===")
    logger.debug(f"  Mode: {mode}")
    logger.debug(f"  Model: {model}")
    logger.debug(f"  Attributes: {attributes}")
    logger.debug(f"  Rate limit: {rate_limit_rps} req/s")
    
    # Create auditor using from_prompt factory
    auditor = AgentAuditor.from_prompt(
        system_prompt=system_prompt,
        api_key=api_key,
        mode=mode,
        model=model,
        attributes=attributes,
        domain=domain,
        positive_outcome=positive_outcome,
        negative_outcome=negative_outcome,
        output_type=output_type,
        rate_limit_rps=rate_limit_rps,
        enable_stress_test=enable_stress_test,
    )
    
    # Run audit
    return await auditor.run(
        seed_case=seed_case,
        progress_callback=progress_callback,
    )


# ══════════════════════════════════════════════════════════════════════════════
# Level 2: Class-Based API
# ══════════════════════════════════════════════════════════════════════════════

class AgentAuditor:
    """
    Class-based auditor interface - for power users who need control.

    Provides:
        - Reusable auditor instance
        - Multiple runs with same config
        - Before/after comparison
        - Progress tracking

    Example:
        >>> auditor = AgentAuditor.from_prompt(
        ...     system_prompt="You are a hiring assistant...",
        ...     api_key="gsk_...",
        ...     mode="standard",
        ... )
        >>> report = await auditor.run(seed_case="...")
        >>> 
        >>> # Update prompt and re-run
        >>> auditor.update_prompt("Improved prompt...")
        >>> report_after = await auditor.run(seed_case="...")
        >>> 
        >>> # Compare
        >>> comparison = auditor.compare(report, report_after)
    """

    def __init__(self, config: AgentAuditConfig):
        """
        Create an auditor from a full config.

        For most users, use the factory methods instead:
            - AgentAuditor.from_prompt()
            - AgentAuditor.from_api()
            - AgentAuditor.from_logs()
        """
        self.config = config
        self._connection_mode: AgentConnectionMode | None = None
        self._connection_config: PromptAgentConfig | APIAgentConfig | ReplayAgentConfig | None = None
        self._system_prompt: str | None = None

    # ── Factory Methods ──────────────────────────────────────────────────────

    @classmethod
    def from_prompt(
        cls,
        system_prompt: str,
        api_key: str,
        mode: str = "standard",
        model: str = "llama-3.1-70b-versatile",
        attributes: list[str] | None = None,
        domain: str = "general",
        **kwargs,
    ) -> AgentAuditor:
        """
        Create auditor from a system prompt (development mode).

        Args:
            system_prompt: The agent's system prompt.
            api_key: API key for the LLM backend.
            mode: Audit depth - "quick" | "standard" | "full".
            model: Model name (auto-detects backend).
            attributes: Protected attributes to test.
            domain: Decision domain.
            **kwargs: Additional config options.

        Returns:
            Configured AgentAuditor instance.
        """
        config = AgentAuditConfig(
            mode=AuditMode(mode),
            domain=domain,
            protected_attributes=attributes or ["gender", "race", "age"],
            backend=_detect_backend(model),
            api_key=api_key,
            model=model,
            **kwargs,
        )

        auditor = cls(config)
        auditor._connection_mode = AgentConnectionMode.SYSTEM_PROMPT
        auditor._connection_config = PromptAgentConfig(
            system_prompt=system_prompt,
            model_backend=model,
            api_key=api_key,
            temperature=0.0,
            enable_smart_rate_limiting=config.enable_smart_rate_limiting,
            max_concurrent_requests=config.max_concurrent_requests,
            tpm_limit=config.tpm_limit,
        )
        auditor._system_prompt = system_prompt
        return auditor

    @classmethod
    def from_api(
        cls,
        endpoint_url: str,
        auth_header: dict,
        request_template: dict,
        response_path: str = "$.result",
        mode: str = "standard",
        attributes: list[str] | None = None,
        domain: str = "general",
        **kwargs,
    ) -> AgentAuditor:
        """
        Create auditor for a deployed API endpoint (production mode).

        Args:
            endpoint_url: API endpoint URL.
            auth_header: Auth headers (e.g., {"Authorization": "Bearer ..."}).
            request_template: Request body template with {input} placeholder.
            response_path: JSONPath to extract decision from response.
            mode: Audit depth.
            attributes: Protected attributes to test.
            domain: Decision domain.
            **kwargs: Additional config options.

        Returns:
            Configured AgentAuditor instance.
        """
        config = AgentAuditConfig(
            mode=AuditMode(mode),
            domain=domain,
            protected_attributes=attributes or ["gender", "race", "age"],
            **kwargs,
        )

        auditor = cls(config)
        auditor._connection_mode = AgentConnectionMode.API_ENDPOINT
        auditor._connection_config = APIAgentConfig(
            endpoint_url=endpoint_url,
            auth_header=auth_header,
            request_template=request_template,
            response_path=response_path,
        )
        return auditor

    @classmethod
    def from_logs(
        cls,
        log_file: str | Path,
        input_field: str = "input",
        output_field: str = "output",
        mode: str = "standard",
        attributes: list[str] | None = None,
        domain: str = "general",
        **kwargs,
    ) -> AgentAuditor:
        """
        Create auditor from historical logs (privacy-friendly mode).

        Args:
            log_file: Path to JSONL file with past interactions.
            input_field: JSON key for input.
            output_field: JSON key for output.
            mode: Audit depth.
            attributes: Protected attributes to test.
            domain: Decision domain.
            **kwargs: Additional config options.

        Returns:
            Configured AgentAuditor instance.
        """
        config = AgentAuditConfig(
            mode=AuditMode(mode),
            domain=domain,
            protected_attributes=attributes or ["gender", "race", "age"],
            **kwargs,
        )

        auditor = cls(config)
        auditor._connection_mode = AgentConnectionMode.LOG_REPLAY
        auditor._connection_config = ReplayAgentConfig(
            log_file=Path(log_file),
            input_field=input_field,
            output_field=output_field,
        )
        return auditor

    # ── Main Methods ─────────────────────────────────────────────────────────

    async def run(
        self,
        seed_case: str,
        system_prompt: str | None = None,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> AgentAuditReport:
        """
        Run the full audit pipeline.

        Args:
            seed_case: Template input case.
            system_prompt: Optional system prompt (for remediation suggestions).
            progress_callback: Optional callback(stage, current, total).

        Returns:
            AgentAuditReport with findings and suggestions.
        """
        # Validate
        seed_errors = validate_seed_case(seed_case)
        if seed_errors:
            raise ValueError(f"Invalid seed case: {seed_errors}")

        if self._connection_mode is None or self._connection_config is None:
            raise RuntimeError(
                "Auditor not properly initialized. Use from_prompt(), from_api(), or from_logs()."
            )

        config_errors = validate_config(
            self.config, self._connection_mode, self._connection_config
        )
        if config_errors:
            raise ValueError(f"Invalid configuration: {config_errors}")

        # Build connector
        connector = build_agent_connector(self._connection_mode, self._connection_config)

        # Run pipeline
        orchestrator = PipelineOrchestrator(self.config)
        report = await orchestrator.run_pipeline(
            connector=connector,
            seed_case=seed_case,
            system_prompt=system_prompt or self._system_prompt,
            progress_callback=progress_callback,
        )

        return report

    def update_prompt(self, new_prompt: str) -> None:
        """
        Update the system prompt (for before/after comparison).

        Only works for system-prompt mode.

        Args:
            new_prompt: The new system prompt.
        """
        if self._connection_mode != AgentConnectionMode.SYSTEM_PROMPT:
            raise RuntimeError("update_prompt() only works in system-prompt mode")

        if isinstance(self._connection_config, PromptAgentConfig):
            self._connection_config.system_prompt = new_prompt
            self._system_prompt = new_prompt

    @staticmethod
    def compare(
        before: AgentAuditReport,
        after: AgentAuditReport,
    ) -> dict:
        """
        Compare two audit reports (before/after remediation).

        Args:
            before: The original audit report.
            after: The post-remediation audit report.

        Returns:
            Dict with per-finding comparisons and summary statistics.
        """
        return compare_audits(before, after)


# ══════════════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════════════

def _detect_backend(model: str) -> str:
    """Auto-detect backend from model name."""
    model_lower = model.lower()
    if any(x in model_lower for x in ["llama", "mixtral", "gemma", "groq"]):
        return "groq"
    elif model_lower.startswith("gpt"):
        return "openai"
    elif model_lower.startswith("claude"):
        return "anthropic"
    return "groq"  # Default to Groq
