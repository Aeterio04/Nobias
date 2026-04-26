"""
Main API for model auditing.
"""
from typing import Union, Any, Optional
from pathlib import Path
import pandas as pd
import numpy as np
import time
import uuid
from datetime import datetime

from .models import (
    ModelAuditReport,
    ModelAuditConfig,
    ModelFinding,
    MitigationOption,
    Severity,
    ModelIntegrity,
    ModelFingerprint,
)
from .loading import prepare_model_and_data, ModelLoadError, DataLoadError
from .baseline import (
    get_predictions,
    compute_baseline_metrics,
    compute_per_group_metrics,
)
from .counterfactual import run_counterfactual_test, identify_high_risk_flips
from .fairness_metrics import compute_all_fairness_metrics
from .intersectional import analyze_intersectional_bias
from .severity import classify_severity, classify_metric_severity
from .report import export_report


def audit_model(
    model: Union[str, Path, Any],
    test_data: Union[str, Path, pd.DataFrame],
    protected_attributes: list[str],
    target_column: str,
    positive_value: Any = 1,
    config: Optional[ModelAuditConfig] = None,
) -> ModelAuditReport:
    """
    Audit a trained ML model for fairness and bias.
    
    This is the main entry point for model auditing. It runs a comprehensive
    fairness analysis including:
    - Baseline performance metrics
    - Counterfactual flip testing
    - Group fairness metrics (demographic parity, equalized odds, etc.)
    - Intersectional bias analysis
    - Severity classification
    - Mitigation recommendations
    
    Args:
        model: Path to serialized model (.pkl, .joblib) or model object
        test_data: Path to test CSV or DataFrame
        protected_attributes: List of protected attribute column names
        target_column: Name of target/label column
        positive_value: Value representing positive class (default: 1)
        config: Optional ModelAuditConfig for custom settings
        
    Returns:
        ModelAuditReport with complete audit results
        
    Raises:
        ModelLoadError: If model cannot be loaded
        DataLoadError: If test data cannot be loaded
        
    Example:
        >>> from nobias.model_audit import audit_model
        >>> report = audit_model(
        ...     model="model.pkl",
        ...     test_data="test.csv",
        ...     protected_attributes=["gender", "race"],
        ...     target_column="hired",
        ...     positive_value=1
        ... )
        >>> print(report)
        >>> report.export("audit_report.json")
    """
    # Use default config if not provided
    if config is None:
        config = ModelAuditConfig(
            protected_attributes=protected_attributes,
            target_column=target_column,
            positive_value=positive_value,
        )
    
    # Start timing
    start_time = time.time()
    audit_id = f"model_audit_{uuid.uuid4().hex[:8]}"
    
    print("=" * 80)
    print("MODEL FAIRNESS AUDIT")
    print("=" * 80)
    print(f"Audit ID: {audit_id}")
    print(f"Timestamp: {datetime.utcnow().isoformat()}")
    
    # Step 1: Load and validate model and data
    print("\n[1/6] Loading model and data...")
    try:
        model_obj, model_name, X_test, y_test, model_type, feature_names, X_for_model = prepare_model_and_data(
            model, test_data, target_column, protected_attributes
        )
        print(f"  [OK] Loaded model: {model_name} ({model_type.value})")
        print(f"  [OK] Test samples: {len(X_test):,}")
        print(f"  [OK] Features used by model: {len(feature_names)}")
        print(f"  [OK] Protected attributes: {', '.join(protected_attributes)}")
    except (ModelLoadError, DataLoadError) as e:
        print(f"  [ERROR] Error: {e}")
        raise
    
    # Step 2: Get baseline predictions
    print("\n[2/6] Computing baseline predictions...")
    predictions, confidence_scores = get_predictions(model_obj, X_for_model, model_type)
    baseline_metrics = compute_baseline_metrics(
        y_test.values, predictions, model_type, positive_value
    )
    per_group_metrics = compute_per_group_metrics(
        X_test, y_test.values, predictions, protected_attributes, model_type, positive_value
    )
    print(f"  [OK] Baseline accuracy: {baseline_metrics.get('accuracy', 0):.4f}")
    
    # Step 3: Run counterfactual testing
    print("\n[3/6] Running counterfactual flip tests...")
    counterfactual_result = run_counterfactual_test(
        model_obj,
        X_test,  # Use full X_test with protected attributes
        predictions,
        confidence_scores,
        protected_attributes,
        model_type,
        sample_limit=config.counterfactual_sample_limit,
        X_for_model_columns=list(X_for_model.columns),  # Pass model feature names
    )
    print(f"  [OK] Flip rate: {counterfactual_result.flip_rate:.2%}")
    print(f"  [OK] Total flips: {counterfactual_result.total_flips:,} / {counterfactual_result.total_comparisons:,}")
    
    # Step 4: Compute fairness metrics
    print("\n[4/6] Computing fairness metrics...")
    scorecard = {}
    
    # For each protected attribute, compute metrics for all pairwise comparisons
    for attr in protected_attributes:
        if attr not in X_test.columns:
            continue
        
        unique_values = sorted(X_test[attr].unique())
        
        # Compare first value (often privileged) with others
        if len(unique_values) >= 2:
            privileged = unique_values[0]
            
            for unprivileged in unique_values[1:]:
                metrics = compute_all_fairness_metrics(
                    X_test,
                    y_test.values,
                    predictions,
                    confidence_scores,
                    attr,
                    privileged,
                    unprivileged,
                    positive_value,
                    config.fairness_thresholds,
                )
                
                # Add to scorecard with unique keys
                for metric_name, metric_result in metrics.items():
                    key = f"{attr}_{privileged}_vs_{unprivileged}_{metric_name}"
                    scorecard[key] = metric_result
    
    passed = sum(1 for m in scorecard.values() if m.passed)
    total = len(scorecard)
    print(f"  [OK] Metrics computed: {passed}/{total} passed")
    
    # Step 5: Intersectional analysis
    intersectional_findings = []
    if config.run_intersectional and len(protected_attributes) >= 2:
        print("\n[5/6] Analyzing intersectional bias...")
        intersectional_findings = analyze_intersectional_bias(
            X_test, predictions, protected_attributes, positive_value
        )
        print(f"  [OK] Intersectional findings: {len(intersectional_findings)}")
    else:
        print("\n[5/6] Skipping intersectional analysis")
    
    # Step 6: Generate findings and recommendations
    print("\n[6/6] Generating findings and recommendations...")
    findings = _generate_findings(
        scorecard, counterfactual_result, intersectional_findings, protected_attributes
    )
    mitigation_options = _generate_mitigation_options(
        scorecard, counterfactual_result, model_type
    )
    
    # Classify overall severity
    overall_severity = classify_severity(scorecard, counterfactual_result, config.severity_thresholds)
    
    print(f"  [OK] Findings: {len(findings)}")
    print(f"  [OK] Mitigation options: {len(mitigation_options)}")
    print(f"  [OK] Overall severity: {overall_severity.value}")
    
    # Compute audit integrity
    duration_seconds = time.time() - start_time
    
    model_fingerprint = ModelFingerprint(
        model_name=model_name,
        model_type=model_type.value,
        feature_count=len(feature_names),
        model_hash=ModelIntegrity.compute_hash(str(model_obj)),
    )
    
    audit_integrity = ModelIntegrity(
        model_hash=model_fingerprint.model_hash,
        predictions_hash=ModelIntegrity.compute_hash(predictions.tolist()),
        config_hash=ModelIntegrity.compute_hash({
            'protected_attributes': protected_attributes,
            'target_column': target_column,
            'positive_value': str(positive_value),
        }),
    )
    audit_integrity.audit_hash = ModelIntegrity.compute_hash({
        'audit_id': audit_id,
        'model_hash': audit_integrity.model_hash,
        'predictions_hash': audit_integrity.predictions_hash,
        'config_hash': audit_integrity.config_hash,
    })
    
    # Create report
    report = ModelAuditReport(
        audit_id=audit_id,
        model_name=model_name,
        model_type=model_type,
        test_sample_count=len(X_test),
        protected_attributes=protected_attributes,
        overall_severity=overall_severity,
        scorecard=scorecard,
        counterfactual_result=counterfactual_result,
        findings=findings,
        mitigation_options=mitigation_options,
        intersectional_findings=intersectional_findings,
        baseline_metrics=baseline_metrics,
        per_group_metrics=per_group_metrics,
        audit_integrity=audit_integrity,
        model_fingerprint=model_fingerprint,
        duration_seconds=duration_seconds,
        timestamp=datetime.utcnow().isoformat(),
    )
    
    print("\n" + "=" * 80)
    print("AUDIT COMPLETE")
    print("=" * 80)
    print(f"\nAudit ID: {audit_id}")
    print(f"Duration: {duration_seconds:.2f}s")
    print(f"Overall Severity: {overall_severity.value}")
    print(f"Critical Findings: {sum(1 for f in findings if f.severity == Severity.CRITICAL)}")
    print(f"Moderate Findings: {sum(1 for f in findings if f.severity == Severity.MODERATE)}")
    print(f"Low Findings: {sum(1 for f in findings if f.severity == Severity.LOW)}")
    
    return report


