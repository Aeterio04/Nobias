"""
agent_audit.interrogation.backends — LLM Backend Implementations
==================================================================

Provides async agent callers for different LLM providers:
    - OpenAI (GPT-4o, GPT-4, etc.)
    - Groq (Llama, Mixtral - fast and affordable)
    - Anthropic (Claude - future)
    - Ollama (Local models - future)
"""

from agent_audit.interrogation.backends.openai import OpenAIBackend
from agent_audit.interrogation.backends.groq import GroqBackend

__all__ = ["OpenAIBackend", "GroqBackend"]
