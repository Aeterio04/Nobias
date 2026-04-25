# Agent Audit Tests

Three test files demonstrating each API level.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up your API key in `library/.env`:
```bash
GROQ_API_KEY=gsk_your_key_here
```

## Running Tests

### Test Level 1 - One-liner Function
```bash
python tests/test_level1_api.py
```

Tests the simplest `audit_agent()` function with quick mode.
- Expected API calls: ~10-15
- Duration: ~30-60 seconds

### Test Level 2 - Class-Based Interface
```bash
python tests/test_level2_api.py
```

Tests `AgentAuditor` class with before/after comparison.
- Expected API calls: ~20-30 (two audits)
- Duration: ~60-90 seconds

### Test Level 3 - Manual Pipeline
```bash
python tests/test_level3_api.py
```

Tests manual control over each layer with limited personas.
- Expected API calls: <20 (enforced)
- Duration: ~20-40 seconds

## Run All Tests
```bash
python tests/test_level1_api.py && \
python tests/test_level2_api.py && \
python tests/test_level3_api.py
```

## What Each Test Validates

### Level 1
- One-liner function works end-to-end
- Report contains all required fields
- Findings are properly classified
- CFR and severity metrics are computed

### Level 2
- Auditor instance can be reused
- Prompt can be updated
- Before/after comparison works
- Comparison metrics are accurate

### Level 3
- Manual connector building works
- Persona generation is controllable
- Direct agent interrogation works
- Basic statistics can be computed manually
- API call limit is respected (<20 calls)

## Troubleshooting

### "GROQ_API_KEY not found"
Create `library/.env` with your API key:
```bash
echo "GROQ_API_KEY=gsk_your_key_here" > library/.env
```

### "Rate limit exceeded"
Wait a few seconds between test runs or use a different model.

### Tests are slow
This is normal - each test makes real API calls. Level 3 is fastest (~20 calls).
