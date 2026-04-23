"""
agent_audit.statistics — Statistical Bias Detection (Layer 4)
===============================================================

THE MOST IMPORTANT LAYER. No LLM touches this code.
Every metric is computed with standard statistical tests in pure Python.

Sub-modules:
    - cfr.py             : Counterfactual Flip Rate (primary metric)
    - masd.py            : Mean Absolute Score Difference
    - parity.py          : Demographic parity + EEOC 80% rule
    - intersectional.py  : k-way intersection disparity scans
    - significance.py    : Chi-square, Welch's t-test, Mann-Whitney U
    - reasoning_trace.py : Keyword freq + embedding similarity (CAFFE)
    - context_impact.py  : Context-prime amplification analysis
    - severity.py        : Severity classifier with benchmarked thresholds
"""
