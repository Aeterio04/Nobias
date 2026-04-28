# Google Gemini Integration

## Overview

Google Gemini support has been added to the NoBias Agent Audit system, allowing you to use Google's latest AI models for bias detection in LLM agents.

## Supported Models

- **gemini-1.5-pro** - Most capable model, best for complex reasoning
- **gemini-1.5-flash** - Faster and more cost-effective
- **gemini-pro** - Previous generation, still highly capable
- **gemini-1.0-pro** - Legacy model

## Installation

```bash
# Install with Gemini support
pip install unbiased[agent]

# Or install the google-generativeai package separately
pip install google-generativeai
```

## Getting Your API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key

## Usage

### Basic Agent Audit with Gemini

```python
import asyncio
from agent_audit import audit_agent

async def main():
    report = await audit_agent(
        system_prompt="You are a hiring assistant...",
        seed_case="Evaluate candidate: Name: Alex...",
        api_key="your-google-api-key",
        model="gemini-1.5-pro",  # Specify Gemini model
        mode="standard",
        protected_attributes=["gender", "race", "age"],
    )
    
    print(f"Severity: {report.overall_severity}")
    print(f"CFR: {report.overall_cfr:.1%}")

asyncio.run(main())
```

### Using Environment Variables

```python
import os
from dotenv import load_dotenv

load_dotenv()

report = await audit_agent(
    system_prompt="...",
    seed_case="...",
    api_key=os.getenv("GOOGLE_API_KEY"),
    model="gemini-1.5-pro",
)
```

### Direct Backend Usage

```python
from agent_audit.interrogation.backends.gemini import GeminiBackend

backend = GeminiBackend(
    api_key="your-api-key",
    model="gemini-1.5-pro",
    system_prompt="You are a helpful assistant.",
    temperature=0.0,
    max_tokens=1024,
)

response = await backend.call("Your input here")
```

## Model Selection Guide

| Model | Speed | Cost | Best For |
|-------|-------|------|----------|
| **gemini-1.5-pro** | Moderate | Higher | Complex reasoning, comprehensive audits |
| **gemini-1.5-flash** | Fast | Lower | Quick scans, development testing |
| **gemini-pro** | Moderate | Moderate | General purpose auditing |

## Configuration Options

```python
from agent_audit import AgentAuditConfig

config = AgentAuditConfig(
    backend="gemini",  # Auto-detected from model name
    model="gemini-1.5-pro",
    api_key="your-api-key",
    temperature=0.0,  # Locked for determinism
    max_tokens=1024,
    rate_limit_rps=10,  # Requests per second
)
```

## Examples

### Example 1: Hiring Assistant Audit

```python
import asyncio
from agent_audit import audit_agent

async def audit_hiring_agent():
    report = await audit_agent(
        system_prompt="""You are a hiring assistant for a tech company.
Evaluate candidates and decide whether to hire them.
Respond with HIRE or REJECT followed by a brief reason.""",
        
        seed_case="""Evaluate this candidate:
Name: Jordan Smith
Age: 29
Experience: 5 years as a software engineer
Education: Bachelor's in Computer Science""",
        
        api_key="your-google-api-key",
        model="gemini-1.5-pro",
        mode="standard",
        protected_attributes=["gender", "race", "age"],
        domain="hiring",
    )
    
    # Check results
    print(f"Overall Severity: {report.overall_severity}")
    print(f"CFR: {report.overall_cfr:.1%}")
    print(f"EEOC Compliant: {report.eeoc_compliant}")
    
    # Export report
    report.export("gemini_audit_report.json")

asyncio.run(audit_hiring_agent())
```

### Example 2: Comparing Gemini Models

```python
async def compare_models():
    models = ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"]
    
    for model in models:
        print(f"\nTesting {model}...")
        report = await audit_agent(
            system_prompt="...",
            seed_case="...",
            api_key="your-api-key",
            model=model,
            mode="quick",
        )
        print(f"  CFR: {report.overall_cfr:.1%}")
        print(f"  Severity: {report.overall_severity}")
```

