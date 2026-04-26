"""
agent_audit.agents.base — Base Agent Interface
===============================================

Abstract base class for all agent types.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict


@dataclass
class AgentResponse:
    """
    Standardized agent response.
    
    Attributes:
        output: The agent's text output
        metadata: Optional metadata (tokens, latency, etc.)
        raw_response: Raw response from underlying system
    """
    output: str
    metadata: Dict[str, Any] = None
    raw_response: Any = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class BaseAgent(ABC):
    """
    Abstract base class for all agent types.
    
    Subclasses must implement the `invoke` method.
    """
    
    def __init__(self, llm: Any = None, **kwargs):
        """
        Initialize agent.
        
        Args:
            llm: Language model instance (optional, depends on agent type)
            **kwargs: Additional agent-specific configuration
        """
        self.llm = llm
        self.config = kwargs
    
    @abstractmethod
    async def invoke(self, input_text: str, **kwargs) -> AgentResponse:
        """
        Execute the agent with given input.
        
        Args:
            input_text: Input text to process
            **kwargs: Additional invocation parameters
        
        Returns:
            AgentResponse with output and metadata
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(llm={self.llm})"
