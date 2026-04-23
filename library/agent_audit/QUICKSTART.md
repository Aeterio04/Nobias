# Agent Audit - Quick Start Guide

## Installation

```bash
pip install groq  # For Groq backend (recommended for testing)
pip install openai  # For OpenAI backend
pip install aiohttp  # For API endpoint mode
```

## Basic Usage - System Prompt Mode with Groq

```python
import asyncio
from agent_audit import (
    build_agent_connector,
    AgentConnectionMode,
    PromptAgentConfig,
)

async def quick_test():
    # 1. Configure your agent
    config = PromptAgentConfig(
        system_prompt="You are a hiring assistant. Evaluate candidates and respond with HIRE or REJECT.",
        model_backend="llama-3.1-70b-versatile",  # Groq - fast & affordable
        api_key="gsk_YOUR_GROQ_API_KEY",
        temperature=0.0,
    )
    
    # 2. Build the connector
    connector = build_agent_connector(
        AgentConnectionMode.SYSTEM_PROMPT,
        config
    )
    
    # 3. Test it
    response = await connector.call("""
    Evaluate this candidate:
    Name: Alex Johnson
    Experience: 5 years in software engineering
    Skills: Python, React, SQL
    """)
    
    print(f"Agent response: {response}")

asyncio.run(quick_test())
```

## Get a Groq API Key

1. Go to https://console.groq.com/
2. Sign up (free tier available)
3. Create an API key
4. Use it in your config: `api_key="gsk_..."`

## Supported Models

### Groq (Recommended for Testing)
- `llama-3.1-70b-versatile` - Best quality
- `llama-3.1-8b-instant` - Fastest
- `mixtral-8x7b-32768` - Long context
- `gemma-7b-it` - Lightweight

### OpenAI
- `gpt-4o` - Latest
- `gpt-4-turbo` - Fast
- `gpt-3.5-turbo` - Cheap

## Three Connection Modes

### 1. System Prompt (Development)
```python
config = PromptAgentConfig(
    system_prompt="Your agent's system prompt",
    model_backend="llama-3.1-70b-versatile",
    api_key="gsk_...",
)
```

### 2. API Endpoint (Production)
```python
config = APIAgentConfig(
    endpoint_url="https://api.yourcompany.com/agent",
    auth_header={"Authorization": "Bearer TOKEN"},
    request_template={"input": "{input}"},
    response_path="$.result",
)
```

### 3. Log Replay (Historical Data)
```python
config = ReplayAgentConfig(
    log_file=Path("interactions.jsonl"),
    input_field="input",
    output_field="output",
)
```

## Next Steps

Once you have a working connector, you can:

1. **Run a full audit** (coming soon - pipeline orchestrator)
2. **Generate persona grids** to test for bias
3. **Get statistical findings** with CFR/MASD metrics
4. **Receive remediation suggestions** for your system prompt

See `context/USAGE.md` for detailed documentation.
