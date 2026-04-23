"""
agent_audit.interrogation.backends.ollama — Ollama Local Backend
==================================================================

Agent caller for locally-hosted models via Ollama.
Zero data leaves the machine — privacy-first option.
Temperature is locked to 0 for deterministic responses.
"""

from __future__ import annotations

from typing import Any

import aiohttp


class OllamaBackend:
    """
    Agent caller using a local Ollama server.

    Args:
        model: Local model name (default "mistral:7b-instruct").
        system_prompt: The agent's system prompt.
        temperature: Response temperature (default 0.0).
        base_url: Ollama API base URL (default "http://localhost:11434").
        max_tokens: Max tokens in response.
    """

    def __init__(
        self,
        model: str = "mistral:7b-instruct",
        system_prompt: str = "",
        temperature: float = 0.0,
        base_url: str = "http://localhost:11434",
        max_tokens: int = 1024,
    ):
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.base_url = base_url.rstrip("/")
        self.max_tokens = max_tokens

    async def call(self, input_text: str) -> str:
        """
        Send input to the local Ollama server and return the response.

        Args:
            input_text: The test case input to send.

        Returns:
            The model's response text.

        Raises:
            ConnectionError: If Ollama server is not running.
        """
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": [],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "num_predict": self.max_tokens,
            },
        }

        if self.system_prompt:
            payload["messages"].append({
                "role": "system",
                "content": self.system_prompt,
            })
        payload["messages"].append({
            "role": "user",
            "content": input_text,
        })

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        raise RuntimeError(
                            f"Ollama returned status {resp.status}: {error_text}"
                        )
                    data = await resp.json()
                    return data.get("message", {}).get("content", "")
        except aiohttp.ClientConnectorError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Ensure Ollama is running: ollama serve"
            )
