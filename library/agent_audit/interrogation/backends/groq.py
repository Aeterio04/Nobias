"""
agent_audit.interrogation.backends.groq — Groq Backend
========================================================

Async agent caller for Groq API (fast inference with Llama, Mixtral, etc.).
Temperature is locked to 0 for deterministic responses.

Groq provides extremely fast inference at low cost, making it ideal
for testing and development.

Includes automatic retry logic for rate limit errors.
"""

from __future__ import annotations

import asyncio
from typing import Any


class GroqBackend:
    """
    Agent caller using the Groq API.

    Args:
        api_key: Groq API key.
        model: Model name (default "llama-3.1-70b-versatile").
        system_prompt: The agent's system prompt to prepend.
        temperature: Response temperature (default 0.0 for determinism).
        max_tokens: Max tokens in response.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-70b-versatile",
        system_prompt: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1024,
    ):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self._client = None

    def _get_client(self) -> Any:
        """Lazy-init the Groq async client."""
        if self._client is None:
            try:
                from groq import AsyncGroq
            except ImportError:
                raise ImportError(
                    "Groq backend requires the 'groq' package. "
                    "Install with: pip install groq"
                )
            self._client = AsyncGroq(api_key=self.api_key)
        return self._client

    async def call(self, input_text: str) -> str:
        """
        Send input to the Groq API and return the response text.
        
        Includes automatic retry logic for rate limit errors (429).
        Retries up to 2 times with 3 second delays.

        Args:
            input_text: The test case input to send.

        Returns:
            The model's response text.
            
        Raises:
            groq.RateLimitError: If rate limit is hit after all retries.
        """
        max_retries = 2
        retry_delay = 3.0  # seconds
        
        for attempt in range(max_retries + 1):
            try:
                client = self._get_client()
                messages = []
                if self.system_prompt:
                    messages.append({"role": "system", "content": self.system_prompt})
                messages.append({"role": "user", "content": input_text})

                response = await client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )

                return response.choices[0].message.content or ""
                
            except Exception as e:
                # Check if it's a rate limit error
                error_str = str(e)
                is_rate_limit = (
                    "rate_limit" in error_str.lower() or 
                    "429" in error_str or
                    "RateLimitError" in type(e).__name__
                )
                
                if is_rate_limit and attempt < max_retries:
                    # Retry after delay
                    print(f"⚠️  Rate limit hit, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})...")
                    await asyncio.sleep(retry_delay)
                    continue
                else:
                    # Not a rate limit error, or out of retries
                    raise
