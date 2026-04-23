"""
agent_audit.interrogation.backends.groq — Groq Backend
========================================================

Async agent caller for Groq API (fast inference with Llama, Mixtral, etc.).
Temperature is locked to 0 for deterministic responses.

Groq provides extremely fast inference at low cost, making it ideal
for testing and development.
"""

from __future__ import annotations

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

        Args:
            input_text: The test case input to send.

        Returns:
            The model's response text.
        """
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
