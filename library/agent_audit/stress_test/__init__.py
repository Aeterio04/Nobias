"""
agent_audit.stress_test — Adaptive Bias-Eliciting Probe Generation
=====================================================================

Implements the mutation-selection loop from Staab et al. (2025),
adapted for our architecture.

The stress test triggers when:
    1. User opts in explicitly, OR
    2. Standard audit returns all-CLEAR findings

Sub-modules:
    - prober.py       : AdaptiveBiasProber (mutation-selection loop)
    - placeholders.py : {male/female} placeholder expansion
"""