## Cost Comparison

| Provider | Model | Input (per 1M tokens) | Output (per 1M tokens) |
|----------|-------|----------------------|------------------------|
| **Google Gemini** | gemini-1.5-pro | $3.50 | $10.50 |
| **Google Gemini** | gemini-1.5-flash | $0.35 | $1.05 |
| **Groq** | llama-3.1-70b | $0.59 | $0.79 |
| **OpenAI** | gpt-4o | $2.50 | $10.00 |

*Prices as of 2024. Check provider websites for current pricing.*

## Performance Tips

1. **Use gemini-1.5-flash for development** - Faster and cheaper for testing
2. **Use gemini-1.5-pro for production** - More accurate and consistent
3. **Set temperature to 0.0** - Ensures deterministic responses (default)
4. **Enable prompt caching** - Reduces costs for repeated audits (automatic)
5. **Use quick mode first** - Test with 14 personas before running full audit

## Rate Limits

Google Gemini has the following rate limits (free tier):

- **Requests per minute**: 60
- **Tokens per minute**: 32,000 (gemini-1.5-pro)
- **Tokens per minute**: 1,000,000 (gemini-1.5-flash)

The library automatically handles rate limiting with configurable `rate_limit_rps`.

## Troubleshooting

### Error: "API key not valid"

**Solution**: Verify your API key at [Google AI Studio](https://makersuite.google.com/app/apikey)

```python
# Test your API key
from agent_audit.interrogation.backends.gemini import GeminiBackend

backend = GeminiBackend(api_key="your-key", model="gemini-1.5-pro")
response = await backend.call("Hello")
print(response)
```

### Error: "Resource exhausted"

**Solution**: You've hit rate limits. Reduce `rate_limit_rps`:

```python
report = await audit_agent(
    ...,
    rate_limit_rps=5,  # Reduce from default 10
)
```

### Error: "Model not found"

**Solution**: Check model name spelling. Valid models:
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- `gemini-pro`

### Slow Performance

**Solution**: Use gemini-1.5-flash for faster responses:

```python
report = await audit_agent(
    ...,
    model="gemini-1.5-flash",  # Faster model
)
```

## Advanced Usage

### Custom System Prompts

```python
backend = GeminiBackend(
    api_key="your-key",
    model="gemini-1.5-pro",
    system_prompt="""You are a loan approval assistant.
Evaluate applicants fairly and consistently.
Respond in JSON format: {"decision": "approve" or "reject", "reason": "..."}""",
)
```

### Adjusting Token Limits

```python
backend = GeminiBackend(
    api_key="your-key",
    model="gemini-1.5-pro",
    max_tokens=2048,  # Increase for longer responses
)
```

## Integration with Other Features

### With Two-Pass Evaluation

```python
report = await audit_agent(
    ...,
    model="gemini-1.5-pro",
    use_two_pass_evaluation=True,  # Reduces API calls by 50%
)
```

### With Prompt Caching

```python
report = await audit_agent(
    ...,
    model="gemini-1.5-pro",
    use_prompt_caching=True,  # Reduces costs by 65%
)
```

### With Optimization

```python
report = await audit_agent(
    ...,
    model="gemini-1.5-pro",
    enable_optimization=True,  # All optimizations enabled
    optimization_tier="tier_2",  # Standard tier
)
```

## See Also

- [Agent Audit Complete Guide](AGENT_AUDIT_COMPLETE_GUIDE.md)
- [API Reference](../library/agent_audit/API_REFERENCE.md)
- [Examples](../examples/gemini_audit_example.py)

## Support

For issues or questions:
- Check [Google AI Studio Documentation](https://ai.google.dev/docs)
- Review [examples/test_gemini_connection.py](../examples/test_gemini_connection.py)
- See [examples/gemini_audit_example.py](../examples/gemini_audit_example.py)

---

**Version**: 1.0  
**Last Updated**: 2026-04-28  
**Supported Models**: Gemini 1.5 Pro, Gemini 1.5 Flash, Gemini Pro
