"""
agent_audit.agents — Modular Agent Execution System
====================================================

Flexible agent execution framework supporting multiple agent types:
    - Simple LLM agents (prompt-based)
    - LangGraph agents (graph-based workflows)
    - Custom agents (user-defined)

Features:
    - Automatic retry with exponential backoff
    - Rate limit handling
    - Unified interface for all agent types
"""

from agent_audit.agents.base import BaseAgent, AgentResponse
from agent_audit.agents.simple import SimpleLLMAgent
from agent_audit.agents.langgraph_agent import LangGraphAgent
from agent_audit.agents.executor import AgentExecutor, execute_with_retry

__all__ = [
    "BaseAgent",
    "AgentResponse",
    "SimpleLLMAgent",
    "LangGraphAgent",
    "AgentExecutor",
    "execute_with_retry",
]
