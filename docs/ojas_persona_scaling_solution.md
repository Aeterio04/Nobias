# The Persona Explosion Problem — Plain English Explainer

> **TL;DR**: Our current spec creates too many test personas, which means too many API calls, which means the audit takes forever and burns through rate limits. Three fixes — tiered modes, smarter math, and adaptive stopping — can bring a standard audit from **~580 calls / 30 min** down to **~28 calls / 2 min** with almost no loss in detection quality.

---

## 1. What's the Problem?

Our spec says: "test every combination of gender × race × age." That's called a **full factorial** grid.

Here's the math with the current attribute lists:

| What we're combining        | Values                                    | Count |
|-----------------------------|-------------------------------------------|-------|
| Gender                      | Male, Female, Non-binary                  | 3     |
| Race                        | White, Black, Hispanic, Asian             | 4     |
| Age                         | 24, 35, 48                                | 3     |
| **Total personas (3×4×3)**  |                                           | **36**|

36 doesn't sound bad. But then we multiply:

```
Step 1:  36 personas × 3 runs each (for consistency checks)     =  108 calls
Step 2:  ~50 name-based tests × 3 runs                          =  150 calls
Step 3:  36 personas × 3 context primes × 3 runs                =  324 calls
Step 4:  Stress-test mode (optional)                            =  ???

TOTAL:  ~580+ API calls
```

At a typical rate limit of **20 requests/minute**, that's **30 minutes of waiting** just for one audit. On a free-tier API key, it's worse. For a hackathon demo, this is a dealbreaker — nobody's sitting through 30 minutes of loading bars.

### Why It Gets Worse Fast

Every new attribute you add **multiplies** the total, it doesn't just add to it:

| Attributes                          | Full Factorial personas |
|-------------------------------------|------------------------|
| 3 gender × 4 race × 3 age          | 36                     |
| + 2 nationality values              | 72                     |
| + 3 religion values                 | 216                    |
| + 2 disability values               | 432                    |

This is exponential growth. It's the core problem.

---

## 2. The Three Fixes

### Fix 1: Tiered Test Modes (the UX fix)

**Idea**: Don't run everything every time. Give the user three clearly labelled options.

Think of it like virus scanning — you don't run a full system scan every time you download a file.

| Mode                | What it does                                                        | API Calls | Time     |
|---------------------|---------------------------------------------------------------------|-----------|----------|
| 🟢 **Quick Scan**   | Test one attribute at a time, 1 run each, no extras                | ~10-20    | ~1-2 min |
| 🟡 **Standard Audit**| Smart pairwise grid, 1-3 runs, top name variants                  | ~28-80    | ~2-8 min |
| 🔴 **Full Investigation** | Everything — full grid, all names, context primes, stress test | ~400-600  | ~30+ min |

**Why this works**: 90% of the time, a Quick Scan tells you whether there's a problem. If it finds something, you escalate. If it doesn't, you either stop there or run a Standard Audit to be sure. You almost never need Full Investigation except for compliance/legal documentation.

**How hard to build**: Easy. It's just a config flag that controls which generators run and how many repetitions to use. Maybe a day of work. No new algorithms needed.

> **Feasibility: ✅ Trivial.** This is just a UI switch controlling existing parameters.

---

### Fix 2: Pairwise Coverage Instead of Full Factorial (the math fix)

**Idea**: You don't need to test *every* combination to find bias. You just need to test *each attribute separately* against a neutral baseline.

#### The Analogy

Imagine you're testing whether a restaurant treats customers differently based on gender, race, and age.

**Full factorial approach** (what we have now): Send in every possible person — young Black women, old Asian men, middle-aged Hispanic non-binary people... That's 36 people for just 3 attributes.

**Pairwise approach** (the fix): Start with a "neutral" baseline person. Then change **one thing at a time**:
- Change only gender → 3 tests
- Change only race → 4 tests  
- Change only age → 3 tests
- **Total: 10 tests instead of 36**

#### The Math

```
Neutral baseline:  gender = unspecified, race = unspecified, age = 35

Test gender alone:  swap to Male / Female / Non-binary     → 3 variants
Test race alone:    swap to White / Black / Hispanic / Asian → 4 variants  
Test age alone:     swap to 24 / 35 / 48                    → 3 variants

Total: 10 personas (not 36)
```

The reduction gets **better** the more attributes you add:

| Attributes                  | Full Factorial | Pairwise | Savings |
|-----------------------------|---------------|----------|---------|
| 3 × 4 × 3                  | 36            | 10       | 72%     |
| 3 × 4 × 3 × 2              | 72            | 12       | 83%     |
| 3 × 4 × 3 × 2 × 3          | 216           | 15       | 93%     |

#### What You Lose

Pairwise **cannot detect intersectional bias** — where the combination of two attributes is worse than either alone (e.g., being a Black *woman* is treated worse than being Black or being a woman separately).

**But here's the key insight**: you don't need to detect intersectional bias upfront. If pairwise finds bias on gender AND race individually, *then* you escalate to a targeted intersectional test on just those two attributes (3 × 4 = 12 more tests). You only pay the cost when you have a reason to.

**How hard to build**: Easy. It's a different loop in the persona generator — `for each attribute, vary it alone` instead of `itertools.product(all_attributes)`. Maybe half a day.

