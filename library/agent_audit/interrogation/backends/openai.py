"""
agent_audit.interrogation.backends.openai — OpenAI Backend
=============================================================

Async agent caller for OpenAI-compatible APIs (GPT-4o, GPT-4, etc.).
Temperature is locked to 0 for deterministic responses.
"""

from __future__ import annotations

from typing import Any


class OpenAIBackend:
    """
    Agent caller using the OpenAI API.

    Args:
        api_key: OpenAI API key.
        model: Model name (default "gpt-4o").
        system_prompt: The agent's system prompt to prepend.
        temperature: Response temperature (default 0.0 for determinism).
        max_tokens: Max tokens in response.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4o",
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
        """Lazy-init the OpenAI async client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
            except ImportError:
                raise ImportError(
                    "OpenAI backend requires the 'openai' package. "
                    "Install with: pip install openai"
                )
            self._client = AsyncOpenAI(api_key=self.api_key)
        return self._client

    async def call(self, input_text: str) -> str:
        """
        Send input to the OpenAI API and return the response text.

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
