import { AlertPanel, type AlertPanelData } from "../components/AlertPanel";
import type { WorkflowSelection } from "../state/workflowStore";

type AlertsViewProps = {
  selection: WorkflowSelection;
  onOpenOutcome: () => void;
};

const shellAlerts: AlertPanelData[] = [
  {
    alertId: "Awaiting /alerts",
    entityId: "Backend alerts",
    alertType: "API client pending",
    severityScore: 0,
    severityLevel: "Pending",
    confidenceLevel: "Pending"
  }
];

export function AlertsView({ selection, onOpenOutcome }: AlertsViewProps) {
  return (
    <div className="page-stack">
      <header className="page-header">
        <div>
          <p className="eyebrow">Alert Review</p>
          <h2>{selection.territoryId}</h2>
        </div>
        <button className="primary-button" onClick={onOpenOutcome} type="button">
          Capture outcome
        </button>
      </header>

      <AlertPanel alerts={shellAlerts} />
    </div>
  );
}
