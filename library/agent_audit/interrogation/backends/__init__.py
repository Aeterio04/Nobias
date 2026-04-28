"""
agent_audit.interrogation.backends — LLM Backend Implementations
==================================================================

Provides async agent callers for different LLM providers:
    - OpenAI (GPT-4o, GPT-4, etc.)
    - Groq (Llama, Mixtral - fast and affordable)
    - Google Gemini (gemini-1.5-pro, gemini-pro, etc.)
    - Anthropic (Claude)
    - Ollama (Local models)
"""

from agent_audit.interrogation.backends.openai import OpenAIBackend
from agent_audit.interrogation.backends.groq import GroqBackend
from agent_audit.interrogation.backends.gemini import GeminiBackend

__all__ = ["OpenAIBackend", "GroqBackend", "GeminiBackend"]
