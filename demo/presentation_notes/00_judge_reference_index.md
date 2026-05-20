# KshetraAI Judge Reference Appendix

## Purpose

This folder contains supporting reference notes for judges who want more detail behind the final presentation deck.

The slide deck is the main story. These files provide the implementation evidence, module responsibilities, demo artifacts, verification checks, and current limitations behind that story.

## How To Read This Appendix

Start with the deck, then use these notes if you want to inspect a specific part of the system.

Recommended reading order:

1. [Data Foundation](01_data_foundation.md)
2. [Feature Generation](02_feature_generation.md)
3. [Dynamic Prioritization](03_dynamic_prioritization.md)
4. [Contextual Decision Engine](04_contextual_decision.md)
5. [Anomaly and Opportunity Detection](05_anomaly_and_opportunity_detection.md)
6. [Explainability and Trust](06_explainability_and_trust.md)
7. [Outcome Learning and Feedback](07_outcome_learning_and_feedback.md)
8. [FastAPI Backend Integration](08_fastapi_backend_integration.md)
9. [Frontend Dashboard and Workflow](09_frontend_dashboard_and_workflow.md)
10. [Demo Integration and Final Polish](10_demo_integration_testing_final_polish.md)

## What These Notes Are

- A technical appendix for the Stage 1 submission.
- A grounded summary of what was implemented.
- A reference for evidence files, outputs, scripts, and tests.
- A clear record of current prototype limits.

## What These Notes Are Not

- They are not marketing copy.
- They are not claims of production readiness.
- They do not expose raw private company data.
- They do not claim unimplemented public-data integrations as completed.

## Core Demo Scenario

The final demo is based on:

```text
rep_id: REP_0164
territory_id: TER_0164
date: 2026-05-17
selected_entity: RTL_01300
```

The demo path is:

```text
Dashboard -> Daily Plan -> Recommendation -> Explanation -> Alerts -> Outcome
```

## Final Deck

The editable PowerPoint deck is available at:

```text
demo/presentation_deck/output.pptx
```

## Grounding Principle

Every module note is written to match the current codebase and generated demo artifacts. Where a capability is a foundation or future scope, it is labeled that way.
