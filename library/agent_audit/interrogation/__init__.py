"""
agent_audit.interrogation — Agent Interrogation Engine (Layer 3)
=================================================================

Async execution engine that sends test cases to the agent under test,
handles rate limiting, output parsing, adaptive sampling, and caching.

Sub-modules:
    - engine.py   : Core InterrogationEngine (async, rate-limited)
    - adaptive.py : Adaptive sampling (early-stop when temperature=0)
    - parsers.py  : Output parser (binary, numeric, free text, CoT)
    - backends/   : LLM backend implementations (OpenAI, Anthropic, Ollama)
"""
