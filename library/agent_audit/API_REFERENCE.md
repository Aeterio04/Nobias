# Agent Audit - API Reference

## Quick Links

- [Level 1: One-Liner API](#level-1-one-liner-api)
- [Level 2: Class-Based API](#level-2-class-based-api)
- [Level 3: Expert API](#level-3-expert-api)
- [Configuration](#configuration)
- [Models](#models)

---

## Level 1: One-Liner API

### `audit_agent()`

The simplest way to audit an agent - one async function call.

```python
async def audit_agent(
    system_prompt: str,
    seed_case: str,
    api_key: str,
    mode: str = "standard",
    model: str = "llama-3.1-70b-versatile",
    attributes: list[str] | None = None,
    domain: str = "general",
    positive_outcome: str = "approved",
    negative_outcome: str = "rejected",
    output_type: str = "binary",
    rate_limit_rps: int = 10,
    enable_stress_test: bool = False,
    progress_callback: Callable[[str, int, int], None] | None = None,
) -> AgentAuditReport
```

**Parameters:**
- `system_prompt`: The agent's system prompt
- `seed_case`: Template input (e.g., "Evaluate: Name: Alex...")
- `api_key`: API key for LLM backend (Groq, OpenAI)
- `mode`: Audit depth - `"quick"` | `"standard"` | `"full"`
- `model`: Model name (auto-detects backend)
- `attributes`: Protected attributes to test (default: `["gender", "race", "age"]`)
- `domain`: Decision domain (e.g., `"hiring"`, `"lending"`)
- `positive_outcome`: Positive decision string (e.g., `"hired"`)
- `negative_outcome`: Negative decision string (e.g., `"rejected"`)
- `output_type`: `"binary"` | `"numeric_score"` | `"free_text"` | `"chain_of_thought"`
- `rate_limit_rps`: Requests per second limit
- `enable_stress_test`: Run adaptive stress test
- `progress_callback`: Optional `callback(stage, current, total)`

**Returns:** `AgentAuditReport`

**Example:**
```python
from agent_audit import audit_agent

report = await audit_agent(
    system_prompt="You are a hiring assistant...",
    seed_case="Evaluate: Name: Alex, Experience: 5 years",
    api_key="gsk_...",
)

print(f"Severity: {report.overall_severity}")
print(f"CFR: {report.overall_cfr:.1%}")
```

---

## Level 2: Class-Based API

### `AgentAuditor`

Reusable auditor instance with before/after comparison.

#### Factory Methods

##### `AgentAuditor.from_prompt()`

Create auditor from a system prompt (development mode).

```python
@classmethod
def from_prompt(
    cls,
    system_prompt: str,
    api_key: str,
    mode: str = "standard",
    model: str = "llama-3.1-70b-versatile",
    attributes: list[str] | None = None,
    domain: str = "general",
    **kwargs,
) -> AgentAuditor
```

**Example:**
```python
from agent_audit import AgentAuditor

auditor = AgentAuditor.from_prompt(
    system_prompt="You are a hiring assistant...",
    api_key="gsk_...",
    mode="standard",
)

report = await auditor.run(seed_case="...")
```

##### `AgentAuditor.from_api()`

Create auditor for a deployed API endpoint (production mode).

```python
@classmethod
def from_api(
    cls,
    endpoint_url: str,
    auth_header: dict,
    request_template: dict,
    response_path: str = "$.result",
    mode: str = "standard",
    attributes: list[str] | None = None,
    domain: str = "general",
    **kwargs,
) -> AgentAuditor
```

**Example:**
```python
auditor = AgentAuditor.from_api(
    endpoint_url="https://api.yourcompany.com/agent",
    auth_header={"Authorization": "Bearer TOKEN"},
    request_template={"input": "{input}"},
    response_path="$.result.decision",
)

report = await auditor.run(seed_case="...")
```

##### `AgentAuditor.from_logs()`

Create auditor from historical logs (privacy-friendly mode).

```python
@classmethod
def from_logs(
    cls,
    log_file: str | Path,
    input_field: str = "input",
    output_field: str = "output",
    mode: str = "standard",
    attributes: list[str] | None = None,
    domain: str = "general",
    **kwargs,
) -> AgentAuditor
```

**Example:**
```python
auditor = AgentAuditor.from_logs(
    log_file="interactions.jsonl",
    input_field="input",
    output_field="output",
)

report = await auditor.run(seed_case="...")
```

#### Instance Methods

##### `run()`

Execute the full audit pipeline.

```python
async def run(
    self,
    seed_case: str,
    system_prompt: str | None = None,
    progress_callback: Callable[[str, int, int], None] | None = None,
) -> AgentAuditReport
```

##### `update_prompt()`

Update the system prompt (for before/after comparison).

```python
def update_prompt(self, new_prompt: str) -> None
```

Only works in system-prompt mode.

##### `compare()`

Compare two audit reports.

```python
@staticmethod
def compare(
    before: AgentAuditReport,
    after: AgentAuditReport,
) -> dict
```

**Returns:** Dict with:
- `comparisons`: Per-finding comparisons
- `total_findings_before/after`: Count of findings
- `resolved`: Number of resolved findings
- `improved/worsened/unchanged`: Change counts
- `overall_cfr_change`: CFR improvement

**Example:**
```python
# Before
report_before = await auditor.run(seed_case="...")

# Update prompt
auditor.update_prompt("Improved prompt...")

# After
report_after = await auditor.run(seed_case="...")

# Compare
comparison = auditor.compare(report_before, report_after)
print(f"CFR improved by {comparison['overall_cfr_change']:.1%}")
```

---

## Level 3: Expert API

Direct access to all layers for full control.

### Layer 1: Context Collection

```python
from agent_audit import (
    build_agent_connector,
    validate_config,
    validate_seed_case,
    AgentConnectionMode,
    PromptAgentConfig,
)

config = PromptAgentConfig(
    system_prompt="...",
    model_backend="llama-3.1-70b-versatile",
    api_key="gsk_...",
)

connector = build_agent_connector(
    AgentConnectionMode.SYSTEM_PROMPT,
    config
)

response = await connector.call("Test input")
```

### Layer 2: Persona Generation

```python
from agent_audit import (
    generate_pairwise_grid,
    generate_factorial_grid,
    generate_name_variants,
    generate_context_variants,
)

# Pairwise grid (default)
personas = generate_pairwise_grid(
    seed_case="...",
    attributes=["gender", "race", "age"],
    domain="hiring",
)

# Factorial grid (full mode)
personas = generate_factorial_grid(
    seed_case="...",
    attributes=["gender", "race"],
)

# Name-based variants
name_personas = generate_name_variants(
    seed_case="...",
    mode="standard",
)

# Context primes
enriched = generate_context_variants(personas, mode="full")
```

### Layer 3: Interrogation

```python
from agent_audit.interrogation import InterrogationEngine

engine = InterrogationEngine(
    config=audit_config,
    agent_caller=connector.call,
)

completed = await engine.run_all(personas)
```

### Layer 4: Statistics

```python
from agent_audit.statistics import (
    compute_all_cfr,
    compute_per_attribute_masd,
    compute_all_parity,
    intersectional_scan,
)

# Build DataFrame from results
df = build_results_dataframe(completed)

# Compute metrics
cfr_results = compute_all_cfr(df, attributes)
masd_results = compute_per_attribute_masd(df, "gender")
parity_results = compute_all_parity(df, attributes)
intersectional = intersectional_scan(df, attributes)
```

### Layer 5: Interpretation

```python
from agent_audit.interpreter import Interpreter

interpreter = Interpreter(
    backend=InterpreterBackend.CLOUD,
    api_key="gsk_...",
)

interpretation, suggestions = await interpreter.interpret(
    findings,
    context,
    system_prompt,
)
```

---

## Configuration

### `AuditMode`

```python
class AuditMode(Enum):
    QUICK = "quick"        # ~14 API calls
    STANDARD = "standard"  # ~28 API calls
    FULL = "full"          # ~400-600 API calls
```

### `AgentConnectionMode`

```python
class AgentConnectionMode(Enum):
    SYSTEM_PROMPT = "prompt"  # Development mode
    API_ENDPOINT = "api"      # Production mode
    LOG_REPLAY = "replay"     # Privacy mode
```

---

## Models

### `AgentAuditReport`

```python
@dataclass
class AgentAuditReport:
    audit_id: str
    mode: str
    total_calls: int
    duration_seconds: float
    overall_severity: str  # "CRITICAL" | "MODERATE" | "LOW" | "CLEAR"
    overall_cfr: float
    benchmark_range: tuple[float, float]
    
    findings: list[AgentFinding]
    persona_results: list[PersonaResult]
    interpretation: Interpretation
    prompt_suggestions: list[PromptSuggestion]
    stress_test_results: StressTestReport | None
    caffe_test_suite: list[dict]
    timestamp: str
```

### `AgentFinding`

```python
@dataclass
class AgentFinding:
    finding_id: str
    attribute: str
    comparison: str
    metric: str  # "cfr" | "masd" | "demographic_parity" | "intersectional"
    value: float
    p_value: float
    severity: str  # "CRITICAL" | "MODERATE" | "LOW" | "CLEAR"
    benchmark_context: str
    details: dict
```

---

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

Backend is auto-detected from model name.

---

## Error Handling

```python
try:
    report = await audit_agent(...)
except ValueError as e:
    # Configuration error
    print(f"Config error: {e}")
except RuntimeError as e:
    # API error
    print(f"API error: {e}")
except Exception as e:
    # Unexpected error
    print(f"Error: {e}")
```

---

## See Also

- [Quick Start Guide](QUICKSTART.md)
- [Library Design](LIBRARY_DESIGN.md)
- [Examples](../examples/)
- [Development Logs](../docs/logs.md)
