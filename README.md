# Unbiased

**Comprehensive bias detection and mitigation for datasets, models, and LLM agents**

Unbiased is a Python library that provides end-to-end fairness auditing across the entire ML pipeline - from raw data to deployed AI agents.

## Features

### 🗂️ Dataset Audit
Detect statistical biases in tabular datasets before model training:
- Representation analysis (demographic imbalances)
- Label bias detection (outcome disparities)
- Proxy feature detection (hidden correlations)
- Missing data patterns
- Intersectional disparities
- KL divergence analysis

### 🤖 Model Audit
Audit trained ML models for fairness violations:
- Counterfactual flip testing
- 5 group fairness metrics (Demographic Parity, Disparate Impact, Equalized Odds, etc.)
- Intersectional bias analysis
- Automatic severity classification
- Mitigation recommendations

### 🧠 Agent Audit
Black-box bias auditing for LLM agents:
- System prompt auditing
- API endpoint testing
- Log replay analysis
- Persona-based counterfactual testing
- Statistical bias detection (CFR, MASD)
- Prompt surgery recommendations

## Installation

```bash
# Basic installation (dataset and model audit)
pip install unbiased

# With LLM agent audit support
pip install unbiased[agent]

# With report generation (PDF, visualizations)
pip install unbiased[reports]

# Full installation with all features
pip install unbiased[all]
```

## Quick Start

### Dataset Audit

```python
from unbiased import audit_dataset

report = audit_dataset(
    data='hiring_data.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Severity: {report.overall_severity}")
print(f"Findings: {len(report.findings)}")
report.export('dataset_audit.json')
```

### Model Audit

```python
from unbiased.model_audit import audit_model

report = audit_model(
    model='trained_model.pkl',
    test_data='test.csv',
    protected_attributes=['gender', 'race'],
    target_column='hired',
    positive_value=1
)

print(f"Severity: {report.overall_severity}")
for finding in report.findings:
    print(f"- {finding.title}: {finding.severity}")
```

### Agent Audit

```python
from unbiased.agent_audit import audit_agent

report = await audit_agent(
    system_prompt="You are a hiring assistant...",
    seed_case="Evaluate candidate: Name: Alex...",
    api_key="your-api-key"
)

print(f"Bias detected: {report.has_bias}")
print(f"CFR: {report.cfr:.3f}")
```

## Documentation

- [Dataset Audit Guide](docs/dataset_audit_guide.md)
- [Model Audit Guide](docs/model_audit_guide.md)
- [Agent Audit Implementation Guide](docs/ojas_AGENT_AUDIT_IMPLEMENTATION_GUIDE.md)
- [API Reference](API_REFERENCE.md)

## Requirements

- Python 3.8+
- pandas >= 2.0.0
- numpy >= 1.24.0
- scipy >= 1.10.0
- scikit-learn >= 1.3.0

## Optional Dependencies

- **Agent audit**: `groq`, `openai`, `anthropic`, `aiohttp`
- **Reports**: `reportlab`, `matplotlib`
- **Embeddings**: `sentence-transformers`
- **LangGraph**: `langgraph`, `langchain`

## Research Foundation

Unbiased implements methods from cutting-edge fairness research:

- **CAFFE** (Parziale et al. 2025) - Counterfactual fairness evaluation
- **CFR/MASD** (Mayilvaghanan et al. 2025) - Statistical bias metrics
- **Hardt et al. (2016)** - Equality of opportunity
- **Chouldechova (2017)** - Fair prediction with disparate impact
- **EEOC Guidelines** - 80% rule for disparate impact

## License

MIT License - see LICENSE file for details

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## Citation

If you use Unbiased in your research, please cite:

```bibtex
@software{unbiased2025,
  title={Unbiased: Comprehensive Bias Detection and Mitigation Library},
  author={NoBias Team},
  year={2025},
  url={https://github.com/nobias/unbiased}
}
```

## Support

- GitHub Issues: https://github.com/nobias/unbiased/issues
- Documentation: https://github.com/nobias/unbiased/blob/main/docs
- Email: contact@nobias.dev
