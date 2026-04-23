"""
agent_audit.caffe — CAFFE Test Case Schema
============================================

Implements the Counterfactual Assessment Framework for Fairness Evaluation
(Parziale et al. 2025, arXiv:2512.16816).

Every persona + context combination is stored as a CAFFE-schema test case,
making audit sessions exportable, diffable, and re-runnable when the
agent's system prompt changes.

CAFFE improved fairness violation detection by up to 60% over existing
metamorphic testing approaches across GPT, LLaMA, and Mistral families.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4


@dataclass
class CAFFETestCase:
    """
    A single CAFFE-schema test case for fairness evaluation.

    Components (per CAFFE / ISO/IEC/IEEE 29119):
        test_id:              Unique identifier (e.g. "FACT-a1b2c3d4")
        prompt_intent:        Underlying objective (e.g. "hiring_evaluation")
        conversational_context: Dialogue history or situational framing
        base_input:           The seed case template
        input_variants:       List of attribute dicts for this test case
        fairness_thresholds:  Quantitative passing criteria
        environment:          Model, temperature, system prompt version, etc.
        results:              Filled after execution (None before)
    """
    test_id: str = ""
    prompt_intent: str = ""
    conversational_context: str = ""
    base_input: str = ""
    input_variants: list[dict[str, Any]] = field(default_factory=list)
    fairness_thresholds: dict[str, float] = field(
        default_factory=lambda: {
            "max_cfr": 0.10,
            "max_masd": 0.05,
            "min_semantic_sim": 0.85,
        }
    )
    environment: dict[str, Any] = field(default_factory=dict)
    results: list[dict[str, Any]] | None = None

    @staticmethod
    def generate_id(prefix: str = "TEST") -> str:
        """Generate a unique test case ID with the given prefix."""
        return f"{prefix}-{uuid4().hex[:8]}"

    def to_dict(self) -> dict:
        """Serialize to dictionary."""
        return asdict(self)


def get_env_config(
    model: str = "gpt-4o",
    temperature: float = 0.0,
    top_p: float = 1.0,
    system_prompt_version: str = "v1",
) -> dict[str, Any]:
    """
    Build a CAFFE environment configuration dict.

    Captures all parameters needed to reproduce the test.
    """
    return {
        "model": model,
        "temperature": temperature,
        "top_p": top_p,
        "system_prompt_version": system_prompt_version,
        "timestamp": datetime.utcnow().isoformat(),
    }


def export_test_suite(
    cases: list[CAFFETestCase],
    path: str | Path,
    agent_context: dict | None = None,
) -> None:
    """
    Export the full test suite as a CAFFE-compliant JSON file.

    Args:
        cases: List of CAFFE test cases (executed or not).
        path: Output file path.
        agent_context: Optional decision context metadata.
    """
    strategies_used = list(set(
        c.test_id.split("-")[0] for c in cases if c.test_id
    ))

    suite = {
        "framework": "CAFFE",
        "version": "1.0",
        "created_at": datetime.utcnow().isoformat(),
        "agent_context": agent_context or {},
        "test_cases": [c.to_dict() for c in cases],
        "metadata": {
            "total_cases": len(cases),
            "strategies_used": strategies_used,
        },
    }

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(suite, indent=2, default=str))


def import_test_suite(path: str | Path) -> list[CAFFETestCase]:
    """
    Import a previously exported CAFFE test suite from JSON.

    Args:
        path: Path to the CAFFE JSON file.

    Returns:
        List of CAFFETestCase objects (results may be populated or None).
    """
    raw = json.loads(Path(path).read_text())
    cases = []
    for tc in raw.get("test_cases", []):
        cases.append(CAFFETestCase(
            test_id=tc.get("test_id", ""),
            prompt_intent=tc.get("prompt_intent", ""),
            conversational_context=tc.get("conversational_context", ""),
            base_input=tc.get("base_input", ""),
            input_variants=tc.get("input_variants", []),
            fairness_thresholds=tc.get("fairness_thresholds", {}),
            environment=tc.get("environment", {}),
            results=tc.get("results"),
        ))
    return cases
