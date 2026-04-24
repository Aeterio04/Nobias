"""
agent_audit.context.agent_connector — Agent Connection Factory
================================================================

Builds the appropriate agent caller based on connection mode:
    - SystemPrompt: Wraps an LLM backend with the user's system prompt
    - APIEndpoint: POSTs to a user-provided API with request templating
    - LogReplay: Reads from a JSONL file (no API calls)

All connectors expose a unified async .call(input: str) -> str interface.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable

import aiohttp

from agent_audit.config import (
    AgentConnectionMode,
    PromptAgentConfig,
    APIAgentConfig,
    ReplayAgentConfig,
)


class AgentConnector:
    """
    Unified interface for calling an agent under test.

    Wraps different connection modes (system prompt, API, log replay)
    behind a single async .call() method.
    """

    def __init__(self, caller: Callable[[str], Any]):
        self._caller = caller

    async def call(self, input_text: str) -> str:
        """
        Send input to the agent and return the response.

        Args:
            input_text: The test case input.

        Returns:
            The agent's response text.
        """
        result = self._caller(input_text)
        # Support both sync and async callables
        if hasattr(result, "__await__"):
            return await result
        return result


def build_agent_connector(
    mode: AgentConnectionMode,
    config: PromptAgentConfig | APIAgentConfig | ReplayAgentConfig,
) -> AgentConnector:
    """
    Factory function to build the appropriate agent connector.

    Args:
        mode: The connection mode (prompt, api, replay).
        config: The mode-specific configuration object.

    Returns:
        AgentConnector with a unified .call() interface.

    Raises:
        ValueError: If mode/config combination is invalid.
    """
    if mode == AgentConnectionMode.SYSTEM_PROMPT:
        if not isinstance(config, PromptAgentConfig):
            raise ValueError("SYSTEM_PROMPT mode requires PromptAgentConfig")
        return _build_prompt_connector(config)

    elif mode == AgentConnectionMode.API_ENDPOINT:
        if not isinstance(config, APIAgentConfig):
            raise ValueError("API_ENDPOINT mode requires APIAgentConfig")
        return _build_api_connector(config)

    elif mode == AgentConnectionMode.LOG_REPLAY:
        if not isinstance(config, ReplayAgentConfig):
            raise ValueError("LOG_REPLAY mode requires ReplayAgentConfig")
        return _build_replay_connector(config)

    else:
        raise ValueError(f"Unknown connection mode: {mode}")


# ── System Prompt Mode ───────────────────────────────────────────────────────

def _build_prompt_connector(config: PromptAgentConfig) -> AgentConnector:
    """
    Build a connector for system-prompt mode.

    Wraps an LLM backend (OpenAI, Groq, etc.) with the user's system prompt.
    """
    backend = _get_backend_for_model(
        model=config.model_backend,
        api_key=config.api_key,
        system_prompt=config.system_prompt,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
    )

    async def caller(input_text: str) -> str:
        return await backend.call(input_text)

    return AgentConnector(caller)


def _get_backend_for_model(
    model: str,
    api_key: str | None,
    system_prompt: str,
    temperature: float,
    max_tokens: int,
) -> Any:
    """
    Get the appropriate backend instance for a model string.

    Supports:
        - "gpt-*" → OpenAI
        - "llama-*", "mixtral-*", "gemma-*" → Groq
        - "claude-*" → Anthropic (future)
        - "ollama/*" → Ollama (future)
    """
    model_lower = model.lower()

    # Groq models
    if any(x in model_lower for x in ["llama", "mixtral", "gemma", "groq"]):
        from agent_audit.interrogation.backends.groq import GroqBackend
        if not api_key:
            raise ValueError("Groq backend requires an API key")
        return GroqBackend(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # OpenAI models
    elif model_lower.startswith("gpt"):
        from agent_audit.interrogation.backends.openai import OpenAIBackend
        if not api_key:
            raise ValueError("OpenAI backend requires an API key")
        return OpenAIBackend(
            api_key=api_key,
            model=model,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    # Anthropic models (future)
    elif model_lower.startswith("claude"):
        raise NotImplementedError(
            "Anthropic backend not yet implemented. Use Groq or OpenAI for now."
        )

    # Ollama models (future)
    elif model_lower.startswith("ollama/"):
        raise NotImplementedError(
            "Ollama backend not yet implemented. Use Groq or OpenAI for now."
        )

    else:
        raise ValueError(
            f"Unknown model: {model}. Supported: gpt-*, llama-*, mixtral-*, gemma-*"
        )


# ── API Endpoint Mode ────────────────────────────────────────────────────────

def _build_api_connector(config: APIAgentConfig) -> AgentConnector:
    """
    Build a connector for API-endpoint mode.

    POSTs test inputs to a user-provided API endpoint using a request
    template and extracts the response via JSONPath.
    """
    async def caller(input_text: str) -> str:
        # Build request body from template
        request_body = _fill_template(config.request_template, input_text)

        # Make async HTTP POST
        async with aiohttp.ClientSession() as session:
            async with session.post(
                config.endpoint_url,
                json=request_body,
                headers=config.auth_header,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                if response.status != 200:
                    raise RuntimeError(
                        f"API endpoint returned status {response.status}: "
                        f"{await response.text()}"
                    )
                response_data = await response.json()

        # Extract decision from response using JSONPath
        result = _extract_from_jsonpath(response_data, config.response_path)
        return str(result)

    return AgentConnector(caller)


def _fill_template(template: dict, input_text: str) -> dict:
    """
    Fill a request template by replacing {input} placeholders.

    Args:
        template: Dict with {input} placeholders.
        input_text: The test case input to inject.

    Returns:
        Filled template dict.
    """
    template_str = json.dumps(template)
    filled_str = template_str.replace("{input}", input_text)
    return json.loads(filled_str)


def _extract_from_jsonpath(data: dict, path: str) -> Any:
    """
    Extract a value from a dict using a simple JSONPath expression.

    Supports basic paths like:
        - "$.result"
        - "$.data.decision"
        - "$.choices[0].message.content"

    Args:
        data: The JSON response dict.
        path: JSONPath expression.

    Returns:
        The extracted value.
    """
    # Remove leading "$." if present
    path = path.lstrip("$").lstrip(".")

    parts = re.split(r"[\.\[]", path)
    current = data

    for part in parts:
        if not part:
            continue

        # Handle array indexing: "choices[0]" → "0]"
        if part.endswith("]"):
            key = part.rstrip("]")
            if key.isdigit():
                current = current[int(key)]
            else:
                current = current[key]
        else:
            current = current[part]

    return current


# ── Log Replay Mode ──────────────────────────────────────────────────────────

def _build_replay_connector(config: ReplayAgentConfig) -> AgentConnector:
    """
    Build a connector for log-replay mode.

    Reads from a JSONL file of past interactions. No API calls are made.
    This is privacy-friendly and useful for auditing historical data.
    """
    # Load the log file into memory
    log_entries = _load_log_file(config.log_file, config.input_field, config.output_field)

    # Build a lookup dict: input → output
    lookup = {entry["input"]: entry["output"] for entry in log_entries}

    def caller(input_text: str) -> str:
        # Exact match lookup
        if input_text in lookup:
            return lookup[input_text]

        # Fuzzy match fallback (strip whitespace, case-insensitive)
        normalized_input = input_text.strip().lower()
        for log_input, log_output in lookup.items():
            if log_input.strip().lower() == normalized_input:
                return log_output

        # No match found
        raise ValueError(
            f"Input not found in log replay file: {input_text[:100]}..."
        )

    return AgentConnector(caller)


def _load_log_file(
    path: Path,
    input_field: str,
    output_field: str,
) -> list[dict[str, str]]:
    """
    Load a JSONL log file into a list of {input, output} dicts.

    Args:
        path: Path to the JSONL file.
        input_field: JSON key for the input.
        output_field: JSON key for the output.

    Returns:
        List of {input, output} dicts.
    """
    if not path.exists():
        raise FileNotFoundError(f"Log replay file not found: {path}")

    entries: list[dict[str, str]] = []
    with path.open("r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                entries.append({
                    "input": data.get(input_field, ""),
                    "output": data.get(output_field, ""),
                })
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON on line {line_num} of {path}: {e}"
                )

    if not entries:
        raise ValueError(f"Log replay file is empty: {path}")

    return entries
