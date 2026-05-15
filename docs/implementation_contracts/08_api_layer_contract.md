# KshetraAI — API Layer Contract (V1)

---

# 1. Objective

The purpose of this contract is to define the implementation boundaries, responsibilities, and engineering rules for the API Layer.

The API Layer is responsible for:

```text
Exposing KshetraAI intelligence capabilities
through stable, structured,
and controlled backend interfaces.
```

This layer acts as the bridge between:

```text
Frontend / External Consumers
        ↓
Core Intelligence Engines
```

---

# 2. Module Identity

| Property | Value |
|---|---|
| Module Name | API Layer |
| Layer | Backend Interface Layer |
| Primary Responsibility | Expose intelligence APIs |
| Upstream Dependencies | All Intelligence Engines |
| Downstream Consumers | Frontend Dashboard, Mobile App |
| Architecture Criticality | High |

---

# 3. Core Philosophy

The API Layer should remain:

- thin
- modular
- stable
- deterministic
- schema-driven
- orchestration-focused

The API Layer should NOT:

- contain business logic
- contain scoring logic
- contain anomaly logic
- contain recommendation logic
- contain explainability generation

Its responsibility is ONLY:

```text
Coordinate and expose backend capabilities.
```

---

# 4. Responsibilities

The API Layer IS responsible for:

- exposing REST endpoints
- request validation
- response formatting
- orchestrating engine calls
- dependency coordination
- structured API responses
- API-level error handling

---

# 5. Non-Responsibilities

The API Layer is NOT responsible for:

- weighted scoring
- anomaly detection
- recommendation generation
- feature engineering
- business rule inference
- frontend rendering
- recalibration logic

These belong to backend intelligence modules.

---

# 6. API Architecture Philosophy

The API Layer should act as:

```text
An orchestration and transport layer.
```

NOT:

```text
A business intelligence layer.
```

---

# 7. Core API Categories

| API Group | Purpose |
|---|---|
| Planning APIs | Daily prioritization |
| Recommendation APIs | Next best actions |
| Alert APIs | Anomaly retrieval |
| Explainability APIs | Operational reasoning |
| Outcome APIs | Feedback submission |
| Health APIs | Service monitoring |

---

# 8. Expected Upstream Dependencies

The API Layer interacts with:

- Feature Builder
- Priority Engine
- Contextual Decision Engine
- Anomaly Detection Engine
- Explainability Engine
- Outcome Learning Engine

---

# 9. Expected Downstream Consumers

Consumers may include:

- React dashboard
- Mobile application
- Admin dashboard
- Future integrations

---

# 10. Recommended API Structure

```text
backend/api/

├── routes/
├── schemas/
├── services/
├── dependencies/
├── middleware/
└── main.py
```

---

# 11. Recommended Route Structure

```text
backend/api/routes/

├── planning_routes.py
├── recommendation_routes.py
├── anomaly_routes.py
├── explainability_routes.py
├── outcome_routes.py
└── health_routes.py
```

---

# 12. Recommended Schema Structure

```text
backend/api/schemas/

├── planning_schema.py
├── recommendation_schema.py
├── anomaly_schema.py
├── explainability_schema.py
└── outcome_schema.py
```

---

# 13. Primary API Endpoints

Suggested V1 endpoints:

| Endpoint | Purpose |
|---|---|
| /get-daily-plan | Ranked visit plan |
| /get-recommendation | Next best action |
| /get-alerts | Active anomalies |
| /get-explanation | Operational reasoning |
| /submit-outcome | Outcome logging |
| /health | Service health |

---

# 14. Daily Plan API

# Purpose

Return prioritized visit list.

---

# Example Request

```json
{
  "rep_id": "REP001",
  "territory_id": "TERR001"
}
```

---

# Example Response

```json
{
  "ranked_entities": [
    {
      "entity_id": "ENT001",
      "priority_score": 83.7,
      "priority_level": "Critical"
    }
  ]
}
```

---

# 15. Recommendation API

# Purpose

Return contextual next best actions.

---

# Example Request

```json
{
  "entity_id": "ENT001"
}
```

---

# Example Response

```json
{
  "recommended_actions": [
    "Inspect crop symptoms",
    "Discuss fungicide advisory"
  ],

  "confidence_level": "High"
}
```

---

# 16. Alert API

# Purpose

