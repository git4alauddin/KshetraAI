# Build 08 — FastAPI Backend Integration

---

# 1. Build Objective

The purpose of this build is to implement the backend API layer that exposes KshetraAI intelligence outputs through stable, structured, and controlled FastAPI endpoints.

This build converts:

```text
Processed datasets + intelligence engine outputs
```

into:

```text
API-accessible operational intelligence.
```

The API layer should allow the frontend/demo workflow to retrieve:

- daily visit plans
- entity-level recommendations
- anomaly alerts
- explanation outputs
- outcome submission responses
- system health status

This build does not implement:

- feature generation logic
- priority scoring logic
- contextual recommendation logic
- anomaly detection logic
- explanation generation logic
- frontend screens
- autonomous orchestration
- architecture redesign

---

# 2. Authoritative References

This build must follow:

- `docs/architecture/07_infrastructure_design.md`
- `docs/architecture/06_prototype.md`
- `docs/architecture/08_data_schema.md`
- `docs/architecture/09_development_plan.md`
- `docs/implementation_contracts/08_api_layer_contract.md`
- `docs/implementation_contracts/00_global_implementation_protocol.md`
- `docs/prompts/01_coding_session_prompt.md`
- `docs/prompts/03_architecture_preservation_prompt.md`

If conflict exists, use this authority order:

```text
Architecture docs
        ↓
Implementation contracts
        ↓
This build checklist
        ↓
Implementation task prompt
```

---

# 3. Build Scope

## In Scope

- Implement FastAPI application skeleton
- Implement API route modules
- Implement request/response schemas
- Expose processed intelligence outputs
- Orchestrate backend service calls
- Validate API inputs
- Return stable structured JSON responses
- Implement health endpoint
- Implement outcome submission endpoint
- Preserve API schema stability
- Add API-level logging and error handling

---

## Out of Scope

- Data pipeline implementation
- Feature engineering implementation
- Priority scoring implementation
- Contextual reasoning implementation
- Anomaly detection implementation
- Explainability generation implementation
- Frontend implementation
- Authentication complexity
- Production deployment infrastructure
- Microservices architecture

---

# 4. Core Philosophy

The API layer should behave as:

```text
A thin orchestration and transport layer.
```

The API layer should remain:

- stable
- schema-driven
- modular
- lightweight
- deterministic
- frontend-friendly

The API layer should NOT:

- contain business logic
- compute scores
- infer recommendations
- detect anomalies
- generate explanations
- duplicate engine logic

Its responsibility is ONLY:

```text
Expose backend capabilities through controlled interfaces.
```

---

# 5. Input Data Sources

This build consumes outputs from previous builds.

Expected processed inputs:

| Input / Output Source | Purpose |
|---|---|
| `ranked_visit_list.csv` | Daily visit plan |
| `recommendation_outputs.csv` | Next-best-action outputs |
| `anomaly_alerts.csv` | Alert outputs |
| `explanation_outputs.csv` | Explanation outputs |
| `outcome_log.csv` | Outcome records |
| Backend engine/service modules | Optional live orchestration |

---

# 6. Expected API Outputs

The API layer should expose:

| Endpoint | Purpose |
|---|---|
| `/health` | Service health |
| `/daily-plan` | Ranked visit list |
| `/recommendations/{entity_id}` | Entity recommendation |
| `/alerts` | Active anomaly alerts |
| `/explanations/{entity_id}` | Entity explanations |
| `/outcomes` | Submit visit outcome |
| `/entities/{entity_id}` | Entity details, if needed |

---

# 7. Expected File Scope

Implementation for this build may modify only:

```text
backend/api/
backend/main.py
backend/utils/
backend/config/
tests/
docs/implementation/
```

If required for service orchestration, limited read-only integration with backend modules is allowed.

---

# 8. Forbidden File Scope

This build must not modify:

```text
private-data/
backend/features/
backend/engines/
backend/anomaly/
backend/explainability/
backend/learning/
frontend/
docs/architecture/
docs/implementation_contracts/
```

Architecture and contracts remain read-only unless explicitly revised by humans.

---

# 9. Recommended API Structure

Suggested structure:

```text
backend/api/

├── routes/
│   ├── health_routes.py
│   ├── planning_routes.py
│   ├── recommendation_routes.py
│   ├── anomaly_routes.py
│   ├── explainability_routes.py
│   └── outcome_routes.py
│
├── schemas/
│   ├── planning_schema.py
│   ├── recommendation_schema.py
│   ├── anomaly_schema.py
│   ├── explainability_schema.py
│   └── outcome_schema.py
│
├── services/
│   ├── planning_service.py
│   ├── recommendation_service.py
│   ├── anomaly_service.py
│   ├── explainability_service.py
│   └── outcome_service.py
│
├── dependencies/
└── middleware/
```

---

# 10. API Route Philosophy

Routes should remain:

```text
Thin request/response handlers.
```

Routes may:

- validate request inputs
- call service layer
- return structured responses
- handle API-level errors

Routes must not:

- compute priority scores
- trigger business rules directly
- duplicate backend engine logic
- perform feature engineering

---

# 11. Service Layer Philosophy

Services should orchestrate:

```text
API request
        ↓
processed data / engine output access
        ↓
response assembly
```

Services should not own core intelligence logic.

---

# 12. Required Endpoint — Health

## Purpose

Verify backend availability.

## Endpoint

```text
GET /health
```

## Expected Response

```json
{
  "status": "ok",
  "service": "kshetraai-backend"
}
```

---

# 13. Required Endpoint — Daily Plan

## Purpose

Return ranked visit plan for a representative or territory.

## Endpoint

```text
GET /daily-plan
```

## Example Query Parameters

```text
rep_id=REP001
territory_id=TERR_WARDHA_01
date=2026-05-16
```

## Expected Response

```json
{
  "rep_id": "REP001",
  "territory_id": "TERR_WARDHA_01",
  "ranked_entities": [
    {
      "rank": 1,
      "entity_id": "ENT001",
      "entity_name": "Ramesh Agro Center",
      "priority_score": 84.7,
      "priority_level": "Critical",
      "main_reason": "High agronomic urgency and inventory need"
    }
  ]
}
```

---

# 14. Required Endpoint — Recommendation Detail

## Purpose

Return contextual next-best-action for one entity.

## Endpoint

```text
GET /recommendations/{entity_id}
```

## Expected Response

```json
{
  "entity_id": "ENT001",
  "risk_or_opportunity": "Possible fungal disease risk",
  "recommended_actions": [
    "Inspect crop symptoms",
    "Discuss fungicide advisory",
    "Recommend inventory replenishment"
  ],
  "recommended_product_category": "Fungicide",
  "confidence_level": "High"
}
```

---

# 15. Required Endpoint — Alerts

## Purpose

Return anomaly and opportunity alerts.

## Endpoint

```text
GET /alerts
```

## Example Query Parameters

```text
territory_id=TERR_WARDHA_01
severity=Critical
```

## Expected Response

```json
{
  "alerts": [
    {
      "alert_id": "ALERT001",
      "entity_id": "ENT001",
      "alert_type": "Stock-Out Risk",
      "severity_score": 91,
      "severity_level": "Critical",
      "confidence_level": "High"
    }
  ]
}
```

---

# 16. Required Endpoint — Explanation Detail

## Purpose

Return explanation for a recommendation, priority, or alert.

## Endpoint

```text
GET /explanations/{entity_id}
```

## Expected Response

```json
{
  "entity_id": "ENT001",
  "explanations": [
    {
      "explanation_type": "recommendation",
      "summary_text": "A fungicide advisory discussion is recommended because cotton is in a vulnerable flowering stage and recent rainfall and humidity increase fungal disease risk.",
      "evidence_items": [
        "Cotton flowering stage",
        "High rainfall deviation",
        "High humidity",
        "NDVI stress detected"
      ],
      "confidence_level": "High"
    }
  ]
}
```

---

# 17. Required Endpoint — Outcome Submission

## Purpose

Capture visit outcome and rep feedback.

## Endpoint

```text
POST /outcomes
```

## Example Request

```json
{
  "recommendation_id": "REC001",
  "entity_id": "ENT001",
  "rep_id": "REP001",
  "visit_completed": true,
  "recommendation_followed": true,
  "sale_made": true,
  "order_placed": true,
  "order_value": 18500,
  "rep_feedback": "Recommendation was useful.",
  "alert_validated": true
}
```

## Expected Response

```json
{
  "status": "success",
  "message": "Outcome recorded successfully."
}
```

---

# 18. Pydantic Schema Requirements

All request and response payloads should be defined using:

```text
Pydantic models.
```

Schemas should remain:

- explicit
- stable
- typed
- frontend-friendly
- deterministic

