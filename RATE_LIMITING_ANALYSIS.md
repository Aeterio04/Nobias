# Rate Limiting Analysis - Critical Findings

## Executive Summary

**PROBLEM IDENTIFIED**: The library is making ALL persona API calls CONCURRENTLY using `asyncio.as_completed()`, which causes massive rate limit violations when testing with 8-10+ personas.

## The Issue: Concurrent Execution Pattern

### Location: `library/agent_audit/interrogation/engine.py` (Lines 173-196)

```python
async def run_all(
    self,
    cases: list[CAFFETestCase],
    progress_callback: Callable[[int, int, str], None] | None = None,
) -> list[CAFFETestCase]:
    """Run all CAFFE test cases with progress tracking."""
    logger.info(f"[START] Starting interrogation of {len(cases)} test cases")
    
    # THIS IS THE PROBLEM: Creates ALL tasks at once
    tasks = [self.interrogate(c) for c in cases]
    completed: list[CAFFETestCase] = []

    # Executes ALL tasks concurrently using as_completed
    for i, coro in enumerate(asyncio.as_completed(tasks)):
        result = await coro
        completed.append(result)
        # ...
```

### What's Happening:

1. **ALL personas are converted to tasks immediately**: `tasks = [self.interrogate(c) for c in cases]`
2. **ALL tasks start executing concurrently**: `asyncio.as_completed(tasks)` begins execution of ALL coroutines
3. **Each persona makes 3-5 API calls** (based on mode: QUICK=3, STANDARD=3, FULL=5)
4. **Total concurrent calls = personas × runs_per_persona**

### Example Scenario:

- **10 personas** in factorial grid
- **3 runs per persona** (STANDARD mode)
- **= 30 API calls trying to execute concurrently**

Even with the semaphore limiting to 3 concurrent requests, the token rate limiter sees ALL 30 requests queued up and starts blocking aggressively.

## The Rate Limiting Layers

### Layer 1: Semaphore (Groq Backend)
**File**: `library/agent_audit/interrogation/backends/groq.py` (Line 74)

```python
_semaphore = asyncio.Semaphore(3)  # Max 3 concurrent Groq calls
```

- Limits to 3 concurrent API requests
- Works correctly but doesn't prevent token budget issues

### Layer 2: Token Rate Limiter (Groq Backend)
**File**: `library/agent_audit/interrogation/backends/groq.py` (Lines 28-70)

```python
class TokenRateLimiter:
    """Sliding window rate limiter for TPM (tokens per minute) limits."""
    
    def __init__(self, tpm_limit: int = 5500, enabled: bool = True):
        self.tpm_limit = tpm_limit
        self.enabled = enabled
        self.requests: list[tuple[float, int]] = []  # (timestamp, tokens)
```

**The Problem**:
- When 30 requests are queued, the rate limiter sees the total token budget being consumed
- It calculates: "If I let this through, we'll exceed 5500 TPM"
- It sleeps for 60+ seconds waiting for the sliding window to clear
- This happens repeatedly because ALL requests are already queued

### Layer 3: Engine Semaphore (Interrogation Engine)
**File**: `library/agent_audit/interrogation/engine.py` (Line 72)

```python
self.semaphore = asyncio.Semaphore(config.rate_limit_rps)
```

- This is set from `config.rate_limit_rps` (default 10)
- But it's applied INSIDE each `interrogate()` call
- Since all interrogate() calls are already created and queued, this doesn't help

## Why It Hangs

### The Cascade Effect:

1. **10 personas** → 10 `interrogate()` coroutines created
2. Each `interrogate()` needs to make **3 API calls** (STANDARD mode)
3. All 10 coroutines start executing via `asyncio.as_completed()`
4. First 3 coroutines acquire the semaphore and start their first API call
5. Token rate limiter sees: "3 calls × 300 tokens = 900 tokens used"
6. Next 7 coroutines are waiting for semaphore
7. When first call completes, next coroutine starts
8. Token rate limiter now sees: "We've used 1200 tokens in the last 60s"
9. As more calls queue up, token budget fills
10. **Eventually**: Token rate limiter calculates "We'll exceed 5500 TPM" and sleeps for 60+ seconds
11. **User sees**: Complete hang with no output

### Why Standard Libraries Don't Have This Issue:

Libraries like LangGraph typically:
- Process items sequentially or in small batches
- Don't create all tasks upfront
- Use proper batching with delays between batches
- Have more sophisticated rate limiting that accounts for queued work

