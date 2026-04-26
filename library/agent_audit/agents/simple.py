"""
agent_audit.agents.simple — Simple LLM Agent
=============================================

Basic prompt-based agent using an LLM directly.
"""

from __future__ import annotations

from typing import Any

from agent_audit.agents.base import BaseAgent, AgentResponse


class SimpleLLMAgent(BaseAgent):
    """
    Simple agent that sends prompts directly to an LLM.
    
    Usage:
        from langchain_groq import ChatGroq
        
        llm = ChatGroq(model="llama-3.1-8b-instant")
        agent = SimpleLLMAgent(llm=llm, system_prompt="You are a helpful assistant")
        
        response = await agent.invoke("What is 2+2?")
        print(response.output)
    """
    
    def __init__(
        self,
        llm: Any,
        system_prompt: str = "",
        **kwargs
    ):
        """
        Initialize simple LLM agent.
        
        Args:
            llm: LangChain-compatible LLM instance
            system_prompt: System prompt to prepend to all inputs
            **kwargs: Additional configuration
        """
        super().__init__(llm=llm, **kwargs)
        self.system_prompt = system_prompt
    
    async def invoke(self, input_text: str, **kwargs) -> AgentResponse:
        """
        Invoke the LLM with input text.
        
        Args:
            input_text: User input
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
        
        Returns:
            AgentResponse with LLM output
        """
        # Build messages
        messages = []
        
        if self.system_prompt:
            messages.append(("system", self.system_prompt))
        
        messages.append(("human", input_text))
        
        # Invoke LLM
        try:
            # Support both sync and async LLMs
            if hasattr(self.llm, 'ainvoke'):
                response = await self.llm.ainvoke(messages, **kwargs)
            else:
                response = self.llm.invoke(messages, **kwargs)
            
            # Extract content
            if hasattr(response, 'content'):
                output = response.content
            else:
                output = str(response)
            
            return AgentResponse(
                output=output,
                metadata={
                    "model": getattr(self.llm, 'model_name', 'unknown'),
                },
                raw_response=response,
            )
        
        except Exception as e:
            # Re-raise with context
            raise RuntimeError(f"LLM invocation failed: {e}") from e