Return anomaly alerts.

---

# Example Response

```json
{
  "alerts": [
    {
      "anomaly_type": "Stock-Out Risk",
      "severity_level": "Critical"
    }
  ]
}
```

---

# 17. Explainability API

# Purpose

Return operational reasoning.

---

# Example Response

```json
{
  "explanation": "High rainfall and humidity increase fungal disease risk."
}
```

---

# 18. Outcome API

# Purpose

Capture field outcomes.

---

# Example Request

```json
{
  "recommendation_id": "REC001",
  "sale_made": true,
  "order_placed": true
}
```

---

# Example Response

```json
{
  "status": "success"
}
```

---

# 19. Allowed File Ownership

The AI MAY modify:

```text
backend/api/
backend/main.py
```

---

# 20. Forbidden File Ownership

The AI MUST NOT modify:

```text
backend/engines/
backend/explainability/
backend/anomaly/
frontend/
contracts/
architecture_docs/
```

unless explicitly instructed.

---

# 21. API Design Rules

The APIs should remain:

- explicit
- stable
- typed
- predictable
- frontend-friendly

Avoid:

- deeply nested responses
- unstable schemas
- hidden fields
- inconsistent naming

---

# 22. Schema Stability Rule

API response schemas are considered:

```text
Public contracts.
```

The AI MUST NOT:

- silently alter response structures
- rename response fields
- break API compatibility

without explicit approval.

---

# 23. Pydantic Usage Rule

All request/response schemas should use:

```text
Pydantic models
```

for:

- validation
- typing
- consistency
- documentation

---

# 24. API Independence Rule

The API Layer should remain:

```text
Business-logic thin.
```

The API Layer MUST NOT:

- calculate scores
- trigger recommendations internally
- duplicate anomaly logic
- recreate explainability logic

All intelligence must come from engines.

---

# 25. Error Handling Rules

Preferred:

```text
Explicit structured API errors.
```

Example:

```json
{
  "error": "Missing entity_id"
}
```

Avoid:

- stack trace exposure
- inconsistent error schemas
- silent failures

---

# 26. Logging Requirements

The API Layer should log:

- incoming requests
- endpoint execution
- engine invocation failures
- validation failures

Example:

```text
INFO:
GET /get-daily-plan executed for REP001
```

---

# 27. Authentication Philosophy

V1 prototype may initially use:

```text
Minimal/no authentication
```

Authentication should remain:

```text
future extensible
```

---

# 28. Deterministic Response Rule

The API Layer MUST preserve:

```text
Deterministic outputs.
```

Given identical backend outputs:

```text
API responses must remain identical.
```

Avoid hidden formatting randomness.

---

# 29. Allowed Dependencies

Allowed:

```text
fastapi
pydantic
typing
uvicorn
```

---

# 30. Forbidden Dependencies

Avoid:

```text
heavy orchestration frameworks
microservice infrastructure
distributed API gateways
```

unless explicitly requested later.

---

# 31. Performance Philosophy

V1 priorities:

- correctness
- stability
- explainability
- predictable orchestration

NOT:

- massive-scale optimization
- distributed serving
- extreme throughput engineering

---

# 32. Testing Requirements

The API Layer should be testable for:

- schema validation
- endpoint correctness
- response consistency
- engine orchestration
- deterministic outputs
- error handling

---

# 33. Anti-Drift Rules

The AI MUST NOT:

- embed business logic inside routes
- duplicate engine behavior
- create hidden intelligence layers
- alter backend architecture silently

The API Layer should remain:

```text
Pure orchestration and transport infrastructure.
```

---

# 34. Example Processing Flow

```text
Frontend Request
        ↓
API Validation
        ↓
Engine Invocation
        ↓
Structured Response Formatting
        ↓
Frontend Response
```

---

# 35. Review Checklist

Before accepting implementation:

| Question | Check |
|---|---|
| Are APIs schema-stable? | Yes/No |
| Is business logic isolated from routes? | Yes/No |
| Are responses deterministic? | Yes/No |
| Are validations explicit? | Yes/No |
| Are errors structured? | Yes/No |
| Is scope respected? | Yes/No |

---

# 36. Final One-Line Definition

```text
A deterministic backend orchestration layer
that exposes explainable agricultural intelligence
through stable, structured,
and modular API interfaces.
```