def _generate_findings(
    scorecard: dict,
    counterfactual_result,
    intersectional_findings: list,
    protected_attributes: list[str],
) -> list[ModelFinding]:
    """Generate findings from audit results."""
    findings = []
    finding_id = 1
    
    # Findings from failed metrics
    for metric_key, metric_result in scorecard.items():
        if not metric_result.passed:
            severity = classify_metric_severity(metric_result)
            
            finding = ModelFinding(
                finding_id=f"F{finding_id:03d}",
                severity=severity,
                category="group_fairness",
                title=f"{metric_result.metric_name} violation",
                description=metric_result.description,
                evidence={
                    "metric_value": metric_result.value,
                    "threshold": metric_result.threshold,
                    "p_value": metric_result.p_value,
                },
                affected_groups=[
                    metric_result.privileged_group or "",
                    metric_result.unprivileged_group or "",
                ],
                metric_results=[metric_result],
            )
            findings.append(finding)
            finding_id += 1
    
    # Findings from counterfactual testing
    high_risk_attrs = identify_high_risk_flips(counterfactual_result, threshold=0.05)
    if high_risk_attrs:
        severity = Severity.CRITICAL if counterfactual_result.flip_rate > 0.15 else Severity.MODERATE
        
        finding = ModelFinding(
            finding_id=f"F{finding_id:03d}",
            severity=severity,
            category="counterfactual",
            title="High counterfactual flip rate detected",
            description=(
                f"Model predictions flip in {counterfactual_result.flip_rate:.2%} of cases "
                f"when protected attributes are changed, indicating individual fairness violations."
            ),
            evidence={
                "flip_rate": counterfactual_result.flip_rate,
                "total_flips": counterfactual_result.total_flips,
                "high_risk_attributes": high_risk_attrs,
                "flips_by_attribute": counterfactual_result.flips_by_attribute,
            },
            affected_groups=high_risk_attrs,
        )
        findings.append(finding)
        finding_id += 1
    
    # Findings from intersectional analysis
    for intersect_finding in intersectional_findings:
        if intersect_finding.severity in [Severity.CRITICAL, Severity.MODERATE]:
            attrs_str = " & ".join(f"{k}={v}" for k, v in intersect_finding.attribute_values.items())
            
            finding = ModelFinding(
                finding_id=f"F{finding_id:03d}",
                severity=intersect_finding.severity,
                category="intersectional",
                title=f"Intersectional bias: {attrs_str}",
                description=(
                    f"Group {attrs_str} shows compounded bias with approval rate "
                    f"{intersect_finding.metric_value:.2%} vs expected {intersect_finding.baseline_value:.2%}"
                ),
                evidence={
                    "approval_rate": intersect_finding.metric_value,
                    "expected_rate": intersect_finding.baseline_value,
                    "sample_count": intersect_finding.sample_count,
                },
                affected_groups=[attrs_str],
            )
            findings.append(finding)
            finding_id += 1
    
    # Sort by severity
    findings.sort(
        key=lambda f: ["CLEAR", "LOW", "MODERATE", "CRITICAL"].index(f.severity.value),
        reverse=True
    )
    
    return findings


