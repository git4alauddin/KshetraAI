import { useEffect, useState } from "react";

import { AlertPanel, type AlertPanelData } from "../components/AlertPanel";
import { LoadingState } from "../components/LoadingState";
import { useAlerts } from "../hooks/useAlerts";
import type { AlertResponse } from "../services/apiClient";
import type { WorkflowSelection } from "../state/workflowStore";

type AlertsViewProps = {
  selection: WorkflowSelection;
  onOpenOutcome: () => void;
};

const ALERT_PAGE_SIZE = 3;

export function AlertsView({ selection, onOpenOutcome }: AlertsViewProps) {
  const [page, setPage] = useState(1);

  useEffect(() => {
    setPage(1);
  }, [selection.territoryId]);

  const { data, error, isLoading, reload } = useAlerts({
    page,
    pageSize: ALERT_PAGE_SIZE,
    territoryId: selection.territoryId
  });
  const alerts = data?.alerts.map(toAlertPanelData) ?? [];
  const totalPages = data?.total_pages ?? 0;
  const canGoPrevious = page > 1;
  const canGoNext = totalPages > 0 && page < totalPages;

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
            <strong>GET /alerts?page={page}&page_size={ALERT_PAGE_SIZE}</strong>
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

      {!isLoading && !error && alerts.length > 0 && (
        <>
          <AlertPanel alerts={alerts} />
          <section className="pagination-row" aria-label="Alert pagination">
            <button
              className="secondary-button"
              disabled={!canGoPrevious}
              onClick={() => setPage((currentPage) => Math.max(1, currentPage - 1))}
              type="button"
            >
              Previous
            </button>
            <span>
              Page {data?.page ?? page} of {totalPages || 1} - {data?.total_count ?? alerts.length} alerts
            </span>
            <button
              className="secondary-button"
              disabled={!canGoNext}
              onClick={() => setPage((currentPage) => currentPage + 1)}
              type="button"
            >
              Next
            </button>
          </section>
        </>
      )}
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
