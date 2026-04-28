# NoBias

Comprehensive AI fairness testing across datasets, models, and LLM agents. Detect bias before it reaches production.

## What This Does

NoBias provides three auditing systems that cover the entire AI lifecycle:

1. **Dataset Auditor** - Scan training data for statistical biases (2-10 seconds, $0)
2. **Model Auditor** - Test trained models for fairness violations (15-60 seconds, $0)
3. **Agent Auditor** - Audit LLM-based agents for demographic bias (2-30 minutes, $0.03-$0.27)

All processing runs locally. Your data never leaves your machine unless you explicitly enable cloud LLM calls for Agent Auditor interpretation.

## Installation

```bash
pip install nobias
```

For full functionality including Agent Auditor:
```bash
pip install nobias[all]
```

## Quick Start

### Dataset Auditor

Analyzes raw training data before model development. Catches representation imbalances, label disparities, proxy features, and intersectional bias.

```python
from nobias import audit_dataset

report = audit_dataset(
    data='hiring_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Severity: {report.overall_severity}")
print(f"EEOC Compliant: {report.eeoc_compliant}")

# Check specific findings
for finding in report.findings:
    if finding.severity == 'CRITICAL':
        print(f"⚠️ {finding.title}")
        print(f"   {finding.description}")
```

What it detects:
- Representation bias (underrepresented groups)
- Label bias (outcome disparities across demographics)
- Proxy features (ZIP code, names encoding protected attributes)
- Missing data patterns (systematic missingness by group)
- Intersectional disparities (compounded underrepresentation)
- Distribution shifts (KL divergence across groups)

### Model Auditor

Tests trained ML models using counterfactual testing. Creates identical inputs differing only in demographics to see if predictions change.

```python
from nobias.model_audit import audit_model

report = audit_model(
    model='trained_model.pkl',
    test_data='test.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Flip Rate: {report.counterfactual_result.flip_rate:.2%}")
print(f"Disparate Impact Ratio: {report.scorecard['disparate_impact_gender'].value:.2f}")

# Check EEOC compliance
if report.scorecard['disparate_impact_gender'].value < 0.80:
    print("⚠️ EEOC VIOLATION: Disparate impact below 80% threshold")
```

What it computes:
- Counterfactual flip rate (individual fairness)
- Demographic parity (equal approval rates)
- Disparate impact ratio (EEOC 80% rule)
- Equalized odds (equal TPR/FPR across groups)
- Predictive parity (equal precision)
- Calibration (predicted probabilities match outcomes)

### Agent Auditor

Tests LLM-based AI agents through persona-based counterfactual testing. Detects bias in hiring assistants, loan evaluators, content moderators, etc.

```python
from nobias.agent_audit import audit_agent

report = await audit_agent(
    system_prompt="You are a hiring assistant. Evaluate candidates objectively.",
    seed_case="Evaluate: Name: Jordan, Age: 29, Experience: 5 years, Skills: Python, ML",
    api_key="gsk_...",  # Groq API key
    mode="standard"  # quick | standard | full
)

print(f"CFR: {report.overall_cfr:.1%}")
print(f"EEOC Compliant: {report.eeoc_compliant}")
print(f"Severity: {report.overall_severity}")

# Get remediation suggestions
print(report.remediation_summary)
```

What it detects:
- Explicit demographic bias (agent sees "gender: Female" and changes decision)
- Implicit proxy bias (agent infers race from names like "Lakisha" vs "Emily")
- Contextual priming (historical context activates stereotypes)
- Reasoning inconsistencies (same decision, different justifications)

## Three Connection Modes for Agent Auditor

### Mode 1: System Prompt (Development)

Test agents during development by providing the system prompt directly.

```python
from nobias.agent_audit import AgentAuditor

auditor = AgentAuditor.from_prompt(
    system_prompt="You are a loan approval assistant...",
    api_key="gsk_...",
    model="llama-3.1-70b-versatile"
)

report = await auditor.run(
    seed_case="Evaluate: Income $55k, Credit 720, Employment 5yr"
)
```

### Mode 2: API Endpoint (Production)

Test deployed production agents via their API.

```python
auditor = AgentAuditor.from_api(
    endpoint_url="https://api.yourcompany.com/agent/evaluate",
    auth_header={"Authorization": "Bearer TOKEN"},
    request_template={"input": "{input}", "mode": "evaluation"},
    response_path="$.result.decision"
)

report = await auditor.run(seed_case="...")
```

### Mode 3: Log Replay (Historical Analysis)

Audit past behavior from interaction logs. Zero API calls, complete privacy.

```python
auditor = AgentAuditor.from_logs(
    log_file="interactions.jsonl",
    input_field="input",
    output_field="output"
)

report = await auditor.run()
```

## Audit Tiers

