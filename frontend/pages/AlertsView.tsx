import { AlertPanel, type AlertPanelData } from "../components/AlertPanel";
import { LoadingState } from "../components/LoadingState";
import { useAlerts } from "../hooks/useAlerts";
import type { AlertResponse } from "../services/apiClient";
import type { WorkflowSelection } from "../state/workflowStore";

type AlertsViewProps = {
  selection: WorkflowSelection;
  onOpenOutcome: () => void;
};

export function AlertsView({ selection, onOpenOutcome }: AlertsViewProps) {
  const { data, error, isLoading, reload } = useAlerts({
    territoryId: selection.territoryId
  });
  const alerts = data?.alerts.map(toAlertPanelData) ?? [];

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

      <section className="panel">
        <div className="panel-heading">
          <p className="eyebrow">Alert Request</p>
          <h3>Backend API filters</h3>
        </div>
        <div className="detail-grid">
          <div>
            <span>Territory</span>
            <strong>{selection.territoryId}</strong>
          </div>
          <div>
            <span>Endpoint</span>
            <strong>GET /alerts</strong>
          </div>
          <div>
            <span>Source</span>
            <strong>Backend API</strong>
          </div>
        </div>
      </section>

      {isLoading && <LoadingState label="Loading alerts from backend API" />}

      {!isLoading && error && (
        <section className="state-panel state-panel-error" role="alert">
          <div>
            <strong>Unable to load alerts</strong>
            <span>{error}</span>
          </div>
          <button className="secondary-button" onClick={() => void reload()} type="button">
            Retry
          </button>
        </section>
      )}

      {!isLoading && !error && alerts.length === 0 && (
        <section className="state-panel">
          <div>
            <strong>No active alerts returned</strong>
            <span>The API returned no anomaly or opportunity alerts for this territory.</span>
          </div>
          <button className="secondary-button" onClick={() => void reload()} type="button">
            Refresh
          </button>
        </section>
      )}

      {!isLoading && !error && alerts.length > 0 && <AlertPanel alerts={alerts} />}
    </div>
  );
}

function toAlertPanelData(alert: AlertResponse): AlertPanelData {
  return {
    alertId: alert.alert_id,
    alertType: alert.alert_type,
    confidenceLevel: alert.confidence_level,
    entityId: alert.entity_id,
    severityLevel: alert.severity_level,
    severityScore: alert.severity_score
  };
}
