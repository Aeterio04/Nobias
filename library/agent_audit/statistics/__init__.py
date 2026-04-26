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
    - confidence.py      : Confidence intervals & Bonferroni correction (FairSight)
    - eeoc_air.py        : EEOC Adverse Impact Ratio (FairSight)
    - stability.py       : Stochastic Stability Score & BA-CFR (FairSight)
"""

from agent_audit.statistics.cfr import compute_all_cfr
from agent_audit.statistics.masd import compute_per_attribute_masd
from agent_audit.statistics.parity import compute_all_parity
from agent_audit.statistics.intersectional import intersectional_scan, should_run_intersectional
from agent_audit.statistics.significance import compute_significance
from agent_audit.statistics.severity import classify_severity, classify_overall_severity
from agent_audit.statistics.confidence import (
    compute_proportion_ci,
    compute_rate_with_ci,
    apply_bonferroni_correction,
    compute_statistical_power,
)
from agent_audit.statistics.eeoc_air import compute_eeoc_air, compute_all_eeoc_air
from agent_audit.statistics.stability import (
    compute_stochastic_stability_score,
    compute_overall_stability,
    compute_bias_adjusted_cfr,
)

__all__ = [
    "compute_all_cfr",
    "compute_per_attribute_masd",
    "compute_all_parity",
    "intersectional_scan",
    "should_run_intersectional",
    "compute_significance",
    "classify_severity",
    "classify_overall_severity",
    "compute_proportion_ci",
    "compute_rate_with_ci",
    "apply_bonferroni_correction",
    "compute_statistical_power",
    "compute_eeoc_air",
    "compute_all_eeoc_air",
    "compute_stochastic_stability_score",
    "compute_overall_stability",
    "compute_bias_adjusted_cfr",
]
