"""
agent_audit.config — Configuration dataclasses and enums
=========================================================

Houses all configuration objects that flow through the pipeline:
    - AuditMode          — quick | standard | full
    - OutputType         — binary | numeric_score | free_text | chain_of_thought
    - AgentConnectionMode — prompt | api | replay
    - DecisionContext    — domain, outcomes, protected attributes
    - AgentAuditConfig   — top-level config combining everything
    - PromptAgentConfig  — config for system-prompt mode
    - APIAgentConfig     — config for API-endpoint mode
    - ReplayAgentConfig  — config for log-replay mode
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


# ── Enums ────────────────────────────────────────────────────────────────────

class AuditMode(Enum):
    """
    Controls audit depth and API call budget.

    | Mode     | Grid       | Names | Context Primes | Runs/persona | Expected calls |
    |----------|------------|-------|----------------|-------------|----------------|
    | quick    | Pairwise   | 0     | No             | 1 (fixed)   | ~14            |
    | standard | Pairwise   | 10    | No             | 1-3 adaptive| ~28            |
    | full     | Factorial  | All   | Yes (5 primes) | 1-5 adaptive| ~400-600       |
    """
    QUICK = "quick"
    STANDARD = "standard"
    FULL = "full"


class OutputType(Enum):
    """How the agent's response should be parsed."""
    BINARY = "binary"                  # keyword match for positive/negative
    NUMERIC_SCORE = "numeric_score"    # regex extraction, normalise to 0-1
    FREE_TEXT = "free_text"            # keyword-based sentiment
    CHAIN_OF_THOUGHT = "chain_of_thought"  # extract final decision + reasoning trace


class AgentConnectionMode(Enum):
    """How the auditor connects to the agent under test."""
    SYSTEM_PROMPT = "prompt"   # User provides prompt text + LLM backend + API key
    API_ENDPOINT = "api"       # User provides URL, auth header, request template
    LOG_REPLAY = "replay"      # User provides JSONL file of past interactions


# ── Agent Connection Configs ─────────────────────────────────────────────────

@dataclass
class PromptAgentConfig:
    """
    Config for testing an agent via its system prompt.
    
    The auditor constructs full LLM calls using the provided prompt
    and sends test inputs through the chosen backend.
    """
    system_prompt: str
    model_backend: str = "llama-3.1-8b-instant"
    api_key: str | None = None
    temperature: float = 0.0
    max_tokens: int = 1024
    
    # Smart rate limiting (automatic, enabled by default)
    enable_smart_rate_limiting: bool = True
    max_concurrent_requests: int = 3
    tpm_limit: int = 5500


@dataclass
class APIAgentConfig:
    """
    Config for testing an agent via its API endpoint.
    
    The auditor POSTs test inputs using the request template
    and extracts decisions from the response via JSONPath.
    """
    endpoint_url: str
    auth_header: dict = field(default_factory=dict)
    request_template: dict = field(default_factory=dict)  # JSON with {input} placeholder
    response_path: str = "$.result"    # JSONPath to extract decision
    rate_limit_rps: int = 5


@dataclass
class ReplayAgentConfig:
    """
    Config for testing from historical logs (no API calls needed).
    
    Each line of the JSONL file should contain an input/output pair.
    Privacy-friendly: no data leaves the machine.
    """
    log_file: Path = field(default_factory=lambda: Path("interactions.jsonl"))
    input_field: str = "input"
    output_field: str = "output"


# ── Decision Context ─────────────────────────────────────────────────────────

@dataclass
class DecisionContext:
    """
    Describes what the agent does and how to interpret its outputs.
    
    This shapes metric interpretation and report language.
    
    Attributes:
        domain: The decision domain (e.g. "hiring", "lending", "medical_triage").
        positive_outcome: The favorable decision string (e.g. "hired", "approved").
        negative_outcome: The unfavorable decision string (e.g. "rejected", "denied").
        protected_attributes: List of attributes to test for bias.
        decision_output_type: How the agent's output should be parsed.
        custom_extraction_hint: Optional hint for output parsing.
    """
    domain: str = "general"
    positive_outcome: str = "approved"
    negative_outcome: str = "rejected"
    protected_attributes: list[str] = field(
        default_factory=lambda: ["gender", "race", "age"]
    )
    decision_output_type: OutputType = OutputType.BINARY
    custom_extraction_hint: str | None = None


# ── Top-Level Audit Config ───────────────────────────────────────────────────

@dataclass
class AgentAuditConfig:
    """
    Top-level configuration for an agent bias audit.
    
    Combines the audit mode, decision context, backend config,
    and rate-limiting parameters into a single object.
    """
    # Audit depth
    mode: AuditMode = AuditMode.STANDARD

    # Decision context
    domain: str = "general"
    positive_outcome: str = "approved"
    negative_outcome: str = "rejected"
    output_type: str = "binary"
    protected_attributes: list[str] = field(
        default_factory=lambda: ["gender", "race", "age"]
    )

    # Backend
    backend: str = "openai"
    
    # Response normalizer (maps agent vocabulary to positive/negative)
    response_normalizer: dict[str, str] | None = None
    api_key: str | None = None
    model: str = "llama-3.1-8b-instant"
    temperature: float = 0.0
    max_tokens: int = 1024

    # Rate limiting
    rate_limit_rps: int = 10
    
    # Advanced rate limiting (automatic, can be disabled)
    enable_smart_rate_limiting: bool = True  # Token-aware rate limiting
    max_concurrent_requests: int = 3  # Limit concurrent API calls
    tpm_limit: int = 5500  # Tokens per minute limit (for Groq/budget providers)

    # Stress test
    enable_stress_test: bool = False

    # Token optimization (internal - enabled by default)
    enable_optimization: bool = True
    use_prompt_caching: bool = True
    use_two_pass_evaluation: bool = True
    optimization_tier: str = "tier_1"  # "tier_1" | "tier_2" | "tier_3" | "adaptive"

    def to_decision_context(self) -> DecisionContext:
        """Convert to a DecisionContext for downstream layers."""
        return DecisionContext(
            domain=self.domain,
            positive_outcome=self.positive_outcome,
            negative_outcome=self.negative_outcome,
            protected_attributes=self.protected_attributes,
            decision_output_type=OutputType(self.output_type),
        )
