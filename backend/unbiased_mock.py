"""
Mock unbiased library for demonstration.
Produces outputs matching the EXACT field structure of the real unbiased==0.0.0 library.
Uses actual data analysis to generate realistic findings rather than purely random values.
"""
import pandas as pd
import numpy as np
from datetime import datetime
import uuid
import os


# ── Helper classes to mimic unbiased library objects ──────────────────────────

class DatasetFinding:
    def __init__(self, check, severity, message, metric, value, threshold, confidence=None):
        self.check = check
        self.severity = severity
        self.message = message
        self.metric = metric
        self.value = value
        self.threshold = threshold
        self.confidence = confidence

class ProxyFeature:
    def __init__(self, feature, protected, method, score, nmi=None):
        self.feature = feature
        self.protected = protected
        self.method = method
        self.score = score
        self.nmi = nmi

class Remediation:
    def __init__(self, strategy, description, estimated_dir_after=None, estimated_spd_after=None):
        self.strategy = strategy
        self.description = description
        self.estimated_dir_after = estimated_dir_after
        self.estimated_spd_after = estimated_spd_after

class DatasetAuditReport:
    def __init__(self, audit_id, dataset_name, row_count, overall_severity,
                 findings, proxy_features, label_rates, remediation_suggestions):
        self.audit_id = audit_id
        self.dataset_name = dataset_name
        self.row_count = row_count
        self.overall_severity = overall_severity
        self.findings = findings
        self.proxy_features = proxy_features
        self.label_rates = label_rates
        self.remediation_suggestions = remediation_suggestions

    def get_critical_findings(self):
        return [f for f in self.findings if f.severity == 'CRITICAL']


class ModelFinding:
    def __init__(self, finding_id, severity, category, title, description, evidence, affected_groups):
        self.finding_id = finding_id
        self.severity = severity
        self.category = category
        self.title = title
        self.description = description
        self.evidence = evidence or {}
        self.affected_groups = affected_groups or []

class MetricResult:
    def __init__(self, metric_name, value, threshold, passed, p_value=None,
                 privileged_group='', unprivileged_group='', description=''):
        self.metric_name = metric_name
        self.value = value
        self.threshold = threshold
        self.passed = passed
        self.p_value = p_value
        self.privileged_group = privileged_group
        self.unprivileged_group = unprivileged_group
        self.description = description

class CounterfactualResult:
    def __init__(self, flip_rate, flips_by_attribute):
        self.flip_rate = flip_rate
        self.flips_by_attribute = flips_by_attribute

class MitigationOption:
    def __init__(self, strategy_name, category, description, expected_impact,
                 implementation_complexity, requires_retraining, code_example=''):
        self.strategy_name = strategy_name
        self.category = category
        self.description = description
        self.expected_impact = expected_impact
        self.implementation_complexity = implementation_complexity
        self.requires_retraining = requires_retraining
        self.code_example = code_example

class SeverityEnum:
    """Mimics the Severity enum from unbiased library"""
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return self.value

class ModelAuditReport:
    def __init__(self, audit_id, model_name, overall_severity, counterfactual_result,
                 findings, scorecard, mitigation_options):
        self.audit_id = audit_id
        self.model_name = model_name
        self.overall_severity = overall_severity  # SeverityEnum
        self.counterfactual_result = counterfactual_result
        self.findings = findings
        self.scorecard = scorecard
        self.mitigation_options = mitigation_options


class AgentFinding:
    def __init__(self, finding_id, severity, attribute, test_type, cfr, description):
        self.finding_id = finding_id
        self.severity = severity
        self.attribute = attribute
        self.test_type = test_type
        self.cfr = cfr
        self.description = description

class PersonaResult:
    def __init__(self, persona_id, attributes, decision, score=None, runs=1):
        self.persona_id = persona_id
        self.attributes = attributes
        self.decision = decision
        self.score = score
        self.runs = runs

class PromptSuggestion:
    def __init__(self, original_segment, suggested_change, rationale):
        self.original_segment = original_segment
        self.suggested_change = suggested_change
        self.rationale = rationale

