"""
agent_audit.interpreter — LLM Interpreter & Remediation (Layer 5)
===================================================================

Single tightly-scoped LLM call on statistical outputs only.
Follows the Checker→Reasoner pattern (Huang & Fan 2025):
    Layer 4 (checker) = deterministic statistics
    Layer 5 (reasoner) = LLM that explains and suggests fixes

Critical constraint: The LLM receives ONLY statistical findings,
never raw agent outputs. Zero hallucination surface in detection.

Sub-modules:
    - prompt_builder.py : Build interpreter prompt from findings
    - interpreter.py    : Call LLM (local/cloud), parse response
    - remediation.py    : Prompt surgery suggestions + verify loop
"""
