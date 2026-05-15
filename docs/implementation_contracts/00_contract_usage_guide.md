# KshetraAI — Contract Usage Guide (V1)

---

# 1. Objective

The purpose of this document is to define:

```text
How implementation contracts should be used
while developing KshetraAI using AI-assisted engineering workflows.
```

This guide establishes the operational protocol that ensures:

- architectural consistency
- controlled implementation
- scoped engineering
- minimal AI drift
- stable modular development
- predictable code generation

---

# 2. Core Philosophy

KshetraAI is a large multi-component system.

If AI coding agents are allowed to generate code without strict constraints, the project may suffer from:

- architectural drift
- random abstractions
- uncontrolled schema changes
- duplicated logic
- hidden coupling
- inconsistent APIs
- unstable implementations

Therefore:

```text
AI should not own the architecture.
AI should implement within controlled boundaries.
```

---

# 3. Purpose of Implementation Contracts

Implementation contracts exist to:

- define module boundaries
- constrain AI behavior
- clarify responsibilities
- stabilize engineering workflows
- reduce implementation ambiguity
- preserve architectural discipline

Each contract acts as:

```text
A localized engineering agreement
between the architecture and the implementation.
```

---

# 4. Project Documentation Hierarchy

The project follows a strict hierarchy of authority.

---

# Level 1 — Architecture Documents

Location:

```text
/docs/architecture/
```

Purpose:

Defines:

- business logic
- system philosophy
- intelligence flow
- scoring systems
- operational reasoning
- infrastructure design

These documents are considered:

```text
Architectural truth.
```

AI agents MUST NOT contradict these documents.

---

# Level 2 — Implementation Contracts

Location:

```text
/docs/implementation_contracts/
```

Purpose:

Defines:

- implementation boundaries
- module responsibilities
- allowed dependencies
- forbidden actions
- input/output expectations
- file ownership

These documents are considered:

```text
Implementation governance.
```

AI agents MUST follow them strictly.

---

# Level 3 — Prompt Instructions

Location:

```text
/docs/prompts/
```

Purpose:

Defines:

- coding workflow
- development discipline
- session constraints
- task scope

These prompts act as:

```text
Operational execution control.
```

---

# 5. Relationship Between Documents

The relationship is:

```text
Architecture Docs
        ↓
Implementation Contracts
        ↓
Coding Prompt
        ↓
Localized Engineering Task
```

---

# 6. How AI-Assisted Development Should Work

Every implementation session should follow this process:

---

# Step 1 — Select Component

Example:

```text
Dynamic Prioritization Engine
```

---

# Step 2 — Attach Relevant Architecture Docs

Example:

```text
01_dynamic_prioritization_engine.md
08_data_schema.md
09_development_plan.md
```

These provide:

- business logic
- feature definitions
- scoring philosophy
- data structures

---

# Step 3 — Attach Relevant Implementation Contract

Example:

```text
04_priority_engine_contract.md
```

This defines:

- module boundaries
- allowed files
- responsibilities
- forbidden behavior

---

# Step 4 — Use Controlled Prompt

Example:

```text
Implement ONLY the weighted scoring logic
inside backend/engines/priority_engine.py.

Do not modify unrelated files.
Do not invent new architecture.
Follow the implementation contract strictly.
```

---

# Step 5 — Review Generated Code

Validate:

- architectural consistency
- module boundaries
- dependency correctness
- explainability preservation
- schema consistency

---

# 7. Implementation Contracts Structure

Every contract should contain:

| Section | Purpose |
|---|---|
| Objective | What this module does |
| Responsibilities | Allowed behavior |
| Non-Responsibilities | Forbidden behavior |
| Inputs | Expected input schema |
| Outputs | Expected output schema |
| Dependencies | Allowed modules/files |
| Forbidden Dependencies | Restricted modules/files |
| File Ownership | Which files may be modified |
| Rules | Architectural constraints |
| Example I/O | Sample workflow |
| Implementation Notes | Additional guidance |

---

# 8. Example Contract Philosophy

