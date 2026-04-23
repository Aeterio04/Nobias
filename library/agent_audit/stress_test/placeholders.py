"""
agent_audit.stress_test.placeholders — Placeholder Expansion
================================================================

Handles natural-language placeholder syntax for stress test probes:
    {male_name/female_name}
    {his/her}
    {son/daughter}
    {man/woman}

Produces more realistic, grammatically natural probes than blunt
attribute injection (Staab et al. 2025).
"""

from __future__ import annotations

import re
from typing import Any


# Default placeholder expansions by attribute
DEFAULT_EXPANSIONS: dict[str, dict[str, list[str]]] = {
    "gender": {
        "male_name/female_name": ["James", "Sarah"],
        "his/her": ["his", "her"],
        "him/her": ["him", "her"],
        "he/she": ["he", "she"],
        "son/daughter": ["son", "daughter"],
        "man/woman": ["man", "woman"],
        "Mr/Ms": ["Mr.", "Ms."],
        "husband/wife": ["husband", "wife"],
        "father/mother": ["father", "mother"],
        "boy/girl": ["boy", "girl"],
    },
    "race": {
        "white_name/black_name": ["Greg", "Jamal"],
        "western/eastern": ["Western", "Eastern"],
    },
}


def expand_placeholders(
    template: str,
    expansions: dict[str, list[str]] | None = None,
) -> list[str]:
    """
    Expand a template with placeholders into all variants.

    Placeholder syntax: {option_a/option_b/option_c}
    Each placeholder produces one variant per option.

    Args:
        template: Text with {a/b} placeholders.
        expansions: Optional custom expansion mappings.

    Returns:
        List of expanded text variants.
    """
    # Find all placeholders
    placeholders = re.findall(r"\{([^}]+)\}", template)
    if not placeholders:
        return [template]

    # Parse each placeholder into its options
    placeholder_options: list[list[str]] = []
    for ph in placeholders:
        options = [opt.strip() for opt in ph.split("/")]
        placeholder_options.append(options)

    # Determine max variants (use the first placeholder's option count)
    if not placeholder_options:
        return [template]

    max_variants = max(len(opts) for opts in placeholder_options)
    variants: list[str] = []

    for variant_idx in range(max_variants):
        text = template
        for ph, options in zip(placeholders, placeholder_options):
            # Use modulo to cycle through options if lengths differ
            opt_idx = variant_idx % len(options)
            text = text.replace(f"{{{ph}}}", options[opt_idx], 1)
        variants.append(text)

    return variants


def detect_placeholders(text: str) -> list[str]:
    """
    Find all placeholder patterns in a text.

    Args:
        text: Text that may contain {a/b} placeholders.

    Returns:
        List of placeholder strings (without braces).
    """
    return re.findall(r"\{([^}]+/[^}]+)\}", text)


def inject_placeholders(
    seed_case: str,
    attribute: str = "gender",
) -> str:
    """
    Convert a plain seed case into a placeholder-enhanced template.

    Detects common attribute-related words and replaces them with
    placeholder syntax for natural counterfactual generation.

    Args:
        seed_case: Original seed case text.
        attribute: Which attribute to create placeholders for.

    Returns:
        Modified text with placeholder syntax.
    """
    if attribute not in DEFAULT_EXPANSIONS:
        return seed_case

    result = seed_case
    expansions = DEFAULT_EXPANSIONS[attribute]

    for placeholder, options in expansions.items():
        for option in options:
            # Replace exact word matches (case-insensitive)
            pattern = re.compile(rf"\b{re.escape(option)}\b", re.IGNORECASE)
            if pattern.search(result):
                replacement = f"{{{placeholder}}}"
                result = pattern.sub(replacement, result, count=1)
                break  # Only replace the first match per placeholder

    return result
