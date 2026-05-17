export type WorkflowStep =
  | "dashboard"
  | "visit-plan"
  | "recommendation"
  | "alerts"
  | "outcome";

export type WorkflowSelection = {
  repId: string;
  territoryId: string;
  planDate: string;
  selectedEntityId: string;
};

export const defaultWorkflowSelection: WorkflowSelection = {
  repId: "REP001",
  territoryId: "TERR_WARDHA_01",
  planDate: "2026-05-17",
  selectedEntityId: "ENT001"
};

export const workflowSteps: Array<{ id: WorkflowStep; label: string; description: string }> = [
  {
    id: "dashboard",
    label: "Overview",
    description: "Rep, territory, and workflow readiness"
  },
  {
    id: "visit-plan",
    label: "Daily Plan",
    description: "Ranked visits from the backend API"
  },
  {
    id: "recommendation",
    label: "Recommendation",
    description: "Next best action and explanation panels"
  },
  {
    id: "alerts",
    label: "Alerts",
    description: "Anomaly and opportunity alerts"
  },
  {
    id: "outcome",
    label: "Outcome",
    description: "Visit result and feedback capture"
  }
];