Agent Auditor offers three tiers balancing cost and coverage:

| Tier | Test Cases | Duration | Cost (Groq) | Cost (Anthropic) | Use Case |
|------|-----------|----------|-------------|------------------|----------|
| Quick | 14 personas | 2 min | $0.03 | $0.11 | Development testing |
| Standard | 80 personas | 5 min | $0.05 | $0.17 | Production validation |
| Full | 430 personas | 30 min | $0.07 | $0.27 | Legal compliance |

```python
# Quick scan for development
report = await audit_agent(..., mode="quick")

# Standard audit for production (default)
report = await audit_agent(..., mode="standard")

# Full investigation for legal compliance
report = await audit_agent(..., mode="full")
```

## Cost Optimization

Agent Auditor includes 82% token reduction through four optimizations:

1. **Compressed JSON Output** - Structured responses instead of verbose text (85% reduction)
2. **Prompt Caching** - Reuse system prompts across calls (65% reduction after first call)
3. **Two-Pass Evaluation** - Only re-test ambiguous cases (50% fewer API calls)
4. **Smart Sampling** - Prioritize high-signal test cases

Before optimization: 240,000 tokens, $1.87 per audit
After optimization: 43,400 tokens, $0.28 per audit

## Local LLM Support

For complete privacy, use local LLMs via Ollama (zero cost, zero external calls):

```python
from nobias.agent_audit import audit_agent

report = await audit_agent(
    system_prompt="...",
    seed_case="...",
    backend="ollama",
    model="llama3.1:8b",
    mode="standard"
)
```

Requires Ollama installed locally. No data leaves your machine.

## Understanding the Metrics

### CFR (Counterfactual Flip Rate)
How often decisions flip when only demographics change. Research benchmarks (Mayilvaghanan et al. 2025):
- 0-5%: Negligible bias
- 5-10%: Below best-in-class, monitor
- 10-15%: Moderate, remediation recommended
- 15%+: Critical, immediate action required

### MASD (Mean Absolute Score Difference)
Score shifts when only demographics change. Catches sub-threshold bias where decisions don't flip but scores systematically differ.
- 0.00-0.03: Perfect consistency
- 0.03-0.08: Detectable but minor
- 0.08-0.15: Meaningful difference
- 0.15+: Large systematic shifts

### EEOC AIR (Adverse Impact Ratio)
Legal compliance with EEOC 80% rule. Formula: (lowest group approval rate) / (highest group approval rate)
- < 0.80: Legal violation (prima facie discrimination)
- 0.80-0.85: Borderline, review recommended
- > 0.85: Compliant

### Disparate Impact Ratio (DIR)
Same as EEOC AIR but for model/dataset audits. Measures approval rate ratios across demographic groups.

## Actionable Insights

All audits generate plain-English summaries and prioritized remediation steps:

```python
# Get actionable insights
insights = report.actionable_insights

print(insights['plain_english']['one_liner'])
print(insights['plain_english']['biggest_problem'])
print(insights['plain_english']['quickest_fix'])

# Prioritized actions
for action in insights['action_priority']:
    print(f"{action['rank']}. {action['action']}")
    print(f"   Effort: {action['effort']} | Impact: {action['impact']}")
    print(f"   {action['reason']}")
```

## Export Formats

```python
# JSON (machine-readable)
report.export('audit_report.json', format='json')

# PDF (human-readable)
report.export('audit_report.pdf', format='pdf')

# Text summary
report.export('audit_report.txt', format='text')

# CAFFE test suite (reproducible)
report.export('test_suite.json', format='caffe')
```

## Advanced Usage

### Compare Before/After

```python
from nobias.agent_audit import AgentAuditor

auditor = AgentAuditor.from_prompt(
    system_prompt="Original prompt...",
    api_key="..."
)

# Run initial audit
report_before = await auditor.run(seed_case="...")

# Update prompt with suggested fix
auditor.update_prompt("Improved prompt with fairness instructions...")

# Re-run audit
report_after = await auditor.run(seed_case="...")

# Compare
comparison = auditor.compare(report_before, report_after)
print(f"CFR improvement: {comparison.cfr_delta:.1%}")
```

### Custom Protected Attributes

```python
report = audit_dataset(
    data='data.csv',
    protected_attributes=['gender', 'race', 'age', 'disability_status'],
    target_column='approved',
    positive_value=1
)
```

### Intersectional Analysis

```python
# Automatically detects compounded bias at intersections
# e.g., Black women may face worse treatment than Black or women individually

for intersection in report.intersectional_findings:
    print(f"{intersection.groups}: {intersection.severity}")
    print(f"Expected rate: {intersection.expected_rate:.2%}")
    print(f"Actual rate: {intersection.actual_rate:.2%}")
```

### Custom Personas for Agent Audit

