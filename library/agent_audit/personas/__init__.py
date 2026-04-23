"""
agent_audit.personas — Persona Grid Generation (Layer 2)
=========================================================

Three generation strategies:
    - pairwise.py       : Pairwise grid (default for quick/standard)
    - factorial.py      : Full factorial grid (full mode)
    - names.py          : Name-based proxy testing (Bertrand & Mullainathan 2004)
    - context_primes.py : Historical-context variants (CFR-motivated)

All personas are wrapped in the CAFFE test case schema for
reproducibility, versioning, and export.
"""