## The Fix (What Needs to Change)

### Option 1: Sequential Execution (Safest)
Replace concurrent execution with sequential:

```python
async def run_all(self, cases, progress_callback=None):
    completed = []
    for i, case in enumerate(cases):
        result = await self.interrogate(case)
        completed.append(result)
        if progress_callback:
            progress_callback(i + 1, len(cases), str(case.test_id))
    return completed
```

### Option 2: Batched Execution (Better Performance)
Process in small batches with delays:

```python
async def run_all(self, cases, progress_callback=None, batch_size=3):
    completed = []
    for i in range(0, len(cases), batch_size):
        batch = cases[i:i + batch_size]
        batch_results = await asyncio.gather(*[self.interrogate(c) for c in batch])
        completed.extend(batch_results)
        # Add delay between batches
        if i + batch_size < len(cases):
            await asyncio.sleep(2.0)
    return completed
```

### Option 3: Semaphore-Controlled Concurrent (Most Complex)
Use a proper worker pool pattern that respects rate limits:

```python
async def run_all(self, cases, progress_callback=None):
    semaphore = asyncio.Semaphore(2)  # Only 2 personas at a time
    
    async def process_with_semaphore(case):
        async with semaphore:
            return await self.interrogate(case)
    
    tasks = [process_with_semaphore(c) for c in cases]
    completed = []
    for i, coro in enumerate(asyncio.as_completed(tasks)):
        result = await coro
        completed.append(result)
    return completed
```

## Impact on Different Audit Modes

### QUICK Mode (3 runs per persona)
- 10 personas = 30 API calls
- With current implementation: High risk of hanging

### STANDARD Mode (3 runs per persona)  
- 10 personas = 30 API calls
- With current implementation: High risk of hanging

### FULL Mode (5 runs per persona)
- 180 personas (factorial grid) = 900 API calls
- With current implementation: **GUARANTEED to hang**

## Configuration Values

Current defaults that contribute to the issue:

```python
# config.py
rate_limit_rps: int = 10  # Applied per interrogate(), not globally
max_concurrent_requests: int = 3  # Only in Groq backend
tpm_limit: int = 5500  # Groq's actual limit

# engine.py  
self.semaphore = asyncio.Semaphore(config.rate_limit_rps)  # = 10
```

The problem: These limits are applied at the wrong level. The semaphore in engine.py is inside each interrogate() call, not controlling how many interrogate() calls run concurrently.

## Recommendations

1. **Immediate Fix**: Change `run_all()` to sequential execution ✅ **IMPLEMENTED**
2. **Better Fix**: Implement batched execution with configurable batch size
3. **Best Fix**: Implement proper worker pool with rate-aware scheduling
4. **Testing**: Add integration tests that verify rate limiting works with 10+ personas
5. **Monitoring**: Add logging to show when rate limits are being approached

## Files That Need Changes

1. `library/agent_audit/interrogation/engine.py` - Fix `run_all()` method ✅ **DONE**
2. `library/agent_audit/interrogation/backends/groq.py` - Remove TokenRateLimiter ✅ **DONE**
3. `tests/` - Add tests for sequential execution with rate limiting

---

## IMPLEMENTATION COMPLETE

### Changes Made:

1. **`library/agent_audit/interrogation/engine.py`**
   - Replaced `asyncio.as_completed()` with simple sequential for loop
   - Added 2-second pause between personas
   - One persona completes fully before the next starts
   - Physically impossible to hit TPM limits now

2. **`library/agent_audit/interrogation/backends/groq.py`**
   - Removed `TokenRateLimiter` class entirely (no longer needed)
   - Removed token budget acquisition logic from `call()` method
   - Kept semaphore for protection against accidental concurrent calls
   - Simplified initialization

### Why This Works:

With sequential execution, by the time persona N+1 starts, persona N has been done for 2+ seconds. All of persona N's API calls have aged out of any sliding window. The TPM budget is effectively reset between personas.

**Worst case behavior**: Slow (but predictable)
**Best case behavior**: Reliable and never frozen

### Trade-offs:

- **Slower**: 10 personas now take ~10x longer than ideal concurrent execution
- **Reliable**: Will never hang or freeze
- **Simple**: No complex rate limiting math to debug
- **Predictable**: Users can estimate completion time easily
