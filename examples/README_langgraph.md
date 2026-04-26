# LangGraph Agent API Endpoint Example

This example demonstrates how to audit a production agent via API endpoint.

## Setup

1. Install dependencies:
```bash
pip install langgraph langchain langchain-groq fastapi uvicorn
```

2. Set your API key in `library/.env`:
```bash
GROQ_API_KEY=gsk_your_key_here
```

## Running the Example

### Step 1: Start the Agent Server

In one terminal:
```bash
python examples/langgraph_agent_server.py
```

You should see:
```
✅ LangGraph agent initialized successfully
Starting server on http://localhost:8000
```

### Step 2: Test the Server (Optional)

In another terminal:
```bash
curl http://localhost:8000/health
```

Or test the evaluate endpoint:
```bash
curl -X POST http://localhost:8000/evaluate \
  -H "Content-Type: application/json" \
  -d '{"input": "Evaluate: Name: Test, Income: $50000, Credit: 700"}'
```

### Step 3: Run the Audit

In another terminal:
```bash
python tests/test_api_endpoint.py
```

The audit will:
1. Check if the server is running
2. Test the endpoint manually
3. Run a full bias audit via API calls
4. Generate comprehensive reports

## What's Happening

The test demonstrates **API Endpoint Mode**:

1. **LangGraph Agent** (`langgraph_agent_server.py`):
   - Built with LangGraph state machine
   - Served via FastAPI
   - Evaluates loan applications
   - Returns APPROVE/DENY decisions

2. **Audit Test** (`test_api_endpoint.py`):
   - Connects to the running server
   - Sends test cases with different personas
   - Analyzes responses for bias
   - Generates reports

## Key Features

- ✅ No access to internal prompts needed
- ✅ Tests actual production behavior
- ✅ Works with any HTTP API
- ✅ Same comprehensive reports as other modes

## API Endpoint Structure

The agent expects:
```json
{
  "input": "Loan application text..."
}
```

And returns:
```json
{
  "decision": "APPROVE",
  "reasoning": "Explanation..."
}
```

## Customization

To audit your own API:

```python
auditor = AgentAuditor.from_api(
    endpoint_url="https://your-api.com/evaluate",
    auth_header={"Authorization": "Bearer YOUR_TOKEN"},
    request_template={"input": "{input}"},
    response_path="$.decision",  # JSONPath to decision
)
```

## Troubleshooting

### "Cannot connect to server"
- Make sure the server is running first
- Check that port 8000 is not in use

### "Rate limit exceeded"
- Wait a few seconds between runs
- Use quick mode instead of standard

### "Agent not initialized"
- Check that GROQ_API_KEY is set in library/.env
- Restart the server

## Next Steps

- Try with your own agent API
- Test different audit modes (quick/standard/full)
- Compare before/after prompt improvements
