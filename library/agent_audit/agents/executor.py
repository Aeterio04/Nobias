"""
agent_audit.agents.executor — Agent Execution with Retry Logic
===============================================================

Robust agent execution with automatic retry and rate limit handling.
"""

from __future__ import annotations

import asyncio
import time
from typing import Any, Callable

from agent_audit.agents.base import BaseAgent, AgentResponse


class AgentExecutor:
    """
    Executes agents with retry logic and rate limit handling.
    
    Features:
        - Automatic retry on rate limits (3 attempts)
        - Exponential backoff (5s, 10s, 15s)
        - Error handling and logging
        - Supports any BaseAgent subclass
    
    Usage:
        executor = AgentExecutor(agent=my_agent, max_retries=3)
        response = await executor.execute("Input text")
    """
    
    def __init__(
        self,
        agent: BaseAgent,
        max_retries: int = 3,
        retry_delays: list[float] = None,
        on_retry: Callable[[int, Exception], None] = None,
    ):
        """
        Initialize executor.
        
        Args:
            agent: Agent to execute
            max_retries: Maximum retry attempts (default 3)
            retry_delays: Delays between retries in seconds (default [5, 10, 15])
            on_retry: Optional callback on retry (retry_num, exception)
        """
        self.agent = agent
        self.max_retries = max_retries
        self.retry_delays = retry_delays or [5.0, 10.0, 15.0]
        self.on_retry = on_retry
        
        # Ensure we have enough delays
        while len(self.retry_delays) < max_retries:
            self.retry_delays.append(self.retry_delays[-1] * 1.5)
    
    async def execute(self, input_text: str, **kwargs) -> AgentResponse:
        """
        Execute agent with retry logic.
        
        Args:
            input_text: Input to agent
            **kwargs: Additional invocation parameters
        
        Returns:
            AgentResponse from successful execution
        
        Raises:
            RuntimeError: If all retries exhausted
        """
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                # Execute agent
                response = await self.agent.invoke(input_text, **kwargs)
                return response
            
            except Exception as e:
                last_exception = e
                error_msg = str(e).lower()
                
                # Check if it's a rate limit error
                is_rate_limit = any(
                    phrase in error_msg
                    for phrase in [
                        "rate limit",
                        "429",
                        "too many requests",
                        "quota exceeded",
                    ]
                )
                
                # If not rate limit or last attempt, raise
                if not is_rate_limit or attempt >= self.max_retries:
                    raise RuntimeError(
                        f"Agent execution failed after {attempt + 1} attempts: {e}"
                    ) from e
                
                # Calculate delay
                delay = self.retry_delays[attempt]
                
                # Call retry callback if provided
                if self.on_retry:
                    self.on_retry(attempt + 1, e)
                
                # Wait before retry
                print(f"⚠️  Rate limit hit. Retrying in {delay}s (attempt {attempt + 1}/{self.max_retries})...")
                await asyncio.sleep(delay)
        
        # Should never reach here, but just in case
        raise RuntimeError(
            f"Agent execution failed after {self.max_retries} retries"
        ) from last_exception


async def execute_with_retry(
    agent: BaseAgent,
    input_text: str,
    max_retries: int = 3,
    retry_delays: list[float] = None,
    **kwargs
) -> AgentResponse:
    """
    Convenience function to execute agent with retry.
    
    Args:
        agent: Agent to execute
        input_text: Input text
        max_retries: Maximum retry attempts
        retry_delays: Delays between retries
        **kwargs: Additional invocation parameters
    
    Returns:
        AgentResponse from successful execution
    
    Example:
        from agent_audit.agents import SimpleLLMAgent, execute_with_retry
        
        agent = SimpleLLMAgent(llm=my_llm)
        response = await execute_with_retry(
            agent=agent,
            input_text="What is 2+2?",
            max_retries=3,
        )
    """
    executor = AgentExecutor(
        agent=agent,
        max_retries=max_retries,
        retry_delays=retry_delays,
    )
    
    return await executor.execute(input_text, **kwargs)


class RateLimitTracker:
    """
    Track rate limits across multiple calls.
    
    Helps prevent hitting rate limits by tracking call frequency.
    """
    
    def __init__(self, calls_per_minute: int = 60):
        """
        Initialize tracker.
        
        Args:
            calls_per_minute: Maximum calls allowed per minute
        """
        self.calls_per_minute = calls_per_minute
        self.call_times: list[float] = []
    
    async def wait_if_needed(self) -> None:
        """Wait if we're approaching rate limit."""
        now = time.time()
        
        # Remove calls older than 1 minute
        self.call_times = [t for t in self.call_times if now - t < 60]
        
        # Check if we need to wait
        if len(self.call_times) >= self.calls_per_minute:
            # Wait until oldest call is >1 minute old
            oldest = self.call_times[0]
            wait_time = 60 - (now - oldest) + 0.1  # Add small buffer
            
            if wait_time > 0:
                print(f"⏳ Rate limit prevention: waiting {wait_time:.1f}s...")
                await asyncio.sleep(wait_time)
        
        # Record this call
        self.call_times.append(time.time())


__all__ = [
    "AgentExecutor",
    "execute_with_retry",
    "RateLimitTracker",
]
