# Logging and Rate Limiting Testing - Implementation Summary

## Overview

Added comprehensive logging throughout the agent_audit library and created a test suite to diagnose rate limiting issues.

## What Was Added

### 1. Logging Infrastructure

#### New Module: `library/agent_audit/logging_config.py`
Centralized logging configuration with easy-to-use functions:

```python
from agent_audit import setup_logging

# Enable INFO level logging
setup_logging(level="INFO")

# Enable DEBUG level for detailed troubleshooting
setup_logging(level="DEBUG")

# Disable logging
from agent_audit import disable_logging
disable_logging()
```

#### Logging Added to Key Modules

1. **Groq Backend** (`library/agent_audit/interrogation/backends/groq.py`)
   - Logs initialization with model and parameters
   - Logs each API call with input length
   - Logs successful responses with response length
   - Logs rate limit warnings with retry attempts
   - Logs errors with detailed error messages

2. **Interrogation Engine** (`library/agent_audit/interrogation/engine.py`)
   - Logs engine initialization with configuration
   - Logs cache hits/misses
   - Logs each interrogation with test case ID
   - Logs run details (decision, score, early stops)
   - Logs final statistics (total cases, API calls, duration)

3. **Orchestrator** (`library/agent_audit/orchestrator.py`)
   - Logs pipeline initialization
   - Logs each layer execution (persona generation, interrogation, statistics, interpretation)
   - Logs progress through the 5-layer pipeline

4. **API** (`library/agent_audit/api.py`)
   - Logs audit_agent() calls with parameters
   - Logs configuration details

### 2. Rate Limiting Test Suite

#### New Test File: `tests/test_rate_limiting.py`

Comprehensive test suite with 6 test scenarios:

1. **test_single_request**: Verify basic API connectivity
2. **test_rate_limit_retry**: Test automatic retry logic
3. **test_concurrent_requests**: Test handling of 10 concurrent requests
4. **test_interrogation_engine_with_rate_limits**: Test full engine under load
5. **test_rate_limit_exhaustion**: Test behavior when retries are exhausted
6. **test_backend_error_handling**: Test various error scenarios

### 3. Documentation

#### `tests/README_RATE_LIMITING.md`
Complete guide covering:
- How to run the tests
- How to enable logging
- Understanding log output
- Common issues and solutions
- Debugging tips
- Performance benchmarks

#### `examples/logging_example.py`
Interactive example demonstrating:
- How to enable logging at different levels
- What information is logged during an audit
- How to interpret the logs
- Both INFO and DEBUG mode examples

## How to Use

### Quick Start - Enable Logging

```python
from agent_audit import audit_agent, setup_logging

# Enable logging before running audit
setup_logging(level="INFO")

report = await audit_agent(
    system_prompt="...",
    seed_case="...",
    api_key="...",
)
```

### Run Rate Limiting Tests

```bash
# Set your API key
export GROQ_API_KEY="your-key-here"

# Run all tests
pytest tests/test_rate_limiting.py -v -s

# Run with debug logging
pytest tests/test_rate_limiting.py -v -s --log-cli-level=DEBUG

# Run specific test
pytest tests/test_rate_limiting.py::TestRateLimiting::test_single_request -v -s
```

### Try the Logging Example

```bash
# Interactive example
python examples/logging_example.py

# Choose option 1 for INFO level or 2 for DEBUG level
```

## What the Logs Show

### INFO Level (Recommended for Normal Use)

```
[INFO] agent_audit.api: === audit_agent() called ===
[INFO] agent_audit.orchestrator: === Starting Audit Pipeline (ID: audit-a1b2c3d4) ===
[INFO] agent_audit.orchestrator: Layer 2: Generating persona grid
[INFO] agent_audit.orchestrator:   Generated 12 personas
[INFO] agent_audit.orchestator: Layer 3: Interrogating agent
[INFO] agent_audit.interrogation.engine: Starting interrogation of 12 test cases
[INFO] agent_audit.interrogation.backends.groq: ✓ Groq API call successful (response length: 150 chars)
[INFO] agent_audit.interrogation.engine: ✓ Interrogation complete: 12 cases, 36 total API calls
[INFO] agent_audit.orchestrator: Layer 4: Computing statistics
[INFO] agent_audit.orchestrator:   Found 3 statistical findings
[INFO] agent_audit.orchestrator: Layer 5: Interpreting findings
```

