"""
agent_audit.interrogation.adaptive — Adaptive Sampling Logic
===============================================================

Replaces the fixed N-runs-per-persona approach with intelligent
early stopping:

    Run 1: Always execute.
    If result is clear + temperature=0: stop (saves 2-4 runs).
    If variance detected: continue up to max_runs.

Expected average: ~1.4 runs/persona (down from fixed 3),
saving ~50% of API calls in standard mode.
"""

from __future__ import annotations


def should_continue_sampling(
    run_idx: int,
    decisions: list[str],
    temperature: float = 0.0,
    mode: str = "standard",
) -> bool:
    """
    Determine whether to continue running more samples for a persona.

    Adaptive sampling logic:
        1. Run 0 always executes (this is called *after* a run completes).
        2. If temperature=0 and first decision is clear → stop.
        3. If variance detected among existing decisions → continue.
        4. In quick mode, always stop after 1 run.

    Args:
        run_idx: Zero-based index of the run just completed.
        decisions: List of decisions collected so far.
        temperature: LLM temperature setting.
        mode: Audit mode — "quick" | "standard" | "full".

    Returns:
        True if more runs should be executed, False to stop.
    """
    # Quick mode: always stop after 1 run
    if mode == "quick":
        return False

    # First run just completed — decide whether to continue
    if run_idx == 0:
        # If temperature is 0, the response is deterministic
        if temperature == 0.0 and _is_clear_decision(decisions[-1]):
            return False
        # Otherwise, run at least one more for variance estimation
        return True

    # Subsequent runs: check for variance
    unique_decisions = set(decisions)
    if len(unique_decisions) == 1:
        # All decisions agree — no variance, stop early
        return False

    # Variance detected — continue up to mode-dependent limit
    max_runs = {"standard": 3, "full": 5}.get(mode, 3)
    return run_idx + 1 < max_runs


def _is_clear_decision(decision: str) -> bool:
    """
    Check if a decision is unambiguous (not "ambiguous").

    Args:
        decision: The parsed decision string.

    Returns:
        True if the decision is clear (positive or negative).
    """
    return decision in ("positive", "negative")
