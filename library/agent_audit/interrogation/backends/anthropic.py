"""
agent_audit.interrogation.backends.anthropic — Anthropic Backend
==================================================================

Async agent caller for Anthropic's Claude API.
Temperature is locked to 0 for deterministic responses.
"""

from __future__ import annotations

from typing import Any


class AnthropicBackend:
    """
    Agent caller using the Anthropic Claude API.

    Args:
        api_key: Anthropic API key.
        model: Model name (default "claude-sonnet-4-20250514").
        system_prompt: The agent's system prompt.
        temperature: Response temperature (default 0.0).
        max_tokens: Max tokens in response.
    """

    def __init__(
        self,
        api_key: str,
        model: str = "claude-sonnet-4-20250514",
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
        """Lazy-init the Anthropic async client."""
        if self._client is None:
            try:
                from anthropic import AsyncAnthropic
            except ImportError:
                raise ImportError(
                    "Anthropic backend requires the 'anthropic' package. "
                    "Install with: pip install anthropic"
                )
            self._client = AsyncAnthropic(api_key=self.api_key)
        return self._client

    async def call(self, input_text: str) -> str:
        """
        Send input to the Anthropic API and return the response text.

        Args:
            input_text: The test case input to send.

        Returns:
            The model's response text.
        """
        client = self._get_client()

        response = await client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            system=self.system_prompt if self.system_prompt else "",
            messages=[{"role": "user", "content": input_text}],
            temperature=self.temperature,
        )

        # Extract text from response content blocks
        text_blocks = [
            block.text for block in response.content
            if hasattr(block, "text")
        ]
        return "\n".join(text_blocks)
