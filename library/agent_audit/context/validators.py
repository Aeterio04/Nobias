"""
agent_audit.context.validators — Input Validation
===================================================

Validates user-provided configuration and seed cases before
starting the audit pipeline.

Catches common errors early:
    - Missing API keys
    - Invalid model names
    - Empty seed cases
    - Malformed API endpoint configs
"""

from __future__ import annotations

from pathlib import Path

from agent_audit.config import (
    AgentAuditConfig,
    AgentConnectionMode,
    PromptAgentConfig,
    APIAgentConfig,
    ReplayAgentConfig,
)


def validate_config(
    config: AgentAuditConfig,
    connection_mode: AgentConnectionMode,
    connection_config: PromptAgentConfig | APIAgentConfig | ReplayAgentConfig,
) -> list[str]:
    """
    Validate the audit configuration.

    Args:
        config: The main audit config.
        connection_mode: How the agent is accessed.
        connection_config: Mode-specific connection config.

    Returns:
        List of error messages (empty if valid).
    """
    errors: list[str] = []

    # Validate protected attributes
    if not config.protected_attributes:
        errors.append("At least one protected attribute must be specified")

    # Validate mode-specific config
    if connection_mode == AgentConnectionMode.SYSTEM_PROMPT:
        errors.extend(_validate_prompt_config(connection_config))
    elif connection_mode == AgentConnectionMode.API_ENDPOINT:
        errors.extend(_validate_api_config(connection_config))
    elif connection_mode == AgentConnectionMode.LOG_REPLAY:
        errors.extend(_validate_replay_config(connection_config))

    # Validate rate limiting
    if config.rate_limit_rps <= 0:
        errors.append("Rate limit must be positive")

    return errors


def validate_seed_case(seed_case: str) -> list[str]:
    """
    Validate the seed case input.

    Args:
        seed_case: The template input text.

    Returns:
        List of error messages (empty if valid).
    """
    errors: list[str] = []

    if not seed_case or not seed_case.strip():
        errors.append("Seed case cannot be empty")

    if len(seed_case.strip()) < 10:
        errors.append("Seed case is too short (minimum 10 characters)")

    # Check for common placeholder patterns that might indicate
    # the user forgot to fill in the template
    suspicious_patterns = ["{name}", "{age}", "[NAME]", "[AGE]", "TODO", "FIXME"]
    for pattern in suspicious_patterns:
        if pattern in seed_case:
            errors.append(
                f"Seed case contains placeholder '{pattern}' — "
                f"please provide a complete example"
            )

    return errors


# ── Mode-Specific Validators ─────────────────────────────────────────────────

def _validate_prompt_config(config: PromptAgentConfig | Any) -> list[str]:
    """Validate system-prompt mode config."""
    errors: list[str] = []

    if not isinstance(config, PromptAgentConfig):
        errors.append("Invalid config type for SYSTEM_PROMPT mode")
        return errors

    if not config.system_prompt or not config.system_prompt.strip():
        errors.append("System prompt cannot be empty")

    if not config.model_backend:
        errors.append("Model backend must be specified")

    # Check if API key is required for this backend
    model_lower = config.model_backend.lower()
    requires_key = any(
        x in model_lower
        for x in ["gpt", "llama", "mixtral", "gemma", "groq", "claude"]
    )
    if requires_key and not config.api_key:
        errors.append(f"API key required for model: {config.model_backend}")

    if config.temperature < 0 or config.temperature > 2:
        errors.append("Temperature must be between 0 and 2")

    if config.max_tokens <= 0:
        errors.append("max_tokens must be positive")

    return errors


def _validate_api_config(config: APIAgentConfig | Any) -> list[str]:
    """Validate API-endpoint mode config."""
    errors: list[str] = []

    if not isinstance(config, APIAgentConfig):
        errors.append("Invalid config type for API_ENDPOINT mode")
        return errors

    if not config.endpoint_url:
        errors.append("API endpoint URL must be specified")

    if not config.endpoint_url.startswith(("http://", "https://")):
        errors.append("API endpoint URL must start with http:// or https://")

    if not config.request_template:
        errors.append("Request template cannot be empty")

    if "{input}" not in str(config.request_template):
        errors.append("Request template must contain {input} placeholder")

    if not config.response_path:
        errors.append("Response JSONPath must be specified")

    if config.rate_limit_rps <= 0:
        errors.append("Rate limit must be positive")

    return errors


def _validate_replay_config(config: ReplayAgentConfig | Any) -> list[str]:
    """Validate log-replay mode config."""
    errors: list[str] = []

    if not isinstance(config, ReplayAgentConfig):
        errors.append("Invalid config type for LOG_REPLAY mode")
        return errors

    if not config.log_file:
        errors.append("Log file path must be specified")

    if not Path(config.log_file).exists():
        errors.append(f"Log file not found: {config.log_file}")

    if not Path(config.log_file).suffix == ".jsonl":
        errors.append("Log file must be in JSONL format (.jsonl extension)")

    if not config.input_field:
        errors.append("Input field name must be specified")

    if not config.output_field:
        errors.append("Output field name must be specified")

    return errors
