"""
agent_audit.context — Layer 1: Context Collection & Agent Interface
=====================================================================

Handles agent connection setup and provides a unified interface
for interrogating agents regardless of how they're accessed.

Three connection modes:
    1. System Prompt: User provides prompt text + LLM backend + API key
    2. API Endpoint: User provides URL, auth, request/response templates
    3. Log Replay: User provides JSONL file of past interactions
"""

from agent_audit.context.agent_connector import AgentConnector, build_agent_connector
from agent_audit.context.validators import validate_config, validate_seed_case

__all__ = [
    "AgentConnector",
    "build_agent_connector",
    "validate_config",
    "validate_seed_case",
]
