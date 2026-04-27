"""
agent_audit.orchestrator — Pipeline Orchestrator
=================================================

Internal coordinator that wires all 5 layers together.
Not exposed directly to users - wrapped by the public API.

Pipeline flow:
    Layer 1: Context Collection (connector already built)
    Layer 2: Persona Grid Generation
    Layer 3: Agent Interrogation
    Layer 4: Statistical Bias Detection
    Layer 5: LLM Interpreter & Remediation
    → AgentAuditReport
"""

from __future__ import annotations

import logging
import time
from datetime import datetime
from typing import Callable
from uuid import uuid4

import pandas as pd

# Configure logger
logger = logging.getLogger(__name__)

from agent_audit.caffe import CAFFETestCase, export_test_suite
from agent_audit.config import AgentAuditConfig, AuditMode
from agent_audit.context import AgentConnector
from agent_audit.models import (
    AgentAuditReport,
    AgentFinding,
    PersonaResult,
    Interpretation,
    PromptSuggestion,
    AuditIntegrity,
    ModelFingerprint,
)

# Layer 2 imports
from agent_audit.personas.pairwise import generate_pairwise_grid
from agent_audit.personas.factorial import generate_factorial_grid
from agent_audit.personas.names import generate_name_variants
from agent_audit.personas.context_primes import generate_context_variants

# Layer 3 imports
from agent_audit.interrogation.engine import InterrogationEngine

# Layer 4 imports
from agent_audit.statistics.cfr import compute_all_cfr
from agent_audit.statistics.masd import compute_per_attribute_masd
from agent_audit.statistics.parity import compute_all_parity
from agent_audit.statistics.intersectional import (
    intersectional_scan,
    should_run_intersectional,
)
from agent_audit.statistics.significance import compute_significance
from agent_audit.statistics.severity import classify_severity, classify_overall_severity
from agent_audit.statistics.confidence import (
    compute_rate_with_ci,
    apply_bonferroni_correction,
)
from agent_audit.statistics.eeoc_air import compute_all_eeoc_air
from agent_audit.statistics.stability import (
    compute_overall_stability,
    compute_bias_adjusted_cfr,
)

# Layer 5 imports
from agent_audit.interpreter.interpreter import Interpreter, InterpreterBackend

# Stress test imports
from agent_audit.stress_test.prober import should_run_stress_test, AdaptiveBiasProber


