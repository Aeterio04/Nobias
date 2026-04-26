"""
agent_audit.optimization.two_pass — Two-Pass Evaluation Strategy
=================================================================

Implements two-pass evaluation to reduce API calls by 50%.

Strategy:
    Pass 1: Run each persona 1x, identify high-variance cases
    Pass 2: Re-run only flagged personas 2x more for SSS

Instead of: N × 3 runs = 3N calls
You get:    N + (0.25N × 2) = 1.5N calls
"""

from __future__ import annotations

from typing import Any
from dataclasses import dataclass


@dataclass
class FirstPassResult:
    """Result from first pass evaluation."""
    persona_id: str
    decision: str
    score: float | None
    reason_code: str
    flags: list[str]
    should_rerun: bool
    rerun_reason: str


def should_flag_for_rerun(
    decision: str,
    score: float | None,
    reason_code: str,
    flags: list[str],
) -> tuple[bool, str]:
    """
    Determine if a persona should be re-run in pass 2.
    
    Flagging criteria:
    1. Ambiguous decisions (high variance expected)
    2. Borderline scores (0.4-0.6 range)
    3. Risk flags detected
    4. Inconsistent reasoning codes
    
    Args:
        decision: "positive" | "negative" | "ambiguous"
        score: Numeric score (0-1) if available
        reason_code: Reason code from evaluation
        flags: List of risk flags
    
    Returns:
        Tuple of (should_rerun: bool, reason: str)
    """
    # Criterion 1: Ambiguous decisions
    if decision == "ambiguous":
        return True, "ambiguous_decision"
    
    # Criterion 2: Borderline scores
    if score is not None and 0.4 <= score <= 0.6:
        return True, "borderline_score"
    
    # Criterion 3: Risk flags present
    risk_flags = {"gender_proxy", "race_proxy", "name_bias", "stereotype"}
    if any(flag in risk_flags for flag in flags):
        return True, f"risk_flag_{flags[0]}"
    
    # Criterion 4: Inconsistent reasoning
    if reason_code in ["risk_detected", "insufficient_data"]:
        return True, f"reason_{reason_code}"
    
    # Clear decision, no flags
    return False, "clear"


class TwoPassEvaluator:
    """
    Manages two-pass evaluation strategy.
    
    Usage:
        evaluator = TwoPassEvaluator()
        
        # Pass 1: Evaluate all personas once
        for persona in personas:
            result = await evaluate_once(persona)
            evaluator.record_pass1(result)
        
        # Get personas to re-run
        flagged = evaluator.get_flagged_personas()
        
        # Pass 2: Re-run flagged personas
        for persona_id in flagged:
            result1 = await evaluate_once(persona_id)
            result2 = await evaluate_once(persona_id)
            evaluator.record_pass2(persona_id, [result1, result2])
        
        # Get final results with SSS
        final = evaluator.get_final_results()
    """
    
    def __init__(self):
        self.pass1_results: dict[str, FirstPassResult] = {}
        self.pass2_results: dict[str, list[dict]] = {}
        self.total_calls = 0
    
    def record_pass1(
        self,
        persona_id: str,
        decision: str,
        score: float | None,
        reason_code: str,
        flags: list[str],
    ) -> FirstPassResult:
        """
        Record a pass 1 result and determine if rerun needed.
        
        Args:
            persona_id: Unique persona identifier
            decision: "positive" | "negative" | "ambiguous"
            score: Numeric score if available
            reason_code: Reason code from evaluation
            flags: List of risk flags
        
        Returns:
            FirstPassResult with rerun decision
        """
        should_rerun, rerun_reason = should_flag_for_rerun(
            decision, score, reason_code, flags
        )
        
        result = FirstPassResult(
            persona_id=persona_id,
            decision=decision,
            score=score,
            reason_code=reason_code,
            flags=flags,
            should_rerun=should_rerun,
            rerun_reason=rerun_reason,
        )
        
        self.pass1_results[persona_id] = result
        self.total_calls += 1
        
        return result
    
    def get_flagged_personas(self) -> list[str]:
        """
        Get list of persona IDs that need re-running.
        
        Returns:
            List of persona IDs flagged for pass 2
        """
        return [
            pid for pid, result in self.pass1_results.items()
            if result.should_rerun
        ]
    
    def record_pass2(
        self,
        persona_id: str,
        additional_results: list[dict[str, Any]],
    ) -> None:
        """
        Record additional runs for a flagged persona.
        
        Args:
            persona_id: Persona being re-run
            additional_results: List of evaluation results (typically 2)
        """
        self.pass2_results[persona_id] = additional_results
        self.total_calls += len(additional_results)
    
    def get_final_results(self) -> dict[str, dict[str, Any]]:
        """
        Compute final results with majority vote and variance.
        
        For non-flagged personas: Use pass 1 result directly
        For flagged personas: Aggregate all 3 runs
        
        Returns:
            Dict mapping persona_id to final result with:
                - majority_decision
                - mean_score
                - decision_variance
                - num_runs
                - all_decisions
                - all_scores
        """
        final_results = {}
        
        for persona_id, pass1 in self.pass1_results.items():
            if persona_id in self.pass2_results:
                # Flagged persona: aggregate all runs
                all_decisions = [pass1.decision]
                all_scores = [pass1.score] if pass1.score is not None else []
                
                for run in self.pass2_results[persona_id]:
                    all_decisions.append(run["decision"])
                    if run.get("score") is not None:
                        all_scores.append(run["score"])
                
                # Majority vote
                from collections import Counter
                majority = Counter(all_decisions).most_common(1)[0][0]
                
                # Variance
                variance = len(set(all_decisions)) / len(all_decisions)
                
                final_results[persona_id] = {
                    "majority_decision": majority,
                    "mean_score": sum(all_scores) / len(all_scores) if all_scores else None,
                    "decision_variance": variance,
                    "num_runs": len(all_decisions),
                    "all_decisions": all_decisions,
                    "all_scores": all_scores,
                    "flagged": True,
                    "flag_reason": pass1.rerun_reason,
                }
            else:
                # Non-flagged: use pass 1 directly
                final_results[persona_id] = {
                    "majority_decision": pass1.decision,
                    "mean_score": pass1.score,
                    "decision_variance": 0.0,  # Single run, no variance
                    "num_runs": 1,
                    "all_decisions": [pass1.decision],
                    "all_scores": [pass1.score] if pass1.score is not None else [],
                    "flagged": False,
                    "flag_reason": "clear",
                }
        
        return final_results
    
    def get_statistics(self) -> dict[str, Any]:
        """
        Get evaluation statistics.
        
        Returns:
            Dict with call counts and flagging stats
        """
        total_personas = len(self.pass1_results)
        flagged_count = len(self.pass2_results)
        
        # Expected calls if we did 3x for everyone
        expected_calls_3x = total_personas * 3
        
        # Actual calls with two-pass
        actual_calls = self.total_calls
        
        # Savings
        savings_percent = ((expected_calls_3x - actual_calls) / expected_calls_3x) * 100
        
        return {
            "total_personas": total_personas,
            "flagged_personas": flagged_count,
            "flagged_percent": (flagged_count / total_personas * 100) if total_personas > 0 else 0,
            "total_calls": actual_calls,
            "expected_calls_3x": expected_calls_3x,
            "calls_saved": expected_calls_3x - actual_calls,
            "savings_percent": savings_percent,
        }


__all__ = [
    "should_flag_for_rerun",
    "FirstPassResult",
    "TwoPassEvaluator",
]
