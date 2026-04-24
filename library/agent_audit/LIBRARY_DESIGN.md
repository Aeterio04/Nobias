# Agent Audit Library - API Design

## Design Philosophy

The library should be **easy to start, powerful when needed**:

1. **Simple by default**: One function call for basic use
2. **Configurable when needed**: Class-based API for control
3. **Composable for experts**: Direct access to all layers

---

## Three-Level API

### Level 1: One-Liner Function (90% of users)

```python
from agent_audit import audit_agent

# Simplest possible usage
report = await audit_agent(
    system_prompt="You are a hiring assistant...",
    seed_case="Evaluate: Name: Alex...",
    api_key="gsk_...",
)

# With options
report = await audit_agent(
    system_prompt="...",
    seed_case="...",
    api_key="gsk_...",
    mode="standard",  # quick | standard | full
    model="llama-3.1-70b-versatile",
    attributes=["gender", "race", "age"],
    domain="hiring",
)
```

**Implementation:** Single async function that:
1. Builds config from kwargs
2. Creates AgentAuditor instance
3. Calls run()
4. Returns report

---

### Level 2: Class-Based API (Power Users)

```python
from agent_audit import AgentAuditor

# Create auditor with factory methods
auditor = AgentAuditor.from_prompt(
    system_prompt="...",
    api_key="gsk_...",
    mode="standard",
)

# Or from API endpoint
auditor = AgentAuditor.from_api(
    endpoint_url="https://...",
    auth_header={"Authorization": "..."},
)

# Or from logs
auditor = AgentAuditor.from_logs(
    log_file="interactions.jsonl",
)

# Run the audit
report = await auditor.run(
    seed_case="...",
    attributes=["gender", "race"],
)

# Re-run with different seed
report2 = await auditor.run(seed_case="...")

# Compare before/after
auditor.update_prompt("New improved prompt...")
report_after = await auditor.run(seed_case="...")
comparison = auditor.compare(report, report_after)
```

**Benefits:**
- Reusable auditor instance
- Easy before/after comparison
- Progress callbacks
- Caching between runs

---

### Level 3: Manual Pipeline (Experts)

```python
from agent_audit.context import build_agent_connector
from agent_audit.personas import generate_pairwise_grid
from agent_audit.interrogation import InterrogationEngine
from agent_audit.statistics import compute_all_statistics
from agent_audit.interpreter import Interpreter
from agent_audit.report import build_report

# Layer 1: Build connector
connector = build_agent_connector(mode, config)

# Layer 2: Generate personas
personas = generate_pairwise_grid(seed_case, attributes)

# Layer 3: Interrogate
engine = InterrogationEngine(config, connector.call)
results = await engine.run_all(personas)

# Layer 4: Statistics
findings = compute_all_statistics(results, attributes)

# Layer 5: Interpret
interpreter = Interpreter()
interpretation = await interpreter.interpret(findings)

# Build report
report = build_report(findings, interpretation)
```

**Benefits:**
- Full control over each step
- Custom persona generation
- Custom statistics
- Integration with other tools

---

## File Structure

```
library/agent_audit/
├── __init__.py                    # Public API exports
├── api.py                         # NEW - Level 1 & 2 implementations
├── orchestrator.py                # NEW - Pipeline coordination
├── config.py                      # Existing
├── models.py                      # Existing
└── [all other modules...]         # Existing
```

---

## Implementation Plan

### 1. Create `orchestrator.py`
The core pipeline logic that all APIs use:

```python
class PipelineOrchestrator:
    """Internal pipeline coordinator - not exposed to users."""
    
    async def run_pipeline(
        self,
        connector: AgentConnector,
        seed_case: str,
        config: AgentAuditConfig,
    ) -> AgentAuditReport:
        # Layer 2: Generate personas
        # Layer 3: Interrogate
        # Layer 4: Statistics
        # Layer 5: Interpret
        # Return report
```

### 2. Create `api.py`
User-facing APIs that wrap the orchestrator:

```python
# Level 1: One-liner
async def audit_agent(...) -> AgentAuditReport:
    config = _build_config_from_kwargs(...)
    auditor = AgentAuditor(config)
    return await auditor.run(seed_case)

# Level 2: Class-based
class AgentAuditor:
    @classmethod
    def from_prompt(cls, ...) -> AgentAuditor:
        ...
    
    @classmethod
    def from_api(cls, ...) -> AgentAuditor:
        ...
    
    @classmethod
    def from_logs(cls, ...) -> AgentAuditor:
        ...
    
    async def run(self, seed_case: str) -> AgentAuditReport:
        # Use PipelineOrchestrator
        ...
    
    def compare(self, before, after) -> dict:
        ...
```

### 3. Update `__init__.py`
Export the right things:

```python
# Level 1 API
from agent_audit.api import audit_agent

# Level 2 API
from agent_audit.api import AgentAuditor

# Level 3 API (for experts)
from agent_audit.context import build_agent_connector
from agent_audit.personas import (
    generate_pairwise_grid,
    generate_factorial_grid,
    generate_name_variants,
)
# ... etc

# Config classes (for all levels)
from agent_audit.config import (
    AgentAuditConfig,
    AuditMode,
    # ...
)

# Report utilities
from agent_audit.report import compare_audits
```

---

## Usage Examples

### Example 1: Quick Test
```python
import asyncio
from agent_audit import audit_agent

async def main():
    report = await audit_agent(
        system_prompt="You are a hiring assistant...",
        seed_case="Evaluate: Name: Alex, Experience: 5 years",
        api_key="gsk_...",
    )
    print(report.overall_severity)
    print(report.overall_cfr)

asyncio.run(main())
```

### Example 2: Before/After Comparison
```python
from agent_audit import AgentAuditor

auditor = AgentAuditor.from_prompt(
    system_prompt="Original prompt...",
    api_key="gsk_...",
)

# Before
report_before = await auditor.run(seed_case="...")

# Update prompt
auditor.update_prompt("Improved prompt with fairness instructions...")

# After
report_after = await auditor.run(seed_case="...")

# Compare
comparison = auditor.compare(report_before, report_after)
print(f"CFR improved by {comparison['overall_cfr_change']:.1%}")
```

### Example 3: Custom Pipeline
```python
from agent_audit.context import build_agent_connector
from agent_audit.personas import generate_factorial_grid
from agent_audit.interrogation import InterrogationEngine

# Build custom persona grid
personas = generate_factorial_grid(
    seed_case="...",
    attributes=["gender", "race", "age", "disability"],
)

# Add custom personas
personas.append(my_custom_persona)

# Run interrogation
connector = build_agent_connector(...)
engine = InterrogationEngine(config, connector.call)
results = await engine.run_all(personas)

# Custom analysis
for result in results:
    print(f"{result.attributes} → {result.decision}")
```

---

## Benefits of This Design

1. **Progressive Disclosure**: Users see complexity only when they need it
2. **Consistent**: All levels use the same underlying pipeline
3. **Testable**: Each level can be tested independently
4. **Documented**: Clear examples for each level
5. **Flexible**: Experts can bypass high-level APIs

---

## Migration Path

Current users of the scaffolding can:
1. Start with Level 1 for quick tests
2. Move to Level 2 when they need control
3. Drop to Level 3 for custom workflows

No breaking changes - just additions!
