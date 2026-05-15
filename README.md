# KshetraAI

AI-guided field force intelligence prototype for Syngenta-style agricultural operations.

KshetraAI helps field representatives decide whom to visit, when to visit, what sequence to follow, and what product or advisory action is most relevant based on dynamic agricultural context such as weather, pest risk, crop stage, inventory, and local market signals.

## Repository Structure

- `docs/architecture/` - problem statement, system architecture, data schema, infrastructure design, and development plan.
- `docs/implementation_contracts/` - module-level implementation contracts for the data pipeline, intelligence engines, API layer, frontend, and demo flow.
- `docs/prompts/` - agent handoff and development prompts for implementation sessions.

## Build Direction

The prototype roadmap follows this sequence:

```text
Data -> Features -> Intelligence -> APIs -> UI -> Feedback
```

See `docs/architecture/09_development_plan.md` for the full implementation roadmap.
