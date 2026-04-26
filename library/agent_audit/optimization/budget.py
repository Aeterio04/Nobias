"""
agent_audit.optimization.budget — Token Budget Management
==========================================================

Track and manage token usage across audit runs.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class TokenBudget:
    """
    Token budget tracker for an audit run.
    
    Tracks input, output, and cached tokens separately.
    """
    max_tokens: int
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    calls: int = 0
    
    def add_call(
        self,
        input_tokens: int,
        output_tokens: int,
        cached: bool = False,
    ) -> None:
        """
        Record a single API call.
        
        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            cached: Whether input was cached (10% cost)
        """
        if cached:
            self.cached_input_tokens += input_tokens
            self.input_tokens += int(input_tokens * 0.1)  # 10% cost for cached
        else:
            self.input_tokens += input_tokens
        
        self.output_tokens += output_tokens
        self.calls += 1
    
    @property
    def total_tokens(self) -> int:
        """Total tokens used (input + output)."""
        return self.input_tokens + self.output_tokens
    
    @property
    def remaining_tokens(self) -> int:
        """Tokens remaining in budget."""
        return max(0, self.max_tokens - self.total_tokens)
    
    @property
    def usage_percent(self) -> float:
        """Percentage of budget used."""
        return (self.total_tokens / self.max_tokens) * 100 if self.max_tokens > 0 else 0
    
    def can_afford(self, estimated_tokens: int) -> bool:
        """Check if we can afford an operation."""
        return self.remaining_tokens >= estimated_tokens
    
    def to_dict(self) -> dict[str, Any]:
        """Export budget stats."""
        return {
            "max_tokens": self.max_tokens,
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "cached_input_tokens": self.cached_input_tokens,
            "total_tokens": self.total_tokens,
            "remaining_tokens": self.remaining_tokens,
            "usage_percent": round(self.usage_percent, 2),
            "calls": self.calls,
            "avg_tokens_per_call": round(self.total_tokens / self.calls, 2) if self.calls > 0 else 0,
        }


def estimate_call_tokens(
    agent_output_length: int,
    context_length: int = 0,
    use_caching: bool = True,
    is_first_call: bool = False,
) -> dict[str, int]:
    """
    Estimate tokens for a single evaluation call.
    
    Args:
        agent_output_length: Length of agent output in characters
        context_length: Length of context in characters
        use_caching: Whether prompt caching is enabled
        is_first_call: If True, system prompt not cached yet
    
    Returns:
        Dict with 'input', 'output', 'total' estimates
    """
    # System prompt: ~350 tokens (cached after first call)
    system_tokens = 350
    
    # User prompt template: ~100 tokens
    template_tokens = 100
    
    # Agent output: ~1 token per 4 chars
    output_content_tokens = agent_output_length // 4
    
    # Context: ~1 token per 4 chars
    context_tokens = context_length // 4
    
    # Total input
    input_tokens = system_tokens + template_tokens + output_content_tokens + context_tokens
    
    # Output: JSON response ~60 tokens
    output_tokens = 60
    
    if use_caching and not is_first_call:
        # System prompt cached at 10% cost
        effective_input = int(system_tokens * 0.1) + template_tokens + output_content_tokens + context_tokens
    else:
        effective_input = input_tokens
    
    return {
        "input": input_tokens,
        "effective_input": effective_input,
        "output": output_tokens,
        "total": effective_input + output_tokens,
    }


@dataclass
class UsageTracker:
    """
    Track usage across multiple audit runs.
    
    Useful for monitoring costs over time.
    """
    runs: list[dict[str, Any]] = field(default_factory=list)
    
    def add_run(
        self,
        audit_id: str,
        budget: TokenBudget,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Record a completed audit run."""
        run_data = {
            "audit_id": audit_id,
            **budget.to_dict(),
            "metadata": metadata or {},
        }
        self.runs.append(run_data)
    
    def get_total_tokens(self) -> int:
        """Total tokens across all runs."""
        return sum(run["total_tokens"] for run in self.runs)
    
    def get_total_calls(self) -> int:
        """Total API calls across all runs."""
        return sum(run["calls"] for run in self.runs)
    
    def get_average_tokens_per_run(self) -> float:
        """Average tokens per audit run."""
        if not self.runs:
            return 0.0
        return self.get_total_tokens() / len(self.runs)
    
    def to_dict(self) -> dict[str, Any]:
        """Export tracker stats."""
        return {
            "total_runs": len(self.runs),
            "total_tokens": self.get_total_tokens(),
            "total_calls": self.get_total_calls(),
            "avg_tokens_per_run": round(self.get_average_tokens_per_run(), 2),
            "runs": self.runs,
        }


# Global tracker instance (optional)
_global_tracker = UsageTracker()


def track_usage(audit_id: str, budget: TokenBudget, metadata: dict | None = None) -> None:
    """Add a run to the global tracker."""
    _global_tracker.add_run(audit_id, budget, metadata)


def get_global_usage() -> dict[str, Any]:
    """Get global usage statistics."""
    return _global_tracker.to_dict()


def reset_global_tracker() -> None:
    """Reset the global tracker."""
    global _global_tracker
    _global_tracker = UsageTracker()


__all__ = [
    "TokenBudget",
    "estimate_call_tokens",
    "UsageTracker",
    "track_usage",
    "get_global_usage",
    "reset_global_tracker",
]
