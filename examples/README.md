# Agent Audit Examples

This folder contains example scripts demonstrating how to use the Agent Audit module.

## Quick Start

### 1. Test Groq Connection

The simplest way to get started - tests the basic agent connection with Groq.

```bash
# Install dependencies
pip install groq

# Set your API key
export GROQ_API_KEY="gsk_your_key_here"

# Run the test
python examples/test_groq_connection.py
```

**What it does:**
- Validates your configuration
- Connects to Groq's Llama model
- Sends test inputs to a hiring assistant agent
- Verifies the responses

**Get a Groq API key:** https://console.groq.com/ (free tier available)

---

## Available Examples

### `test_groq_connection.py`
Basic connection test with Groq backend. Start here!

**Use case:** Verify your setup works before running full audits.

---

## Coming Soon

- `full_audit_example.py` - Complete bias audit workflow
- `compare_prompts.py` - Before/after comparison
- `api_endpoint_example.py` - Testing deployed agents
- `log_replay_example.py` - Auditing historical data

---

## Troubleshooting

### "ModuleNotFoundError: No module named 'groq'"
```bash
pip install groq
```

### "API key required for model"
Set your API key:
```bash
export GROQ_API_KEY="gsk_..."
```

Or pass it directly in the config:
```python
config = PromptAgentConfig(
    api_key="gsk_...",
    ...
)
```

### "Rate limit exceeded"
Groq has generous rate limits, but if you hit them:
1. Add delays between requests
2. Use a slower model (llama-3.1-8b-instant)
3. Upgrade your Groq plan

---

## Next Steps

After testing the connection:

1. **Read the docs:** `library/agent_audit/QUICKSTART.md`
2. **Explore Layer 1:** `library/agent_audit/context/USAGE.md`
3. **Run a full audit:** (coming soon - pipeline orchestrator)

---

## Support

- Groq API docs: https://console.groq.com/docs
- Agent Audit spec: `docs/module3_agent_auditor_spec.md`
- Development logs: `docs/logs.md`
