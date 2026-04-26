"""
agent_audit.interrogation.engine — Core Interrogation Engine
==============================================================

Async execution engine that sends CAFFE test cases to the agent
under test. Handles:
    - Semaphore-based rate limiting (default 10 req/s)
    - Adaptive sampling (early-stop for deterministic agents)
    - Disk-based result caching (hash of input → output)
    - Progress callbacks for UI integration
"""

from __future__ import annotations

import asyncio
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Callable

import numpy as np

from agent_audit.caffe import CAFFETestCase
from agent_audit.config import AgentAuditConfig, AuditMode
from agent_audit.interrogation.parsers import OutputParser
from agent_audit.interrogation.adaptive import should_continue_sampling

# Import optimization modules (internal use)
try:
    from agent_audit.optimization import (
        build_optimized_evaluation_prompt,
        parse_json_response,
        TwoPassEvaluator,
        TokenBudget,
    )
    OPTIMIZATION_AVAILABLE = True
except ImportError:
    OPTIMIZATION_AVAILABLE = False


class InterrogationEngine:
    """
    Async engine that interrogates an agent with CAFFE test cases.

    Attributes:
        config: The audit configuration.
        agent_caller: Callable that sends input to the agent and returns output.
        semaphore: Asyncio semaphore for rate limiting.
        cache: In-memory cache (hash → result); optionally backed by disk.
        parser: Output parser for extracting decisions/scores.
    """

    def __init__(
        self,
        config: AgentAuditConfig,
        agent_caller: Callable[[str], Any] | None = None,
        cache_dir: Path | None = None,
    ):
        self.config = config
        self.agent_caller = agent_caller
        self.semaphore = asyncio.Semaphore(config.rate_limit_rps)
        self.parser = OutputParser(
            positive=config.positive_outcome,
            negative=config.negative_outcome,
            output_type=config.output_type,
            response_normalizer=config.response_normalizer,
        )
        self.cache: dict[str, dict] = {}
        self.cache_dir = cache_dir
        self._total_calls = 0
        
        # Token optimization (internal)
        self.optimization_enabled = (
            config.enable_optimization and OPTIMIZATION_AVAILABLE
        )
        self.use_two_pass = config.use_two_pass_evaluation and self.optimization_enabled
        self.token_budget = None
        self.two_pass_evaluator = None
        
        if self.optimization_enabled:
            # Initialize token budget based on tier
            tier_budgets = {
                "tier_1": 50_000,
                "tier_2": 80_000,
                "tier_3": 130_000,
                "adaptive": 130_000,
            }
            budget_limit = tier_budgets.get(config.optimization_tier, 50_000)
            self.token_budget = TokenBudget(max_tokens=budget_limit)
            
            if self.use_two_pass:
                self.two_pass_evaluator = TwoPassEvaluator()

        # Load disk cache if available
        if cache_dir and cache_dir.exists():
            self._load_cache()

    @property
    def total_calls(self) -> int:
        """Total API calls made during this session."""
        return self._total_calls
    
    def get_optimization_stats(self) -> dict[str, Any] | None:
        """
        Get token optimization statistics (internal).
        
        Returns None if optimization is disabled.
        """
        if not self.optimization_enabled:
            return None
        
        stats = {
            "optimization_enabled": True,
            "two_pass_enabled": self.use_two_pass,
        }
        
        if self.token_budget:
            stats["token_budget"] = self.token_budget.to_dict()
        
        if self.two_pass_evaluator:
            stats["two_pass_stats"] = self.two_pass_evaluator.get_statistics()
        
        return stats

    # ── Public API ───────────────────────────────────────────────────────

    async def interrogate(self, case: CAFFETestCase) -> CAFFETestCase:
        """
        Run one CAFFE test case through the agent.

        Uses adaptive sampling: starts with 1 run, continues only
        if variance is detected (or if mode requires multiple runs).
        
        Automatically uses token optimization if enabled (internal).

        Args:
            case: A CAFFE test case to execute.

        Returns:
            The same case with results populated.
        """
        input_text = self._build_input(case)
        cache_key = self._hash_input(input_text)

        # Check cache first
        if cache_key in self.cache:
            case.results = [self.cache[cache_key]]
            return case

        # Use two-pass evaluation if enabled (internal optimization)
        if self.use_two_pass and self.two_pass_evaluator is not None:
            return await self._interrogate_two_pass(case, input_text, cache_key)
        else:
            return await self._interrogate_standard(case, input_text, cache_key)

    async def run_all(
        self,
        cases: list[CAFFETestCase],
        progress_callback: Callable[[int, int, str], None] | None = None,
    ) -> list[CAFFETestCase]:
        """
        Run all CAFFE test cases with progress tracking.

        Args:
            cases: List of test cases to execute.
            progress_callback: Optional callback(completed, total, current_persona).

        Returns:
            List of completed test cases with results populated.
        """
        tasks = [self.interrogate(c) for c in cases]
        completed: list[CAFFETestCase] = []

        for i, coro in enumerate(asyncio.as_completed(tasks)):
            result = await coro
            completed.append(result)
            if progress_callback:
                persona_desc = (
                    result.input_variants[0]
                    if result.input_variants
                    else {}
                )
                progress_callback(i + 1, len(cases), str(persona_desc))

        return completed

    # ── Private Helpers ──────────────────────────────────────────────────

    async def _interrogate_standard(
        self, case: CAFFETestCase, input_text: str, cache_key: str
    ) -> CAFFETestCase:
        """Standard interrogation (no optimization)."""
        max_runs = self._max_runs_for_mode()
        raw_outputs: list[str] = []
        parsed_decisions: list[str] = []
        parsed_scores: list[float] = []

        async with self.semaphore:
            for run_idx in range(max_runs):
                response = await self._call_agent(input_text)
                raw_outputs.append(response)
                self._total_calls += 1

                decision, score = self.parser.parse(response)
                parsed_decisions.append(decision)
                if score is not None:
                    parsed_scores.append(score)

                # Adaptive early-stop check
                if not should_continue_sampling(
                    run_idx=run_idx,
                    decisions=parsed_decisions,
                    temperature=self.config.temperature,
                    mode=self.config.mode.value,
                ):
                    break

        # Aggregate results
        result = {
            "raw_outputs": raw_outputs,
            "majority_decision": Counter(parsed_decisions).most_common(1)[0][0],
            "decision_variance": (
                len(set(parsed_decisions)) / len(parsed_decisions)
                if parsed_decisions else 0.0
            ),
            "mean_score": float(np.mean(parsed_scores)) if parsed_scores else None,
            "score_std": float(np.std(parsed_scores)) if parsed_scores else None,
            "all_decisions": parsed_decisions,
            "all_scores": parsed_scores,
            "num_runs": len(raw_outputs),
        }

        case.results = [result]

        # Cache the result
        self.cache[cache_key] = result
        if self.cache_dir:
            self._save_cache_entry(cache_key, result)

        return case

    async def _interrogate_two_pass(
        self, case: CAFFETestCase, input_text: str, cache_key: str
    ) -> CAFFETestCase:
        """Two-pass interrogation (optimized)."""
        # Pass 1: Single run
        async with self.semaphore:
            response = await self._call_agent(input_text)
            self._total_calls += 1

        decision, score = self.parser.parse(response)
        
        # Record in two-pass evaluator
        pass1_result = self.two_pass_evaluator.record_pass1(
            persona_id=case.test_id,
            decision=decision,
            score=score,
            reason_code="standard",  # Would come from optimized parser
            flags=[],
        )

        # Check if we need pass 2
        if pass1_result.should_rerun:
            # Pass 2: Two additional runs
            additional_results = []
            async with self.semaphore:
                for _ in range(2):
                    response2 = await self._call_agent(input_text)
                    self._total_calls += 1
                    decision2, score2 = self.parser.parse(response2)
                    additional_results.append({
                        "decision": decision2,
                        "score": score2,
                    })
            
            self.two_pass_evaluator.record_pass2(case.test_id, additional_results)

        # Get final aggregated result
        final_results = self.two_pass_evaluator.get_final_results()
        final = final_results[case.test_id]

        # Build result dict
        result = {
            "raw_outputs": [response],  # Simplified for now
            "majority_decision": final["majority_decision"],
            "decision_variance": final["decision_variance"],
            "mean_score": final["mean_score"],
            "score_std": None,
            "all_decisions": final["all_decisions"],
            "all_scores": final["all_scores"],
            "num_runs": final["num_runs"],
        }

        case.results = [result]

        # Cache the result
        self.cache[cache_key] = result
        if self.cache_dir:
            self._save_cache_entry(cache_key, result)

        return case

    # ── Private Helpers ──────────────────────────────────────────────────

    def _build_input(self, case: CAFFETestCase) -> str:
        """Build the full input text for an agent call."""
        parts = []
        if case.conversational_context:
            parts.append(case.conversational_context)
        parts.append(case.base_input)

        # Inject attributes if present
        if case.input_variants:
            attrs = {
                k: v for k, v in case.input_variants[0].items()
                if not k.startswith("_")
                and k not in ("name", "context_prime", "inferred_race", "inferred_gender")
            }
            if attrs:
                attr_text = "\n".join(f"{k.title()}: {v}" for k, v in attrs.items())
                parts.append(attr_text)

        return "\n\n".join(parts)

    async def _call_agent(self, input_text: str) -> str:
        """Call the agent (via the injected callable)."""
        if self.agent_caller is None:
            raise RuntimeError(
                "No agent_caller provided. Set agent_caller in the constructor "
                "or use a backend from agent_audit.interrogation.backends."
            )
        result = self.agent_caller(input_text)
        # Support both sync and async callables
        if asyncio.iscoroutine(result):
            return await result
        return result

    def _max_runs_for_mode(self) -> int:
        """
        Maximum runs per persona based on audit mode.
        
        FairSight compliance requires minimum 3 runs per persona
        for stochastic stability analysis.
        """
        return {
            AuditMode.QUICK: 3,      # Minimum for stability
            AuditMode.STANDARD: 3,   # Standard compliance
            AuditMode.FULL: 5,       # Enhanced stability
        }.get(self.config.mode, 3)

    @staticmethod
    def _hash_input(input_text: str) -> str:
        """Hash input text for cache lookup."""
        return hashlib.sha256(input_text.encode()).hexdigest()[:16]

    def _load_cache(self) -> None:
        """Load disk cache."""
        cache_file = self.cache_dir / "interrogation_cache.json"
        if cache_file.exists():
            try:
                self.cache = json.loads(cache_file.read_text())
            except (json.JSONDecodeError, OSError):
                self.cache = {}

    def _save_cache_entry(self, key: str, result: dict) -> None:
        """Save a single cache entry to disk."""
        if self.cache_dir:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file = self.cache_dir / "interrogation_cache.json"
            try:
                cache_file.write_text(json.dumps(self.cache, indent=2, default=str))
            except OSError:
                pass  # Non-critical — cache is best-effort
