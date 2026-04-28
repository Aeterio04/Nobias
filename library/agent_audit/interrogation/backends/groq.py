"""
agent_audit.interrogation.backends.groq — Groq Backend
========================================================

Async agent caller for Groq API (fast inference with Llama, Mixtral, etc.).
Temperature is locked to 0 for deterministic responses.

Groq provides extremely fast inference at low cost, making it ideal
for testing and development.

Includes automatic retry logic for rate limit errors and token-aware rate limiting.
"""

from __future__ import annotations

import asyncio
import logging
import time
import re
from typing import Any

# Configure logger
logger = logging.getLogger(__name__)


# TokenRateLimiter removed - no longer needed with sequential execution
# Sequential processing ensures we never hit TPM limits since previous
# calls have aged out of the sliding window before new ones start

# Semaphore to limit concurrent requests
_semaphore = asyncio.Semaphore(3)  # Max 3 concurrent Groq calls


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
        model: str = "llama-3.1-8b-instant",
        system_prompt: str = "",
        temperature: float = 0.0,
        max_tokens: int = 1024,
        enable_smart_rate_limiting: bool = True,
        max_concurrent_requests: int = 3,
        tpm_limit: int = 5500,
    ):
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.enable_smart_rate_limiting = enable_smart_rate_limiting
        self._client = None
        
        # Configure semaphore (protects against accidental concurrent calls)
        global _semaphore
        _semaphore = asyncio.Semaphore(max_concurrent_requests)
        
        logger.info(f"Initialized GroqBackend with model={model}, max_tokens={max_tokens}")
        logger.info(f"  Sequential execution with {max_concurrent_requests} max concurrent requests")

    def _get_client(self) -> Any:
        """Lazy-init the Groq async client."""
        if self._client is None:
            try:
                from groq import AsyncGroq
                logger.debug("Importing AsyncGroq client")
            except ImportError:
                logger.error("Failed to import groq package")
                raise ImportError(
                    "Groq backend requires the 'groq' package. "
                    "Install with: pip install groq"
                )
            self._client = AsyncGroq(api_key=self.api_key)
            logger.info("Groq client initialized successfully")
        return self._client

    async def call(self, input_text: str) -> str:
        """
        Send input to the Groq API and return the response text.
        
        Includes:
        - Concurrency limiting (max concurrent requests, protects against accidental parallel calls)
        - Automatic retry with exponential backoff for rate limit errors
        - Parses retry_after from error messages
        
        Note: Sequential execution at the engine level prevents TPM issues,
        so token-aware rate limiting is no longer needed.

        Args:
            input_text: The test case input to send.

        Returns:
            The model's response text.
            
        Raises:
            groq.RateLimitError: If rate limit is hit after all retries.
        """
        # Limit concurrency (protects against accidental concurrent calls)
        semaphore = _semaphore if self.enable_smart_rate_limiting else asyncio.Semaphore(999)
        
        logger.debug(f"[WAIT] Waiting for semaphore (max concurrent: {semaphore._value})...")
        async with semaphore:
            logger.debug("[OK] Semaphore acquired, making API call")
            max_retries = 3
            base_delay = 2.0
            
            logger.debug(f"Calling Groq API with input length: {len(input_text)} chars")
            
            for attempt in range(max_retries + 1):
                try:
                    client = self._get_client()
                    messages = []
                    if self.system_prompt:
                        messages.append({"role": "system", "content": self.system_prompt})
                    messages.append({"role": "user", "content": input_text})

                    logger.debug(f"Attempt {attempt + 1}/{max_retries + 1}: Sending request to model={self.model}")
                    
                    response = await client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        max_tokens=self.max_tokens,
                    )

                    response_text = response.choices[0].message.content or ""
                    logger.info(f"[OK] Groq API call successful (response length: {len(response_text)} chars)")
                    return response_text
                    
                except Exception as e:
                    error_str = str(e)
                    is_rate_limit = (
                        "rate_limit" in error_str.lower() or 
                        "429" in error_str or
                        "RateLimitError" in type(e).__name__
                    )
                    
                    if is_rate_limit and attempt < max_retries:
                        # Parse retry_after from error message
                        retry_after = self._parse_retry_after(error_str)
                        if retry_after is None:
                            # Exponential backoff if no retry_after
                            retry_after = base_delay * (2 ** attempt)
                        
                        logger.warning(f"[WARN] RATE LIMIT HIT: {error_str[:150]}")
                        logger.warning(f"   Sleeping for {retry_after:.1f}s before retry (attempt {attempt + 1}/{max_retries})")
                        print(f"[WARN] Rate limit hit, sleeping {retry_after:.1f}s... (attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(retry_after)
                        logger.info(f"[OK] Woke up after {retry_after:.1f}s, retrying API call")
                        continue
                    else:
                        # Not a rate limit error, or out of retries
                        if is_rate_limit:
                            logger.error(f"[FAIL] Rate limit exceeded after {max_retries} retries")
                        else:
                            logger.error(f"[FAIL] Groq API error: {type(e).__name__}: {str(e)[:200]}")
                        raise
    
    def _parse_retry_after(self, error_message: str) -> float | None:
        """Parse retry_after duration from error message."""
        # Look for "Please try again in X.XXs"
        match = re.search(r'try again in ([\d.]+)s', error_message)
        if match:
            return float(match.group(1)) + 0.5  # Add 0.5s buffer
        return None