```python
from nobias.agent_audit import audit_agent_with_personas

custom_personas = [
    {"name": "John Smith", "age": 35, "experience": 5},
    {"name": "Lakisha Washington", "age": 35, "experience": 5},
    {"name": "Wei Chen", "age": 35, "experience": 5},
]

report = await audit_agent_with_personas(
    system_prompt="...",
    personas=custom_personas,
    api_key="..."
)
```

## Supported LLM Providers

Agent Auditor supports multiple providers:

- **Groq** - Fast and affordable (llama-3.1-70b-versatile, mixtral-8x7b)
- **OpenAI** - GPT-4o, GPT-4-turbo, GPT-3.5-turbo
- **Anthropic** - Claude 3.5 Sonnet, Claude 3 Opus
- **Google Gemini** - Gemini 1.5 Pro, Gemini Pro, Gemini Flash
- **Ollama** - Local models (llama3.1, mistral, etc.)

```python
# Groq (default, fastest)
report = await audit_agent(..., backend="groq", model="llama-3.1-70b-versatile")

# OpenAI
report = await audit_agent(..., backend="openai", model="gpt-4o")

# Anthropic
report = await audit_agent(..., backend="anthropic", model="claude-3-5-sonnet-20241022")

# Gemini
report = await audit_agent(..., backend="gemini", model="gemini-1.5-pro")

# Ollama (local)
report = await audit_agent(..., backend="ollama", model="llama3.1:8b")
```

## Integration Examples

### CI/CD Pipeline

```python
def validate_before_deployment():
    # Dataset check
    dataset_report = audit_dataset('training_data.csv', ...)
    if dataset_report.overall_severity == 'CRITICAL':
        raise ValueError("Dataset has critical bias - blocking deployment")
    
    # Model check
    model_report = audit_model('model.pkl', 'test.csv', ...)
    if not model_report.eeoc_compliant:
        raise ValueError("Model fails EEOC compliance - blocking deployment")
    
    # Agent check
    agent_report = await audit_agent(system_prompt="...", ...)
    if agent_report.overall_cfr > 0.15:
        raise ValueError("Agent CFR exceeds 15% - blocking deployment")
```

### Monitoring Dashboard

```python
import schedule

def daily_audit():
    report = await audit_agent(...)
    
    # Log metrics
    metrics = {
        'cfr': report.overall_cfr,
        'eeoc_compliant': report.eeoc_compliant,
        'severity': report.overall_severity,
        'timestamp': datetime.now()
    }
    
    log_to_dashboard(metrics)
    
    if report.overall_severity in ['CRITICAL', 'MODERATE']:
        send_alert(report)

schedule.every().day.at("02:00").do(daily_audit)
```

## Performance

| Auditor | Input Size | Duration | Cost | Resources |
|---------|-----------|----------|------|-----------|
| Dataset | 10k rows | 2-10 sec | $0 | CPU, 200MB RAM |
| Model | 2k samples | 15-60 sec | $0 | CPU, 500MB RAM |
| Agent (Quick) | 14 personas | 2 min | $0.03-$0.11 | CPU, 300MB RAM |
| Agent (Standard) | 80 personas | 5 min | $0.05-$0.17 | CPU, 300MB RAM |
| Agent (Full) | 430 personas | 30 min | $0.07-$0.27 | CPU, 300MB RAM |

## Research Foundation

NoBias implements methods from peer-reviewed fairness research:

- CAFFE Framework (Cruciani et al. 2025) - Counterfactual fairness evaluation
- CFR/MASD Metrics (Mayilvaghanan et al. 2025) - Statistical bias detection
- Structured Reasoning (Nguyen et al. 2025) - Multi-agent bias interpretation
- Equality of Opportunity (Hardt et al. 2016) - Group fairness metrics
- EEOC Guidelines - 80% rule for disparate impact

## Documentation

- [Complete Presentation Guide](docs/NOBIAS_COMPLETE_PRESENTATION_GUIDE.md)
- [Agent Audit Implementation](docs/AGENT_AUDIT_COMPLETE_GUIDE.md)
- [Token Optimization](docs/ojas_TOKEN_OPTIMIZATION.md)
- [API Reference](docs/API_REFERENCE.md)
- [Examples](examples/)

## Requirements

- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- scipy >= 1.10.0
- scikit-learn >= 1.3.0

Optional dependencies installed with `nobias[all]`:
- groq, openai, anthropic, google-generativeai (LLM providers)
- aiohttp (async HTTP)
- reportlab, matplotlib (PDF reports)
- sentence-transformers (embeddings)

## License

MIT License

## Citation

```bibtex
@software{nobias2025,
  title={NoBias: Comprehensive AI Fairness Testing Platform},
  author={NoBias Team},
  year={2025},
  url={https://github.com/nobias/nobias}
}
```
