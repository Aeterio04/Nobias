# Layer 1 Context Collection - Usage Guide

## Overview

Layer 1 provides three ways to connect to an agent under test:

1. **System Prompt Mode**: Test an agent by providing its system prompt + LLM backend
2. **API Endpoint Mode**: Test a deployed agent via its HTTP API
3. **Log Replay Mode**: Audit historical interactions from a JSONL file (privacy-friendly)

All modes expose a unified `AgentConnector` interface with an async `.call(input) -> output` method.

---

## 1. System Prompt Mode

Best for: Testing agents during development, comparing different prompts.

### Example with Groq (Recommended for Testing)

```python
import asyncio
from agent_audit.config import AgentConnectionMode, PromptAgentConfig
from agent_audit.context import build_agent_connector

async def test_with_groq():
    config = PromptAgentConfig(
        system_prompt="You are a hiring assistant. Evaluate candidates and respond with HIRE or REJECT.",
        model_backend="llama-3.1-70b-versatile",  # Fast and affordable
        api_key="gsk_...",  # Your Groq API key
        temperature=0.0,
        max_tokens=200,
    )
    
    connector = build_agent_connector(AgentConnectionMode.SYSTEM_PROMPT, config)
    
    test_input = """
    Evaluate this candidate:
    Name: Alex Johnson
    Experience: 5 years
    Skills: Python, React
    """
    
    response = await connector.call(test_input)
    print(response)

asyncio.run(test_with_groq())
```

### Supported Models

**Groq** (recommended for testing - fast & cheap):
- `llama-3.1-70b-versatile`
- `llama-3.1-8b-instant`
- `mixtral-8x7b-32768`
- `gemma-7b-it`

**OpenAI**:
- `gpt-4o`
- `gpt-4-turbo`
- `gpt-3.5-turbo`

The backend is auto-detected from the model name:
- `llama-*`, `mixtral-*`, `gemma-*` → Groq
- `gpt-*` → OpenAI

---

## 2. API Endpoint Mode

Best for: Testing deployed production agents.

### Example

```python
from agent_audit.config import AgentConnectionMode, APIAgentConfig
from agent_audit.context import build_agent_connector

config = APIAgentConfig(
    endpoint_url="https://api.yourcompany.com/agent/evaluate",
    auth_header={"Authorization": "Bearer YOUR_TOKEN"},
    request_template={
        "input": "{input}",
        "mode": "evaluation",
        "version": "v2"
    },
    response_path="$.result.decision",  # JSONPath to extract decision
    rate_limit_rps=10,
)

connector = build_agent_connector(AgentConnectionMode.API_ENDPOINT, config)

# Use the connector
response = await connector.call("Evaluate candidate X")
```

### JSONPath Examples

The `response_path` uses JSONPath to extract the decision from the API response:

```python
# Response: {"result": "HIRE"}
response_path = "$.result"

# Response: {"data": {"decision": "REJECT"}}
response_path = "$.data.decision"

# Response: {"choices": [{"message": {"content": "HIRE"}}]}
response_path = "$.choices[0].message.content"
```

---

## 3. Log Replay Mode

Best for: Privacy-sensitive audits, testing on historical data.

### Example

```python
from pathlib import Path
from agent_audit.config import AgentConnectionMode, ReplayAgentConfig
from agent_audit.context import build_agent_connector

# Your JSONL file format:
# {"input": "Evaluate candidate A", "output": "HIRE"}
# {"input": "Evaluate candidate B", "output": "REJECT"}

config = ReplayAgentConfig(
    log_file=Path("interactions.jsonl"),
    input_field="input",
    output_field="output",
)

connector = build_agent_connector(AgentConnectionMode.LOG_REPLAY, config)

# Lookup is exact-match (with fuzzy fallback)
response = connector.call("Evaluate candidate A")  # Returns "HIRE"
```

### JSONL Format

Each line must be valid JSON:

```jsonl
{"input": "Evaluate candidate: John Smith, 5 years exp", "output": "HIRE"}
{"input": "Evaluate candidate: Jane Doe, 2 years exp", "output": "REJECT"}
```

Field names are configurable via `input_field` and `output_field`.

---

## Validation

Always validate your config before starting an audit:

```python
from agent_audit.config import AgentAuditConfig
from agent_audit.context import validate_config, validate_seed_case

# Validate connection config
errors = validate_config(
    config=AgentAuditConfig(),
    connection_mode=AgentConnectionMode.SYSTEM_PROMPT,
    connection_config=your_prompt_config,
)

if errors:
    print(f"Configuration errors: {errors}")
    exit(1)

# Validate seed case
seed_case = "Evaluate this candidate: ..."
errors = validate_seed_case(seed_case)

if errors:
    print(f"Seed case errors: {errors}")
    exit(1)
```

---

## Error Handling

```python
try:
    response = await connector.call(test_input)
except ValueError as e:
    print(f"Configuration error: {e}")
except RuntimeError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

## Next Steps

Once you have a working `AgentConnector`, you can:

1. Pass it to the `InterrogationEngine` (Layer 3)
2. Generate persona grids (Layer 2)
3. Run the full audit pipeline

See the main `AgentAuditor` class for the complete workflow.
