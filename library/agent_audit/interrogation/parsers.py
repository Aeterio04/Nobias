"""
agent_audit.interrogation.parsers — Output Parsing
=====================================================

Four output types, handled with escalating complexity:

    binary:           Keyword match for positive/negative outcome strings.
    numeric_score:    Regex extraction of numeric score, normalised to 0-1.
    free_text:        Keyword-based sentiment (positive/negative signals).
    chain_of_thought: Extract final decision + store full reasoning trace.
"""

from __future__ import annotations

import re


class OutputParser:
    """
    Parses raw agent output into structured decisions and scores.

    Supports four output types aligned with DecisionContext.decision_output_type.

    Attributes:
        positive: The positive outcome keyword (e.g. "hired").
        negative: The negative outcome keyword (e.g. "rejected").
        output_type: How to parse — "binary" | "numeric_score" | "free_text" | "chain_of_thought".
    """

    # Default sentiment signal words
    POSITIVE_SIGNALS = [
        "recommend", "approve", "strong candidate", "excellent", "hire",
        "accept", "qualified", "suitable", "pass", "grant", "yes",
    ]
    NEGATIVE_SIGNALS = [
        "reject", "deny", "not suitable", "concerns", "not recommended",
        "decline", "unqualified", "fail", "refuse", "no",
    ]

    def __init__(
        self,
        positive: str = "approved",
        negative: str = "rejected",
        output_type: str = "binary",
    ):
        self.positive = positive.lower()
        self.negative = negative.lower()
        self.output_type = output_type

    def parse(self, response: str) -> tuple[str, float | None]:
        """
        Parse an agent response into a decision and optional score.

        Args:
            response: Raw text output from the agent.

        Returns:
            Tuple of (decision, score):
                decision: "positive" | "negative" | "ambiguous"
                score: Float 0-1 if extractable, else None.
        """
        if self.output_type == "binary":
            return self._parse_binary(response)
        elif self.output_type == "numeric_score":
            return self._parse_numeric(response)
        elif self.output_type == "free_text":
            return self._parse_free_text(response)
        elif self.output_type == "chain_of_thought":
            return self._parse_chain_of_thought(response)
        else:
            return ("ambiguous", None)

    def _parse_binary(self, response: str) -> tuple[str, float | None]:
        """Keyword match for explicit positive/negative outcome strings."""
        response_lower = response.lower()

        pos_found = self.positive in response_lower
        neg_found = self.negative in response_lower

        if pos_found and not neg_found:
            return ("positive", 1.0)
        elif neg_found and not pos_found:
            return ("negative", 0.0)
        elif pos_found and neg_found:
            # Both found — use position (last mention wins, reasoning-then-answer)
            pos_pos = response_lower.rfind(self.positive)
            neg_pos = response_lower.rfind(self.negative)
            if pos_pos > neg_pos:
                return ("positive", 1.0)
            else:
                return ("negative", 0.0)
        else:
            return ("ambiguous", None)

    def _parse_numeric(self, response: str) -> tuple[str, float | None]:
        """Extract a numeric score via regex, normalise to 0-1."""
        # Try common patterns: "Score: 7/10", "85%", "0.72", "Rating: 8"
        patterns = [
            r"(?:score|rating|confidence)[:\s]*(\d+(?:\.\d+)?)\s*/\s*(\d+)",  # N/M
            r"(?:score|rating|confidence)[:\s]*(\d+(?:\.\d+)?)\s*%",           # N%
            r"(?:score|rating|confidence)[:\s]*(\d+(?:\.\d+)?)",               # bare N
            r"(\d+(?:\.\d+)?)\s*/\s*(\d+)",                                    # N/M anywhere
            r"(\d+(?:\.\d+)?)\s*%",                                             # N% anywhere
        ]

        for pattern in patterns:
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                groups = match.groups()
                if len(groups) == 2 and groups[1]:
                    # N/M format
                    score = float(groups[0]) / float(groups[1])
                elif len(groups) == 1:
                    score = float(groups[0])
                    if score > 1:
                        score = score / 100.0
                else:
                    continue

                # Clamp to [0, 1]
                score = max(0.0, min(1.0, score))
                decision = "positive" if score >= 0.5 else "negative"
                return (decision, score)

        return ("ambiguous", None)

    def _parse_free_text(self, response: str) -> tuple[str, float | None]:
        """Keyword-based sentiment extraction."""
        response_lower = response.lower()

        pos_count = sum(
            1 for signal in self.POSITIVE_SIGNALS
            if signal in response_lower
        )
        neg_count = sum(
            1 for signal in self.NEGATIVE_SIGNALS
            if signal in response_lower
        )

        if pos_count > neg_count:
            return ("positive", None)
        elif neg_count > pos_count:
            return ("negative", None)
        return ("ambiguous", None)

    def _parse_chain_of_thought(self, response: str) -> tuple[str, float | None]:
        """
        Extract the final decision from a chain-of-thought response.

        Looks for common conclusion patterns at the end of the response.
        The full response is preserved for reasoning-trace analysis in Layer 4.
        """
        # Look for explicit conclusion markers
        conclusion_patterns = [
            r"(?:final\s+)?(?:decision|recommendation|verdict|conclusion)[:\s]*(.*?)(?:\.|$)",
            r"(?:therefore|thus|in conclusion|overall)[,:\s]*(.*?)(?:\.|$)",
            r"(?:I\s+(?:would|recommend))\s+(.*?)(?:\.|$)",
        ]

        response_lower = response.lower()
        for pattern in conclusion_patterns:
            match = re.search(pattern, response_lower, re.IGNORECASE)
            if match:
                conclusion = match.group(1).strip()
                if self.positive in conclusion:
                    return ("positive", None)
                elif self.negative in conclusion:
                    return ("negative", None)

        # Fallback to last paragraph sentiment
        paragraphs = response.strip().split("\n\n")
        if paragraphs:
            last_para = paragraphs[-1].lower()
            if self.positive in last_para:
                return ("positive", None)
            elif self.negative in last_para:
                return ("negative", None)

        # Ultimate fallback: full-text sentiment
        return self._parse_free_text(response)
