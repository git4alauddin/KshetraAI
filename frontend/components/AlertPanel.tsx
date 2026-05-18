import { statusToneClass } from "../utils/statusTone";

export type AlertPanelData = {
  alertId: string;
  entityId: string;
  alertType: string;
  severityScore: number;
  severityLevel: string;
  confidenceLevel: string;
};

type AlertPanelProps = {
  alerts: AlertPanelData[];
};

export function AlertPanel({ alerts }: AlertPanelProps) {
  return (
    <section className="panel">
      <div className="panel-heading">
        <p className="eyebrow">Active Signals</p>
        <h2>Alerts</h2>
      </div>
      <div className="alert-list">
        {alerts.map((alert) => (
          <article className="alert-row" key={alert.alertId}>
            <div>
              <h3>{alert.alertType}</h3>
              <p>{alert.entityId}</p>
            </div>
            <div className="alert-status-grid">
              <div className="alert-status-block">
                <span>Score</span>
                <div>
                  <strong>{alert.severityScore.toFixed(1)}</strong>
                </div>
              </div>
              <div className="alert-status-block">
                <span>Severity</span>
                <div>
                  <span className={statusToneClass(alert.severityLevel)}>{alert.severityLevel}</span>
                </div>
              </div>
              <div className="alert-status-block">
                <span>Confidence</span>
                <div>
                  <span className={statusToneClass(alert.confidenceLevel)}>{alert.confidenceLevel}</span>
                </div>
              </div>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