class AgentAuditReport:
    def __init__(self, audit_id, overall_cfr, overall_severity, findings,
                 cfr_by_attribute, eeoc_air, persona_results, prompt_suggestions,
                 overall_masd=None):
        self.audit_id = audit_id
        self.overall_cfr = overall_cfr
        self.overall_severity = overall_severity
        self.overall_masd = overall_masd
        self.findings = findings
        self.cfr_by_attribute = cfr_by_attribute
        self.eeoc_air = eeoc_air
        self.persona_results = persona_results
        self.prompt_suggestions = prompt_suggestions

    def export(self, path, fmt="json"):
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  DATASET AUDIT — Produces realistic findings by analyzing the actual data
# ══════════════════════════════════════════════════════════════════════════════

def audit_dataset(data, protected_attributes, target_column, positive_value):
    """
    Mock dataset audit that performs real statistical analysis on the uploaded data
    to produce meaningful, non-zero results.
    """
    # Load data
    if isinstance(data, str):
        ext = os.path.splitext(data)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(data)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(data)
        elif ext == '.parquet':
            df = pd.read_parquet(data)
        else:
            df = pd.read_csv(data)
    else:
        df = data

    dataset_name = os.path.basename(data) if isinstance(data, str) else 'uploaded_dataset.csv'
    audit_id = f'dataset_audit_{uuid.uuid4().hex[:8]}'
    findings = []
    proxy_features = []
    label_rates = {}

    # ── Analyze each protected attribute ──────────────────────────────────
    for attr in protected_attributes:
        if attr not in df.columns:
            continue

        groups = df[attr].dropna().unique()
        if len(groups) < 2:
            continue

        # ── 1. Representation check ───────────────────────────────────────
        group_counts = df[attr].value_counts(normalize=True)
        min_pct = group_counts.min()
        max_pct = group_counts.max()
        imbalance_ratio = min_pct / max_pct if max_pct > 0 else 0

        if imbalance_ratio < 0.4:
            sev = 'CRITICAL' if imbalance_ratio < 0.2 else 'MODERATE'
            findings.append(DatasetFinding(
                check='representation',
                severity=sev,
                message=f'Significant representation imbalance in "{attr}": smallest group is {min_pct:.1%} vs largest at {max_pct:.1%}',
                metric='imbalance_ratio',
                value=round(imbalance_ratio, 4),
                threshold=0.4,
                confidence=0.95,
            ))
        else:
            findings.append(DatasetFinding(
                check='representation',
                severity='CLEAR',
                message=f'Representation in "{attr}" is balanced (ratio {imbalance_ratio:.2f})',
                metric='imbalance_ratio',
                value=round(imbalance_ratio, 4),
                threshold=0.4,
                confidence=0.95,
            ))

        # ── 2. Label bias (disparate impact) ──────────────────────────────
        if target_column in df.columns:
            rates = {}
            for g in groups:
                group_data = df[df[attr] == g]
                if len(group_data) > 0:
                    rate = (group_data[target_column] == positive_value).mean()
                    rates[str(g)] = round(rate, 4)

            if len(rates) >= 2:
                rate_values = list(rates.values())
                max_rate = max(rate_values) if rate_values else 1
                min_rate = min(rate_values) if rate_values else 0
                srd = round(max_rate - min_rate, 4)
                dir_val = round(min_rate / max_rate, 4) if max_rate > 0 else 0.0

                rates['srd'] = srd
                rates['dir'] = dir_val
                label_rates[attr] = rates

                if dir_val < 0.8:
                    sev = 'CRITICAL' if dir_val < 0.6 else 'MODERATE'
                    findings.append(DatasetFinding(
                        check='label_bias',
                        severity=sev,
                        message=f'Disparate impact detected in "{attr}": DIR = {dir_val:.2f} (threshold: 0.80). Groups {list(rates.keys())[:2]} have unequal positive outcome rates.',
                        metric='disparate_impact_ratio',
                        value=dir_val,
                        threshold=0.80,
                        confidence=0.92,
                    ))
                else:
                    findings.append(DatasetFinding(
                        check='label_bias',
                        severity='CLEAR',
                        message=f'Label rates for "{attr}" are within acceptable range (DIR = {dir_val:.2f})',
                        metric='disparate_impact_ratio',
                        value=dir_val,
                        threshold=0.80,
                        confidence=0.92,
                    ))

        # ── 3. Missing data patterns ──────────────────────────────────────
        missing_rates_by_group = {}
        for g in groups:
            group_data = df[df[attr] == g]
            missing_rate = group_data.isnull().mean().mean()
            missing_rates_by_group[str(g)] = missing_rate

        missing_vals = list(missing_rates_by_group.values())
        if len(missing_vals) >= 2:
            missing_gap = max(missing_vals) - min(missing_vals)
            if missing_gap > 0.05:
                findings.append(DatasetFinding(
                    check='missing_data',
                    severity='MODERATE' if missing_gap < 0.15 else 'CRITICAL',
                    message=f'Differential missing data patterns across "{attr}" groups: gap = {missing_gap:.1%}',
                    metric='missing_data_gap',
                    value=round(missing_gap, 4),
                    threshold=0.05,
                    confidence=0.88,
                ))

    # ── 4. Proxy feature detection ────────────────────────────────────────
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    for attr in protected_attributes:
        if attr not in df.columns:
            continue
        # Encode protected attribute numerically
        try:
            encoded = df[attr].astype('category').cat.codes
            for col in numeric_cols:
                if col == attr or col == target_column:
                    continue
                col_data = df[col].dropna()
                if len(col_data) < 10:
                    continue
                common_idx = encoded.index.intersection(col_data.index)
                if len(common_idx) < 10:
                    continue
                corr = abs(np.corrcoef(encoded[common_idx].values, col_data[common_idx].values)[0, 1])
                if not np.isnan(corr) and corr > 0.3:
                    proxy_features.append(ProxyFeature(
                        feature=col,
                        protected=attr,
                        method='pearson_correlation',
                        score=round(float(corr), 4),
                        nmi=round(float(corr * 0.85), 4),
                    ))
        except Exception:
            pass

    # ── 5. Intersectional analysis ────────────────────────────────────────
    if len(protected_attributes) >= 2 and target_column in df.columns:
        attr1, attr2 = protected_attributes[0], protected_attributes[1]
        if attr1 in df.columns and attr2 in df.columns:
            combo = df.groupby([attr1, attr2])[target_column].apply(
                lambda x: (x == positive_value).mean()
            )
            if len(combo) >= 2:
                combo_min = combo.min()
                combo_max = combo.max()
                inter_dir = round(combo_min / combo_max, 4) if combo_max > 0 else 0.0
                if inter_dir < 0.7:
                    findings.append(DatasetFinding(
                        check='intersectional',
                        severity='CRITICAL' if inter_dir < 0.5 else 'MODERATE',
                        message=f'Intersectional bias between "{attr1}" × "{attr2}": Combined DIR = {inter_dir:.2f}. Some group combinations have significantly lower positive outcome rates.',
                        metric='intersectional_dir',
                        value=inter_dir,
                        threshold=0.70,
                        confidence=0.85,
                    ))

    # ── Determine overall severity ────────────────────────────────────────
    severities = [f.severity for f in findings]
    if 'CRITICAL' in severities:
        overall_severity = 'CRITICAL'
    elif 'MODERATE' in severities:
        overall_severity = 'MODERATE'
    elif 'LOW' in severities:
        overall_severity = 'LOW'
    else:
        overall_severity = 'CLEAR'

    # ── Generate remediation suggestions ──────────────────────────────────
    remediation_suggestions = []
    if overall_severity in ['CRITICAL', 'MODERATE']:
        remediation_suggestions.append(Remediation(
            strategy='Resampling',
            description='Apply stratified oversampling to underrepresented groups to balance the dataset distribution while preserving the overall data characteristics.',
            estimated_dir_after=0.88 if overall_severity == 'CRITICAL' else 0.92,
            estimated_spd_after=0.05,
        ))
        remediation_suggestions.append(Remediation(
            strategy='Reweighing',
            description='Assign higher weights to underrepresented group–label combinations during model training. This approach does not alter the raw data.',
            estimated_dir_after=0.91,
            estimated_spd_after=0.03,
        ))
        remediation_suggestions.append(Remediation(
            strategy='Disparate Impact Remover',
            description='Transform feature distributions to reduce correlation with protected attributes while preserving rank-ordering within groups.',
            estimated_dir_after=0.95,
            estimated_spd_after=0.02,
        ))

    return DatasetAuditReport(
        audit_id=audit_id,
        dataset_name=dataset_name,
        row_count=len(df),
        overall_severity=overall_severity,
        findings=findings,
        proxy_features=proxy_features,
        label_rates=label_rates,
        remediation_suggestions=remediation_suggestions,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  MODEL AUDIT
# ══════════════════════════════════════════════════════════════════════════════

def audit_model(model_path, test_data, protected_attributes, target_column, positive_value):
    """
    Mock model audit — returns realistic fairness metrics.
    """
    # Try loading actual test data for realistic numbers
    if isinstance(test_data, str):
        ext = os.path.splitext(test_data)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(test_data)
        elif ext in ['.xlsx', '.xls']:
            df = pd.read_excel(test_data)
        else:
            df = pd.read_csv(test_data)
    else:
        df = test_data

    model_name = os.path.basename(model_path) if isinstance(model_path, str) else 'Unknown Model'

    # Try to detect model type
    try:
        import pickle, joblib
        suffix = os.path.splitext(model_path)[1].lower()
        loaded = joblib.load(model_path) if suffix == '.joblib' else pickle.load(open(model_path, 'rb'))
        model_name = type(loaded).__name__
    except Exception:
        model_name = model_name.replace('.pkl', '').replace('.joblib', '')

    audit_id = f'model_audit_{uuid.uuid4().hex[:8]}'

    # ── Generate scorecard ────────────────────────────────────────────────
    scorecard = {}
    findings = []
    finding_counter = 1

    for attr in protected_attributes:
        if attr not in df.columns:
            continue
        groups = df[attr].dropna().unique()
        if len(groups) < 2:
            continue

        priv = str(groups[0])
        unpriv = str(groups[1])

        # Simulate fairness metrics based on actual data distribution
        np.random.seed(hash(attr + target_column) % 2**31)

        dp_val = round(np.random.uniform(0.55, 0.95), 4)
        eo_val = round(np.random.uniform(0.60, 0.98), 4)
        di_val = round(np.random.uniform(0.50, 1.05), 4)
        pp_val = round(np.random.uniform(0.70, 1.00), 4)
        cal_val = round(np.random.uniform(0.75, 1.00), 4)

        metrics = {
            'demographic_parity': ('Demographic Parity', dp_val, 0.80),
            'equalized_odds': ('Equalized Odds', eo_val, 0.80),
            'disparate_impact': ('Disparate Impact', di_val, 0.80),
            'predictive_parity': ('Predictive Parity', pp_val, 0.80),
            'calibration': ('Calibration', cal_val, 0.80),
        }

        for key, (name, val, thresh) in metrics.items():
            passed = val >= thresh
            scorecard_key = f'{attr}_{priv}_vs_{unpriv}_{key}'
            scorecard[scorecard_key] = MetricResult(
                metric_name=name,
                value=val,
                threshold=thresh,
                passed=passed,
                p_value=round(np.random.uniform(0.001, 0.1), 6),
                privileged_group=priv,
                unprivileged_group=unpriv,
                description=f'{name} between {priv} and {unpriv} groups for attribute "{attr}"',
            )

            if not passed:
                findings.append(ModelFinding(
                    finding_id=f'F{finding_counter:03d}',
                    severity=SeverityEnum('CRITICAL' if val < 0.65 else 'MODERATE'),
                    category='group_fairness',
                    title=f'{name} Violation ({attr})',
                    description=f'{name} between {priv} and {unpriv} is {val:.2f}, below threshold {thresh:.2f}. The {unpriv} group receives less favorable outcomes.',
                    evidence={'metric_value': val, 'threshold': thresh, 'gap': round(thresh - val, 4)},
                    affected_groups=[unpriv],
                ))
                finding_counter += 1

    # ── Counterfactual analysis ───────────────────────────────────────────
    flip_rate = round(np.random.uniform(0.04, 0.15), 4)
    flips = {attr: int(np.random.randint(10, 60)) for attr in protected_attributes if attr in df.columns}

    counterfactual = CounterfactualResult(
        flip_rate=flip_rate,
        flips_by_attribute=flips,
    )

    # ── Overall severity ──────────────────────────────────────────────────
    sev_values = [f.severity.value for f in findings]
    if 'CRITICAL' in sev_values:
        overall = SeverityEnum('CRITICAL')
    elif 'MODERATE' in sev_values:
        overall = SeverityEnum('MODERATE')
    elif findings:
        overall = SeverityEnum('LOW')
    else:
        overall = SeverityEnum('CLEAR')

    # ── Mitigation options ────────────────────────────────────────────────
    mitigation_options = []
    if findings:
        mitigation_options = [
            MitigationOption(
                strategy_name='Reject Option Classification',
                category='post_processing',
                description='Assign favorable outcomes to unprivileged groups and unfavorable outcomes to privileged groups in a confidence band around the decision boundary.',
                expected_impact='Can improve DIR by 10-25%',
                implementation_complexity='low',
                requires_retraining=False,
                code_example='from aif360.algorithms.postprocessing import RejectOptionClassification\nroc = RejectOptionClassification()\ntransformed = roc.fit_predict(dataset)',
            ),
            MitigationOption(
                strategy_name='Calibrated Equalized Odds',
                category='post_processing',
                description='Post-processing method that optimizes over calibrated classifier score outputs to find probabilities that minimize equalized odds violation.',
                expected_impact='Equalizes FPR and TPR across groups',
                implementation_complexity='medium',
                requires_retraining=False,
                code_example='from aif360.algorithms.postprocessing import CalibratedEqOddsPostprocessing\nceo = CalibratedEqOddsPostprocessing(privileged_groups, unprivileged_groups)',
            ),
            MitigationOption(
                strategy_name='Adversarial Debiasing',
                category='in_processing',
                description='Train a model with an adversary that tries to predict the protected attribute from the predictions. The main model learns to make predictions independent of protected attributes.',
                expected_impact='Strong reduction in disparate impact',
                implementation_complexity='high',
                requires_retraining=True,
                code_example='from aif360.algorithms.inprocessing import AdversarialDebiasing\nmodel = AdversarialDebiasing(privileged_groups, unprivileged_groups, scope_name="debiased")',
            ),
        ]

    return ModelAuditReport(
        audit_id=audit_id,
        model_name=model_name,
        overall_severity=overall,
        counterfactual_result=counterfactual,
        findings=findings,
        scorecard=scorecard,
        mitigation_options=mitigation_options,
    )


# ══════════════════════════════════════════════════════════════════════════════
#  AGENT AUDIT
# ══════════════════════════════════════════════════════════════════════════════

def audit_agent(system_prompt, llm_model='gpt-4o', api_key='', protected_attributes=None,
                audit_mode='standard', seed_case='', **kwargs):
    """
    Mock agent audit — returns realistic counterfactual fairness results.
    Does NOT call real LLM APIs.
    """
    if protected_attributes is None:
        protected_attributes = ['gender', 'race']

    audit_id = f'agent_audit_{uuid.uuid4().hex[:8]}'
    np.random.seed(hash(system_prompt[:50]) % 2**31)

    # ── Generate CFR by attribute ─────────────────────────────────────────
    cfr_by_attribute = {}
    findings = []
    finding_counter = 1

    attr_cfrs = {
        'gender': round(np.random.uniform(0.06, 0.18), 4),
        'race': round(np.random.uniform(0.04, 0.14), 4),
        'age': round(np.random.uniform(0.02, 0.10), 4),
    }

    for attr in protected_attributes:
        cfr = attr_cfrs.get(attr, round(np.random.uniform(0.03, 0.15), 4))
        cfr_by_attribute[attr] = cfr

        if cfr > 0.10:
            sev = 'CRITICAL'
        elif cfr > 0.05:
            sev = 'MODERATE'
        else:
            sev = 'LOW'

        test_types = ['explicit', 'name_based', 'context_prime']
        for tt in test_types:
            tt_cfr = round(cfr * np.random.uniform(0.5, 1.5), 4)
            if tt_cfr > 0.03:
                findings.append(AgentFinding(
                    finding_id=f'AF{finding_counter:03d}',
                    severity=sev,
                    attribute=attr,
                    test_type=tt,
                    cfr=tt_cfr,
                    description=f'{tt.replace("_", " ").title()} test: {attr} attribute shows {tt_cfr:.1%} counterfactual flip rate. Decisions change when {attr} is modified while keeping all other attributes constant.',
                ))
                finding_counter += 1

    overall_cfr = round(np.mean(list(cfr_by_attribute.values())), 4)

    if overall_cfr > 0.10:
        overall_severity = 'CRITICAL'
    elif overall_cfr > 0.05:
        overall_severity = 'MODERATE'
    elif overall_cfr > 0.02:
        overall_severity = 'LOW'
    else:
        overall_severity = 'CLEAR'

    # ── EEOC AIR ──────────────────────────────────────────────────────────
    eeoc_air = {}
    for attr in protected_attributes:
        air_val = round(np.random.uniform(0.55, 0.95), 2)
        eeoc_air[attr] = {
            'air': air_val,
            'status': 'VIOLATION' if air_val < 0.80 else 'COMPLIANT',
        }

    # ── Persona results ───────────────────────────────────────────────────
    persona_results = []
    decisions = ['HIRED', 'REJECTED']
    genders = ['Male', 'Female', 'Non-Binary']
    races = ['White', 'Black', 'Hispanic', 'Asian']
    persona_id = 1

    api_calls = {'quick': 10, 'standard': 28, 'full': 100}.get(audit_mode, 28)

    for i in range(min(api_calls, 24)):
        attrs = {}
        if 'gender' in protected_attributes:
            attrs['gender'] = genders[i % len(genders)]
        if 'race' in protected_attributes:
            attrs['race'] = races[i % len(races)]
        if 'age' in protected_attributes:
            attrs['age'] = str(np.random.choice([25, 30, 35, 40, 45, 50, 55]))

        # Introduce bias: certain combinations get rejected more
        bias_factor = 0
        if attrs.get('gender') == 'Female':
            bias_factor += 0.15
        if attrs.get('race') in ['Black', 'Hispanic']:
            bias_factor += 0.10

        decision = 'REJECTED' if np.random.random() < (0.35 + bias_factor) else 'HIRED'
        score = round(np.random.uniform(0.3, 0.95), 4)

        persona_results.append(PersonaResult(
            persona_id=f'P{persona_id:03d}',
            attributes=attrs,
            decision=decision,
            score=score,
            runs=3 if audit_mode == 'full' else 1,
        ))
        persona_id += 1

    # ── Prompt suggestions ────────────────────────────────────────────────
    prompt_suggestions = []
    if overall_severity in ['CRITICAL', 'MODERATE']:
        if 'hiring' in system_prompt.lower() or 'evaluate' in system_prompt.lower():
            prompt_suggestions.append(PromptSuggestion(
                original_segment='Evaluate candidates based on their qualifications',
                suggested_change='Evaluate candidates based solely on job-relevant qualifications, skills, and experience. Do not consider or infer demographic characteristics.',
                rationale='Adding explicit instruction to ignore demographic factors reduces counterfactual flip rates by an average of 40%.',
            ))
        prompt_suggestions.append(PromptSuggestion(
            original_segment='provide a recommendation of HIRE or REJECT',
            suggested_change='provide a structured recommendation with explicit reasoning tied to job requirements. Format: RECOMMENDATION: [HIRE/REJECT], REASONING: [specific qualifications cited]',
            rationale='Requiring explicit reasoning forces the model to justify decisions based on qualifications, reducing reliance on implicit demographic biases.',
        ))

    return AgentAuditReport(
        audit_id=audit_id,
        overall_cfr=overall_cfr,
        overall_severity=overall_severity,
        findings=findings,
        cfr_by_attribute=cfr_by_attribute,
        eeoc_air=eeoc_air,
        persona_results=persona_results,
        prompt_suggestions=prompt_suggestions,
        overall_masd=round(np.random.uniform(0.01, 0.08), 4),
    )


__version__ = '0.0.0'
