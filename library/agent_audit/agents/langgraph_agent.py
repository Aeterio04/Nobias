"""
agent_audit.agents.langgraph_agent — LangGraph Agent Wrapper
=============================================================

Wrapper for LangGraph-based agents.
"""

from __future__ import annotations

from typing import Any

from agent_audit.agents.base import BaseAgent, AgentResponse


class LangGraphAgent(BaseAgent):
    """
    Wrapper for LangGraph compiled graphs.
    
    Usage:
        from langgraph.graph import StateGraph
        
        # Build your graph
        graph = StateGraph(...)
        # ... add nodes, edges ...
        compiled_graph = graph.compile()
        
        # Wrap in agent
        agent = LangGraphAgent(graph=compiled_graph)
        
        response = await agent.invoke("Process this input")
        print(response.output)
    """
    
    def __init__(
        self,
        graph: Any,
        llm: Any = None,
        input_key: str = "input",
        output_key: str = "output",
        **kwargs
    ):
        """
        Initialize LangGraph agent.
        
        Args:
            graph: Compiled LangGraph graph
            llm: Optional LLM (for compatibility, not used directly)
            input_key: Key to use for input in graph state
            output_key: Key to extract output from graph state
            **kwargs: Additional configuration
        """
        super().__init__(llm=llm, **kwargs)
        self.graph = graph
        self.input_key = input_key
        self.output_key = output_key
    
    async def invoke(self, input_text: str, **kwargs) -> AgentResponse:
        """
        Invoke the LangGraph graph.
        
        Args:
            input_text: Input text
            **kwargs: Additional graph invocation parameters
        
        Returns:
            AgentResponse with graph output
        """
        try:
            # Build input state
            input_state = {self.input_key: input_text}
            
            # Invoke graph
            if hasattr(self.graph, 'ainvoke'):
                result = await self.graph.ainvoke(input_state, **kwargs)
            else:
                result = self.graph.invoke(input_state, **kwargs)
            
            # Extract output
            if isinstance(result, dict):
                output = result.get(self.output_key, str(result))
            else:
                output = str(result)
            
            return AgentResponse(
                output=output,
                metadata={
                    "graph_type": "langgraph",
                },
                raw_response=result,
            )
        
        except Exception as e:
            raise RuntimeError(f"LangGraph invocation failed: {e}") from e
