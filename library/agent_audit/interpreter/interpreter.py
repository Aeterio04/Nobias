"""
agent_audit.interpreter.interpreter — LLM Call & Response Parsing
====================================================================

Calls the interpreter LLM (local or cloud) and parses the
structured JSON response into Interpretation and PromptSuggestion
objects.

Supports two backends:
    LOCAL: Ollama + Mistral 7B — zero data leaves machine
    CLOUD: Claude / GPT-4o — opt-in, higher quality interpretation
"""

from __future__ import annotations

import json
from enum import Enum
from typing import Any

from agent_audit.config import DecisionContext
from agent_audit.models import (
    AgentFinding,
    Interpretation,
    PromptSuggestion,
)
from agent_audit.interpreter.prompt_builder import build_interpreter_prompt


class InterpreterBackend(Enum):
    """Which LLM backend to use for interpretation."""
    LOCAL = "local"     # Ollama — zero data leaves machine
    CLOUD = "cloud"     # Claude / GPT-4o — opt-in


class Interpreter:
    """
    Calls the interpreter LLM and parses the response.

    The interpreter receives ONLY statistical findings (from Layer 4).
    It produces explanations, justifications, and prompt surgery
    suggestions. It cannot hallucinate findings.

    Attributes:
        backend: Which LLM to use (local/cloud).
        model: Specific model name.
        api_key: API key (only for cloud backend).
    """

    def __init__(
        self,
        backend: InterpreterBackend = InterpreterBackend.CLOUD,
        model: str | None = None,
        api_key: str | None = None,
    ):
        self.backend = backend
        self.model = model or self._default_model()
        self.api_key = api_key

    async def interpret(
        self,
        findings: list[AgentFinding],
        context: DecisionContext,
        system_prompt: str | None = None,
    ) -> tuple[Interpretation, list[PromptSuggestion]]:
        """
        Generate interpretation and remediation suggestions.

        Args:
            findings: Statistical findings from Layer 4.
            context: Decision context.
            system_prompt: Optional agent system prompt.

        Returns:
            Tuple of (Interpretation, list[PromptSuggestion]).
        """
        prompt = build_interpreter_prompt(findings, context, system_prompt)
        raw_response = await self._call_llm(prompt)
        return self._parse_response(raw_response)

    async def _call_llm(self, prompt: str) -> str:
        """Call the appropriate LLM backend."""
        if self.backend == InterpreterBackend.LOCAL:
            return await self._call_local(prompt)
        else:
            return await self._call_cloud(prompt)

    async def _call_local(self, prompt: str) -> str:
        """Call local Ollama backend."""
        from agent_audit.interrogation.backends.ollama import OllamaBackend
        backend = OllamaBackend(
            model=self.model,
            temperature=0.0,
            max_tokens=2048,
        )
        return await backend.call(prompt)

    async def _call_cloud(self, prompt: str) -> str:
        """Call cloud LLM backend."""
        if not self.api_key:
            raise ValueError("API key required for cloud interpreter backend")

        # Detect backend from model name
        model_lower = self.model.lower()
        
        if any(x in model_lower for x in ["llama", "mixtral", "gemma", "groq"]):
            # Use Groq
            from agent_audit.interrogation.backends.groq import GroqBackend
            backend = GroqBackend(
                api_key=self.api_key,
                model=self.model,
                temperature=0.0,
                max_tokens=2048,
            )
        elif any(x in model_lower for x in ["gemini", "bison", "palm"]):
            # Use Google Gemini
            from agent_audit.interrogation.backends.gemini import GeminiBackend
            backend = GeminiBackend(
                api_key=self.api_key,
                model=self.model,
                temperature=0.0,
                max_tokens=2048,
            )
        elif model_lower.startswith("claude"):
            # Use Anthropic
            from agent_audit.interrogation.backends.anthropic import AnthropicBackend
            backend = AnthropicBackend(
                api_key=self.api_key,
                model=self.model,
                temperature=0.0,
                max_tokens=2048,
            )
        else:
            # Default to OpenAI
            from agent_audit.interrogation.backends.openai import OpenAIBackend
            backend = OpenAIBackend(
                api_key=self.api_key,
                model=self.model,
                temperature=0.0,
                max_tokens=2048,
            )
        
        return await backend.call(prompt)

    def _parse_response(
        self, raw_response: str
    ) -> tuple[Interpretation, list[PromptSuggestion]]:
        """
        Parse the LLM's JSON response into structured objects.

        Args:
            raw_response: Raw text from the LLM.

        Returns:
            Tuple of (Interpretation, list[PromptSuggestion]).
        """
        # Try to extract JSON from the response
        parsed = self._extract_json(raw_response)

        interpretation = Interpretation(
            finding_explanations=[
                {
                    "finding_id": f.get("finding_id", ""),
                    "explanation": f.get("explanation", ""),
                    "justification": f.get("justification", ""),
                    "confidence": f.get("confidence", "medium"),
                }
                for f in parsed.get("findings", [])
            ],
            overall_assessment=parsed.get("overall_assessment", ""),
            priority_order=parsed.get("priority_order", []),
        )

        suggestions = [
            PromptSuggestion(
                finding_id=f.get("finding_id", ""),
                suggestion_text=f.get("suggested_prompt_addition", ""),
                rationale=f.get("justification", ""),
                confidence=f.get("confidence", "medium"),
            )
            for f in parsed.get("findings", [])
            if f.get("suggested_prompt_addition")
        ]

        return interpretation, suggestions

    @staticmethod
    def _extract_json(text: str) -> dict:
        """Extract JSON from a response that may contain markdown fences."""
        # Try direct parsing first
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Try extracting from markdown code block
        import re
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if json_match:
            try:
                return json.loads(json_match.group(1).strip())
            except json.JSONDecodeError:
                pass

        # Try finding JSON object boundaries
        brace_start = text.find("{")
        brace_end = text.rfind("}") + 1
        if brace_start >= 0 and brace_end > brace_start:
            try:
                return json.loads(text[brace_start:brace_end])
            except json.JSONDecodeError:
                pass

        return {"findings": [], "overall_assessment": "Failed to parse interpreter response"}

    def _default_model(self) -> str:
        """Default model for the chosen backend."""
        if self.backend == InterpreterBackend.LOCAL:
            return "mistral:7b-instruct"
        return "gpt-4o"
