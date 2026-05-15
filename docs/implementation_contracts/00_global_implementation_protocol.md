# KshetraAI — Global Implementation Protocol (V1)

---

# 1. Objective

The purpose of this document is to define the global engineering rules that every implementation session inside KshetraAI must follow.

This protocol acts as:

```text
The master engineering behavior policy
for all AI-assisted development.
```

It ensures:

- architectural consistency
- deterministic implementation
- controlled code generation
- modular engineering discipline
- stable long-term scalability

---

# 2. Core Engineering Philosophy

KshetraAI is an:

```text
Explainable operational intelligence platform.
```

Therefore the implementation must prioritize:

- correctness
- explainability
- modularity
- maintainability
- operational realism

over:

- unnecessary abstraction
- premature optimization
- flashy complexity
- uncontrolled experimentation

---

# 3. Global Development Principles

The system must always remain:

| Principle | Meaning |
|---|---|
| Modular | Components remain isolated |
| Explainable | Reasoning remains traceable |
| Deterministic | Logic remains predictable |
| Extensible | Future expansion remains possible |
| Stable | Architecture remains consistent |
| Human-Governed | AI does not own architecture |

---

# 4. AI Role Definition

The AI assistant acts as:

```text
A constrained implementation accelerator.
```

The AI assistant is NOT:

- the system architect
- the business owner
- the intelligence designer
- the schema owner
- the infrastructure authority

---

# 5. Human Ownership Areas

The human developer retains ownership of:

- architecture
- business logic
- scoring philosophy
- intelligence design
- implementation sequencing
- system boundaries
- final code review

---

# 6. Architecture Preservation Rule

The AI MUST NOT:

- redesign architecture
- introduce hidden abstractions
- restructure unrelated modules
- invent new system layers
- silently change schemas
- merge unrelated responsibilities

If ambiguity exists:

```text
Preserve existing architecture.
```

DO NOT improvise.

---

# 7. Scope Restriction Rule

Every coding session must be:

```text
strictly localized.
```

Correct:

```text
Implement weighted scoring logic
inside priority_engine.py.
```

Incorrect:

```text
Build the prioritization system.
```

---

# 8. Single Responsibility Principle

Each module should do:

```text
One clear operational responsibility.
```

Example:

| Module | Responsibility |
|---|---|
| priority_engine.py | score ranking |
| anomaly_engine.py | anomaly detection |
| explanation_engine.py | reasoning generation |
| feedback_processor.py | outcome handling |

Avoid:

- mixed responsibilities
- cross-module business logic
- hidden coupling

---

# 9. Dependency Discipline

Modules should only depend on:

- explicitly allowed layers
- approved utilities
- defined schemas
- approved feature pipelines

Forbidden:

- circular dependencies
- frontend/backend cross leakage
- direct cross-engine coupling

---

# 10. File Ownership Rule

Implementation contracts define:

```text
Which files may be modified.
```

The AI MUST NOT modify files outside allowed ownership boundaries.

Example:

Allowed:

```text
backend/engines/priority_engine.py
```

Forbidden:

```text
frontend/
database schemas/
other engines/
```

unless explicitly requested.

---

# 11. Schema Stability Rule

Schemas are considered:

```text
Architecture-level assets.
```

The AI MUST NOT:

- rename columns
- change table structures
- alter API contracts
- modify response formats

unless explicitly instructed.

---

# 12. Explainability Preservation Rule

Every intelligence component must preserve:

- traceability
- evidence mapping
- interpretable outputs
- reasoning visibility

Avoid:

- opaque scoring
- hidden heuristics
- unexplained confidence

---

# 13. Rule-Based First Principle

The system initially prioritizes:

```text
Rule-based explainable intelligence.
```

NOT:

```text
Uncontrolled black-box ML systems.
```

Reason:

- easier debugging
- operational clarity
- easier demos
- safer iteration
- stronger explainability

---

# 14. Incremental Intelligence Evolution

Implementation evolution should follow:

```text
Rule-based
    ↓
Data-assisted
    ↓
Adaptive
    ↓
ML-enhanced
```

NOT immediate overengineering.

---

# 15. Logging & Traceability Rule

All important intelligence outputs should be loggable.

Examples:

- feature scores
- priority scores
- triggered rules
- anomaly reasons
- recommendation outputs
- confidence levels

This supports:

- explainability
- debugging
- evaluation
- future learning

---

# 16. Avoid Premature Complexity

The AI MUST avoid introducing:

- microservices
- distributed systems
- event buses
- orchestration frameworks
- heavy infrastructure
- unnecessary async layers

unless explicitly required.

Prototype-first engineering is preferred.

---

# 17. Technology Discipline

Preferred stack:

---

## Backend

```text
Python + FastAPI
```

---

## Data Processing

```text
Pandas
NumPy
```

---

## Storage

```text
SQLite / PostgreSQL
```

---

## Frontend

```text
React / Next.js
```

---

## Explainability

```text
Template-based structured reasoning
```

---

# 18. Frontend Philosophy

The frontend should prioritize:

- operational clarity
- information hierarchy
- explainability visibility
- workflow simplicity

NOT:

- animation-heavy UI
- dashboard clutter
- visual overload

---

# 19. Backend Philosophy

Backend modules should remain:

- lightweight
- composable
- testable
- isolated
- deterministic

Avoid:

- giant service files
- hidden business logic
- deeply nested abstractions

---

# 20. Prompting Discipline

Every coding session prompt should include:

| Element | Purpose |
|---|---|
| Architecture docs | business logic reference |
| Implementation contract | boundary control |
| Scoped task | localized implementation |
| Constraints | anti-drift control |

---

# 21. Code Generation Rules

Generated code should be:

- readable
- modular
- typed where useful
- minimally abstracted
- operationally clear

Avoid:

- excessive design patterns
- unnecessary inheritance
- generic frameworks
- hidden utility layers

---

# 22. Naming Convention Rules

Names should remain:

- explicit
- domain-aligned
- operationally meaningful

Preferred:

```python
priority_score
weather_risk_score
stockout_risk_score
```

Avoid:

```python
x
temp1
processor2
manager_engine_v3
```

---

# 23. Error Handling Philosophy

Prefer:

```text
Explicit operational errors.
```

Example:

```text
Missing weather signal for entity_id=ENT001
```

Avoid silent failures.

---

# 24. Testing Philosophy

Testing should validate:

- scoring correctness
- rule triggering
- output schemas
- API stability
- explanation consistency

Avoid:

- excessive test scaffolding early
- premature coverage obsession

---

# 25. Git & Versioning Discipline

Recommended workflow:

```text
small commits
component-wise commits
feature-isolated branches
```

Avoid:

```text
massive mixed commits
```

---

# 26. Documentation Rule

Every major component should preserve:

- implementation notes
- assumptions
- scoring logic
- rule references
- API behavior

Documentation is considered:

```text
part of the architecture.
```

---

# 27. Review Rule

Every generated implementation should be reviewed against:

- architecture docs
- implementation contracts
- schema consistency
- explainability preservation
- modularity principles

---

# 28. Anti-Drift Checklist

Before accepting generated code, verify:

| Question | Check |
|---|---|
| Did architecture change accidentally? | Yes/No |
| Were unrelated files modified? | Yes/No |
| Did schemas change? | Yes/No |
| Is explainability preserved? | Yes/No |
| Is scope respected? | Yes/No |
| Is logic deterministic? | Yes/No |

---

# 29. Prototype-First Rule

The immediate goal is:

```text
A strong explainable working prototype.
```

NOT:

```text
A perfect enterprise platform.
```

---

# 30. Final Engineering Goal

The final system should demonstrate:

```text
How agricultural field-force operations
can become adaptive, explainable,
signal-driven, and operationally intelligent.
```

---

# 31. Final One-Line Definition

```text
A master engineering governance protocol
for building KshetraAI through controlled,
modular, explainable, and architecture-preserving AI-assisted development.
```