---

# 19. Error Handling Requirements

API errors should be structured and explicit.

Example:

```json
{
  "error": "Missing required parameter: territory_id",
  "status_code": 400
}
```

Avoid:

- raw stack traces
- inconsistent error shapes
- silent empty responses

---

# 20. Logging Requirements

The API layer should log:

- endpoint access
- validation failures
- service errors
- missing data warnings
- outcome submission events

Avoid excessive noisy logging.

---

# 21. Determinism Requirements

Given identical processed data and request parameters:

```text
API responses must remain identical.
```

Requirements:

- stable ordering
- stable response schemas
- stable filtering
- stable error responses

---

# 22. Output Schema Stability

API responses become frontend contracts.

The API layer must preserve:

- stable field names
- stable nesting patterns
- stable response structure
- stable status/error shapes

---

# 23. Configuration Requirements

Configurable API settings may include:

```text
data_paths.yaml
api_settings.yaml
```

Avoid hardcoding dataset paths across route files.

---

# 24. Testing Requirements

Tests should validate:

- health endpoint response
- daily plan response schema
- recommendation response schema
- alert response schema
- explanation response schema
- outcome submission validation
- deterministic response behavior
- structured error handling

---

# 25. Anti-Drift Rules

This build MUST NOT:

- implement intelligence logic inside API routes
- duplicate engine logic
- modify backend engines
- modify feature generation
- modify anomaly detection
- modify explanation generation
- implement frontend UI
- redesign architecture
- silently alter schemas

This build is ONLY responsible for:

```text
FastAPI orchestration and transport infrastructure.
```

---

# 26. Deliverables

Expected outputs:

- FastAPI app entrypoint
- route modules
- service modules
- Pydantic schemas
- health endpoint
- daily plan endpoint
- recommendation endpoint
- alerts endpoint
- explanation endpoint
- outcome submission endpoint
- API tests
- API validation layer

---

# 27. Completion Criteria

This build is complete when:

- FastAPI app starts successfully
- health endpoint works
- daily plan endpoint returns stable ranked outputs
- recommendation endpoint returns stable action outputs
- alerts endpoint returns stable alert outputs
- explanations endpoint returns stable explanation outputs
- outcome endpoint validates and records submissions
- response schemas remain stable
- API contains no business logic duplication
- architecture boundaries remain preserved

---

# 28. Final One-Line Definition

```text
A deterministic FastAPI orchestration layer
that exposes KshetraAI intelligence outputs
through stable,
typed,
frontend-ready API endpoints
without duplicating core business logic.
```

---

# 29. Task Breakdown & Execution Order

Use `docs/implementation/build_execution_prompt.md` while working through this build.

Each task heading below is intended to be usable as the future commit heading. Work one task at a time: present the heading, short brief, expected file scope, and what will not be touched; then wait for explicit implementation approval.

| Order | Commit Heading | Scope | Primary Files |
|---|---|---|---|
| 1 | Build 08: Implement FastAPI app entrypoint | Wire the app startup, router registration, and health-ready structure without business logic duplication. | `backend/main.py`, `backend/api/routes/health_routes.py` |
| 2 | Build 08: Define API schemas | Create typed request and response schemas for planning, recommendations, alerts, explanations, and outcomes. | `backend/api/schemas/` |
| 3 | Build 08: Implement planning and recommendation routes | Expose daily plan and recommendation outputs from existing engines or processed views. | `backend/api/routes/planning_routes.py`, `backend/api/routes/recommendation_routes.py` |
| 4 | Build 08: Implement alert and explainability routes | Expose anomaly alerts and explanation outputs without recalculating core business logic in routes. | `backend/api/routes/anomaly_routes.py`, `backend/api/routes/explainability_routes.py` |
| 5 | Build 08: Implement outcome and health routes | Accept outcome submissions and provide operational health checks with stable responses. | `backend/api/routes/outcome_routes.py`, `backend/api/routes/health_routes.py` |
| 6 | Build 08: Add API tests | Validate route schemas, happy paths, missing input behavior, and stable response shapes. | `tests/` |
| 7 | Build 08: Verify API integration checklist | Confirm this build exposes existing intelligence only and does not modify scoring, recommendations, alerts, explanations, or frontend behavior. | `docs/implementation/08_fastApi_backend_integration.md` |

Per-task completion rule: after the human commits and says done, verify the committed scope, confirm the matching checklist items, and propose the next task.
