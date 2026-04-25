"""
agent_audit.report.utils — Report Utility Functions
====================================================

Helper functions for report generation:
    - Severity badges
    - Text wrapping
    - Duration formatting
    - Statistical calculations
"""

from __future__ import annotations


def severity_badge(severity: str, use_emoji: bool = True) -> str:
    """
    Return a formatted severity badge with emoji.
    
    Args:
        severity: Severity level (CRITICAL, MODERATE, LOW, CLEAR).
        use_emoji: If False, uses ASCII-safe symbols for Windows compatibility.
    
    Returns:
        Formatted badge string.
    """
    if use_emoji:
        badges = {
            "CRITICAL": "🔴 CRITICAL",
            "MODERATE": "🟡 MODERATE",
            "LOW": "🟢 LOW",
            "CLEAR": "✅ CLEAR",
        }
    else:
        badges = {
            "CRITICAL": "[!] CRITICAL",
            "MODERATE": "[~] MODERATE",
            "LOW": "[*] LOW",
            "CLEAR": "[+] CLEAR",
        }
    return badges.get(severity, severity)


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds.
    
    Returns:
        Formatted duration string (e.g., "2m 30s", "1h 15m").
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def wrap_text(text: str, width: int, indent: str = "") -> str:
    """
    Wrap text to specified width with optional indent.
    
    Args:
        text: Text to wrap.
        width: Maximum line width.
        indent: String to prepend to each line.
    
    Returns:
        Wrapped text with newlines.
    """
    words = text.split()
    lines = []
    current_line = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) + 1 <= width:
            current_line.append(word)
            current_length += len(word) + 1
        else:
            if current_line:
                lines.append(indent + " ".join(current_line))
            current_line = [word]
            current_length = len(word)
    
    if current_line:
        lines.append(indent + " ".join(current_line))
    
    return "\n".join(lines)


def std_dev(values: list[float]) -> float:
    """
    Calculate standard deviation.
    
    Args:
        values: List of numeric values.
    
    Returns:
        Standard deviation.
    """
    if not values:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    return variance ** 0.5


def estimate_tokens(api_calls: int, avg_tokens_per_call: int = 500) -> dict[str, int]:
    """
    Estimate token usage from API calls.
    
    Args:
        api_calls: Number of API calls made.
        avg_tokens_per_call: Average tokens per call (default 500).
    
    Returns:
        Dict with total, input, and output token estimates.
    """
    total = api_calls * avg_tokens_per_call
    return {
        "total": total,
        "input_tokens": int(total * 0.6),  # Rough 60/40 split
        "output_tokens": int(total * 0.4),
    }


__all__ = [
    "severity_badge",
    "format_duration",
    "wrap_text",
    "std_dev",
    "estimate_tokens",
]