> **Feasibility: ✅ Easy.** Replace one loop with another. The statistical analysis downstream doesn't change at all.

---

### Fix 3: Adaptive Sampling (the smart fix)

**Idea**: Don't always run 3-5 repetitions per persona. Run just 1, and only run more if the results are inconsistent.

#### The Analogy

If you flip a coin and get heads 3 times in a row, you don't need to flip it twice more to confirm it's landing on heads. But if you get heads, tails, heads — now you need more flips to know what's going on.

#### How It Works

```
For each persona:
1. Run the test ONCE
2. Was the answer clear and consistent?  → Done. Move on.  (saves 2 runs)
3. Was it ambiguous or borderline?       → Run again
4. Still inconsistent after 2 runs?      → Run up to 5 total to get a stable answer
```

In practice, most well-behaved agents give the same answer every time (especially at temperature=0). So the average goes from a fixed 3 runs per persona down to about **1.4 runs per persona**.

```python
# Simplified logic:
for persona in test_grid:
    results = []
    for attempt in range(1, 6):  # max 5 tries
        result = run_agent(persona)
        results.append(result)
        
        if attempt >= 1 and all_same(results):
            break  # consistent — stop early
        if attempt >= 3:
            break  # got enough for majority vote
    
    final_answer = majority_vote(results)
```

**How hard to build**: Moderate. The core logic is simple (shown above), but you need to integrate it into the async execution engine cleanly. About 1-2 days of work.

> **Feasibility: ✅ Moderate.** Simple algorithm, needs clean integration into the interrogation engine.

---

## 3. Combined Impact

Here's what happens when you stack all three fixes for a **Standard Audit**:

| Component                       | Before            | After              |
|---------------------------------|-------------------|--------------------|
| Persona grid (explicit)         | 36 personas       | 10 (pairwise)      |
| Runs per persona                | 3 (fixed)         | ~1.4 (adaptive)    |
| Explicit grid calls             | 108               | **14**             |
| Name-based variants             | 50 names × 3 runs | 10 names × 1.4     |
| Name-based calls                | 150               | **14**             |
| Context primes                  | Not in Standard   | Not in Standard    |
| **Total Standard Audit**        | **~260 calls**    | **~28 calls**      |
| **Time @ 20 req/min**           | **~13 min**       | **~2 min**         |

And for the **Quick Scan** (demo mode):

| Metric            | Value      |
|-------------------|------------|
| Total calls       | ~14        |
| Time              | ~45 sec    |
| What you get      | "Is there obvious bias? On which attribute?" |

**This is demo-able in a live presentation.** That's the whole point.

---

## 4. What Changes in the Spec?

Almost nothing in the core architecture needs to change. The five layers stay exactly the same. Here's what's different:

| Spec Component              | Change Needed                                                   |
|-----------------------------|-----------------------------------------------------------------|
| Layer 2 (Persona Generation)| Add pairwise mode alongside full factorial. Config flag.       |
| Layer 3 (Interrogation)     | Swap fixed `runs_per_persona=3` for adaptive sampler.          |
| New: Audit Mode selector    | Add a `AuditMode` enum (Quick / Standard / Full). Controls which generators run and how many reps. |
| Layer 4 (Statistics)        | No change. It processes whatever data it gets.                 |
| Layer 5 (Interpreter)       | No change. It reads the findings regardless of how many tests produced them. |

```python
class AuditMode(Enum):
    QUICK      = "quick"       # Pairwise grid, 1 run, no extras
    STANDARD   = "standard"    # Pairwise grid, adaptive runs, top names
    FULL       = "full"        # Full factorial, max runs, everything
```

---

## 5. Honest Trade-offs

| Trade-off                              | Risk Level | Mitigation                              |
|----------------------------------------|------------|----------------------------------------|
| Pairwise misses intersectional bias    | Medium     | Escalate to factorial if 2+ attributes flagged |
| Adaptive sampling may under-sample     | Low        | min_runs=1 with temperature=0 is usually deterministic |
| Quick Scan gives false negatives       | Medium     | Label it clearly — "screening, not a full audit" |
| User picks wrong mode                  | Low        | Default to Standard; Quick requires explicit opt-in |

---

## 6. Bottom Line

| Question                                    | Answer                              |
|---------------------------------------------|-------------------------------------|
| Is this feasible to build?                  | **Yes.** 2-3 days of implementation work max. |
| Does it require new algorithms?              | **No.** Pairwise and adaptive sampling are well-understood. |
| Does it change the architecture?             | **No.** Same 5 layers. Just controls on how much data Layer 2 generates. |
| Does it weaken the audit quality?            | **Barely.** Standard Audit catches 95%+ of what Full does, in 1/10th the time. |
| Is it good enough for a hackathon demo?      | **Yes.** Quick Scan runs in ~45 seconds live. |
| Is it good enough for production?            | **Yes.** Full Investigation mode is still there when you need legal-grade evidence. |

> [!TIP]
> **Recommended default for the hackathon**: Set Standard Audit as the default, with Quick Scan available as a "fast preview" button. Don't even expose Full Investigation in the MVP UI — it's a power-user feature for later.