def _generate_mitigation_options(
    scorecard: dict,
    counterfactual_result,
    model_type,
) -> list[MitigationOption]:
    """Generate mitigation recommendations."""
    options = []
    
    # Check if we have fairness violations
    has_violations = any(not m.passed for m in scorecard.values())
    has_high_flip_rate = counterfactual_result.flip_rate > 0.05
    
    if not has_violations and not has_high_flip_rate:
        return options
    
    # Post-processing: Threshold adjustment
    if any("demographic_parity" in k or "equalized_odds" in k for k in scorecard.keys()):
        options.append(MitigationOption(
            strategy_name="Threshold Adjustment",
            category="post_processing",
            description="Adjust decision thresholds per demographic group to equalize error rates",
            expected_impact="Can achieve equalized odds with minimal accuracy loss (typically <2%)",
            implementation_complexity="low",
            requires_retraining=False,
            parameters={"method": "equalized_odds_postprocessing"},
            code_example="# Use fairlearn's ThresholdOptimizer\nfrom fairlearn.postprocessing import ThresholdOptimizer",
        ))
    
    # Pre-processing: Sample reweighting
    if has_violations:
        options.append(MitigationOption(
            strategy_name="Sample Reweighting",
            category="pre_processing",
            description="Assign fairness-aware weights to training samples to reduce bias",
            expected_impact="Moderate improvement in fairness metrics, may reduce accuracy by 1-3%",
            implementation_complexity="medium",
            requires_retraining=True,
            parameters={"method": "reweighting"},
            code_example="# Use fairlearn's reweighting\nfrom fairlearn.reductions import ExponentiatedGradient",
        ))
    
    # Feature removal if high flip rate
    if has_high_flip_rate:
        options.append(MitigationOption(
            strategy_name="Remove Proxy Features",
            category="pre_processing",
            description="Remove features highly correlated with protected attributes",
            expected_impact="Reduces individual fairness violations, may impact accuracy",
            implementation_complexity="low",
            requires_retraining=True,
            parameters={"correlation_threshold": 0.3},
        ))
    
    return options


# Convenience function for quick audits
def quick_audit(
    model: Any,
    X_test: pd.DataFrame,
    y_test: pd.Series,
    protected_attributes: list[str],
    positive_value: Any = 1,
) -> ModelAuditReport:
    """
    Quick audit for models already loaded in memory.
    
    Args:
        model: Model object with predict() method
        X_test: Test features (includes protected attributes)
        y_test: Test labels
        protected_attributes: List of protected attribute column names
        positive_value: Value representing positive class
        
    Returns:
        ModelAuditReport
    """
    # Create temporary DataFrame with target
    test_data = X_test.copy()
    test_data['_target'] = y_test
    
    return audit_model(
        model=model,
        test_data=test_data,
        protected_attributes=protected_attributes,
        target_column='_target',
        positive_value=positive_value,
    )

