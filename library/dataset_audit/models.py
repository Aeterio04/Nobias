from dataclasses import dataclass
from typing import Optional


@dataclass
class DatasetFinding:
    """Represents a single bias finding in the dataset."""
    check: str
    severity: str
    message: str
    metric: str
    value: float
    threshold: float
    confidence: float


@dataclass
class ProxyFeature:
    """Represents a feature that may be a proxy for a protected attribute."""
    feature: str
    protected: str
    method: str
    score: float
    nmi: float


@dataclass
class Remediation:
    """Represents a remediation strategy with estimated impact."""
    strategy: str
    estimated_dir_after: float
    estimated_spd_after: float
    description: Optional[str] = None