Example:

## Priority Engine

Allowed:

- weighted scoring
- ranking logic
- priority classification

Not allowed:

- anomaly detection
- recommendation generation
- explanation generation
- schema modification

This ensures:

```text
Single-responsibility implementation.
```

---

# 9. Why Contracts Are Critical

Without contracts:

```text
AI agents tend to improvise architecture.
```

Common problems:

- random helper layers
- duplicate business logic
- inconsistent naming
- hidden coupling
- API drift
- uncontrolled abstractions

Contracts prevent this.

---

# 10. Golden Rule

The AI should NEVER:

- redesign the architecture
- invent missing business logic
- modify unrelated modules
- introduce uncontrolled abstractions
- silently change schemas
- merge responsibilities across components

The AI should ALWAYS:

- remain scoped
- preserve architecture
- respect module boundaries
- follow contracts strictly
- implement deterministically

---

# 11. Scope Discipline

The most important rule:

```text
Never ask the AI to build the entire system at once.
```

Always use:

```text
Localized implementation tasks.
```

Correct example:

```text
Implement only the feature normalization logic
inside agronomic_features.py.
```

Incorrect example:

```text
Build the intelligence engine.
```

---

# 12. File Ownership Principle

Each contract must define:

```text
Which files the AI is allowed to modify.
```

Example:

```text
Allowed:
backend/engines/priority_engine.py

Forbidden:
frontend/
anomaly/
database schemas/
```

This dramatically reduces accidental drift.

---

# 13. Dependency Discipline

Contracts should define:

## Allowed Dependencies

Example:

```text
features/
config/
utils/
```

## Forbidden Dependencies

Example:

```text
frontend/
anomaly_engine/
explainability_engine/
```

This preserves clean architecture.

---

# 14. Architecture Freeze Principle

Once architecture documents are finalized:

```text
Architecture should not evolve accidentally during coding.
```

Architecture changes must be:

- explicit
- intentional
- documented
- reviewed

Implementation sessions should NOT silently modify architecture.

---

# 15. Controlled LLM Role

The LLM should act as:

```text
A constrained implementation accelerator.
```

NOT as:

```text
An autonomous software architect.
```

The human developer retains ownership of:

- architecture
- business logic
- intelligence philosophy
- system boundaries
- implementation sequencing

---

# 16. Recommended Session Workflow

Recommended workflow for every coding session:

```text
1. Identify target component
2. Open related architecture docs
3. Open related implementation contract
4. Provide scoped task prompt
5. Generate localized implementation
6. Review code against contract
7. Commit changes incrementally
```

---

# 17. Incremental Development Principle

The system should evolve through:

```text
Small validated implementation steps.
```

NOT:

```text
Large uncontrolled generation bursts.
```

Preferred approach:

```text
dataset
→ features
→ scoring
→ recommendation
→ anomaly
→ explainability
→ feedback
→ APIs
→ frontend
```

---

# 18. Recommended Prompting Strategy

Each coding prompt should contain:

---

## Context

Which component is being implemented.

---

## Attached References

Which architecture docs and contracts are relevant.

---

## Scope Restriction

Exactly what should be implemented.

---

## Constraints

What must NOT be modified.

---

## Expected Output

Code only, explanation only, tests only, etc.

---

# 19. Recommended Prompt Template

```text
You are implementing a scoped module inside KshetraAI.

Follow the attached implementation contract strictly.

Relevant architecture documents:
- [list]

Relevant implementation contract:
- [contract]

Task:
- [specific task]

Constraints:
- Do not modify unrelated files
- Do not invent new architecture
- Preserve existing schemas
- Keep implementation deterministic
- Preserve explainability
```

---

# 20. Engineering Goal

The purpose of this workflow is to create:

```text
Predictable, modular, explainable,
and architecturally stable AI-assisted development.
```

---

# 21. Final One-Line Definition

```text
A governance framework for controlled AI-assisted engineering
that preserves architectural integrity
through scoped implementation contracts and disciplined workflows.
```