### DEBUG Level (For Troubleshooting)

Shows everything from INFO plus:
- Input text length for each API call
- Cache operations
- Individual run details (decision, score)
- Early stop triggers
- Detailed error messages

### Rate Limit Warnings

```
[WARNING] agent_audit.interrogation.backends.groq: ⚠️  Rate limit hit, retrying in 3.0s (attempt 1/2)
⚠️  Rate limit hit, retrying in 3.0s (attempt 1/2)...
```

## Diagnosing Rate Limiting Issues

### Step 1: Enable Logging

```python
from agent_audit import setup_logging
setup_logging(level="INFO")
```

### Step 2: Run Your Audit

Watch for rate limit warnings in the output.

### Step 3: If You See Rate Limits

Adjust your configuration:

```python
from agent_audit import audit_agent

report = await audit_agent(
    # ... other parameters ...
    rate_limit_rps=5,  # Reduce from default 10
    mode="quick",      # Use quick mode for fewer API calls
)
```

### Step 4: Run the Test Suite

```bash
pytest tests/test_rate_limiting.py -v -s
```

This will help identify:
- Whether rate limiting is consistent or intermittent
- How many concurrent requests you can handle
- Whether retry logic is working correctly

## Key Features

### Automatic Retry Logic

The Groq backend automatically retries on rate limit errors:
- Up to 2 retries
- 3-second delay between retries
- Clear logging of retry attempts

### Rate Limiting Control

Control request rate with `rate_limit_rps` parameter:

```python
config = AgentAuditConfig(
    rate_limit_rps=5,  # 5 requests per second
)
```

### Caching

Enable caching to avoid redundant API calls:

```python
config = AgentAuditConfig(
    cache_enabled=True,
)
```

## Performance Tips

1. **Start with Quick Mode**: Use `mode="quick"` for initial testing
2. **Reduce Rate Limit**: Lower `rate_limit_rps` if you hit limits
3. **Enable Caching**: Set `cache_enabled=True` to reuse results
4. **Test Fewer Attributes**: Start with 1-2 attributes, then scale up
5. **Monitor Logs**: Watch for rate limit warnings

## Troubleshooting

### Issue: Frequent Rate Limits

**Solution:**
```python
# Reduce concurrent requests
config = AgentAuditConfig(rate_limit_rps=3)

# Use quick mode
report = await audit_agent(..., mode="quick")

# Test fewer attributes
report = await audit_agent(..., attributes=["gender"])
```

### Issue: Slow Execution

**Solution:**
```python
# Enable caching
config = AgentAuditConfig(cache_enabled=True)

# Check if rate limiting is the cause
setup_logging(level="INFO")
# Look for retry messages in logs
```

### Issue: Inconsistent Results

**Solution:**
```bash
# Run the test suite to diagnose
pytest tests/test_rate_limiting.py::TestRateLimiting::test_concurrent_requests -v -s

# Enable debug logging
setup_logging(level="DEBUG")
```

## Next Steps

1. Run the test suite to establish a baseline
2. Enable logging in your production code
3. Monitor for rate limit warnings
4. Adjust configuration based on results
5. Use caching for repeated tests

## Files Modified/Created

### New Files
- `library/agent_audit/logging_config.py` - Logging configuration
- `tests/test_rate_limiting.py` - Rate limiting test suite
- `tests/README_RATE_LIMITING.md` - Testing guide
- `examples/logging_example.py` - Interactive logging example
- `LOGGING_AND_TESTING_SUMMARY.md` - This file

### Modified Files
- `library/agent_audit/interrogation/backends/groq.py` - Added logging
- `library/agent_audit/interrogation/engine.py` - Added logging
- `library/agent_audit/orchestrator.py` - Added logging
- `library/agent_audit/api.py` - Added logging
- `library/agent_audit/__init__.py` - Exported logging functions

## Summary

The library now has comprehensive logging that helps you:
- Understand what's happening during an audit
- Diagnose rate limiting issues
- Debug problems quickly
- Monitor performance

The test suite helps you:
- Verify rate limiting behavior
- Test under different load conditions
- Identify configuration issues
- Establish performance baselines

All logging is opt-in and can be enabled with a single function call.
