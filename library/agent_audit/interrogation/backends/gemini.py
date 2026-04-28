"""
agent_audit.interrogation.backends.gemini — Google Gemini Backend
===================================================================

Async agent caller for Google Gemini API (gemini-pro, gemini-1.5-pro, etc.).
Temperature is locked to 0 for deterministic responses.
"""

from __future__ import annotations

from typing import Any


class GeminiBackend:
    """
    Agent caller using the Google Gemini API.

    Args:
        api_key: Google API key for Gemini.
        model: Model name (default "gemini-1.5-pro").
        system_prompt: The agent's system prompt to prepend.
        temperature: Response temperature (default 0.0 for determinism).
        max_tokens: Max tokens in response (max_output_tokens in Gemini).
    """

    def __init__(
        self,
        api_key: str,
        model: str = "gemini-1.5-pro",
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
        """Lazy-init the Google Generative AI client."""
        if self._client is None:
            try:
                import google.generativeai as genai
            except ImportError:
                raise ImportError(
                    "Gemini backend requires the 'google-generativeai' package. "
                    "Install with: pip install google-generativeai"
                )
            genai.configure(api_key=self.api_key)
            self._client = genai
        return self._client

    async def call(self, input_text: str) -> str:
        """
        Send input to the Google Gemini API and return the response text.

        Args:
            input_text: The test case input to send.

        Returns:
            The model's response text.
        """
        genai = self._get_client()
        
        # Configure generation parameters
        generation_config = {
            "temperature": self.temperature,
            "max_output_tokens": self.max_tokens,
        }
        
        # Create model instance
        model = genai.GenerativeModel(
            model_name=self.model,
            generation_config=generation_config,
        )
        
        # Combine system prompt with input if system prompt exists
        if self.system_prompt:
            full_prompt = f"{self.system_prompt}\n\n{input_text}"
        else:
            full_prompt = input_text
        
        # Generate response asynchronously
        response = await model.generate_content_async(full_prompt)
        
        return response.text if response.text else ""