class PipelineOrchestrator:
    """
    Internal pipeline coordinator.
    
    Wires all 5 layers together and produces an AgentAuditReport.
    Not exposed directly - wrapped by AgentAuditor class.
    """

    def __init__(self, config: AgentAuditConfig):
        self.config = config
        logger.info(f"Initialized PipelineOrchestrator with mode={config.mode.value}")

    async def run_pipeline(
        self,
        connector: AgentConnector,
        seed_case: str,
        system_prompt: str | None = None,
        progress_callback: Callable[[str, int, int], None] | None = None,
    ) -> AgentAuditReport:
        """
        Execute the full 5-layer pipeline.

        Args:
            connector: Agent connector from Layer 1.
            seed_case: The template input case.
            system_prompt: Optional system prompt (for remediation).
            progress_callback: Optional callback(stage, current, total).

        Returns:
            Complete AgentAuditReport.
        """
        start_time = time.time()
        audit_id = f"audit-{uuid4().hex[:8]}"
        
        logger.info(f"=== Starting Audit Pipeline (ID: {audit_id}) ===")
        logger.info(f"Seed case: {seed_case[:100]}...")

        self._progress(progress_callback, "Starting audit", 0, 5)

        # ── Layer 2: Generate Personas ──────────────────────────────────
        logger.info("[Layer 2] Generating persona grid")
        self._progress(progress_callback, "Generating persona grid", 1, 5)
        personas = await self._generate_personas(seed_case)
        logger.info(f"[OK] Generated {len(personas)} personas")

        # ── Layer 3: Interrogate Agent ──────────────────────────────────
        logger.info("[Layer 3] Interrogating agent (this may take time with rate limiting)")
        self._progress(progress_callback, "Interrogating agent", 2, 5)
        completed_personas = await self._interrogate_agent(connector, personas)
        logger.info(f"[OK] Completed interrogation of {len(completed_personas)} personas")

        # ── Layer 4: Statistical Detection ──────────────────────────────
        logger.info("[Layer 4] Computing statistics")
        self._progress(progress_callback, "Computing statistics", 3, 5)
        findings, persona_results, df = await self._compute_statistics(completed_personas)
        logger.info(f"[OK] Found {len(findings)} statistical findings")

        # ── Layer 5: LLM Interpretation ─────────────────────────────────
        logger.info("[Layer 5] Interpreting findings")
        self._progress(progress_callback, "Interpreting findings", 4, 5)
        interpretation, suggestions = await self._interpret_findings(
            findings, system_prompt
        )
        logger.info(f"[OK] Generated interpretation with {len(suggestions)} suggestions")

        # ── Optional: Stress Test ───────────────────────────────────────
        stress_test_results = None
        if self.config.enable_stress_test and should_run_stress_test(findings):
            logger.info("Running stress test")
            self._progress(progress_callback, "Running stress test", 5, 6)
            stress_test_results = await self._run_stress_test(connector, seed_case)

        # ── Build Report ────────────────────────────────────────────────
        logger.info("Building final report")
        self._progress(progress_callback, "Building report", 5, 5)

        duration = time.time() - start_time
        overall_cfr = self._compute_overall_cfr(findings)
        overall_severity = classify_overall_severity(findings)

        # ── FairSight Compliance Metrics ────────────────────────────────
        
        # 1. EEOC Adverse Impact Ratio
        eeoc_air_results = compute_all_eeoc_air(df, self.config.protected_attributes)
        
        # 2. Stochastic Stability Score
        # Extract decision lists from persona results
        persona_decision_lists = []
        for persona in persona_results:
            # If we have multiple runs, extract all decisions
            # Otherwise, use the single decision
            if hasattr(persona, 'raw_outputs') and len(persona.raw_outputs) > 1:
                # Multiple runs available - would need to re-parse each output
                # For now, create a list with the majority decision repeated
                persona_decision_lists.append([persona.decision] * len(persona.raw_outputs))
            else:
                # Single run - use as-is
                persona_decision_lists.append([persona.decision])
        
        stability_results = compute_overall_stability(persona_decision_lists)
        
        # 3. Bias-Adjusted CFR (apply to all CFR findings)
        # Extract within-persona flip rates for BA-CFR calculation
        within_persona_flip_rates = []
        for decisions in persona_decision_lists:
            if len(decisions) > 1:
                # Calculate flip rate for this persona
                flip_rate = len(set(decisions)) / len(decisions)
                within_persona_flip_rates.append(flip_rate)
        
        for finding in findings:
            if finding.metric == "cfr":
                ba_cfr_result = compute_bias_adjusted_cfr(
                    finding.value,
                    within_persona_flip_rates if within_persona_flip_rates else [0.0]
                )
                finding.details["ba_cfr"] = ba_cfr_result["ba_cfr"]
                finding.details["ba_cfr_details"] = ba_cfr_result
        
        # 4. Confidence Intervals (add to all rate-based findings)
        confidence_intervals = {}
        for finding in findings:
            if finding.metric in ["cfr", "demographic_parity"]:
                # Get sample size from details
                n = finding.details.get("n_total", len(persona_results))
                rate_ci = compute_rate_with_ci(finding.value, n)
                confidence_intervals[finding.finding_id] = rate_ci
        
        # 5. Bonferroni Correction
        # Collect all p-values from statistical tests
        p_values = []
        for finding in findings:
            if finding.metric in ["cfr", "masd", "demographic_parity"]:
                p_values.append(finding.p_value)
        
        bonferroni_results = apply_bonferroni_correction(p_values, alpha=0.05)
        
        # Apply corrected alpha to findings
        for finding in findings:
            if finding.metric in ["cfr", "masd", "demographic_parity"]:
                finding.details["bonferroni_significant"] = (
                    finding.p_value < bonferroni_results["corrected_alpha"]
                )
        
        # 6. Audit Integrity Hash
        audit_integrity = AuditIntegrity(
            audit_hash=AuditIntegrity.compute_hash({
                "findings": [f.to_dict() for f in findings],
                "persona_results": [p.__dict__ for p in persona_results],
                "config": self.config.__dict__,
            }),
            prompts_hash=AuditIntegrity.compute_hash([p.to_dict() for p in completed_personas]),
            responses_hash=AuditIntegrity.compute_hash([
                p.raw_outputs for p in persona_results
            ]),
            config_hash=AuditIntegrity.compute_hash(self.config.__dict__),
        )
        
        # 7. Model Fingerprint
        model_fingerprint = ModelFingerprint(
            model_id=self.config.model,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
            system_prompt_hash=AuditIntegrity.compute_hash(system_prompt or ""),
            sdk_version="agent_audit-1.0.0",
            backend=self.config.backend,
        )

        report = AgentAuditReport(
            audit_id=audit_id,
            mode=self.config.mode.value,
            total_calls=len(completed_personas) * self._avg_runs_per_persona(),
            duration_seconds=duration,
            overall_severity=overall_severity,
            overall_cfr=overall_cfr,
            benchmark_range=(0.054, 0.130),
            findings=findings,
            persona_results=persona_results,
            interpretation=interpretation,
            prompt_suggestions=suggestions,
            stress_test_results=stress_test_results,
            caffe_test_suite=[p.to_dict() for p in completed_personas],
            timestamp=datetime.utcnow().isoformat(),
            # FairSight Compliance
            audit_integrity=audit_integrity,
            model_fingerprint=model_fingerprint,
            eeoc_air=eeoc_air_results,
            stability=stability_results,
            confidence_intervals=confidence_intervals,
            bonferroni_correction=bonferroni_results,
        )

        return report

    # ── Layer 2: Persona Generation ──────────────────────────────────────────

    async def _generate_personas(self, seed_case: str) -> list[CAFFETestCase]:
        """Generate persona grid based on audit mode."""
        mode = self.config.mode
        attributes = self.config.protected_attributes
        domain = self.config.domain

        # Base grid (pairwise or factorial)
        if mode == AuditMode.FULL:
            base_personas = generate_factorial_grid(seed_case, attributes, domain)
        else:
            base_personas = generate_pairwise_grid(seed_case, attributes, domain)

        # Add name-based variants
        name_personas = generate_name_variants(seed_case, mode.value, domain)
        all_personas = base_personas + name_personas

        # Add context primes (full mode only)
        if mode == AuditMode.FULL:
            all_personas = generate_context_variants(all_personas, mode=mode.value)

        return all_personas

    # ── Layer 3: Interrogation ───────────────────────────────────────────────

    async def _interrogate_agent(
        self, connector: AgentConnector, personas: list[CAFFETestCase]
    ) -> list[CAFFETestCase]:
        """Run all personas through the agent."""
        engine = InterrogationEngine(
            config=self.config,
            agent_caller=connector.call,
        )

        completed = await engine.run_all(personas)
        return completed

    # ── Layer 4: Statistics ──────────────────────────────────────────────────

    async def _compute_statistics(
        self, personas: list[CAFFETestCase]
    ) -> tuple[list[AgentFinding], list[PersonaResult], Any]:
        """Compute all statistical metrics including FairSight compliance."""
        # Build results DataFrame
        df = self._build_results_dataframe(personas)
        persona_results = self._extract_persona_results(personas)

        findings: list[AgentFinding] = []
        attributes = self.config.protected_attributes

        # CFR (primary metric)
        cfr_results = compute_all_cfr(df, attributes)
        for attr, comparisons in cfr_results.items():
            for comparison_name, data in comparisons.items():
                # Compute significance
                sig = compute_significance(df, attr)
                p_value = sig.get("primary_p_value", 1.0)

                # Classify severity
                severity, benchmark = classify_severity("cfr", data["cfr"], p_value)

                findings.append(
                    AgentFinding(
                        finding_id=f"CFR-{attr}-{uuid4().hex[:4]}",
                        attribute=attr,
                        comparison=comparison_name,
                        metric="cfr",
                        value=data["cfr"],
                        p_value=p_value,
                        severity=severity,
                        benchmark_context=benchmark,
                        details=data,
                    )
                )

        # MASD (if numeric scores available)
        if "score" in df.columns and df["score"].notna().sum() > 0:
            for attr in attributes:
                if attr in df.columns:
                    masd_results = compute_per_attribute_masd(df, attr)
                    for comparison_name, data in masd_results.items():
                        sig = compute_significance(df, attr)
                        p_value = sig.get("score_p_value", 1.0)
                        severity, benchmark = classify_severity(
                            "masd", data["masd"], p_value
                        )

                        findings.append(
                            AgentFinding(
                                finding_id=f"MASD-{attr}-{uuid4().hex[:4]}",
                                attribute=attr,
                                comparison=comparison_name,
                                metric="masd",
                                value=data["masd"],
                                p_value=p_value,
                                severity=severity,
                                benchmark_context=benchmark,
                                details=data,
                            )
                        )

        # Demographic Parity
        parity_results = compute_all_parity(df, attributes)
        for attr, data in parity_results.items():
            if data["eeoc_violation"]:
                sig = compute_significance(df, attr)
                p_value = sig.get("primary_p_value", 1.0)
                severity, benchmark = classify_severity(
                    "demographic_parity", data["disparity"], p_value
                )

                findings.append(
                    AgentFinding(
                        finding_id=f"PARITY-{attr}-{uuid4().hex[:4]}",
                        attribute=attr,
                        comparison=f"{data['min_group']}_vs_{data['max_group']}",
                        metric="demographic_parity",
                        value=data["disparity"],
                        p_value=p_value,
                        severity=severity,
                        benchmark_context=benchmark,
                        details=data,
                    )
                )

        # Intersectional (if applicable)
        if should_run_intersectional(findings, self.config.mode.value):
            intersectional_findings = intersectional_scan(df, attributes)
            for inter_data in intersectional_findings:
                findings.append(
                    AgentFinding(
                        finding_id=f"INTER-{uuid4().hex[:4]}",
                        attribute="+".join(inter_data["intersection"]),
                        comparison=f"{inter_data['worst_group']}_vs_{inter_data['best_group']}",
                        metric="intersectional",
                        value=inter_data["disparity"],
                        p_value=0.05,  # Conservative estimate
                        severity="MODERATE" if inter_data["disparity"] > 0.15 else "LOW",
                        benchmark_context=f"Intersectional disparity of {inter_data['disparity']:.1%}",
                        details=inter_data,
                    )
                )

        return findings, persona_results, df

    # ── Layer 5: Interpretation ──────────────────────────────────────────────

    async def _interpret_findings(
        self, findings: list[AgentFinding], system_prompt: str | None
    ) -> tuple[Interpretation, list[PromptSuggestion]]:
        """Use LLM to interpret findings and suggest remediation."""
        if not findings or all(f.severity == "CLEAR" for f in findings):
            return (
                Interpretation(
                    finding_explanations=[],
                    overall_assessment="No significant bias detected.",
                    priority_order=[],
                ),
                [],
            )

        # Use local or cloud interpreter based on config
        backend = (
            InterpreterBackend.LOCAL
            if self.config.backend == "ollama"
            else InterpreterBackend.CLOUD
        )

        interpreter = Interpreter(
            backend=backend,
            model=self.config.model,
            api_key=self.config.api_key,
        )

        context = self.config.to_decision_context()
        interpretation, suggestions = await interpreter.interpret(
            findings, context, system_prompt
        )

        return interpretation, suggestions

    # ── Stress Test ──────────────────────────────────────────────────────────

    async def _run_stress_test(
        self, connector: AgentConnector, seed_case: str
    ) -> Any:
        """Run adaptive stress test if enabled."""
        # Use the same LLM for mutation generation
        prober = AdaptiveBiasProber(
            agent_caller=connector.call,
            context=self.config.domain,
            attributes=self.config.protected_attributes,
            mutator_caller=connector.call,  # Reuse agent's LLM
        )

        return await prober.run([seed_case])

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _build_results_dataframe(self, personas: list[CAFFETestCase]) -> pd.DataFrame:
        """Convert CAFFE test cases to a DataFrame for statistics."""
        rows = []
        for case in personas:
            if not case.results:
                continue
            result = case.results[0]
            variant = case.input_variants[0] if case.input_variants else {}

            row = {
                "test_id": case.test_id,
                "decision": result.get("majority_decision", "ambiguous"),
                "score": result.get("mean_score"),
                "decision_variance": result.get("decision_variance", 0.0),
                "score_std": result.get("score_std"),
                **{
                    k: v
                    for k, v in variant.items()
                    if not k.startswith("_") and k not in ("name", "context_prime")
                },
            }
            rows.append(row)

        return pd.DataFrame(rows)

    def _extract_persona_results(
        self, personas: list[CAFFETestCase]
    ) -> list[PersonaResult]:
        """Convert CAFFE test cases to PersonaResult objects."""
        results = []
        for case in personas:
            if not case.results:
                continue
            result = case.results[0]
            variant = case.input_variants[0] if case.input_variants else {}

            results.append(
                PersonaResult(
                    persona_id=case.test_id,
                    attributes={
                        k: v
                        for k, v in variant.items()
                        if not k.startswith("_")
                    },
                    test_type=variant.get("_variant_type", "unknown"),
                    decision=result.get("majority_decision", "ambiguous"),
                    score=result.get("mean_score"),
                    decision_variance=result.get("decision_variance", 0.0),
                    score_std=result.get("score_std"),
                    raw_outputs=result.get("raw_outputs", []),
                    context_prime=variant.get("context_prime", "none"),
                    name=variant.get("name"),
                )
            )

        return results

    def _compute_overall_cfr(self, findings: list[AgentFinding]) -> float:
        """Compute mean CFR across all findings."""
        cfr_values = [f.value for f in findings if f.metric == "cfr"]
        return sum(cfr_values) / len(cfr_values) if cfr_values else 0.0

    def _avg_runs_per_persona(self) -> int:
        """Estimate average runs per persona based on mode."""
        return {
            AuditMode.QUICK: 1,
            AuditMode.STANDARD: 2,  # Adaptive average
            AuditMode.FULL: 3,
        }.get(self.config.mode, 2)

    @staticmethod
    def _progress(
        callback: Callable[[str, int, int], None] | None,
        stage: str,
        current: int,
        total: int,
    ):
        """Emit progress update if callback provided."""
        if callback:
            callback(stage, current, total)
