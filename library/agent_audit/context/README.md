# Layer 1: Context Collection

## Overview

Layer 1 handles agent connection setup and provides a unified interface for interrogating agents regardless of how they're accessed.

## Architecture

```
User Config
    ↓
build_agent_connector()
    ↓
AgentConnector (unified interface)
    ↓
Backend Implementation (Groq, OpenAI, API, Logs)
    ↓
async .call(input) → output
```

## Files

### `agent_connector.py`
The main factory and connector implementations.

**Key functions:**
- `build_agent_connector()` - Factory that builds the right connector
- `AgentConnector` - Unified wrapper with `.call()` method

**Supported modes:**
- System Prompt: Wraps LLM backends (Groq, OpenAI)
- API Endpoint: POSTs to user-provided APIs
- Log Replay: Reads from JSONL files

### `validators.py`
Input validation for configs and seed cases.

**Key functions:**
- `validate_config()` - Validates audit configuration
- `validate_seed_case()` - Validates seed case input

**Catches:**
- Missing API keys
- Invalid model names
- Empty seed cases
- Malformed API configs

### `test_context.py`
Test suite for Layer 1 functionality.

**Tests:**
- System prompt mode with Groq
- API endpoint mode validation
- Log replay mode with sample data
- Seed case validation

### `USAGE.md`
Comprehensive usage guide with examples for all three modes.

### `__init__.py`
Public API exports.

## Usage

### Quick Example

```python
from agent_audit import (
    build_agent_connector,
    AgentConnectionMode,
    PromptAgentConfig,
)

# Configure
config = PromptAgentConfig(
    system_prompt="You are a hiring assistant...",
    model_backend="llama-3.1-70b-versatile",
    api_key="gsk_...",
)

# Build
connector = build_agent_connector(
    AgentConnectionMode.SYSTEM_PROMPT,
    config
)

# Use
response = await connector.call("Evaluate this candidate...")
```

## Backend Support

### ✅ Implemented
- **Groq**: Llama, Mixtral, Gemma (fast & affordable)
- **OpenAI**: GPT-4o, GPT-4, GPT-3.5

### ❌ Not Yet Implemented
- **Anthropic**: Claude models
- **Ollama**: Local models

## Design Decisions

### Why a unified interface?
The `AgentConnector` wrapper ensures that Layers 2-5 don't need to know how the agent is accessed. This makes the pipeline modular and testable.

### Why auto-detect backends?
Users shouldn't need to specify both a model name AND a backend. The model name implies the backend:
- `llama-*` → Groq
- `gpt-*` → OpenAI

### Why support log replay?
Privacy-sensitive organizations may not want to send data to external APIs during audits. Log replay lets them audit historical interactions without any external calls.

## Integration with Other Layers

Layer 1 produces an `AgentConnector` that is consumed by:

**Layer 3 (Interrogation Engine):**
```python
engine = InterrogationEngine(
    config=audit_config,
    agent_caller=connector.call,  # ← Layer 1 output
)
```

The engine doesn't know or care whether it's calling Groq, OpenAI, an API, or reading from logs. It just calls `connector.call()` and gets a response.

## Testing

Run the test suite:
```bash
python library/agent_audit/context/test_context.py
```

Run the example:
```bash
export GROQ_API_KEY="gsk_..."
python examples/test_groq_connection.py
```

## Next Steps

With Layer 1 complete, the next step is to wire it into the main pipeline orchestrator (`AgentAuditor.run()`) so users can run full audits end-to-end.
